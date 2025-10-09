
from __future__ import annotations
import json, os, networkx as nx
from typing import Dict, Any
from enum import Enum

class GraphStore:
    def __init__(self):
        self.g = nx.MultiDiGraph()  # 방향/복수 엣지 허용

    def add_node(self, ntype: str, id: str, **attrs):
        nid = f"{ntype}:{id}"
        if nid not in self.g:
            self.g.add_node(nid, ntype=ntype, **attrs)
        else:
            # 업데이트 형태로 동작
            self.g.nodes[nid].update(attrs)
        return nid

    def add_edge(self, src: str, dst: str, etype: str = "RELATES_TO", **attrs):
        self.g.add_edge(src, dst, key=etype, etype=etype, **attrs)

    def subgraph_by_hops(self, center_id: str, depth: int = 1):
        # BFS 방식으로 이웃 탐색
        nodes = set([center_id])
        frontier = set([center_id])
        for _ in range(depth):
            nxt = set()
            for u in frontier:
                for v in self.g.predecessors(u):
                    nxt.add(v)
                for v in self.g.successors(u):
                    nxt.add(v)
            nodes |= nxt
            frontier = nxt
        return self.g.subgraph(nodes).copy()

    def save(self, path: str):
        data = nx.readwrite.json_graph.node_link_data(self.g)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.g = nx.readwrite.json_graph.node_link_graph(data, multigraph=True, directed=True)
