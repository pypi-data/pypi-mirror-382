
from __future__ import annotations
from typing import Iterable, Tuple

class Linker:
    def __init__(self, store):
        self.store = store

    def cites(self, paper_from: str, paper_to: str, **attrs):
        self.store.add_edge(paper_from, paper_to, etype="CITES", **attrs)

    def implements(self, repo: str, paper: str, **attrs):
        self.store.add_edge(repo, paper, etype="IMPLEMENTS", **attrs)

    def uses(self, src: str, dataset: str, **attrs):
        self.store.add_edge(src, dataset, etype="USES", **attrs)

    def relates(self, a: str, b: str, **attrs):
        self.store.add_edge(a, b, etype="RELATES_TO", **attrs)

    def auto(self):
        # MVP: 자리표시자. 향후 키워드/임베딩 유사도 기반 제안으로 확장
        return {"status": "ok", "message": "auto-linker stub (implement keyword/embedding match later)"}
