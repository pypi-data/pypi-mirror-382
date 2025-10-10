# src/atlas/ingest/basic.py
from __future__ import annotations

from typing import List, Dict, Any
import json
from pathlib import Path

from ..types import NodeType
from ..cache import get, set


class Ingestor:
    """
    Atlas 기본 데이터 수집기 (v0.4.2b)
    ---------------------------------------------------
    - arXiv, code repo, dataset 등 다양한 노드 타입 지원
    - 간단한 JSON 입력 → 그래프 노드/엣지 구조화 가능
    - 캐시(.atlas_cache)를 활용해 중복 요청 최소화
    """

    def __init__(self, source: str = "local", cache: bool = True):
        self.source = source
        self.cache = cache
        self._data: Dict[str, Any] = {}

    # ---------------------------------------------------

    def from_json(self, path: str | Path) -> List[Dict[str, Any]]:
        """
        JSON 파일을 읽어 노드 리스트 반환
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"[Ingestor] File not found: {p}")
        data = json.loads(p.read_text(encoding="utf-8"))
        self._data = data
        return data

    # ---------------------------------------------------

    def from_arxiv(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        arXiv API 검색 결과를 수집하고 캐싱.
        """
        from ..data_sources.arxiv_client import search_arxiv

        cache_key = f"arxiv::{query}::{max_results}"
        if self.cache:
            cached = get(cache_key)
            if cached:
                return cached

        results = search_arxiv(query, max_results=max_results)
        data = [p.model_dump() for p in results]

        if self.cache:
            set(cache_key, data)
        self._data = data
        return data

    # ---------------------------------------------------

    def summarize(self) -> None:
        """
        로드된 데이터 간단 요약 출력
        """
        if not self._data:
            print("[Ingestor] No data loaded.")
            return

        if isinstance(self._data, list):
            print(f"[Ingestor] Loaded {len(self._data)} records.")
            if len(self._data) > 0 and isinstance(self._data[0], dict):
                print(f"Fields: {list(self._data[0].keys())[:6]}")
        else:
            print(f"[Ingestor] Data type: {type(self._data)}")

    # ---------------------------------------------------

    def to_nodes(self, node_type: NodeType = NodeType.PAPER) -> List[Dict[str, Any]]:
        """
        수집 데이터를 Atlas 그래프 노드 구조로 변환
        """
        if not self._data:
            raise ValueError("[Ingestor] No data to convert.")

        nodes = []
        for item in self._data:
            node = {
                "id": item.get("id") or item.get("identifier") or f"{node_type.value.lower()}_{len(nodes)}",
                "label": item.get("title", "Untitled"),
                "type": node_type.value,
                "meta": {
                    "authors": item.get("authors", []),
                    "summary": item.get("summary", ""),
                    "link": item.get("link", ""),
                },
            }
            nodes.append(node)
        return nodes

    # ---------------------------------------------------

    def save_local(self, filename: str = "ingest_output.json", out_dir: str = "outputs") -> Path:
        """
        현재 데이터셋을 로컬에 저장
        """
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        p = Path(out_dir) / filename
        p.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[Ingestor] Saved → {p}")
        return p

