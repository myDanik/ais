"""Read exported L02 slides; render review PNGs and record exact SVG text."""
from pathlib import Path
import hashlib
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[3]
QA = Path(__file__).resolve().parent
RENDER = QA / "review_png"
RENDER.mkdir(exist_ok=True)
sys.stdout.reconfigure(encoding="utf-8")
ns = {"s": "http://www.w3.org/2000/svg"}
content = json.loads((ROOT / "source/figma/L02_content.json").read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
slides = []
for i in range(1, 24):
    stem = f"slide-{i:02}"
    pdf = QA / f"{stem}.pdf"
    svg = ROOT / f"assets/figma/L02/{stem}.svg"
    if not pdf.exists() or not svg.exists():
        continue
    root = ET.parse(svg).getroot()
    text_nodes = []
    for text in root.findall(".//s:text", ns):
        lines = [{"text": "".join(t.itertext()), "x": t.get("x"), "baseline": t.get("y")}
                 for t in text.findall("s:tspan", ns)]
        text_nodes.append({"font": text.get("font-family"), "font_size": float(text.get("font-size")),
                           "fill": text.get("fill"), "lines": lines,
                           "text": " ".join(l["text"] for l in lines)})
    title = content[i-1]["title"]
    assert title in [" ".join(t["text"].split()) for t in text_nodes], (i, title)
    doc = fitz.open(pdf)
    assert len(doc) == 1
    page = doc[0]
    assert tuple(page.rect) == (0, 0, 1920, 1080)
    target = RENDER / f"{stem}.png"
    if not target.exists() or target.stat().st_mtime < pdf.stat().st_mtime:
        page.get_pixmap(alpha=False).save(target)
    spans = [s for b in page.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]
    outside = [s["bbox"] for s in spans if not page.rect.contains(fitz.Rect(s["bbox"]))]
    # Type3 mappings make the PDF's extracted Unicode unreliable. Bboxes still
    # work as conservative visual geometry; exact characters come from SVG.
    overlaps = []
    for a in range(len(spans)):
        ra = fitz.Rect(spans[a]["bbox"])
        for b in range(a+1, len(spans)):
            rb = fitz.Rect(spans[b]["bbox"])
            cross = ra & rb
            if cross.is_empty:
                continue
            ratio = cross.get_area() / min(ra.get_area(), rb.get_area())
            if ratio > .15:
                overlaps.append({"a": a, "b": b, "fraction_of_smaller_bbox": round(ratio, 4),
                                 "a_bbox": list(ra), "b_bbox": list(rb)})
    slides.append({"number": i, "title": title, "pdf_sha256": sha(pdf), "svg_sha256": sha(svg),
                   "render_sha256": sha(target), "dimensions": [1920, 1080], "text_nodes": text_nodes,
                   "outside_page_text_bbox": outside, "possible_bbox_overlaps": overlaps})

rows = list(csv.DictReader((ROOT / "data/requests.csv").open(encoding="utf-8-sig", newline="")))
exact_inputs = []
for slide_num, low, high, row_id in [(22, 380, 550, "library-19-1"),
                                    (23, 400, 560, "library-20-1"),
                                    (23, 680, 810, "library-20-2")]:
    slide = next((s for s in slides if s["number"] == slide_num), None)
    if slide is None:
        continue
    lines = {}
    for node in slide["text_nodes"]:
        for part in node["lines"]:
            x, y = float(part["x"]), float(part["baseline"])
            if x < 1300 and low < y < high:
                lines.setdefault(round(y, 1), []).append((x, part["text"]))
    reconstructed = " ".join("".join(t for _, t in sorted(parts)) for _, parts in sorted(lines.items()))
    reconstructed = " ".join(reconstructed.split()).strip("«»")
    expected = next(r["text"] for r in rows if r["id"] == row_id)
    assert reconstructed == expected, (slide_num, reconstructed, expected)
    exact_inputs.append({"slide": slide_num, "row_id": row_id, "input": reconstructed, "matches_csv_exactly": True})

lecture_pdf = ROOT / "dist/teacher/L02/lecture.pdf"
lecture_doc = fitz.open(lecture_pdf)
lecture_headings = []
for pi, page in enumerate(lecture_doc, 1):
    for line in page.get_text().splitlines():
        if match := re.match(r"^Слайд (\d+)\. (.+)$", line):
            lecture_headings.append({"number": int(match.group(1)), "title": match.group(2), "page": pi})
assert [h["number"] for h in lecture_headings] == list(range(1, 24))
assert [h["title"] for h in lecture_headings] == [c["title"] for c in content]
out = {
    "date": "2026-09-08", "mode": "review of exported local SVG/PDF; no Figma calls",
    "slides_available": len(slides), "expected_slides": 23, "slides": slides,
    "exact_input_checks": exact_inputs,
    "lecture": {"pdf_sha256": sha(lecture_pdf), "pages": len(lecture_doc), "headings": lecture_headings},
    "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in [
        ROOT / "source/lectures/L02.md", ROOT / "source/figma/L02_content.json", ROOT / "source/figma/L02_design.md"]},
    "manual_review": "see presentation_review.md; bbox overlaps are candidates, not automatic failures",
}
(QA / "presentation_review_evidence.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"slides": len(slides), "outside_page": sum(len(s["outside_page_text_bbox"]) for s in slides),
                  "bbox_overlap_candidates": {s["number"]: s["possible_bbox_overlaps"] for s in slides if s["possible_bbox_overlaps"]},
                  "lecture_pages": len(lecture_doc), "lecture_headings": len(lecture_headings)}, ensure_ascii=False, indent=2))
