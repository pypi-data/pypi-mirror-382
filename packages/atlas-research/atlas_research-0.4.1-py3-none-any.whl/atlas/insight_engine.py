from __future__ import annotations
from typing import List, Tuple
from pathlib import Path
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .data_sources.arxiv_client import search_arxiv
from .graph_builder import build_graph
from .types import Paper
from .visualize import export_pyvis

def summarize_corpus(papers: List[Paper], top_terms: int = 15) -> List[str]:
    docs = [f"{p.title}\n{p.summary}" for p in papers]
    if not docs:
        return []
    vec = TfidfVectorizer(max_features=5000, stop_words="english")
    X = vec.fit_transform(docs)
    vocab = np.array(vec.get_feature_names_out())
    weights = np.asarray(X.mean(axis=0)).ravel()
    top_idx = np.argsort(-weights)[:top_terms]
    return vocab[top_idx].tolist()

def recommend_next_papers(papers: List[Paper], k: int = 5) -> List[Tuple[str, float]]:
    if len(papers) < 2:
        return []
    docs = [f"{p.title} \n {p.summary}" for p in papers]
    vec = TfidfVectorizer(max_features=5000, stop_words="english")
    X = vec.fit_transform(docs)
    sim = cosine_similarity(X)
    scores = sim.mean(axis=1)
    order = np.argsort(-scores)
    return [(papers[idx].title, float(scores[idx])) for idx in order[:k]]

def insight_report(papers: List[Paper], out_dir: str | Path = "outputs", name: str = "report") -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    terms = summarize_corpus(papers)
    recs = recommend_next_papers(papers)
    payload = {
        "top_terms": terms,
        "recommendations": [{"title": t, "score": s} for t, s in recs],
        "num_papers": len(papers),
    }
    path = out / f"{name}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def build_and_report(query: str, max_results: int = 50, out_dir: str | Path = "outputs"):
    papers = search_arxiv(query=query, max_results=max_results)
    G, _ = build_graph(papers)
    html_path = export_pyvis(G, out_dir=out_dir, name=f"graph_{query.replace(' ', '_')}")
    rpt_path = insight_report(papers, out_dir=out_dir, name=f"insight_{query.replace(' ', '_')}")
    return html_path, rpt_path
