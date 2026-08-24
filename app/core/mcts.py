from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


@dataclass
class Node:
    candidate: dict
    parent: "Node | None" = None
    visits: int = 0
    value: float = 0.0
    children: list["Node"] = field(default_factory=list)

    @property
    def mean_value(self) -> float:
        return self.value / self.visits if self.visits else 0.0


def uct(node: Node, exploration: float = 1.414) -> float:
    if node.visits == 0:
        return float("inf")
    parent_visits = node.parent.visits if node.parent else max(node.visits, 1)
    return node.mean_value + exploration * math.sqrt(math.log(max(parent_visits, 1)) / node.visits)


class MCTS:
    def __init__(self, candidates: list[dict], scorer, iterations: int = 8):
        self.candidates = candidates
        self.scorer = scorer
        self.iterations = max(1, iterations)

    def run(self) -> tuple[dict, list[dict]]:
        root = Node(candidate={"action": "ROOT", "answer": "", "evidence": [], "summary": "Root"})
        nodes = [Node(candidate=c, parent=root) for c in self.candidates]
        root.children = nodes
        rng = random.Random(42)

        for node in nodes:
            score, checks = self.scorer.score(node.candidate["answer"])
            node.candidate["factuality_score"] = score
            node.candidate["statement_checks"] = checks

        for _ in range(self.iterations):
            node = max(nodes, key=uct)
            node.visits += 1
            # The small roll-out estimates the already computed factuality reward plus
            # a tiny deterministic exploration signal so tied candidates are explored.
            rollout = node.candidate.get("factuality_score", 0.0) + rng.random() * 0.01
            node.value += rollout
            root.visits += 1

        for idx, node in enumerate(nodes):
            node.candidate["value"] = round(node.mean_value, 4)
            node.candidate["id"] = f"trajectory-{idx + 1}"

        ranked = sorted((n.candidate for n in nodes), key=lambda c: (c["factuality_score"], c["value"]), reverse=True)
        return ranked[0], ranked
