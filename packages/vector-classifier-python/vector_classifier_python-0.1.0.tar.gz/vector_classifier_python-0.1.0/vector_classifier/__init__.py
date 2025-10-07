from .classifier import VectorClassifier
from .utils.cost import estimate_embedding_cost

# RAG interfaces (added)
try:
    from .rag.client import RAGClient  # type: ignore[attr-defined]
    from .rag.tools import search_documents, extract_content  # type: ignore[attr-defined]
except Exception:
    # Modules may not be available at import time during partial installs; keep base API working
    RAGClient = None  # type: ignore[assignment]
    def search_documents(*args, **kwargs):  # type: ignore[no-redef]
        raise ImportError("RAG modules not available")
    def extract_content(*args, **kwargs):  # type: ignore[no-redef]
        raise ImportError("RAG modules not available")

__all__ = [
    "VectorClassifier",
    "estimate_embedding_cost",
    "RAGClient",
    "search_documents",
    "extract_content",
]

