from __future__ import annotations
import json
import os
from typing import Any, Dict, List, Optional


class LocalRegistry:
    def __init__(self, path: Optional[str] = None) -> None:
        self._path = path or os.path.join(os.path.expanduser("~"), ".vcp_sources.json")
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        if not os.path.exists(self._path):
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump({"sources": []}, f)

    def _read(self) -> Dict[str, Any]:
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"sources": []}

    def _write(self, data: Dict[str, Any]) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def upsert_source(self, *, url: str, type: str, title: Optional[str] = None, chunk_count: Optional[int] = None, status: Optional[str] = None, chunk_ids: Optional[list[str]] = None) -> None:
        data = self._read()
        sources = data.get("sources", [])
        found = next((s for s in sources if s.get("url") == url), None)
        if found:
            found.update({k: v for k, v in {"type": type, "title": title, "chunkCount": chunk_count, "status": status}.items() if v is not None})
            if chunk_ids is not None:
                found["chunkIds"] = list(chunk_ids)
        else:
            sources.append({"url": url, "type": type, "title": title, "chunkCount": chunk_count, "status": status, "chunkIds": list(chunk_ids or [])})
        data["sources"] = sources
        self._write(data)

    def list_sources(self) -> List[Dict[str, Any]]:
        return list(self._read().get("sources", []))

    def get_chunk_ids_by_url(self, url: str) -> list[str]:
        for s in self._read().get("sources", []):
            if s.get("url") == url:
                return list(s.get("chunkIds", []) or [])
        return []


