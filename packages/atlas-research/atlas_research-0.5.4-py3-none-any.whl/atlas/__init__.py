# src/atlas/__init__.py
from __future__ import annotations

# 기존 공개 API 유지 + v0.4.2의 시각화 함수형 API 노출
from .project import Atlas  # 기존 프로젝트 엔트리
from .types import NodeType
from .ingest import Ingestor
from .link import Linker
from .visualize import export_pyvis

# (선택) 이전 버전 호환: Visualizer가 있을 경우만 노출
try:
    from .viz.visualizer import Visualizer  # 과거 클래스형 API (있으면)
    __all__ = ["Atlas", "NodeType", "Ingestor", "Linker", "Visualizer", "export_pyvis"]
except Exception:
    __all__ = ["Atlas", "NodeType", "Ingestor", "Linker", "export_pyvis"]
