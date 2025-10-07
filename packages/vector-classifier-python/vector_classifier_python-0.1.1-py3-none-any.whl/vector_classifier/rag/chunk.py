from __future__ import annotations
import hashlib
from typing import Any, Dict, List, Optional


def _hash_text(text: str) -> str:
    h = hashlib.md5(text.encode("utf-8")).hexdigest()
    return h


def chunk_text(
    *,
    text: str,
    source_url: str,
    source_path: Optional[str] = None,
    source_title: Optional[str] = None,
    approx_tokens_per_chunk: int = 2048,
    overlap_ratio: float = 0.1,
) -> List[Dict[str, Any]]:
    if approx_tokens_per_chunk <= 0:
        approx_tokens_per_chunk = 2048
    approx_chars = max(128, int(approx_tokens_per_chunk * 4))
    overlap = int(approx_chars * max(0.0, min(overlap_ratio, 0.5)))

    out: List[Dict[str, Any]] = []
    idx = 0
    pos = 0
    while pos < len(text):
        end = min(len(text), pos + approx_chars)
        slice_ = text[pos:end]
        out.append({
            "id": f"{source_url}:{source_path or ''}:{idx}",
            "content": slice_,
            "type": "documentation",
            "source": {"url": source_url, "type": "documentation", "path": source_path, "title": source_title},
            "metadata": {"size": len(slice_), "hash": _hash_text(slice_)},
        })
        pos = end - overlap
        if pos <= 0:
            pos = end
        idx += 1
    return out



