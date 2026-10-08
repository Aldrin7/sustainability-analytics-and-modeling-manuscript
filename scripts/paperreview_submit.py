"""
Submit docs/manuscript/GATE_F_MANUSCRIPT.pdf to paperreview.ai and save the
review token.

Flow (per public endpoints used by cnfjlhj/paperreview):
  1. POST /api/get-upload-url        -> presigned POST fields
  2. POST <presigned_url>            -> upload PDF to S3
  3. POST /api/confirm-upload        -> returns review token

Token is written to docs/manuscript/paperreview.token.txt
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "docs" / "manuscript" / "GATE_F_MANUSCRIPT.pdf"
TOKEN_FILE = ROOT / "docs" / "manuscript" / "paperreview.token.txt"
BASE_URL = "https://paperreview.ai"
VENUE = "Sustainability Analytics and Modeling"
EMAIL = "51796415+Aldrin7@users.noreply.github.com"
TIMEOUT = 60.0


def main() -> int:
    if not PDF.exists():
        print(f"ERROR: {PDF} not found")
        return 2
    data = PDF.read_bytes()
    if not data.startswith(b"%PDF-"):
        print("ERROR: not a valid PDF")
        return 2
    print(f"pdf: {PDF} ({len(data)} bytes)")
    print(f"venue: {VENUE}")
    print(f"email: {EMAIL}")

    # Step 1: presigned URL
    r1 = requests.post(
        f"{BASE_URL}/api/get-upload-url",
        json={"filename": PDF.name, "venue": VENUE},
        timeout=TIMEOUT,
    )
    print(f"get-upload-url -> {r1.status_code}")
    if not r1.ok:
        print(f"ERROR: {r1.text[:500]}")
        return 1
    d1 = r1.json()
    if not d1.get("success"):
        print(f"ERROR: success=false: {json.dumps(d1)[:500]}")
        return 1
    presigned_url = d1["presigned_url"]
    s3_key = d1["s3_key"]
    fields = d1["presigned_fields"]
    print(f"s3_key: {s3_key}")

    # Step 2: upload to S3
    with PDF.open("rb") as f:
        r2 = requests.post(
            presigned_url,
            data=fields,
            files={"file": (PDF.name, f, "application/pdf")},
            timeout=TIMEOUT,
        )
    print(f"s3 upload -> {r2.status_code}")
    if not r2.ok:
        print(f"ERROR: {r2.text[:500]}")
        return 1

    # Step 3: confirm (triggers processing + returns token)
    r3 = requests.post(
        f"{BASE_URL}/api/confirm-upload",
        data={"s3_key": s3_key, "venue": VENUE, "email": EMAIL},
        timeout=TIMEOUT,
    )
    print(f"confirm-upload -> {r3.status_code}")
    if not r3.ok:
        print(f"ERROR: {r3.text[:500]}")
        return 1
    d3 = r3.json()
    token = d3.get("token")
    if not token:
        print(f"ERROR: no token in response: {json.dumps(d3)[:500]}")
        return 1
    TOKEN_FILE.write_text(f"{token}\n", encoding="utf-8")
    print(f"token: {token}")
    print(f"token_file: {TOKEN_FILE}")
    print("response:", json.dumps(d3, indent=2)[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
