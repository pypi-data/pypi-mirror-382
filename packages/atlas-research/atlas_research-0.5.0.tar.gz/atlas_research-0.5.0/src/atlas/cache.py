# src/atlas/cache.py
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

# 사용자 홈 디렉토리에 캐시 디렉토리 생성
CACHE_DIR = Path.home() / ".atlas_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_SAFE_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def _safe_key(key: str) -> str:
    """파일 시스템 친화적인 캐시 키로 정규화."""
    return _SAFE_RE.sub("_", key)


def _key_to_path(key: str) -> Path:
    return CACHE_DIR / f"{_safe_key(key)}.json"


def get(key: str) -> Optional[Any]:
    """
    캐시에서 키를 읽어 반환.
    파일이 없거나 파싱 실패 시 None 반환.
    """
    p = _key_to_path(key)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def set(key: str, payload: Any) -> Path:
    """
    캐시에 값 저장. JSON 직렬화 가능해야 함.
    """
    p = _key_to_path(key)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def delete(key: str) -> None:
    """해당 키의 캐시 파일 삭제(존재하지 않아도 조용히 무시)."""
    p = _key_to_path(key)
    try:
        p.unlink(missing_ok=True)  # py3.8+: missing_ok 지원
    except TypeError:
        # python 3.7 호환
        if p.exists():
            p.unlink()


def clear() -> None:
    """캐시 디렉토리 비우기."""
    for f in CACHE_DIR.glob("*.json"):
        try:
            f.unlink()
        except Exception:
            pass

