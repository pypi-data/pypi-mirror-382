
from __future__ import annotations
from typing import Optional
from pathlib import Path

# ---- Atlas Navy Theme ----
BG_COLOR = "#13264E"
NODE_COLORS = {
    "Paper":   "#AFC7FF",
    "CodeRepo":"#A9E6C6",
    "Dataset": "#FFD08A",
    "Concept": "#D6B2FF",
    "Author":  "#E6E6E6",
    "Venue":   "#E6E6E6",
}
EDGE_STYLE = {
    "CITES":       {"dashes": True,  "width": 1},
    "IMPLEMENTS":  {"dashes": False, "width": 3},
    "USES":        {"dashes": False, "width": 2},
    "RELATES_TO":  {"dashes": True,  "width": 1},
}

class Visualizer:
    def __init__(self, store):
        self.store = store

    def _node_color(self, ntype: str) -> str:
        return NODE_COLORS.get(ntype, "#FFFFFF")

    def _edge_style(self, etype: str):
        return EDGE_STYLE.get(etype, {"dashes": False, "width": 1})

    def show(self, subgraph=None, out_html: Optional[str] = None, height: str = "700px", physics: bool = True):
        """Render the graph (or subgraph) to an HTML file."""
        try:
            from pyvis.network import Network
        except Exception as e:
            raise RuntimeError("pyvis가 설치되어 있어야 합니다. pip install pyvis") from e

        G = subgraph or self.store.g
        net = Network(height=height, width='100%', bgcolor=BG_COLOR, font_color='white', notebook=False, directed=True)
        net.toggle_physics(physics)

        # Nodes
        for nid, data in G.nodes(data=True):
            ntype = data.get("ntype", "")
            label = data.get("title") or data.get("name") or nid
            url = data.get("url", "")
            year = data.get("year", "")
            color = self._node_color(ntype)
            tooltip_parts = [f"<b>{label}</b>", f"Type: {ntype}"]
            if year: tooltip_parts.append(f"Year: {year}")
            if url: tooltip_parts.append(f"URL: {url}")
            tooltip = "<br>".join(tooltip_parts)
            size = 22 if ntype in ("Paper","CodeRepo","Dataset") else 16
            net.add_node(nid, label=label, title=tooltip, color=color, size=size, shape="dot")

        # Edges
        for u, v, key, data in G.edges(keys=True, data=True):
            etype = data.get("etype", key)
            style = self._edge_style(etype)
            net.add_edge(u, v, label=etype, color="#FFFFFF", **style)

        out_html = out_html or "outputs/graph.html"
        Path(out_html).parent.mkdir(parents=True, exist_ok=True)
        net.write_html(out_html, notebook=False)
        return out_html
