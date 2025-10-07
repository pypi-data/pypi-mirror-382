import asyncio
import os

from vector_classifier import RAGClient
from vector_classifier.rag.index import index_url
from vector_classifier.rag.tools import search_documents, extract_content


async def main() -> None:
    client = RAGClient(
        pinecone_api_key=os.environ["PINECONE_API_KEY"],
        pinecone_index=os.environ.get("PINECONE_INDEX_NAME", "docs"),
        embedding_provider=os.environ.get("EMBED_PROVIDER", "openai"),
        embedding_model=os.environ.get("EMBED_MODEL", "text-embedding-3-small"),
    )

    # Index a documentation page
    res = await index_url(client, "https://example.com", tokens_per_chunk=1024)
    print("Indexed:", res)

    # Search documents
    s = await search_documents(client=client, query="what is example?", top_k=3)
    print("Search results:", s)

    # Extract content for the first hit
    if s.get("results"):
        first = s["results"][0]
        chunk_id = first["id"]
        doc_url = first["chunk"]["sourceUrl"]
        content = await extract_content(client=client, url=doc_url, chunk_id=chunk_id)
        print("Content: ", content)


if __name__ == "__main__":
    asyncio.run(main())


