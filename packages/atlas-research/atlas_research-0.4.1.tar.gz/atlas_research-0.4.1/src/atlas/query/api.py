
from __future__ import annotations
from typing import Any, Dict
import networkx as nx

class QueryAPI:
    def __init__(self, store):
        self.store = store

    def neighborhood(self, node_id: str, depth: int = 1):
        return self.store.subgraph_by_hops(node_id, depth=depth)

    def paths(self, source: str, target: str, cutoff: int = 3):
        try:
            return list(nx.all_simple_paths(self.store.g, source=source, target=target, cutoff=cutoff))
        except nx.NetworkXNoPath:
            return []
