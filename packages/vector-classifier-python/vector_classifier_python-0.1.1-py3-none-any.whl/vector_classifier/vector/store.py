from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol, Literal

Metric = Literal["cosine", "euclidean"]

@dataclass
class VectorUpsert:
    id: str
    values: List[float]
    metadata: Optional[Dict[str, object]] = None

@dataclass
class QueryMatch:
    id: str
    score: float
    metadata: Optional[Dict[str, object]] = None

class VectorStore(Protocol):
    async def ensure_index(self, dimension: int, metric: Metric) -> None: ...

    async def upsert(self, vectors: List[VectorUpsert], namespace: Optional[str] = None) -> Dict[str, int]: ...

    async def query(
        self,
        vector: List[float],
        top_k: int,
        namespace: Optional[str] = None,
        filter: Optional[Dict[str, object]] = None,
        include_values: bool = False,
    ) -> List[QueryMatch]: ...

    async def fetch(self, ids: List[str], namespace: Optional[str] = None) -> List[QueryMatch]: ...

    async def update(self, id: str, vector: List[float], metadata: Optional[Dict[str, object]] = None, namespace: Optional[str] = None) -> None: ...

    async def delete_index(self) -> None: ...

