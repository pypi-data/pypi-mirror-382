from __future__ import annotations
from typing import Dict, List, Optional

OPENAI_EMBED_COST_PER_1K_TOKENS: Dict[str, float] = {
    "text-embedding-3-small": 0.02 / 1000,
    "text-embedding-3-large": 0.13 / 1000,
}

def _approx_tokens(text: str) -> int:
    return (len(text) + 3) // 4


def estimate_embedding_cost(*, provider: str, model: str, inputs: List[str]) -> Dict[str, Optional[float]]:
    tokens = sum(_approx_tokens(t or "") for t in inputs)
    if provider == "openai":
        rate = OPENAI_EMBED_COST_PER_1K_TOKENS.get(model)
        if rate is not None:
            return {"tokens": float(tokens), "costUSD": float(tokens) / 1000.0 * rate}
        return {"tokens": float(tokens), "costUSD": None}
    return {"tokens": float(tokens), "costUSD": None}

