# src/atlas/viz/visualizer.py
"""
Visualizer Stub (for backward compatibility)
--------------------------------------------
Atlas v0.4.x에서는 `export_pyvis()`로 통합되었지만,
기존 예제들의 `Visualizer` 클래스를 안전하게 호환하기 위해
간단한 wrapper 형태로 제공합니다.
"""

from ..visualize import export_pyvis


class Visualizer:
    def __init__(self, height: str = "900px", width: str = "100%", bgcolor: str = "#ffffff"):
        self.height = height
        self.width = width
        self.bgcolor = bgcolor
        self._edges = []
        self._nodes = {}

    def add_node(self, node_id: str, label: str, node_type: str = "paper"):
        self._nodes[node_id] = {"label": label, "type": node_type}

    def add_edge(self, source: str, target: str, label: str = ""):
        self._edges.append((source, target, label))

    def show(self, output_path: str):
        """
        기존 Visualizer API 호환:
        내부적으로 export_pyvis() 호출.
        """
        import networkx as nx

        G = nx.Graph()
        for node_id, data in self._nodes.items():
            G.add_node(node_id, label=data["label"], type=data["type"])
        for s, t, label in self._edges:
            G.add_edge(s, t, relation=label or "related")

        export_pyvis(G, out_dir="outputs", name=output_path.split("/")[-1].replace(".html", ""), bgcolor=self.bgcolor)
        print(f"[Visualizer Stub] Graph visualization saved to {output_path}")
