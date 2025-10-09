from __future__ import annotations
import os, json, time
from pathlib import Path   # ✅ Path 클래스를 불러옴
from typing import Any, Optional


CACHE_DIR = Path(os.environ.get("ATLAS_CACHE_DIR", Path.home() / ".atlas_cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_TTL = 60 * 60 * 24 * 7  # 7 days


def _key_to_path(key: str) -> Path:
    """
    Converts cache key into a safe filename.
    Windows는 :, ?, *, <, > 등의 문자를 허용하지 않으므로
    모두 밑줄(_)로 대체합니다.
    """
    safe = (
        key.replace(":", "_")
           .replace("/", "_")
           .replace("\\", "_")
           .replace("?", "_")
           .replace("*", "_")
           .replace("<", "_")
           .replace(">", "_")
           .replace("|", "_")
           .replace("\"", "_")
           .replace(" ", "_")
    )
    return CACHE_DIR / f"{safe}.json"


def get(key: str) -> Optional[Any]:
    p = _key_to_path(key)
    if not p.exists():
        return None
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        if obj.get("_expires") and obj["_expires"] < time.time():
            return None
        return obj.get("data")
    except Exception:
        return None


def set(key: str, data: Any, ttl: int = DEFAULT_TTL) -> None:
    p = _key_to_path(key)
    payload = {"data": data, "_expires": time.time() + ttl}
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
