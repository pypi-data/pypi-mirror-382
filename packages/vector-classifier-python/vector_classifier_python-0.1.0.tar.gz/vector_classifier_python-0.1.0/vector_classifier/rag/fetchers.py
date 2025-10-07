from __future__ import annotations
import os
import re
import shutil
import tempfile
from typing import Optional

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from git import Repo


def fetch_url_markdown(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    # Remove script/style
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    markdown = md(str(soup))
    return markdown


def read_local_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def clone_repo_to_temp(repo_url: str, token: Optional[str] = None) -> str:
    tmp = tempfile.mkdtemp(prefix="vcp_repo_")
    if token and repo_url.startswith("https://"):
        # inject token
        repo_url = repo_url.replace("https://", f"https://{token}:x-oauth-basic@")
    Repo.clone_from(repo_url, tmp)
    return tmp


def cleanup_temp_dir(path: str) -> None:
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass



