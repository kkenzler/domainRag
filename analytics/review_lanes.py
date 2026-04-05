from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from review_workflow import review_progress


ANALYTICS_DIR = Path(__file__).resolve().parent
SHARED_INPUT_JSON = ANALYTICS_DIR / "review_input.json"


@dataclass(frozen=True)
class ReviewLane:
    key: str
    label: str
    decisions_json: Path
    sheet_name: str
    status_command: str


CLAUDE_DECISIONS = (
    ANALYTICS_DIR / "claude_aigenticHumanReview" / "claude_review_workdir" / "claude_review_decisions.json"
).resolve()
CODEX_DECISIONS = (
    ANALYTICS_DIR / "codex_aigenticHumanReview" / "codex_review_workdir" / "codex_review_decisions.json"
).resolve()


REVIEW_LANES: tuple[ReviewLane, ...] = (
    ReviewLane(
        key="claude",
        label="Claude",
        decisions_json=CLAUDE_DECISIONS,
        sheet_name="Claude Review",
        status_command=r"python analytics\claude_aigenticHumanReview\aigenticHumanReview.py --status",
    ),
    ReviewLane(
        key="codex",
        label="Codex",
        decisions_json=CODEX_DECISIONS,
        sheet_name="Codex Review",
        status_command=r"python analytics\codex_aigenticHumanReview\aigenticHumanReview.py --status",
    ),
)


def shared_input_json() -> Path:
    return SHARED_INPUT_JSON


def lane_progress(lane: ReviewLane) -> dict[str, object]:
    progress = review_progress(SHARED_INPUT_JSON, lane.decisions_json)
    return {
        "key": lane.key,
        "label": lane.label,
        "sheet_name": lane.sheet_name,
        "input_json": SHARED_INPUT_JSON,
        "decisions_json": lane.decisions_json,
        "status_command": lane.status_command,
        **progress,
    }


def all_lane_progress() -> list[dict[str, object]]:
    return [lane_progress(lane) for lane in REVIEW_LANES]


def all_lanes_complete() -> bool:
    progress = all_lane_progress()
    return bool(progress) and all(bool(item["complete"]) for item in progress)
