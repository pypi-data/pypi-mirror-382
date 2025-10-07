from __future__ import annotations
import os
import glob
from typing import Any, Dict, List, Optional

from .fetchers import fetch_url_markdown, read_local_file, clone_repo_to_temp, cleanup_temp_dir
from .chunk import chunk_text
from .client import RAGClient


def index_from_url(url: str, *, tokens_per_chunk: int = 2048) -> List[Dict[str, Any]]:
    text = fetch_url_markdown(url)
    return chunk_text(text=text, source_url=url, source_path=url, source_title=url, approx_tokens_per_chunk=tokens_per_chunk)


def index_from_file(path: str, *, tokens_per_chunk: int = 2048) -> List[Dict[str, Any]]:
    text = read_local_file(path)
    return chunk_text(text=text, source_url=f"file://{os.path.abspath(path)}", source_path=path, source_title=os.path.basename(path), approx_tokens_per_chunk=tokens_per_chunk)


def index_from_github(repo_url: str, *, github_token: Optional[str] = None, include_patterns: Optional[List[str]] = None, exclude_patterns: Optional[List[str]] = None, tokens_per_chunk: int = 2048) -> List[Dict[str, Any]]:
    temp_dir = clone_repo_to_temp(repo_url, token=github_token)
    try:
        include_patterns = include_patterns or ["**/*.md", "**/*.txt", "**/*.py", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]
        exclude_patterns = exclude_patterns or ["**/node_modules/**", "**/.git/**"]

        # Collect files
        files: List[str] = []
        for pat in include_patterns:
            files.extend(glob.glob(os.path.join(temp_dir, pat), recursive=True))
        # Apply excludes
        def is_excluded(p: str) -> bool:
            for ex in exclude_patterns or []:
                if glob.fnmatch.fnmatch(p, os.path.join(temp_dir, ex)):
                    return True
            return False
        files = [f for f in files if os.path.isfile(f) and not is_excluded(f)]

        chunks: List[Dict[str, Any]] = []
        for fp in files:
            try:
                text = read_local_file(fp)
            except Exception:
                continue
            rel = os.path.relpath(fp, temp_dir)
            chunks.extend(chunk_text(text=text, source_url=repo_url, source_path=rel, source_title=os.path.basename(fp), approx_tokens_per_chunk=tokens_per_chunk))
        return chunks
    finally:
        cleanup_temp_dir(temp_dir)


# Convenience: index and upsert in one call
async def index_url(client: RAGClient, url: str, *, tokens_per_chunk: int = 2048) -> Dict[str, Any]:
    chunks = index_from_url(url, tokens_per_chunk=tokens_per_chunk)
    await client.ensure_index()
    res = await client.upsert_chunks(chunks)
    return {"success": True, "upserted": res.get("upsertedCount", 0), "chunkIds": [c["id"] for c in chunks]}


async def index_file(client: RAGClient, path: str, *, tokens_per_chunk: int = 2048) -> Dict[str, Any]:
    chunks = index_from_file(path, tokens_per_chunk=tokens_per_chunk)
    await client.ensure_index()
    res = await client.upsert_chunks(chunks)
    return {"success": True, "upserted": res.get("upsertedCount", 0), "chunkIds": [c["id"] for c in chunks]}


async def index_github(client: RAGClient, repo_url: str, *, github_token: Optional[str] = None, include_patterns: Optional[List[str]] = None, exclude_patterns: Optional[List[str]] = None, tokens_per_chunk: int = 2048) -> Dict[str, Any]:
    chunks = index_from_github(repo_url, github_token=github_token, include_patterns=include_patterns, exclude_patterns=exclude_patterns, tokens_per_chunk=tokens_per_chunk)
    await client.ensure_index()
    res = await client.upsert_chunks(chunks)
    return {"success": True, "upserted": res.get("upsertedCount", 0), "chunkIds": [c["id"] for c in chunks]}


