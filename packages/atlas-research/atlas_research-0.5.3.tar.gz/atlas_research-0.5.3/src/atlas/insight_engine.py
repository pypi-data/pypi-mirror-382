# src/atlas/insight_engine.py
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Tuple, Any
import json
import networkx as nx

from .visualize import export_pyvis
from .data_sources.arxiv_client import search_arxiv

# Scikit-learn 기반 TF-IDF / 유사도 계산
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def _top_k_keywords(texts: List[str], k: int = 12) -> List[List[Tuple[str, float]]]:
    """
    문서 리스트에 대해 TF-IDF 기반 상위 키워드 추출.
    반환: 각 문서별 [(keyword, score), ...]
    """
    if not texts:
        return []

    vec = TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
    )
    X = vec.fit_transform(texts)
    terms = vec.get_feature_names_out()

    results: List[List[Tuple[str, float]]] = []
    for i in range(X.shape[0]):
        row = X.getrow(i).toarray().ravel()
        top_idx = row.argsort()[::-1][:k]
        results.append([(terms[j], float(row[j])) for j in top_idx if row[j] > 0])
    return results


def _paper_similarity_matrix(texts: List[str]) -> Any:
    """
    문서 임베딩(TF-IDF)로 코사인 유사도 행렬 생성.
    """
    if not texts:
        return None
    vec = TfidfVectorizer(
        max_features=6000,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
    )
    X = vec.fit_transform(texts)
    return linear_kernel(X, X)


def _extract_author_names(paper) -> str:
    """
    논문 객체의 authors 필드에서 이름만 안전하게 추출.
    - Author 객체 → .name 사용
    - 문자열 → 그대로 사용
    """
    raw_authors = getattr(paper, "authors", [])
    names = []
    for a in raw_authors:
        if hasattr(a, "name"):
            names.append(a.name)
        elif isinstance(a, str):
            names.append(a)
    return ", ".join(names)


def build_and_report(
    query: str,
    max_results: int = 20,
    out_dir: str = "outputs",
) -> Tuple[str, str]:
    """
    End-to-End 파이프라인:
    - arXiv 검색 → 네트워크 그래프 구성 → 시각화 HTML + 인사이트 JSON 저장
    - 반환: (html_path, report_path)
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # 1️⃣ 데이터 수집
    papers = search_arxiv(query, max_results=max_results)
    if not papers:
        empty_html = out / f"graph_{query.replace(' ', '_')}.html"
        empty_report = out / f"insight_{query.replace(' ', '_')}.json"
        empty_html.write_text("<html><body><h3>No results</h3></body></html>", encoding="utf-8")
        empty_report.write_text(json.dumps({"query": query, "papers": []}, indent=2), encoding="utf-8")
        return str(empty_html), str(empty_report)

    titles = [getattr(p, "title", "") for p in papers]
    abstracts = [getattr(p, "summary", "") for p in papers]
    ids = [getattr(p, "id", f"paper_{i}") for i, p in enumerate(papers)]
    urls = [getattr(p, "link", "") for p in papers]
    authors_list = [_extract_author_names(p) for p in papers]  # ✅ 안전 처리됨

    # 2️⃣ 키워드 / 유사도 계산
    top_kw_per_paper = _top_k_keywords(abstracts, k=10)
    sim_mat = _paper_similarity_matrix([t + " " + a for t, a in zip(titles, abstracts)])

    # 3️⃣ 그래프 구축
    G = nx.Graph()

    # (1) 논문 노드
    for pid, title, auth in zip(ids, titles, authors_list):
        G.add_node(
            pid,
            type="paper",
            label=title or pid,
            authors=auth,
            url=urls[ids.index(pid)] if pid in ids else "",
        )

    # (2) 키워드 노드 + 엣지 (논문→키워드)
    for pid, kw_list in zip(ids, top_kw_per_paper):
        for kw, score in kw_list[:8]:
            kw_id = f"kw:{kw}"
            if not G.has_node(kw_id):
                G.add_node(kw_id, type="keyword", label=kw)
            G.add_edge(pid, kw_id, relation="mentions", weight=float(score))

    # (3) 논문 간 유사도 엣지 (논문↔논문)
    if sim_mat is not None:
        n = len(ids)
        for i in range(n):
            for j in range(i + 1, n):
                sim = float(sim_mat[i, j])
                if sim >= 0.22:
                    G.add_edge(ids[i], ids[j], relation="similar", weight=sim)

    # (4) relation 누락 보정
    for _, _, data in G.edges(data=True):
        if "relation" not in data and "label" not in data:
            data["relation"] = "related"

    # 4️⃣ 시각화 출력 (HTML)
    html_path = export_pyvis(
        G,
        out_dir=out_dir,
        name=f"graph_{query.replace(' ', '_')}",
        bgcolor="#ffffff",
    )

    # 5️⃣ 인사이트 리포트(JSON)
    report: Dict[str, Any] = {
        "query": query,
        "count": len(papers),
        "papers": [],
    }

    id_to_idx = {pid: i for i, pid in enumerate(ids)}

    for pid, title, url, kws in zip(ids, titles, urls, top_kw_per_paper):
        # 인접 논문(유사 논문) 상위 5개만
        neighbors = []
        if pid in G:
            for nbr in G.neighbors(pid):
                if nbr.startswith("kw:"):
                    continue
                w = G[pid][nbr].get("weight", 1.0)
                neighbors.append((nbr, float(w)))
            neighbors.sort(key=lambda x: x[1], reverse=True)
            neighbors = [n for n, _ in neighbors[:5]]

        report["papers"].append(
            {
                "id": pid,
                "title": title,
                "url": url,
                "authors": authors_list[ids.index(pid)],
                "top_keywords": [{"term": k, "score": s} for k, s in kws[:8]],
                "similar_papers": neighbors,
            }
        )

    report_path = Path(out_dir) / f"insight_{query.replace(' ', '_')}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return html_path, str(report_path)
