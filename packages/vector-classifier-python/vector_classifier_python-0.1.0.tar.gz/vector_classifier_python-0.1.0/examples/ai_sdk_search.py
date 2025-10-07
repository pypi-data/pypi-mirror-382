"""
Example: Use ai-sdk-python tools to search an indexed document in Pinecone

Prereqs:
- Env: OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME
- Your docs are indexed in Pinecone with metadata: sourceUrl, sourcePath, sourceTitle, content

Install:
  pip install ai-sdk-python pinecone openai pydantic

Run:
  python -m vector_classifier.examples.ai_sdk_search
"""

import os
from typing import List, Optional

from ai_sdk import generate_text, openai, tool, embed_many
from pydantic import BaseModel, Field
from pinecone import Pinecone


# Pinecone client & index
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(os.environ["PINECONE_INDEX_NAME"])

# Embedding model via ai-sdk-python (OpenAI provider)
embed_model = openai.embedding("text-embedding-3-small")


def _embed_query(text: str) -> List[float]:
    res = embed_many(model=embed_model, values=[text])
    return list(res.embeddings[0])


class SearchParams(BaseModel):
    query: str
    top_k: int = Field(8, ge=1, le=200, description="Number of chunks to return")
    sources: Optional[List[str]] = Field(None, description="Filter by sourceUrl list")
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Min similarity score")


@tool(
    name="search_documents",
    description="Finds the top-k chunks for a query from previously indexed documents.",
    parameters=SearchParams,
)
def search_documents(query: str, top_k: int = 8, sources: Optional[List[str]] = None, threshold: Optional[float] = None) -> dict:
    vector = _embed_query(query)
    flt = {"sourceUrl": {"$in": sources}} if sources else None
    res = index.query(top_k=top_k, vector=vector, include_metadata=True, include_values=False, filter=flt)
    matches = []
    for m in (res.matches or []):
        score = float(getattr(m, "score", 0.0) or 0.0)
        if threshold is not None and score < float(threshold):
            continue
        md = getattr(m, "metadata", {}) or {}
        matches.append({
            "id": m.id,
            "score": score,
            "chunk": {
                "id": m.id,
                "sourceUrl": md.get("sourceUrl"),
                "sourcePath": md.get("sourcePath"),
                "sourceTitle": md.get("sourceTitle"),
            },
        })
    return {"results": matches, "totalResults": len(matches)}


class ExtractParams(BaseModel):
    url: str = Field(description="Document URL")
    chunk_id: Optional[str] = Field(None, description="Specific chunk id to fetch")
    include_all_chunks: bool = Field(False, description="When true, returns all chunks for the URL (best-effort)")
    chunk_ids: Optional[List[str]] = Field(None, description="Optional known chunk ids to fetch en masse")


@tool(
    name="extract_content",
    description="Extracts content for a chunk id or all chunks belonging to a URL.",
    parameters=ExtractParams,
)
def extract_content(url: str, chunk_id: Optional[str] = None, include_all_chunks: bool = False, chunk_ids: Optional[List[str]] = None) -> dict:
    ids: List[str] = []
    if chunk_id:
        ids = [chunk_id]
    elif include_all_chunks and chunk_ids:
        ids = list(chunk_ids)
    if not ids:
        # Fallback discovery: query by URL to find chunks (up to 100)
        vector = _embed_query(url)
        qr = index.query(top_k=100, vector=vector, include_metadata=True, filter={"sourceUrl": url})
        ids = [m.id for m in (qr.matches or [])]
    if not ids:
        return {"chunks": []}
    fetched = index.fetch(ids=ids)
    vectors = getattr(fetched, "vectors", {}) or {}
    chunks = []
    for cid in ids:
        v = vectors.get(cid)
        if not v:
            continue
        md = getattr(v, "metadata", None) or {}
        chunks.append({
            "id": cid,
            "content": md.get("content"),
            "sourceUrl": md.get("sourceUrl"),
            "sourcePath": md.get("sourcePath"),
            "sourceTitle": md.get("sourceTitle"),
        })
    return {"chunks": chunks}


def main() -> None:
    model = openai("gpt-4o-mini")
    prompt = (
        "You have access to tools for document search. "
        "1) Use search_documents to find the most relevant chunks about 'Example'. "
        "2) Then call extract_content for the best chunk to cite the exact text. "
        "Answer briefly."
    )
    res = generate_text(model=model, prompt=prompt, tools=[search_documents, extract_content])
    print(res.text)


if __name__ == "__main__":
    main()


