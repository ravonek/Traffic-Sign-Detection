#!/usr/bin/env python3
"""Build the five-slide defense deck from real notebook artifacts.

The script never invents missing metrics. Without an artifact bundle it creates
an explicitly marked pre-run deck; with the completed Colab ZIP it fills the
tables and uses exported prediction/failure images.
"""

from __future__ import annotations

import argparse
import csv
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Iterable

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "CSCI1409_Bonus_Traffic_Signs_Defense_3min.pptx"

NAVY = RGBColor(12, 25, 48)
BLUE = RGBColor(37, 99, 235)
CYAN = RGBColor(14, 203, 180)
ORANGE = RGBColor(249, 160, 67)
INK = RGBColor(24, 35, 54)
MUTED = RGBColor(93, 107, 128)
PALE = RGBColor(238, 244, 251)
WHITE = RGBColor(255, 255, 255)
RED = RGBColor(202, 54, 75)


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
            if root not in target.parents and target != root:
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
    direct = artifacts / "evidence"
    if direct.is_dir():
        return direct
    found = list(artifacts.rglob("test_metrics.json"))
    return found[0].parent if found else None


def add_rect(slide, x, y, w, h, fill, radius=True, line=None):
    kind = MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE if radius else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line or fill
    return shape


def add_text(
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
    font="Aptos",
    margin=0.04,
    valign=MSO_ANCHOR.TOP,
):
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.clear()
    frame.margin_left = frame.margin_right = Inches(margin)
    frame.margin_top = frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_rich_lines(slide, lines: Iterable[tuple[str, str]], x, y, w, h, size=18):
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(0.08)
    for index, (lead, body) in enumerate(lines):
        p = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        p.space_after = Pt(10)
        p.font.name = "Aptos"
        p.font.size = Pt(size)
        r = p.add_run()
        r.text = lead
        r.font.bold = True
        r.font.color.rgb = BLUE
        r2 = p.add_run()
        r2.text = body
        r2.font.color.rgb = INK
    return box


def add_title(slide, number: str, title: str, subtitle: str | None = None):
    add_text(slide, number, Inches(0.55), Inches(0.30), Inches(0.52), Inches(0.40),
             size=14, color=CYAN, bold=True, valign=MSO_ANCHOR.MIDDLE)
    add_text(slide, title, Inches(1.05), Inches(0.22), Inches(11.65), Inches(0.55),
             size=27, color=NAVY, bold=True)
    if subtitle:
        add_text(slide, subtitle, Inches(1.08), Inches(0.77), Inches(11.2), Inches(0.35),
                 size=12, color=MUTED)


def add_footer(slide, slide_number: int):
    add_text(slide, "CSCI1409 · Individual Bonus Project", Inches(0.62), Inches(7.14),
             Inches(4.0), Inches(0.20), size=9, color=MUTED)
    add_text(slide, str(slide_number), Inches(12.15), Inches(7.10), Inches(0.55),
             Inches(0.24), size=10, color=MUTED, align=PP_ALIGN.RIGHT)


def set_notes(slide, notes: str) -> None:
    try:
        frame = slide.notes_slide.notes_text_frame
        frame.text = notes
    except (AttributeError, NotImplementedError):
        pass


def metric(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "Pending"


def minutes(value: Any) -> str:
    try:
        return f"{float(value):.1f} min"
    except (TypeError, ValueError):
        return "Pending"


def add_metric_card(slide, label: str, value: str, x, y, color=BLUE):
    add_rect(slide, x, y, Inches(2.05), Inches(1.02), PALE)
    add_text(slide, label, x + Inches(0.16), y + Inches(0.13), Inches(1.72), Inches(0.24),
             size=10, color=MUTED, bold=True)
    add_text(slide, value, x + Inches(0.14), y + Inches(0.41), Inches(1.74), Inches(0.42),
             size=24 if value != "Pending" else 18, color=color, bold=True)


def add_table(slide, rows: list[list[str]], x, y, widths: list[float], row_height=0.46):
    total_w = sum(widths)
    for r, row in enumerate(rows):
        x_pos = x
        for c, value in enumerate(row):
            fill = NAVY if r == 0 else (WHITE if r % 2 else PALE)
            color = WHITE if r == 0 else INK
            add_rect(slide, x_pos, y + Inches(row_height * r), Inches(widths[c]),
                     Inches(row_height), fill, radius=False, line=PALE if r else NAVY)
            add_text(slide, value, x_pos + Inches(0.05), y + Inches(row_height * r + 0.06),
                     Inches(widths[c] - 0.10), Inches(row_height - 0.08),
                     size=10 if r else 9, color=color, bold=(r == 0 or c == 0),
                     valign=MSO_ANCHOR.MIDDLE)
            x_pos += Inches(widths[c])
    return Inches(total_w), Inches(row_height * len(rows))


def add_picture_contain(slide, path: Path, x, y, w, h):
    from PIL import Image

    with Image.open(path) as image:
        iw, ih = image.size
    scale = min(w / iw, h / ih)
    pw, ph = int(iw * scale), int(ih * scale)
    return slide.shapes.add_picture(str(path), x + (w - pw) // 2, y + (h - ph) // 2, pw, ph)


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

    # Slide 1
    slide = prs.slides.add_slide(blank)
    add_rect(slide, 0, 0, prs.slide_width, prs.slide_height, NAVY, radius=False)
    add_rect(slide, Inches(0.72), Inches(0.76), Inches(0.12), Inches(4.95), CYAN, radius=False)
    add_text(slide, "TRAFFIC SIGN\nDETECTION", Inches(1.16), Inches(1.05), Inches(8.2), Inches(1.55),
             size=36, color=WHITE, bold=True)
    add_text(slide, "YOLO11n · controlled brightness experiment", Inches(1.18), Inches(2.67),
             Inches(7.3), Inches(0.46), size=20, color=CYAN)
    add_text(slide, "Does HSV brightness augmentation improve road-sign detection\nunder different lighting conditions?",
             Inches(1.18), Inches(3.34), Inches(7.5), Inches(1.15), size=22, color=WHITE)
    status_color = CYAN if measured else ORANGE
    status_text = "MEASURED RESULTS" if measured else "PRE-RUN · RESULTS PENDING"
    add_rect(slide, Inches(9.35), Inches(1.10), Inches(3.10), Inches(0.55), status_color)
    add_text(slide, status_text, Inches(9.47), Inches(1.23), Inches(2.86), Inches(0.24),
             size=11, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    for idx, label in enumerate(["crosswalk", "speed limit", "stop", "traffic light"]):
        add_rect(slide, Inches(9.42), Inches(2.15 + idx * 0.76), Inches(2.92), Inches(0.53),
                 RGBColor(27, 44, 72))
        add_text(slide, f"0{idx}  {label}", Inches(9.62), Inches(2.29 + idx * 0.76),
                 Inches(2.45), Inches(0.23), size=13, color=WHITE, bold=True)
    add_text(slide, "CSCI1409 Deep Learning · KBTU · Fall 2026", Inches(1.18), Inches(6.58),
             Inches(7.6), Inches(0.30), size=12, color=RGBColor(165, 180, 203))
    set_notes(slide, "Introduce the four-class object-detection task and the brightness research question.")

    # Slide 2
    slide = prs.slides.add_slide(blank)
    add_title(slide, "01", "Dataset and leakage-aware preparation",
              "PASCAL VOC source → audit → grouped split → YOLO labels")
    class_names = ["crosswalk", "speedlimit", "stop", "trafficlight"]
    for i, name in enumerate(class_names):
        x = Inches(0.68 + i * 2.18)
        add_rect(slide, x, Inches(1.30), Inches(1.95), Inches(0.64), [CYAN, BLUE, ORANGE, RED][i])
        add_text(slide, f"{i}  {name}", x + Inches(0.10), Inches(1.49), Inches(1.73), Inches(0.22),
                 size=12, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_rich_lines(slide, [
        ("Source · ", "877 documented street images with XML bounding boxes"),
        ("Audit · ", "missing labels, unknown classes, invalid boxes and image sizes"),
        ("Leakage control · ", "SHA-256 + perceptual hash groups stay in one split"),
        ("Locked test · ", "provider hold-out is used only after model selection"),
    ], Inches(0.68), Inches(2.30), Inches(7.55), Inches(3.6), size=17)
    if counts:
        rows = [["Split", "Images", "Objects"]]
        rows.extend([[r.get("split", ""), r.get("images", ""), r.get("objects", "")] for r in counts])
        add_table(slide, rows, Inches(8.55), Inches(2.30), [1.35, 1.25, 1.25], row_height=0.55)
        add_text(slide, "Observed after execution", Inches(8.60), Inches(4.78), Inches(3.5), Inches(0.28),
                 size=11, color=CYAN, bold=True, align=PP_ALIGN.CENTER)
    else:
        add_rect(slide, Inches(8.55), Inches(2.30), Inches(3.85), Inches(2.60), PALE)
        add_text(slide, "SPLIT COUNTS", Inches(8.88), Inches(2.70), Inches(3.18), Inches(0.30),
                 size=14, color=MUTED, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, "Pending Colab run", Inches(8.88), Inches(3.30), Inches(3.18), Inches(0.45),
                 size=22, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, "dataset_counts.csv will fill this panel", Inches(8.88), Inches(4.02),
                 Inches(3.18), Inches(0.48), size=11, color=MUTED, align=PP_ALIGN.CENTER)
    add_text(slide, "Limitation: original video IDs are unavailable, so video-level grouping cannot be guaranteed.",
             Inches(0.73), Inches(6.53), Inches(11.7), Inches(0.35), size=12, color=RED, bold=True)
    add_footer(slide, 2)
    set_notes(slide, "Explain VOC-to-YOLO conversion, the locked test set, and near-duplicate grouping. State the video-ID limitation.")

    # Slide 3
    slide = prs.slides.add_slide(blank)
    add_title(slide, "02", "One controlled change",
              "Both runs begin from the same pretrained yolo11n.pt checkpoint")
    add_rect(slide, Inches(0.72), Inches(1.35), Inches(5.55), Inches(4.55), PALE)
    add_text(slide, "RUN A · BASELINE", Inches(1.03), Inches(1.72), Inches(4.92), Inches(0.35),
             size=17, color=BLUE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "hsv_v = 0.00", Inches(1.03), Inches(2.38), Inches(4.92), Inches(0.60),
             size=34, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "No brightness jitter", Inches(1.03), Inches(3.10), Inches(4.92), Inches(0.34),
             size=17, color=MUTED, align=PP_ALIGN.CENTER)
    add_rect(slide, Inches(7.05), Inches(1.35), Inches(5.55), Inches(4.55), NAVY)
    add_text(slide, "RUN B · EXPERIMENT", Inches(7.36), Inches(1.72), Inches(4.92), Inches(0.35),
             size=17, color=CYAN, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "hsv_v = 0.35", Inches(7.36), Inches(2.38), Inches(4.92), Inches(0.60),
             size=34, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Moderate brightness jitter", Inches(7.36), Inches(3.10), Inches(4.92), Inches(0.34),
             size=17, color=RGBColor(190, 205, 226), align=PP_ALIGN.CENTER)
    add_rect(slide, Inches(4.72), Inches(4.22), Inches(3.92), Inches(1.22), WHITE, line=CYAN)
    add_text(slide, "FIXED", Inches(5.00), Inches(4.42), Inches(3.35), Inches(0.24),
             size=11, color=CYAN, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "512 px · 14 epochs · batch 16\nSGD · lr 0.01 · seed 42", Inches(4.97), Inches(4.75),
             Inches(3.42), Inches(0.50), size=14, color=INK, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Hypothesis: brightness variation may improve validation mAP@0.50; improvement is not assumed.",
             Inches(1.03), Inches(6.28), Inches(11.26), Inches(0.42), size=14, color=INK,
             bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 3)
    set_notes(slide, "Emphasize that only hsv_v changes. All other settings, including initialization and data split, are identical.")

    # Slide 4
    slide = prs.slides.add_slide(blank)
    add_title(slide, "03", "Validation comparison and model selection",
              "Selection: highest validation mAP@0.50, then validation Precision")
    if validation:
        rows = [["Run", "hsv_v", "Precision", "Recall", "mAP@0.50", "Time"]]
        for row in validation:
            short = "A · baseline" if "baseline" in row.get("run", "") else "B · brightness"
            rows.append([short, row.get("hsv_v", ""), metric(row.get("precision")),
                         metric(row.get("recall")), metric(row.get("mAP50")),
                         minutes(row.get("training_minutes"))])
        add_table(slide, rows, Inches(0.72), Inches(1.45), [2.25, 1.0, 1.55, 1.4, 1.65, 1.35], row_height=0.64)
        chosen = selection.get("selected_run", "Pending")
        add_rect(slide, Inches(0.72), Inches(4.15), Inches(6.18), Inches(1.30), NAVY)
        add_text(slide, "SELECTED ON VALIDATION", Inches(1.02), Inches(4.43), Inches(5.58), Inches(0.25),
                 size=11, color=CYAN, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, chosen, Inches(1.00), Inches(4.79), Inches(5.60), Inches(0.38),
                 size=19, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
        winner = next((r for r in validation if r.get("run") == chosen), {})
        add_metric_card(slide, "WINNER mAP@0.50", metric(winner.get("mAP50")), Inches(7.38), Inches(4.15), CYAN)
        add_metric_card(slide, "WINNER PRECISION", metric(winner.get("precision")), Inches(9.75), Inches(4.15), BLUE)
    else:
        add_rect(slide, Inches(0.72), Inches(1.45), Inches(11.88), Inches(3.75), PALE)
        add_text(slide, "RESULTS PENDING", Inches(1.22), Inches(2.20), Inches(10.88), Inches(0.55),
                 size=31, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, "Run the full Colab notebook. The deck will read validation_table.csv\nand model_selection.json without estimating any metric.",
                 Inches(1.22), Inches(3.06), Inches(10.88), Inches(1.10), size=18, color=INK,
                 align=PP_ALIGN.CENTER)
    add_text(slide, "The locked test set is not used to choose the winner or revise settings.",
             Inches(0.92), Inches(6.32), Inches(11.48), Inches(0.38), size=14, color=RED,
             bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 4)
    set_notes(slide, "Read the two validation rows, identify the winner, and explain that test performance played no role in selection.")

    # Slide 5
    slide = prs.slides.add_slide(blank)
    add_title(slide, "04", "Held-out test, error review and conclusion",
              "Test is evaluated once after model selection")
    test_metrics = test.get("metrics", {})
    add_metric_card(slide, "TEST PRECISION", metric(test_metrics.get("precision")), Inches(0.72), Inches(1.35), CYAN)
    add_metric_card(slide, "TEST RECALL", metric(test_metrics.get("recall")), Inches(3.00), Inches(1.35), BLUE)
    add_metric_card(slide, "TEST mAP@0.50", metric(test_metrics.get("mAP50")), Inches(5.28), Inches(1.35), ORANGE)
    chosen = test.get("selected_run") or selection.get("selected_run") or "Pending after run"
    add_rect(slide, Inches(7.65), Inches(1.35), Inches(4.95), Inches(1.02), NAVY)
    add_text(slide, "FINAL CHECKPOINT", Inches(7.94), Inches(1.55), Inches(4.37), Inches(0.20),
             size=10, color=CYAN, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, str(chosen), Inches(7.93), Inches(1.85), Inches(4.39), Inches(0.30),
             size=14, color=WHITE, bold=True, align=PP_ALIGN.CENTER)

    pictures: list[Path] = []
    if evidence:
        pictures.extend(sorted(evidence.glob("failure_*.png"))[:2])
        if not pictures and (evidence / "test_predictions_8.png").exists():
            pictures.append(evidence / "test_predictions_8.png")
    if pictures:
        for idx, picture in enumerate(pictures[:2]):
            x = Inches(0.72 + idx * 3.35)
            add_rect(slide, x, Inches(2.75), Inches(3.08), Inches(2.65), PALE)
            add_picture_contain(slide, picture, x + Inches(0.06), Inches(2.81), Inches(2.96), Inches(2.40))
            add_text(slide, picture.stem, x + Inches(0.08), Inches(5.18), Inches(2.92), Inches(0.18),
                     size=9, color=MUTED, align=PP_ALIGN.CENTER)
    else:
        add_rect(slide, Inches(0.72), Inches(2.75), Inches(6.43), Inches(2.65), PALE)
        add_text(slide, "REAL FAILURE IMAGES\nPENDING", Inches(1.12), Inches(3.47), Inches(5.63), Inches(0.90),
                 size=25, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)

    cases = failures.get("cases", []) if isinstance(failures, dict) else []
    case_text = "\n".join(
        f"• {c.get('image', 'image')}: {', '.join(c.get('failure_types') or ['challenging correct case'])}"
        for c in cases[:3]
    ) or "• Inspect exported green GT and orange prediction boxes\n• Confirm causes from visible evidence\n• Do not turn possible causes into measured claims"
    add_rect(slide, Inches(7.48), Inches(2.75), Inches(5.12), Inches(2.65), WHITE, line=PALE)
    add_text(slide, "ERROR REVIEW", Inches(7.78), Inches(3.00), Inches(4.52), Inches(0.26),
             size=13, color=BLUE, bold=True)
    add_text(slide, case_text, Inches(7.78), Inches(3.40), Inches(4.46), Inches(1.63),
             size=13, color=INK)
    conclusion = ("Measured conclusion: compare the two validation runs and keep the claim limited to this split."
                  if measured else
                  "Conclusion remains pending until both runs, locked-test evaluation and manual failure review finish.")
    add_text(slide, conclusion, Inches(0.86), Inches(6.10), Inches(11.60), Inches(0.55),
             size=15, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 5)
    set_notes(slide, "Report only measured test values. Describe visible failures, limitations, and the appropriately narrow conclusion.")

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

