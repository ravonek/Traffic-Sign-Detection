#!/usr/bin/env python3
"""Build a polished five-slide defense deck from Traffic Sign artifacts.

The deck has two truthful modes:

* without artifacts: an explicitly marked pre-run presentation with no metrics;
* with the completed Colab ZIP/directory: measured validation/test values and
  exported evidence are inserted automatically.

No result is estimated or fabricated.
"""

from __future__ import annotations

import argparse
import csv
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Iterable

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "CSCI1409_Bonus_Traffic_Signs_Defense_3min.pptx"
COLAB_URL = (
    "https://colab.research.google.com/github/ravonek/Traffic-Sign-Detection/"
    "blob/main/CSCI1409_Bonus_Traffic_Signs_Colab.ipynb"
)


def C(value: str) -> RGBColor:
    value = value.lstrip("#")
    return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


NAVY = C("07111F")
NAVY_2 = C("0D1B2E")
SLATE = C("17283E")
PANEL = C("1D314A")
INK = C("132238")
MUTED = C("60708A")
WHITE = C("FFFFFF")
PAPER = C("F6F8FC")
LINE = C("DCE4EF")
CYAN = C("18D5C3")
BLUE = C("3977F6")
BLUE_2 = C("2154C7")
ORANGE = C("FFB04A")
RED = C("F04F5F")
GREEN = C("28C891")
YELLOW = C("FFD166")
SOFT_CYAN = C("DDF8F5")
SOFT_BLUE = C("E8F0FF")
SOFT_ORANGE = C("FFF0DD")
SOFT_RED = C("FFE8EB")

FONT_HEAD = "Aptos Display"
FONT_BODY = "Aptos"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def safe_extract(zip_path: Path, destination: Path) -> None:
    with zipfile.ZipFile(zip_path) as archive:
        root = destination.resolve()
        for item in archive.infolist():
            target = (destination / item.filename).resolve()
            if target != root and root not in target.parents:
                raise ValueError(f"Unsafe ZIP entry: {item.filename}")
        archive.extractall(destination)


def locate_artifacts(path: Path | None, temporary: Path) -> Path | None:
    if path is None:
        return None
    path = path.expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    if path.is_dir():
        return path
    if path.suffix.lower() != ".zip":
        raise ValueError("--artifacts must be a directory or a .zip file")
    safe_extract(path, temporary)
    return temporary


def evidence_root(artifacts: Path | None) -> Path | None:
    if artifacts is None:
        return None
    if (artifacts / "evidence").is_dir():
        return artifacts / "evidence"
    found = list(artifacts.rglob("test_metrics.json"))
    return found[0].parent if found else None


def fill(shape, color: RGBColor) -> None:
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def rect(slide, x, y, w, h, color, *, radius=True, line=None, line_width=1):
    x, y, w, h = map(int, (x, y, w, h))
    kind = (
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE
        if radius
        else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    )
    shape = slide.shapes.add_shape(kind, x, y, w, h)
    fill(shape, color)
    shape.line.color.rgb = line if line is not None else color
    shape.line.width = Pt(line_width)
    return shape


def shadow_card(slide, x, y, w, h, color=WHITE, *, radius=True, line=LINE):
    rect(slide, x + Inches(0.055), y + Inches(0.07), w, h, C("D5DDE9"), radius=radius)
    return rect(slide, x, y, w, h, color, radius=radius, line=line)


def circle(slide, x, y, d, color, *, line=None, line_width=1):
    x, y, d = map(int, (x, y, d))
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL, x, y, d, d)
    fill(shape, color)
    shape.line.color.rgb = line if line is not None else color
    shape.line.width = Pt(line_width)
    return shape


def line(slide, x1, y1, x2, y2, color, width=2):
    x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
    shape = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
    shape.line.color.rgb = color
    shape.line.width = Pt(width)
    return shape


def textbox(
    slide,
    text: str,
    x,
    y,
    w,
    h,
    *,
    size=20,
    color=INK,
    bold=False,
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.TOP,
    font=FONT_BODY,
    margin=0.02,
    spacing=1.0,
):
    x, y, w, h = map(int, (x, y, w, h))
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(margin)
    frame.margin_top = frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    paragraph.line_spacing = spacing
    run = paragraph.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def rich_text(slide, parts: Iterable[tuple[str, dict]], x, y, w, h, *, align=PP_ALIGN.LEFT):
    x, y, w, h = map(int, (x, y, w, h))
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = 0
    frame.margin_top = frame.margin_bottom = 0
    p = frame.paragraphs[0]
    p.alignment = align
    for value, style in parts:
        r = p.add_run()
        r.text = value
        r.font.name = style.get("font", FONT_BODY)
        r.font.size = Pt(style.get("size", 20))
        r.font.bold = style.get("bold", False)
        r.font.color.rgb = style.get("color", INK)
    return box


def pill(slide, text, x, y, w, color, *, text_color=WHITE, border=None):
    rect(slide, x, y, w, Inches(0.34), color, radius=True, line=border or color)
    textbox(
        slide,
        text.upper(),
        x + Inches(0.08),
        y + Inches(0.075),
        w - Inches(0.16),
        Inches(0.17),
        size=9,
        color=text_color,
        bold=True,
        align=PP_ALIGN.CENTER,
    )


def set_background(slide, color):
    rect(slide, 0, 0, Inches(13.333), Inches(7.5), color, radius=False)


def add_header(slide, section: str, title: str, subtitle: str | None = None, *, dark=False):
    fg = WHITE if dark else NAVY
    muted = C("A9B7CA") if dark else MUTED
    pill(
        slide,
        section,
        Inches(0.58),
        Inches(0.37),
        Inches(0.77),
        CYAN if dark else NAVY,
        text_color=NAVY if dark else WHITE,
    )
    textbox(
        slide,
        title,
        Inches(1.52),
        Inches(0.30),
        Inches(11.2),
        Inches(0.46),
        size=25,
        color=fg,
        bold=True,
        font=FONT_HEAD,
    )
    if subtitle:
        textbox(
            slide,
            subtitle,
            Inches(1.54),
            Inches(0.79),
            Inches(10.8),
            Inches(0.30),
            size=11,
            color=muted,
        )


def add_footer(slide, number: int, *, dark=False):
    color = C("8FA1B9") if dark else MUTED
    line(slide, Inches(0.62), Inches(7.04), Inches(12.70), Inches(7.04), C("29405E") if dark else LINE, 1)
    textbox(
        slide,
        "CSCI1409 DEEP LEARNING  ·  INDIVIDUAL BONUS PROJECT",
        Inches(0.64),
        Inches(7.13),
        Inches(5.2),
        Inches(0.18),
        size=8,
        color=color,
        bold=True,
    )
    textbox(
        slide,
        f"0{number}",
        Inches(12.16),
        Inches(7.10),
        Inches(0.52),
        Inches(0.20),
        size=9,
        color=color,
        bold=True,
        align=PP_ALIGN.RIGHT,
    )


def set_notes(slide, notes: str) -> None:
    try:
        slide.notes_slide.notes_text_frame.text = notes
    except (AttributeError, NotImplementedError):
        pass


def add_speed_sign(slide, x, y, d, number="50"):
    circle(slide, x, y, d, WHITE, line=RED, line_width=5)
    textbox(
        slide,
        number,
        x,
        y + d * 0.24,
        d,
        d * 0.40,
        size=max(12, int(d / 50000)),
        color=NAVY,
        bold=True,
        align=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE,
        font=FONT_HEAD,
    )


def add_stop_sign(slide, x, y, d):
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OCTAGON, x, y, d, d)
    fill(shape, RED)
    shape.line.color.rgb = WHITE
    shape.line.width = Pt(3)
    textbox(
        slide,
        "STOP",
        x,
        y + d * 0.34,
        d,
        d * 0.26,
        size=max(10, int(d / 60000)),
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE,
        font=FONT_HEAD,
    )


def add_traffic_light(slide, x, y, w, h):
    rect(slide, x, y, w, h, NAVY_2, radius=True, line=C("39516C"), line_width=1.5)
    d = min(w * 0.55, h * 0.22)
    cx = x + (w - d) / 2
    gap = (h - 3 * d) / 4
    for index, color in enumerate([RED, YELLOW, GREEN]):
        circle(slide, cx, y + gap + index * (d + gap), d, color)


def add_crosswalk_sign(slide, x, y, d):
    rect(slide, x, y, d, d, BLUE, radius=False, line=WHITE, line_width=2)
    tri = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ISOSCELES_TRIANGLE,
        int(x + d * 0.10),
        int(y + d * 0.08),
        int(d * 0.80),
        int(d * 0.74),
    )
    fill(tri, WHITE)
    tri.line.color.rgb = WHITE
    # Person
    circle(slide, x + d * 0.44, y + d * 0.25, d * 0.10, NAVY)
    line(slide, x + d * 0.49, y + d * 0.35, x + d * 0.47, y + d * 0.55, NAVY, 3)
    line(slide, x + d * 0.47, y + d * 0.41, x + d * 0.34, y + d * 0.49, NAVY, 3)
    line(slide, x + d * 0.47, y + d * 0.42, x + d * 0.61, y + d * 0.48, NAVY, 3)
    line(slide, x + d * 0.47, y + d * 0.55, x + d * 0.36, y + d * 0.70, NAVY, 3)
    line(slide, x + d * 0.47, y + d * 0.55, x + d * 0.59, y + d * 0.69, NAVY, 3)
    for i in range(4):
        rect(
            slide,
            x + d * (0.19 + i * 0.16),
            y + d * (0.77 - i * 0.01),
            d * 0.12,
            d * 0.055,
            NAVY,
            radius=False,
        )


def add_sun(slide, x, y, d):
    circle(slide, x, y, d, YELLOW)
    cx, cy = x + d / 2, y + d / 2
    for dx, dy in [(0, -0.42), (0, 0.42), (-0.42, 0), (0.42, 0), (-0.30, -0.30), (0.30, 0.30), (-0.30, 0.30), (0.30, -0.30)]:
        line(slide, cx + d * dx * 0.72, cy + d * dy * 0.72, cx + d * dx, cy + d * dy, YELLOW, 2)


def add_moon(slide, x, y, d):
    circle(slide, x, y, d, C("C4D5F2"))
    circle(slide, x + d * 0.30, y - d * 0.03, d * 0.84, NAVY_2)


def metric(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "—"


def minutes(value: Any) -> str:
    try:
        return f"{float(value):.1f} min"
    except (TypeError, ValueError):
        return "—"


def add_picture_contain(slide, path: Path, x, y, w, h):
    with Image.open(path) as image:
        iw, ih = image.size
    scale = min(w / iw, h / ih)
    pw, ph = int(iw * scale), int(ih * scale)
    return slide.shapes.add_picture(str(path), x + (w - pw) // 2, y + (h - ph) // 2, pw, ph)


def add_metric_card(slide, label, value, x, y, w, *, accent=CYAN, dark=False, sub=None):
    bg = PANEL if dark else WHITE
    fg = WHITE if dark else NAVY
    muted = C("A9B7CA") if dark else MUTED
    if dark:
        rect(slide, x, y, w, Inches(1.28), bg, radius=True, line=C("38506D"))
    else:
        shadow_card(slide, x, y, w, Inches(1.28))
    rect(slide, x, y, Inches(0.075), Inches(1.28), accent, radius=False)
    textbox(slide, label.upper(), x + Inches(0.22), y + Inches(0.19), w - Inches(0.35), Inches(0.22), size=9, color=muted, bold=True)
    textbox(slide, value, x + Inches(0.20), y + Inches(0.47), w - Inches(0.34), Inches(0.42), size=25, color=fg, bold=True, font=FONT_HEAD)
    if sub:
        textbox(slide, sub, x + Inches(0.22), y + Inches(0.99), w - Inches(0.35), Inches(0.17), size=8, color=muted)


def add_pipeline_step(slide, number, title, detail, x, y, w, *, accent):
    shadow_card(slide, x, y, w, Inches(1.55), WHITE)
    circle(slide, x + Inches(0.20), y + Inches(0.20), Inches(0.42), accent)
    textbox(slide, str(number), x + Inches(0.20), y + Inches(0.30), Inches(0.42), Inches(0.16), size=10, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    textbox(slide, title, x + Inches(0.20), y + Inches(0.76), w - Inches(0.40), Inches(0.28), size=14, color=NAVY, bold=True, font=FONT_HEAD)
    textbox(slide, detail, x + Inches(0.20), y + Inches(1.10), w - Inches(0.40), Inches(0.30), size=9, color=MUTED)


def build_deck(artifacts: Path | None, output: Path) -> None:
    evidence = evidence_root(artifacts)
    validation = read_csv(evidence / "validation_table.csv") if evidence else []
    counts = read_csv(evidence / "dataset_counts.csv") if evidence else []
    selection = read_json(evidence / "model_selection.json") if evidence else {}
    test = read_json(evidence / "test_metrics.json") if evidence else {}
    failures = read_json(evidence / "failure_analysis_candidates.json") if evidence else {}
    measured = len(validation) == 2 and bool(test.get("metrics"))

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # ------------------------------------------------------------------ Slide 1
    slide = prs.slides.add_slide(blank)
    set_background(slide, NAVY)
    rect(slide, Inches(0), Inches(0), Inches(0.13), Inches(7.5), CYAN, radius=False)
    rect(slide, Inches(8.45), Inches(0), Inches(4.88), Inches(7.5), NAVY_2, radius=False)
    pill(slide, "CSCI1409 · BONUS PROJECT", Inches(0.72), Inches(0.62), Inches(2.34), C("1F3853"), text_color=CYAN)
    pill(
        slide,
        "MEASURED" if measured else "PRE-RUN · RESULTS PENDING",
        Inches(3.20),
        Inches(0.62),
        Inches(2.35 if measured else 2.75),
        GREEN if measured else ORANGE,
        text_color=NAVY,
    )

    rich_text(
        slide,
        [
            ("DOES ", {"size": 39, "color": WHITE, "bold": True, "font": FONT_HEAD}),
            ("BRIGHTNESS", {"size": 39, "color": CYAN, "bold": True, "font": FONT_HEAD}),
            ("\nAUGMENTATION\nHELP YOLO11n?", {"size": 39, "color": WHITE, "bold": True, "font": FONT_HEAD}),
        ],
        Inches(0.72),
        Inches(1.38),
        Inches(7.25),
        Inches(2.55),
    )
    textbox(
        slide,
        "A controlled object-detection experiment across four road-sign classes",
        Inches(0.76),
        Inches(4.18),
        Inches(6.75),
        Inches(0.62),
        size=18,
        color=C("B8C7D9"),
    )
    textbox(slide, "BASELINE", Inches(0.76), Inches(5.20), Inches(1.18), Inches(0.22), size=9, color=C("91A5BD"), bold=True)
    textbox(slide, "hsv_v = 0.00", Inches(0.76), Inches(5.50), Inches(2.10), Inches(0.34), size=20, color=WHITE, bold=True, font=FONT_HEAD)
    line(slide, Inches(3.00), Inches(5.18), Inches(3.00), Inches(5.98), C("34506F"), 1)
    textbox(slide, "EXPERIMENT", Inches(3.28), Inches(5.20), Inches(1.40), Inches(0.22), size=9, color=CYAN, bold=True)
    textbox(slide, "hsv_v = 0.35", Inches(3.28), Inches(5.50), Inches(2.10), Inches(0.34), size=20, color=CYAN, bold=True, font=FONT_HEAD)
    textbox(slide, "Adilkhan Kaldybekov", Inches(0.76), Inches(6.56), Inches(3.20), Inches(0.28), size=12, color=C("8FA1B9"), bold=True)

    # Sign constellation
    rect(slide, Inches(8.86), Inches(0.66), Inches(3.94), Inches(5.95), C("12243A"), radius=True, line=C("28425E"), line_width=1.5)
    textbox(slide, "4 CLASSES", Inches(9.24), Inches(0.99), Inches(3.16), Inches(0.24), size=10, color=CYAN, bold=True, align=PP_ALIGN.CENTER)
    add_crosswalk_sign(slide, Inches(9.18), Inches(1.48), Inches(1.22))
    add_speed_sign(slide, Inches(11.05), Inches(1.44), Inches(1.30), "50")
    add_stop_sign(slide, Inches(9.14), Inches(3.50), Inches(1.32))
    add_traffic_light(slide, Inches(11.29), Inches(3.42), Inches(0.82), Inches(1.72))
    textbox(slide, "crosswalk", Inches(8.96), Inches(2.83), Inches(1.64), Inches(0.22), size=10, color=C("A9B7CA"), align=PP_ALIGN.CENTER)
    textbox(slide, "speed limit", Inches(10.90), Inches(2.83), Inches(1.62), Inches(0.22), size=10, color=C("A9B7CA"), align=PP_ALIGN.CENTER)
    textbox(slide, "stop", Inches(9.03), Inches(5.12), Inches(1.50), Inches(0.22), size=10, color=C("A9B7CA"), align=PP_ALIGN.CENTER)
    textbox(slide, "traffic light", Inches(10.83), Inches(5.32), Inches(1.74), Inches(0.22), size=10, color=C("A9B7CA"), align=PP_ALIGN.CENTER)
    pill(slide, "YOLO11n · 512 px · 14 epochs", Inches(9.35), Inches(5.94), Inches(2.96), C("1F3853"), text_color=WHITE)
    set_notes(
        slide,
        "Hello. This project studies four-class traffic-sign detection with YOLO11n. "
        "The research question is whether one controlled change—brightness augmentation—"
        "improves validation mAP at IoU 0.50.",
    )

    # ------------------------------------------------------------------ Slide 2
    slide = prs.slides.add_slide(blank)
    set_background(slide, PAPER)
    add_header(slide, "01", "From raw VOC data to a locked test set", "The split is designed before training and keeps perceptual duplicate groups together")

    # Data headline
    rich_text(
        slide,
        [
            ("877", {"size": 42, "color": NAVY, "bold": True, "font": FONT_HEAD}),
            ("  documented images", {"size": 18, "color": MUTED, "bold": True}),
        ],
        Inches(0.66),
        Inches(1.38),
        Inches(4.35),
        Inches(0.66),
    )
    pill(slide, "PASCAL VOC XML", Inches(5.05), Inches(1.49), Inches(1.52), NAVY)
    pill(slide, "4 CLASSES", Inches(6.72), Inches(1.49), Inches(1.14), BLUE)
    pill(slide, "SEED 42", Inches(8.01), Inches(1.49), Inches(1.00), GREEN, text_color=NAVY)

    # Four-step pipeline
    xs = [0.66, 3.77, 6.88, 9.99]
    steps = [
        (1, "Audit", "XML, classes, boxes, image sizes", BLUE),
        (2, "Group", "SHA-256 + pHash ≤ 4", CYAN),
        (3, "Split", "train / validation / locked test", ORANGE),
        (4, "Convert", "normalized YOLO labels", RED),
    ]
    for i, (n, title, detail, accent) in enumerate(steps):
        add_pipeline_step(slide, n, title, detail, Inches(xs[i]), Inches(2.25), Inches(2.62), accent=accent)
        if i < 3:
            textbox(slide, "→", Inches(xs[i] + 2.68), Inches(2.78), Inches(0.31), Inches(0.28), size=21, color=MUTED, bold=True, align=PP_ALIGN.CENTER)

    # Class strip
    rect(slide, Inches(0.66), Inches(4.20), Inches(12.00), Inches(1.66), NAVY, radius=True)
    class_items = [
        ("00", "crosswalk", CYAN),
        ("01", "speed limit", BLUE),
        ("02", "stop", RED),
        ("03", "traffic light", ORANGE),
    ]
    for idx, (num, label, accent) in enumerate(class_items):
        x = Inches(0.94 + idx * 2.93)
        circle(slide, x, Inches(4.55), Inches(0.52), accent)
        textbox(slide, num, x, Inches(4.69), Inches(0.52), Inches(0.15), size=9, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
        textbox(slide, label, x + Inches(0.70), Inches(4.53), Inches(1.92), Inches(0.27), size=14, color=WHITE, bold=True, font=FONT_HEAD)
        if counts:
            total = sum(int(float(row.get(label.replace(" ", ""), 0) or 0)) for row in counts)
            detail = f"{total} objects observed"
        else:
            detail = "count after Colab run"
        textbox(slide, detail, x + Inches(0.70), Inches(4.91), Inches(1.92), Inches(0.23), size=9, color=C("A9B7CA"))

    rect(slide, Inches(0.66), Inches(6.12), Inches(12.00), Inches(0.58), SOFT_RED, radius=True, line=C("F7C5CB"))
    textbox(slide, "LIMITATION", Inches(0.89), Inches(6.32), Inches(0.84), Inches(0.16), size=8, color=RED, bold=True)
    textbox(slide, "Source-video IDs are unavailable; perceptual grouping reduces near-duplicate leakage but cannot prove video-level separation.", Inches(1.78), Inches(6.26), Inches(10.56), Inches(0.26), size=10, color=INK, bold=True)
    add_footer(slide, 2)
    set_notes(
        slide,
        "The source contains 877 documented images with VOC boxes. The notebook audits every annotation, "
        "groups exact and perceptual duplicates, reserves the provider hold-out for final testing, and converts labels to YOLO format. "
        "The important limitation is that original video IDs are unavailable.",
    )

    # ------------------------------------------------------------------ Slide 3
    slide = prs.slides.add_slide(blank)
    set_background(slide, NAVY)
    add_header(slide, "02", "One variable changes. Everything else stays fixed.", "A controlled comparison—not a hyperparameter search", dark=True)

    # Baseline panel
    rect(slide, Inches(0.66), Inches(1.42), Inches(5.56), Inches(3.58), NAVY_2, radius=True, line=C("36506E"), line_width=1.5)
    add_moon(slide, Inches(1.07), Inches(1.83), Inches(0.72))
    pill(slide, "RUN A · BASELINE", Inches(2.02), Inches(1.88), Inches(1.76), C("243A54"), text_color=C("C8D5E6"))
    textbox(slide, "hsv_v", Inches(1.07), Inches(2.82), Inches(1.50), Inches(0.28), size=13, color=C("93A8C0"), bold=True)
    textbox(slide, "0.00", Inches(1.07), Inches(3.14), Inches(2.35), Inches(0.70), size=45, color=WHITE, bold=True, font=FONT_HEAD)
    textbox(slide, "No brightness jitter", Inches(1.10), Inches(4.04), Inches(3.25), Inches(0.31), size=16, color=C("B2C2D4"), bold=True)
    rect(slide, Inches(4.50), Inches(2.00), Inches(1.22), Inches(2.48), C("101B2A"), radius=True)
    add_speed_sign(slide, Inches(4.73), Inches(2.37), Inches(0.76), "50")
    textbox(slide, "same scene", Inches(4.61), Inches(3.53), Inches(1.00), Inches(0.20), size=8, color=C("758AA4"), align=PP_ALIGN.CENTER)

    # Experiment panel
    rect(slide, Inches(7.11), Inches(1.42), Inches(5.56), Inches(3.58), C("163752"), radius=True, line=CYAN, line_width=1.8)
    add_sun(slide, Inches(7.52), Inches(1.83), Inches(0.72))
    pill(slide, "RUN B · EXPERIMENT", Inches(8.47), Inches(1.88), Inches(2.05), CYAN, text_color=NAVY)
    textbox(slide, "hsv_v", Inches(7.52), Inches(2.82), Inches(1.50), Inches(0.28), size=13, color=C("9EDBD6"), bold=True)
    textbox(slide, "0.35", Inches(7.52), Inches(3.14), Inches(2.35), Inches(0.70), size=45, color=CYAN, bold=True, font=FONT_HEAD)
    textbox(slide, "Moderate brightness jitter", Inches(7.55), Inches(4.04), Inches(3.35), Inches(0.31), size=16, color=WHITE, bold=True)
    rect(slide, Inches(10.95), Inches(2.00), Inches(1.22), Inches(2.48), C("DBEAF4"), radius=True)
    add_speed_sign(slide, Inches(11.18), Inches(2.37), Inches(0.76), "50")
    textbox(slide, "same scene", Inches(11.06), Inches(3.53), Inches(1.00), Inches(0.20), size=8, color=C("5C6F84"), align=PP_ALIGN.CENTER)

    # One-variable bridge
    pill(slide, "ONLY THIS CHANGES", Inches(5.35), Inches(2.92), Inches(2.64), ORANGE, text_color=NAVY)
    line(slide, Inches(6.22), Inches(3.61), Inches(7.11), Inches(3.61), ORANGE, 2)
    line(slide, Inches(6.22), Inches(3.61), Inches(6.04), Inches(3.49), ORANGE, 2)
    line(slide, Inches(6.22), Inches(3.61), Inches(6.04), Inches(3.73), ORANGE, 2)
    line(slide, Inches(7.11), Inches(3.61), Inches(6.93), Inches(3.49), ORANGE, 2)
    line(slide, Inches(7.11), Inches(3.61), Inches(6.93), Inches(3.73), ORANGE, 2)

    textbox(slide, "FIXED IN BOTH RUNS", Inches(0.70), Inches(5.42), Inches(1.90), Inches(0.23), size=9, color=CYAN, bold=True)
    settings = ["YOLO11n", "512 × 512", "14 epochs", "batch 16", "SGD · 0.01", "seed 42", "same split"]
    x = 0.70
    for setting in settings:
        width = 1.28 if len(setting) < 10 else 1.54
        pill(slide, setting, Inches(x), Inches(5.80), Inches(width), C("1D314A"), text_color=WHITE, border=C("3A526E"))
        x += width + 0.16
    rect(slide, Inches(0.70), Inches(6.37), Inches(11.92), Inches(0.42), C("13283D"), radius=True)
    textbox(slide, "HYPOTHESIS  ·  brightness variation may improve validation mAP@0.50 across darker and brighter scenes", Inches(0.93), Inches(6.50), Inches(11.46), Inches(0.16), size=9, color=C("BDD0E2"), bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 3, dark=True)
    set_notes(
        slide,
        "Both runs start from the same pretrained YOLO11n weights and use the same data split, optimizer, seed, image size and duration. "
        "Only HSV value augmentation changes from zero to 0.35. The hypothesis is written before training, and an improvement is not required.",
    )

    # ------------------------------------------------------------------ Slide 4
    slide = prs.slides.add_slide(blank)
    set_background(slide, PAPER)
    add_header(slide, "03", "Validation decides the winner", "The locked test set remains invisible until after model selection")

    validation_by_name = {row.get("run", ""): row for row in validation}
    base = validation_by_name.get("baseline_no_brightness", {})
    exp = validation_by_name.get("experiment_brightness_035", {})
    chosen = selection.get("selected_run")

    # Run name labels
    pill(slide, "A · hsv_v 0.00", Inches(0.70), Inches(1.39), Inches(1.55), NAVY)
    pill(slide, "B · hsv_v 0.35", Inches(6.86), Inches(1.39), Inches(1.55), CYAN, text_color=NAVY)
    if measured and chosen:
        winner_x = 0.70 if chosen == "baseline_no_brightness" else 6.86
        pill(slide, "SELECTED", Inches(winner_x + 1.72), Inches(1.39), Inches(1.10), GREEN, text_color=NAVY)
    else:
        pill(slide, "AWAITING COLAB RUN", Inches(10.15), Inches(1.39), Inches(2.18), ORANGE, text_color=NAVY)

    labels = [("Precision", "precision", BLUE), ("Recall", "recall", ORANGE), ("mAP@0.50", "mAP50", CYAN)]
    for i, (label, key, accent) in enumerate(labels):
        x1 = Inches(0.70 + i * 1.84)
        x2 = Inches(6.86 + i * 1.84)
        add_metric_card(slide, label, metric(base.get(key)), x1, Inches(2.03), Inches(1.62), accent=accent, sub="validation")
        add_metric_card(slide, label, metric(exp.get(key)), x2, Inches(2.03), Inches(1.62), accent=accent, sub="validation")
    add_metric_card(slide, "Training time", minutes(base.get("training_minutes")), Inches(0.70), Inches(3.56), Inches(5.54), accent=MUTED, sub="Run A wall-clock time")
    add_metric_card(slide, "Training time", minutes(exp.get("training_minutes")), Inches(6.86), Inches(3.56), Inches(5.54), accent=MUTED, sub="Run B wall-clock time")

    # Selection logic
    rect(slide, Inches(0.70), Inches(5.18), Inches(11.70), Inches(1.14), NAVY, radius=True)
    textbox(slide, "MODEL SELECTION", Inches(0.98), Inches(5.42), Inches(1.42), Inches(0.18), size=9, color=CYAN, bold=True)
    circle(slide, Inches(2.61), Inches(5.31), Inches(0.40), CYAN)
    textbox(slide, "1", Inches(2.63), Inches(5.36), Inches(0.34), Inches(0.34), size=13, color=NAVY, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
    textbox(slide, "highest validation mAP@0.50", Inches(3.18), Inches(5.40), Inches(2.42), Inches(0.22), size=11, color=WHITE, bold=True)
    textbox(slide, "→", Inches(5.69), Inches(5.37), Inches(0.35), Inches(0.25), size=17, color=C("8195AD"), bold=True, align=PP_ALIGN.CENTER)
    circle(slide, Inches(6.17), Inches(5.31), Inches(0.40), ORANGE)
    textbox(slide, "2", Inches(6.19), Inches(5.36), Inches(0.34), Inches(0.34), size=13, color=NAVY, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
    textbox(slide, "Precision tie-break", Inches(6.75), Inches(5.40), Inches(1.70), Inches(0.22), size=11, color=WHITE, bold=True)
    textbox(slide, "→", Inches(8.54), Inches(5.37), Inches(0.35), Inches(0.25), size=17, color=C("8195AD"), bold=True, align=PP_ALIGN.CENTER)
    pill(slide, "best.pt → final_best.pt", Inches(9.02), Inches(5.36), Inches(2.88), GREEN, text_color=NAVY)
    pill(slide, "TEST SET LOCKED", Inches(4.98), Inches(6.51), Inches(2.32), RED)
    textbox(slide, "No tuning after test metrics", Inches(7.48), Inches(6.58), Inches(2.70), Inches(0.18), size=9, color=RED, bold=True)
    add_footer(slide, 4)
    set_notes(
        slide,
        "Compare Precision, Recall, mAP at 0.50 and time for both validation runs. "
        "The winner is selected by validation mAP, then Precision as a tie-breaker. "
        "The final test set is not used to choose the model or revise settings.",
    )

    # ------------------------------------------------------------------ Slide 5
    slide = prs.slides.add_slide(blank)
    set_background(slide, NAVY)
    add_header(slide, "04", "Final evidence, failure review and conclusion", "The conclusion is limited to this dataset, split and single run per condition", dark=True)

    test_metrics = test.get("metrics", {})
    selected = test.get("selected_run") or selection.get("selected_run")
    add_metric_card(slide, "Test Precision", metric(test_metrics.get("precision")), Inches(0.66), Inches(1.42), Inches(2.22), accent=CYAN, dark=True, sub="held-out test")
    add_metric_card(slide, "Test Recall", metric(test_metrics.get("recall")), Inches(3.06), Inches(1.42), Inches(2.22), accent=BLUE, dark=True, sub="held-out test")
    add_metric_card(slide, "Test mAP@0.50", metric(test_metrics.get("mAP50")), Inches(5.46), Inches(1.42), Inches(2.22), accent=ORANGE, dark=True, sub="held-out test")
    rect(slide, Inches(7.98), Inches(1.42), Inches(4.66), Inches(1.28), C("13283D"), radius=True, line=C("38506D"))
    textbox(slide, "SELECTED CHECKPOINT", Inches(8.25), Inches(1.64), Inches(4.12), Inches(0.18), size=9, color=CYAN, bold=True)
    textbox(slide, selected or "pending after validation", Inches(8.25), Inches(2.02), Inches(4.10), Inches(0.31), size=16 if selected else 15, color=WHITE, bold=True, font=FONT_HEAD)

    images: list[Path] = []
    if evidence:
        images.extend(sorted(evidence.glob("failure_*.png"))[:3])
        if not images and (evidence / "test_predictions_8.png").exists():
            images.append(evidence / "test_predictions_8.png")
    if images:
        for i, image_path in enumerate(images[:3]):
            x = Inches(0.66 + i * 2.20)
            rect(slide, x, Inches(3.02), Inches(2.06), Inches(2.45), C("12243A"), radius=True, line=C("38506D"))
            add_picture_contain(slide, image_path, x + Inches(0.08), Inches(3.10), Inches(1.90), Inches(2.12))
            textbox(slide, image_path.stem.replace("_", " "), x + Inches(0.12), Inches(5.25), Inches(1.82), Inches(0.16), size=8, color=C("9DB0C5"), align=PP_ALIGN.CENTER)
    else:
        rect(slide, Inches(0.66), Inches(3.02), Inches(6.64), Inches(2.45), C("12243A"), radius=True, line=C("38506D"))
        # Abstract prediction canvas
        rect(slide, Inches(0.94), Inches(3.32), Inches(2.66), Inches(1.72), C("1B334B"), radius=True)
        add_crosswalk_sign(slide, Inches(1.20), Inches(3.59), Inches(0.78))
        rect(slide, Inches(1.08), Inches(3.48), Inches(1.12), Inches(1.12), C("1B334B"), radius=False, line=GREEN, line_width=2)
        pill(slide, "GT crosswalk", Inches(1.04), Inches(4.68), Inches(1.18), GREEN, text_color=NAVY)
        rect(slide, Inches(3.93), Inches(3.32), Inches(2.88), Inches(1.72), C("1B334B"), radius=True)
        add_stop_sign(slide, Inches(4.28), Inches(3.60), Inches(0.76))
        rect(slide, Inches(4.11), Inches(3.46), Inches(1.14), Inches(1.14), C("1B334B"), radius=False, line=ORANGE, line_width=2)
        pill(slide, "PRED stop 0.84", Inches(4.06), Inches(4.68), Inches(1.40), ORANGE, text_color=NAVY)
        textbox(slide, "REAL PREDICTION & FAILURE IMAGES APPEAR HERE AFTER THE COLAB RUN", Inches(1.16), Inches(5.19), Inches(5.62), Inches(0.18), size=8, color=C("9DB0C5"), bold=True, align=PP_ALIGN.CENTER)

    # Conclusion / checklist
    rect(slide, Inches(7.62), Inches(3.02), Inches(5.02), Inches(2.45), C("13283D"), radius=True, line=C("38506D"))
    if measured:
        cases = failures.get("cases", []) if isinstance(failures, dict) else []
        textbox(slide, "EVIDENCE-BASED REVIEW", Inches(7.94), Inches(3.34), Inches(4.38), Inches(0.24), size=12, color=CYAN, bold=True)
        rows = []
        for case in cases[:3]:
            kinds = ", ".join(case.get("failure_types") or ["challenging correct case"])
            rows.append(f"• {case.get('image', 'image')}: {kinds}")
        text = "\n".join(rows) or "• Review green ground-truth and orange prediction boxes\n• Confirm causes from visible evidence"
        textbox(slide, text, Inches(7.94), Inches(3.78), Inches(4.34), Inches(1.00), size=11, color=WHITE)
        textbox(slide, "Claim only what this split and one run per condition support.", Inches(7.94), Inches(4.95), Inches(4.30), Inches(0.28), size=10, color=ORANGE, bold=True)
        try:
            delta_recall = float(exp["recall"]) - float(base["recall"])
            delta_map = float(exp["mAP50"]) - float(base["mAP50"])
            delta_precision = float(exp["precision"]) - float(base["precision"])
            conclusion = (
                f"Brightness changed validation: Recall {delta_recall:+.4f}, "
                f"mAP@0.50 {delta_map:+.4f}, Precision {delta_precision:+.4f}."
            )
        except (KeyError, TypeError, ValueError):
            conclusion = "The measured conclusion is limited to this split and one run per condition."
    else:
        textbox(slide, "FINISH BEFORE DEFENSE", Inches(7.94), Inches(3.31), Inches(4.38), Inches(0.24), size=12, color=ORANGE, bold=True)
        checklist = [
            ("01", "Run both trainings"),
            ("02", "Evaluate locked test once"),
            ("03", "Inspect three failure cases"),
            ("04", "Regenerate this deck"),
        ]
        for idx, (num, label) in enumerate(checklist):
            y = 3.74 + idx * 0.37
            circle(slide, Inches(7.96), Inches(y), Inches(0.25), C("29445F"))
            textbox(slide, num, Inches(7.96), Inches(y + 0.07), Inches(0.25), Inches(0.10), size=6, color=CYAN, bold=True, align=PP_ALIGN.CENTER)
            textbox(slide, label, Inches(8.36), Inches(y + 0.02), Inches(3.56), Inches(0.18), size=10, color=WHITE, bold=True)
        button = rect(slide, Inches(10.44), Inches(4.84), Inches(1.74), Inches(0.40), CYAN, radius=True)
        button.click_action.hyperlink.address = COLAB_URL
        box = textbox(slide, "OPEN COLAB ↗", Inches(10.54), Inches(4.96), Inches(1.54), Inches(0.16), size=8, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
        box.text_frame.paragraphs[0].runs[0].hyperlink.address = COLAB_URL
        conclusion = "Conclusion pending: no checkpoint and no measured metric are claimed yet."

    rect(slide, Inches(0.66), Inches(5.85), Inches(11.98), Inches(0.70), C("173047"), radius=True)
    textbox(slide, "CONCLUSION", Inches(0.93), Inches(6.09), Inches(1.05), Inches(0.16), size=8, color=CYAN, bold=True)
    textbox(slide, conclusion, Inches(2.12), Inches(6.02), Inches(9.98), Inches(0.27), size=13, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    pill(slide, "SMALL DATA", Inches(0.74), Inches(6.67), Inches(1.12), C("243A54"), text_color=C("B8C7D9"))
    pill(slide, "ONE RUN / CONDITION", Inches(1.99), Inches(6.67), Inches(1.80), C("243A54"), text_color=C("B8C7D9"))
    pill(slide, "NO VIDEO IDs", Inches(3.92), Inches(6.67), Inches(1.30), C("243A54"), text_color=C("B8C7D9"))
    pill(slide, "NOT SAFETY-CRITICAL", Inches(5.35), Inches(6.67), Inches(1.85), C("243A54"), text_color=C("B8C7D9"))
    add_footer(slide, 5, dark=True)
    set_notes(
        slide,
        "After model selection, evaluate the chosen checkpoint once on the held-out test set. "
        "Show real predictions and failure cases, then describe only what is visible. "
        "The conclusion must remain limited by the small dataset, one run per condition and missing source-video IDs.",
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    prs.save(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, help="Completed Colab artifact ZIP or extracted directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Destination PPTX path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with tempfile.TemporaryDirectory(prefix="traffic_sign_artifacts_") as folder:
        artifacts = locate_artifacts(args.artifacts, Path(folder))
        build_deck(artifacts, args.output.resolve())
    print(f"Saved: {args.output.resolve()}")


if __name__ == "__main__":
    main()
