"""
Poll paperreview.ai for a completed review.

GET /api/review/{token} -> HTTP 200 means the review is ready.
Saves JSON + Markdown artifacts next to the manuscript when ready.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
MDIR = ROOT / "docs" / "manuscript"
TOKEN_FILE = MDIR / "paperreview.token.txt"
BASE_URL = "https://paperreview.ai"


def to_markdown(review: dict) -> str:
    lines = ["# PaperReview.ai Review", "", "## Metadata", ""]
    for key in ("title", "venue", "submission_date", "overall_score", "score", "rating"):
        if review.get(key):
            lines.append(f"- {key}: {review[key]}")
    lines.append(f"- Retrieved at: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    sections = review.get("sections") or {}
    if isinstance(sections, dict):
        for key, val in sections.items():
            if val is None or not str(val).strip():
                continue
            lines.append(f"## {key.replace('_', ' ').title()}")
            lines.append("")
            lines.append(str(val).strip())
            lines.append("")
    if not sections and isinstance(review.get("review"), str):
        lines.append("## Review")
        lines.append("")
        lines.append(review["review"])
        lines.append("")
    return "\n".join(lines)


def check(token: str) -> tuple[int, object]:
    r = requests.get(f"{BASE_URL}/api/review/{token}", timeout=30)
    try:
        body = r.json()
    except Exception:
        body = r.text[:500]
    return r.status_code, body


def main() -> int:
    if not TOKEN_FILE.exists():
        print("ERROR: token file not found; submit first")
        return 2
    token = TOKEN_FILE.read_text(encoding="utf-8").strip()
    interval_s = 60  # poll every 60s locally (site suggests 10 min for long waits)
    max_attempts = 40  # ~40 minutes per run

    for attempt in range(1, max_attempts + 1):
        status, body = check(token)
        print(f"[{datetime.now().isoformat(timespec='seconds')}] attempt {attempt}: HTTP {status}")
        if status == 200 and isinstance(body, dict):
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = MDIR / f"paperreview_review_{stamp}.json"
            md_path = MDIR / f"paperreview_review_{stamp}.md"
            json_path.write_text(json.dumps(body, indent=2, ensure_ascii=False), encoding="utf-8")
            md_path.write_text(to_markdown(body), encoding="utf-8")
            # also refresh stable-name copies
            (MDIR / "paperreview_review_latest.json").write_text(
                json.dumps(body, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            (MDIR / "paperreview_review_latest.md").write_text(to_markdown(body), encoding="utf-8")
            print(f"REVIEW READY: {json_path}")
            print(f"markdown: {md_path}")
            return 0
        if attempt < max_attempts:
            time.sleep(interval_s)

    print("Review not ready yet; re-run later.")
    return 3


if __name__ == "__main__":
    sys.exit(main())
