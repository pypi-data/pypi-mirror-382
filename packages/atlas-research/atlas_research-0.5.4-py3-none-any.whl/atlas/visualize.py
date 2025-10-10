# src/atlas/visualize.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import networkx as nx
from pyvis.network import Network


SIG_COLORS: Dict[str, str] = {
    "paper":   "#3B82F6",  # Blue
    "keyword": "#FACC15",  # Yellow
    "author":  "#9CA3AF",  # Gray
    "dataset": "#10B981",  # Green
    "code":    "#8B5CF6",  # Purple
    "venue":   "#FB923C",  # Orange
    "concept": "#60A5FA",  # Light Blue
}
DEFAULT_NODE_COLOR = "#6B7280"  # fallback gray


def _shorten(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def export_pyvis(
    G: nx.Graph,
    out_dir: str = "outputs",
    name: str = "graph",
    *,
    bgcolor: str = "#ffffff",
    label_max_len: int = 36,
    size_min: int = 10,
    size_max: int = 34,
    min_edge_weight: float = 0.0,
    fit_scale: float = 0.85,
) -> str:
    """
    Atlas v0.4.2-pre — White Signature Map Edition
    ------------------------------------------------
    - 화이트 시그니처 테마 고정
    - ForceAtlas2 고급 튜닝(간격 확장/겹침 최소화)
    - degree 기반 자동 노드 스케일링
    - 긴 라벨 자동 축약
    - 초기 화면 자동 맞춤 (fit + moveTo)
    - 안전한 HTML 출력(write_html)
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    html_path = out / f"{name}.html"

    # PyVis 네트워크
    net = Network(
        height="900px",
        width="100%",
        bgcolor=bgcolor,
        font_color="#111111",
        directed=True,
        notebook=False,
    )

    # 물리 레이아웃: 간격을 크게, 중심 끌림은 약하게
    net.force_atlas_2based(
        gravity=-80,                # (더 음수일수록 퍼짐)
        central_gravity=0.005,      # 중심으로 모이는 힘 약화
        spring_length=180,          # 🔑 간격 확장
        spring_strength=0.03,       # 🔑 밀착 방지
        damping=0.80,
        overlap=0.50,
    )

    # degree 기반 크기 스케일링
    degree_dict = dict(G.degree())
    if degree_dict:
        d_min, d_max = min(degree_dict.values()), max(degree_dict.values())
    else:
        d_min = d_max = 0

    def _scale(deg: int) -> int:
        if d_max == d_min:
            return max(size_min, min(size_max, (size_min + size_max) // 2))
        # 선형 스케일링
        ratio = (deg - d_min) / (d_max - d_min)
        return int(size_min + ratio * (size_max - size_min))

    # 노드 추가
    for node, attrs in G.nodes(data=True):
        ntype = str(attrs.get("type", "paper")).lower()
        label = _shorten(str(attrs.get("label", node)), label_max_len)
        color = SIG_COLORS.get(ntype, DEFAULT_NODE_COLOR)
        size = _scale(degree_dict.get(node, 0))
        net.add_node(
            node,
            label=label,
            color=color,
            title=f"{ntype}",
            shape="dot",
            size=size,
        )

    # 엣지 추가 (존재 노드만, 가중치 필터 적용)
    visible = set(G.nodes())
    for u, v, data in G.edges(data=True):
        if u not in visible or v not in visible:
            continue
        weight = float(data.get("weight", 1.0))
        if weight < min_edge_weight:
            continue
        relation = str(data.get("relation", data.get("label", "")))
        net.add_edge(u, v, title=relation, value=max(weight, 0.1), color="#B0B0B0")

    # PyVis 옵션 — JSON 순수 형식
    net.set_options(
        """
        {
          "nodes": {
            "shape": "dot",
            "scaling": { "min": 10, "max": 40 },
            "font": { "size": 16, "face": "arial", "align": "center" },
            "borderWidth": 1,
            "borderWidthSelected": 2,
            "shadow": true
          },
          "edges": {
            "smooth": { "enabled": false },
            "color": { "color": "#B0B0B0", "highlight": "#000000" },
            "width": 1.2,
            "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 } }
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 120,
            "zoomView": true,
            "dragNodes": true,
            "keyboard": true,
            "navigationButtons": true
          },
          "physics": {
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
              "gravitationalConstant": -80,
              "springLength": 180,
              "springConstant": 0.03,
              "damping": 0.8
            },
            "minVelocity": 0.75,
            "stabilization": { "iterations": 80 }
          }
        }
        """
    )

    # 안전한 HTML 출력 (브라우저 자동오픈 X)
    net.write_html(str(html_path))

    # 초기 화면 자동 맞춤 (fit + moveTo scale)
    # PyVis가 생성한 스크립트에 한 줄 삽입
    try:
        html = html_path.read_text(encoding="utf-8")
        marker = "new vis.Network(container, data, options);"
        if marker in html:
            injected = (
                f"{marker}\n  network.fit();\n  network.moveTo({{\"scale\": {fit_scale}}});"
            )
            html = html.replace(marker, injected)
            html_path.write_text(html, encoding="utf-8")
    except Exception:
        # 삽입 실패해도 치명적이지 않으므로 조용히 패스
        pass

    print(f"[Atlas Visualization] Exported → {html_path}")
    return str(html_path)
