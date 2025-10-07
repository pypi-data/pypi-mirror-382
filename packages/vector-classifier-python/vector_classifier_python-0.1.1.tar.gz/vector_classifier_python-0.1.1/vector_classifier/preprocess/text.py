from __future__ import annotations

def normalize_text(input: str, *, lowercase: bool = True, trim: bool = True, collapse_whitespace: bool = True) -> str:
    s = input
    if trim:
        s = s.strip()
    if collapse_whitespace:
        s = " ".join(s.split())
    if lowercase:
        s = s.lower()
    return s

