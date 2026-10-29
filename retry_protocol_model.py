"""Bounded crash/retry model of the one-intent, one-effect problem.

A small explicit-state transition system, NOT a real idempotency implementation.
All persistent writes are modeled as durable. An 'atomic' step is legitimate
only when the ledger and effect share one true transaction boundary (or the
external endpoint itself enforces deduplication for the intent).
"""
from collections import deque
from dataclasses import dataclass, replace
from typing import Dict, List, Tuple

PROTOCOLS = ("effect_then_mark", "mark_then_effect", "atomic")
PHASES = ("idle", "prepared", "effect_done", "marked_pre", "marked_post",
          "atomic_done", "effect_done_pre", "finished")


@dataclass(frozen=True)
class State:
    effects: int = 0  # durable count of actual committed external effects
    marker: bool = False  # durable idempotency marker for this intent
    phase: str = "idle"  # volatile handler program counter
    attempts: int = 0
    crashes: int = 0
    acknowledged: bool = False


def successors(state: State, protocol: str, max_attempts: int = 2,
               max_crashes: int = 1) -> Tuple[Tuple[str, State], ...]:
    """Enumerate exactly the transitions allowed by the stated protocol."""
    if protocol not in PROTOCOLS:
        raise ValueError("Unknown protocol")
    if max_attempts < 1 or max_crashes < 0:
        raise ValueError("Invalid bounds")
    if state.phase not in PHASES:
        raise ValueError("Invalid state")
    if state.phase == "finished":
        return ()
    nxt: List[Tuple[str, State]] = []
    if state.phase == "idle" and state.attempts < max_attempts:
        if state.marker:
            nxt.append(("retry-reads-durable-marker", replace(
                state, attempts=state.attempts+1, phase="finished")))
        else:
            nxt.append(("begin-attempt", replace(
                state, attempts=state.attempts+1, phase="prepared")))
    if state.phase == "prepared":
        if protocol == "effect_then_mark":
            nxt.append(("commit-external-effect", replace(
                state, effects=state.effects+1, phase="effect_done")))
        elif protocol == "mark_then_effect":
            nxt.append(("write-durable-marker", replace(
                state, marker=True, phase="marked_pre")))
        else:
            nxt.append(("atomic-effect-and-marker", replace(
                state, marker=True, effects=state.effects+1, phase="atomic_done")))
    if protocol == "effect_then_mark" and state.phase == "effect_done":
        nxt.append(("write-durable-marker", replace(
            state, marker=True, phase="marked_post")))
    if protocol == "mark_then_effect" and state.phase == "marked_pre":
        nxt.append(("commit-external-effect", replace(
            state, effects=state.effects+1, phase="effect_done_pre")))
    if state.phase in ("marked_post", "effect_done_pre", "atomic_done"):
        nxt.append(("acknowledge", replace(
            state, acknowledged=True, phase="finished")))
    if state.phase not in ("idle", "finished") and state.crashes < max_crashes:
        nxt.append(("crash-lose-volatile-phase", replace(
            state, phase="idle", crashes=state.crashes+1)))
    return tuple(nxt)


def explore(protocol: str, max_attempts: int = 2, max_crashes: int = 1
            ) -> Dict[State, Tuple[str, ...]]:
    """BFS with shortest action witness for every reachable state.

    This exhaustively explores a bounded, finite transition graph: each
    attempt and crash count increases monotonically and is capped.
    """
    initial = State()
    visited = {initial: ()}
    queue = deque([initial])
    while queue:
        state = queue.popleft()
        for action, after in successors(state, protocol, max_attempts, max_crashes):
            if after not in visited:
                visited[after] = visited[state] + (action,)
                queue.append(after)
    return visited


def shortest_counterexample(protocol: str, property_name: str):
    """Find a concrete violating trace; return (state, witness) or None.

    at_most_once: no reachable state has two or more committed effects.
    no_lost_intent: no finished state has zero committed effects.
    """
    if property_name not in ("at_most_once", "no_lost_intent"):
        raise ValueError("Unknown property")
    for state, actions in explore(protocol).items():
        bad = (state.effects > 1 if property_name == "at_most_once" else
               state.phase == "finished" and state.effects == 0)
        if bad:
            return state, actions
    return None


def model_report():
    rows = []
    for protocol in PROTOCOLS:
        visited = explore(protocol)
        duplicate = shortest_counterexample(protocol, "at_most_once")
        lost = shortest_counterexample(protocol, "no_lost_intent")
        rows.append({
            "protocol": protocol,
            "reachable_states": len(visited),
            "at_most_once": duplicate is None,
            "terminal_intent_never_lost": lost is None,
            "duplicate_witness": None if duplicate is None else duplicate[1],
            "lost_witness": None if lost is None else lost[1],
        })
    return rows


if __name__ == "__main__":
    for row in model_report():
        print(row)
