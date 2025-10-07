from __future__ import annotations
from typing import Iterable, Literal, Optional, Tuple

VoteMode = Literal["majority", "weighted"]


def vote_label(matches: Iterable[Tuple[Optional[str], float]], mode: VoteMode) -> Tuple[Optional[str], float]:
    scores: dict[str, float] = {}
    for label, similarity in matches:
        if not label:
            continue
        inc = similarity if mode == "weighted" else 1.0
        scores[label] = scores.get(label, 0.0) + inc
    best_label: Optional[str] = None
    best_score = float("-inf")
    for label, score in scores.items():
        if score > best_score:
            best_label, best_score = label, score
    return best_label, best_score

