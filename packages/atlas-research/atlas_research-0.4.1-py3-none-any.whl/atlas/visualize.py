"""
visualize.py (v0.4.0-V stable)
------------------------------
Atlas Graph Visualization Module — View-Optimized Edition
- PyVis ForceAtlas2 레이아웃 튜닝
- 노드 간 간격 확장 및 중심 논문 강조
- 겹침 최소화, 가독성 향상
"""

import networkx as nx
from pyvis.network import Network
from pathlib import Path


def export_pyvis(G: nx.Graph, out_dir: str = "outputs", name: str = "atlas_graph") -> str:
    """
    네트워크 그래프를 PyVis 기반으로 시각화하여 HTML로 저장.
    """

    # ✅ 출력 경로
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    html_path = Path(out_dir) / f"{name}.html"

    # ✅ PyVis 네트워크 기본 설정
    net = Network(
        height="900px",
        width="100%",
        bgcolor="#fafafa",
        font_color="#222",
        notebook=False,
        directed=False
    )

    # ✅ 노드 색상 팔레트
    COLOR_MAP = {
        "paper": "#3B82F6",     # 파랑 (핵심 논문)
        "author": "#9CA3AF",    # 회색 (저자)
        "keyword": "#FACC15",   # 노랑 (핵심 키워드)
        "dataset": "#34D399",   # 민트 (데이터셋)
        "code": "#A855F7",      # 보라 (코드)
        "venue": "#FB923C",     # 주황 (학회/저널)
        "concept": "#60A5FA"    # 연파랑 (개념)
    }

    # ✅ 노드 수 제한 (복잡도 조절)
    MAX_NODES = 150
    nodes_to_add = list(G.nodes(data=True))
    if len(nodes_to_add) > MAX_NODES:
        nodes_to_add = nodes_to_add[:MAX_NODES]

    visible_nodes = {n for n, _ in nodes_to_add}

    # ✅ 노드 추가
    for node, attrs in nodes_to_add:
        ntype = attrs.get("type", "paper").lower()
        label = attrs.get("label", node)
        color = COLOR_MAP.get(ntype, "#A3A3A3")

        # 중심 논문은 크게, 키워드는 중간
        size = 35 if ntype == "paper" else 18 if ntype == "keyword" else 10

        net.add_node(
            node,
            label=label,
            color=color,
            size=size,
            title=f"{ntype}",
        )

    # ✅ 엣지 추가 (필터링 + 안전 검사)
    for u, v, data in G.edges(data=True):
        if u not in visible_nodes or v not in visible_nodes:
            continue
        weight = data.get("weight", 1.0)
        if weight < 0.5:
            continue
        relation = data.get("relation", "related")
        net.add_edge(u, v, value=weight, title=relation)

    # ✅ 물리 레이아웃 및 인터랙션 옵션
    net.set_options("""
    {
      "nodes": {
        "shape": "dot",
        "scaling": { "min": 10, "max": 40 },
        "font": { "size": 16, "face": "arial" }
      },
      "edges": {
        "smooth": false,
        "color": { "opacity": 0.35 },
        "width": 0.5
      },
      "physics": {
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
          "gravitationalConstant": -45,
          "centralGravity": 0.003,
          "springLength": 180,
          "springConstant": 0.04
        },
        "minVelocity": 0.75,
        "stabilization": { "iterations": 200 }
      },
      "interaction": {
        "zoomView": true,
        "dragView": true,
        "hover": true
      }
    }
    """)

    # ✅ HTML 출력
    net.show(str(html_path))
    return str(html_path)
