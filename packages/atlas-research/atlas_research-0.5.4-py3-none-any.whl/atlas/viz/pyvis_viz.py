# src/atlas/viz/pyvis_viz.py
"""
PyVisVisualizer Compatibility Stub
----------------------------------
Atlas v0.4.x 이상 버전에서 제거된 모듈.
기존 예제(`from atlas.viz.pyvis_viz import Visualizer`)
호환을 위해 유지되는 간단한 wrapper입니다.
"""

from ..visualize import export_pyvis
import networkx as nx


class PyVisVisualizer:
    """
    구버전 PyVis 기반 시각화 클래스의 호환용 래퍼.
    내부적으로 export_pyvis() 호출.
    """

    def __init__(self, height: str = "900px", width: str = "100%", bgcolor: str = "#ffffff"):
        self.height = height
        self.width = width
        self.bgcolor = bgcolor
        self.G = nx.Graph()

    def add_node(self, node_id: str, label: str, node_type: str = "paper"):
        self.G.add_node(node_id, label=label, type=node_type)

    def add_edge(self, source: str, target: str, label: str = "related"):
        self.G.add_edge(source, target, relation=label)

    def render(self, output_path: str):
        """export_pyvis()로 실제 시각화 수행"""
        name = output_path.split("/")[-1].replace(".html", "")
        export_pyvis(self.G, out_dir="outputs", name=name, bgcolor=self.bgcolor)
        print(f"[PyVisVisualizer Stub] Graph saved to {output_path}")


# ✅ 구버전 호환용 별칭
Visualizer = PyVisVisualizer
