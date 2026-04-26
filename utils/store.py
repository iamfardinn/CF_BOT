import json
import logging
import os

logger = logging.getLogger(__name__)

_STATE_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "state.json"))
_VALID_EVENTS = {"announced", "1_hour_warning", "started"}


def _load() -> dict:
    try:
        with open(_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "notified" not in data:
                data["notified"] = {}
            for ev in _VALID_EVENTS:
                data["notified"].setdefault(ev, [])
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"notified": {ev: [] for ev in _VALID_EVENTS}}


def _save(data: dict) -> None:
    os.makedirs(os.path.dirname(_STATE_PATH), exist_ok=True)
    tmp_path = _STATE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, _STATE_PATH)


def already_notified(contest_id: int, event: str) -> bool:
    state = _load()
    return contest_id in state["notified"].get(event, [])


def mark_notified(contest_id: int, event: str) -> None:
    state = _load()
    bucket = state["notified"].setdefault(event, [])
    if contest_id not in bucket:
        bucket.append(contest_id)
    _save(state)


def prune_old_entries(active_ids: set[int]) -> None:
    state = _load()
    changed = False
    for ev in _VALID_EVENTS:
        before = state["notified"].get(ev, [])
        after = [cid for cid in before if cid in active_ids]
        if len(after) != len(before):
            state["notified"][ev] = after
            changed = True
    if changed:
        _save(state)
        logger.debug("Pruned stale contest IDs from state.json")


def bootstrap_announced(contest_ids: list[int]) -> None:
    state = _load()
    bucket = state["notified"].setdefault("announced", [])
    changed = False
    for cid in contest_ids:
        if cid not in bucket:
            bucket.append(cid)
            changed = True
    if changed:
        _save(state)
        logger.info(f"Bootstrapped {len(contest_ids)} contest IDs into announced list")
