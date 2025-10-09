from pyvis.network import Network
import os

class Visualizer:
    def __init__(self, height="900px", width="100%", bgcolor="#fff", font_color="black"):
        self.net = Network(height=height, width=width, bgcolor=bgcolor, font_color=font_color)
        self.net.force_atlas_2based()  # 기본 물리엔진

    def add_node(self, node_id, label, node_type="paper"):
        color_map = {"paper": "#1f77b4", "code": "#2ca02c", "dataset": "#ff7f0e"}
        self.net.add_node(node_id, label=label, color=color_map.get(node_type, "#999"))

    def add_edge(self, src, dst, label=None):
        self.net.add_edge(src, dst, label=label)

    def show(self, path="outputs/graphs/network.html"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.net.repulsion(
            node_distance=450,
            central_gravity=0.3,
            spring_length=220,
            spring_strength=0.03,
            damping=0.8
        )
        self.net.write_html(path)
        print(f"Graph saved to {path}")
