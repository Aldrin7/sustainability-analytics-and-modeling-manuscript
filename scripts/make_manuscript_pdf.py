"""
Convert docs/manuscript/GATE_F_MANUSCRIPT.txt into a typeset PDF suitable for
external review submission (paperreview.ai requires a PDF < 10MB).

Prefers weasyprint (HTML -> PDF); falls back to reportlab (pure Python).
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "manuscript" / "GATE_F_MANUSCRIPT.txt"
OUT = ROOT / "docs" / "manuscript" / "GATE_F_MANUSCRIPT.pdf"
TITLE = "Machine Learning-Driven Optimized Land Use Mix Planning for Sustainable Urban Development"

RULE_RE = re.compile(r"^={10,}$")


def parse_manuscript(text: str) -> list[tuple[str, str]]:
    """Return list of (kind, content); kind in {"heading", "para", "list"}."""
    lines = text.splitlines()
    blocks: list[tuple[str, str]] = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if RULE_RE.match(line.strip()):
            j = i + 1
            head_lines: list[str] = []
            while j < n and not RULE_RE.match(lines[j].strip()):
                head_lines.append(lines[j])
                j += 1
            head = " ".join(l.strip() for l in head_lines if l.strip()).strip()
            if head:
                blocks.append(("heading", head))
            i = j
            continue
        if not line.strip():
            i += 1
            continue
        para_lines: list[str] = []
        while i < n and lines[i].strip() and not RULE_RE.match(lines[i].strip()):
            para_lines.append(lines[i].rstrip())
            i += 1
        raw = "\n".join(para_lines)
        kind = "list" if raw.lstrip().startswith("- ") else "para"
        blocks.append((kind, raw))
    return blocks


def clean_heading(text: str) -> str:
    if text.startswith("MANUSCRIPT:"):
        return ""
    if text.startswith(TITLE[:40]):
        return ""
    return text


def blocks_to_html(blocks: list[tuple[str, str]]) -> str:
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'><style>",
        "@page { size: A4; margin: 2.2cm 2cm; @bottom-center { content: 'Page ' counter(page) ' of ' counter(pages); font-size: 9pt; color: #666; } }",
        "body { font-family: 'Georgia', 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.45; color: #111; }",
        "h1 { font-size: 15pt; text-align: center; margin: 0 0 4pt 0; }",
        ".subtitle { text-align: center; font-size: 9pt; color: #666; margin-bottom: 18pt; }",
        "h2 { font-size: 12pt; margin: 16pt 0 6pt 0; border-bottom: 1px solid #999; padding-bottom: 2pt; page-break-after: avoid; }",
        "p { margin: 0 0 8pt 0; text-align: justify; }",
        "ul { margin: 0 0 8pt 0; padding-left: 18pt; }",
        "li { margin-bottom: 3pt; }",
        "</style></head><body>",
        f"<h1>{html.escape(TITLE)}</h1>",
        "<div class='subtitle'>Manuscript submitted to Sustainability Analytics and Modeling (Elsevier/IFORS)</div>",
    ]
    for kind, content in blocks:
        if kind == "heading":
            h = clean_heading(content)
            if h:
                parts.append(f"<h2>{html.escape(h)}</h2>")
        elif kind == "list":
            items = [l.strip()[2:].strip() for l in content.splitlines() if l.strip().startswith("- ")]
            lis = "".join(f"<li>{html.escape(it)}</li>" for it in items)
            parts.append(f"<ul>{lis}</ul>")
        else:
            para = " ".join(l.strip() for l in content.splitlines())
            parts.append(f"<p>{html.escape(para)}</p>")
    parts.append("</body></html>")
    return "".join(parts)


def make_pdf_html(blocks: list[tuple[str, str]]) -> bool:
    try:
        import weasyprint  # type: ignore
    except Exception as exc:
        print(f"weasyprint unavailable: {exc}")
        return False
    try:
        weasyprint.HTML(string=blocks_to_html(blocks), base_url=str(ROOT)).write_pdf(str(OUT))
        return True
    except Exception as exc:
        print(f"weasyprint failed: {exc}")
        return False


def make_pdf_reportlab(blocks: list[tuple[str, str]]) -> bool:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("T", parent=styles["Title"], fontName="Times-Bold", fontSize=15, leading=18, spaceAfter=4)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Times-Bold", fontSize=11.5, leading=14, spaceBefore=12, spaceAfter=4)
    body_style = ParagraphStyle("B", parent=styles["BodyText"], fontName="Times-Roman", fontSize=10.5, leading=13.5, alignment=4, spaceAfter=7)

    story: list = [
        Paragraph(html.escape(TITLE), title_style),
        Paragraph(
            "Manuscript submitted to Sustainability Analytics and Modeling (Elsevier/IFORS)",
            ParagraphStyle("Sub", parent=body_style, alignment=1, fontSize=9, textColor="#555555"),
        ),
        Spacer(1, 10),
    ]
    for kind, content in blocks:
        if kind == "heading":
            h = clean_heading(content)
            if h:
                story.append(Paragraph(html.escape(h), h2_style))
        elif kind == "list":
            items = [l.strip()[2:].strip() for l in content.splitlines() if l.strip().startswith("- ")]
            story.append(
                ListFlowable(
                    [ListItem(Paragraph(html.escape(it), body_style)) for it in items],
                    bulletType="bullet",
                    start="\u2022",
                    leftIndent=16,
                )
            )
        else:
            para = " ".join(l.strip() for l in content.splitlines())
            story.append(Paragraph(html.escape(para), body_style))

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2.2 * cm, bottomMargin=2.2 * cm,
        title=TITLE, author="Aldrin Manon",
    )
    doc.build(story)
    return True


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: {SRC} not found")
        return 2
    blocks = parse_manuscript(SRC.read_text(encoding="utf-8"))
    print(f"parsed {len(blocks)} blocks from {SRC.name}")

    ok = make_pdf_html(blocks)
    if not ok:
        print("falling back to reportlab...")
        ok = make_pdf_reportlab(blocks)
    if not ok:
        print("ERROR: both PDF backends failed")
        return 1

    data = OUT.read_bytes()
    if not data.startswith(b"%PDF-"):
        print("ERROR: output is not a valid PDF")
        return 1
    size = len(data)
    print(f"OK: {OUT} ({size} bytes, {size / 1024:.1f} KB)")
    if size > 10 * 1024 * 1024:
        print("WARN: exceeds 10MB limit")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
