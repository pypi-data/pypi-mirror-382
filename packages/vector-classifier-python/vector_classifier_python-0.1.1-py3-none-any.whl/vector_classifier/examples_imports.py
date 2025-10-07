"""
Shared example runner to avoid code duplication between top-level examples and package examples.
"""

import os
from typing import List, Optional

from ai_sdk import generate_text, openai, tool, embed_many
from pydantic import BaseModel, Field
from pinecone import Pinecone, ServerlessSpec

# Load .env if present
try:  # pragma: no cover
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


def run_ai_sdk_example() -> None:
    # Read and sanitize credentials
    api_key = (os.environ.get("PINECONE_API_KEY") or "").strip().strip('"').strip("'")
    if not api_key:
        raise RuntimeError("PINECONE_API_KEY is not set. Set it in your environment or .env file.")

    pc = Pinecone(api_key=api_key)
    index_name = (os.environ.get("PINECONE_INDEX_NAME") or "").strip().strip('"').strip("'")
    # Auto-create an index if not provided or missing
    if not index_name:
        index_name = "vcp-1536-cosine"
    existing = pc.list_indexes()
    if not any(i.name == index_name for i in (existing.indexes or [])):
        pc.create_index(name=index_name, dimension=1536, metric="cosine", spec=ServerlessSpec(cloud="aws", region="us-east-1"))
    index = pc.Index(index_name)

    # Sanitize OpenAI key to avoid quotes in Authorization header
    oai = (os.environ.get("OPENAI_API_KEY") or "").strip().strip('"').strip("'")
    if oai:
        os.environ["OPENAI_API_KEY"] = oai
    embed_model = openai.embedding("text-embedding-3-small")

    def _embed_query(text: str) -> List[float]:
        res = embed_many(model=embed_model, values=[text])
        return list(res.embeddings[0])

    class SearchParams(BaseModel):
        query: str
        top_k: int = Field(8, ge=1, le=200)
        sources: Optional[List[str]] = None
        threshold: Optional[float] = Field(None, ge=0.0, le=1.0)

    def _exec_search_documents(query: str, top_k: int = 8, sources: Optional[List[str]] = None, threshold: Optional[float] = None) -> dict:
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
                "chunk": {"id": m.id, "sourceUrl": md.get("sourceUrl"), "sourcePath": md.get("sourcePath"), "sourceTitle": md.get("sourceTitle")},
            })
        return {"results": matches, "totalResults": len(matches)}
    def _schema(model_cls):
        try:
            return model_cls.model_json_schema()  # pydantic v2
        except Exception:
            try:
                return model_cls.schema()  # pydantic v1
            except Exception:
                return {"type": "object"}
    search_documents_tool = tool(name="search_documents", description="Search indexed documents", parameters=_schema(SearchParams), execute=_exec_search_documents)

    class ExtractParams(BaseModel):
        url: str
        chunk_id: Optional[str] = None
        include_all_chunks: bool = False
        chunk_ids: Optional[List[str]] = None

    def _exec_extract_content(url: str, chunk_id: Optional[str] = None, include_all_chunks: bool = False, chunk_ids: Optional[List[str]] = None) -> dict:
        ids: List[str] = []
        if chunk_id:
            ids = [chunk_id]
        elif include_all_chunks and chunk_ids:
            ids = list(chunk_ids)
        if not ids:
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
            chunks.append({"id": cid, "content": md.get("content"), "sourceUrl": md.get("sourceUrl"), "sourcePath": md.get("sourcePath"), "sourceTitle": md.get("sourceTitle")})
        return {"chunks": chunks}
    extract_content_tool = tool(name="extract_content", description="Extract chunk content", parameters=_schema(ExtractParams), execute=_exec_extract_content)

    model = openai("gpt-4o-mini")
    prompt = (
        "You have access to tools for document search. "
        "1) Use search_documents to find the most relevant chunks about 'Example'. "
        "2) Then call extract_content for the best chunk to cite the exact text. "
        "Answer briefly."
    )
    res = generate_text(model=model, prompt=prompt, tools=[search_documents_tool, extract_content_tool])
    print(res.text)


