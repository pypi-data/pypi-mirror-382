import asyncio
import os
from vector_classifier import VectorClassifier

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

async def main() -> None:
    classifier = VectorClassifier({
        "pinecone": {
            "apiKey": os.environ["PINECONE_API_KEY"],
            "indexName": os.environ.get("PINECONE_INDEX_NAME", "animals"),
            "metric": os.environ.get("PINECONE_METRIC", "cosine"),
            "namespace": os.environ.get("PINECONE_NAMESPACE", "prod"),
        },
        "embedding": {
            "provider": os.environ.get("EMBED_PROVIDER", "openai"),
            "model": os.environ.get("EMBED_MODEL", "text-embedding-3-small"),
            "apiKey": os.environ["OPENAI_API_KEY"],
        },
        "defaults": {
            "topK": int(os.environ.get("VC_TOPK", "5")),
            "threshold": float(os.environ.get("VC_THRESHOLD", "0")),
            "vote": os.environ.get("VC_VOTE", "weighted"),
        },
    })

    await classifier.index_data([
        {"id": "1", "label": "Cat", "description": "Small domestic cat", "metadata": {"color": "gray"}},
        {"id": "2", "label": "Dog", "description": "Friendly domestic dog", "metadata": {"size": "medium"}},
        {"id": "3", "label": "Rabbit", "description": "Small herbivorous mammal", "metadata": {"color": "white"}},
    ])

    result = await classifier.classify({"description": "Playful feline"}, {"topK": 3, "threshold": 0.1})
    print(result)

    # RAG quickstart (uncomment and configure env vars to try)
    # from vector_classifier.rag.index import index_from_url
    # from vector_classifier import RAGClient
    # rag = RAGClient(
    #     pinecone_api_key=os.environ["PINECONE_API_KEY"],
    #     pinecone_index=os.environ.get("PINECONE_INDEX_NAME", "docs"),
    # )
    # await rag.ensure_index()
    # chunks = index_from_url("https://example.com")
    # await rag.upsert_chunks(chunks)
    # hits = await rag.query(query="what is example?", top_k=3)
    # print(hits)

if __name__ == "__main__":
    asyncio.run(main())
