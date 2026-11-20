#!/usr/bin/env python3
"""OCR / model figures for the Methodology chapter, generated from a real handwritten jamabandi.

Run with the ai-service virtualenv so OpenCV, Tesseract and TrOCR are available:
    ai-service/.venv/bin/python docs/report_assets/draw_ocr_figures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEVANAGARI_FALLBACK = "Devanagari Sangam MN"
MONO = ["DejaVu Sans Mono", DEVANAGARI_FALLBACK]
plt.rcParams["font.family"] = ["DejaVu Sans", DEVANAGARI_FALLBACK]
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-service" / "src"))

import ocr  # noqa: E402
from extract import extract_fields  # noqa: E402

SAMPLE = ROOT / "samples" / "handwritten" / "manual_tests" / "2.jpg"
FAILURE_SAMPLE = ROOT / "samples" / "handwritten" / "manual_tests" / "3.jpg"
FIG_DIR = Path(__file__).resolve().parent / "figures"

NAVY = "#13294B"
NAVY_EDGE = "#0B1A33"
ARROW = "#3B4A5E"
LAYER_EDGE = "#7C8BA1"
TEXT_DARK = "#1F2A3A"
GREEN = "#1E6B52"
AMBER = "#B7791F"
PURPLE = "#5B3F8C"
RED = "#9B2C2C"
BAND_COLORS = ["#1D4E89", "#1E6B52", "#9A5B13", "#5B3F8C", "#9B2C2C", "#2C7A7B",
               "#6B46C1", "#B83280", "#2F855A", "#C05621", "#2B6CB0", "#744210"]


def save(fig, name):
    out = FIG_DIR / name
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Wrote", out)


def rgb(img_bgr):
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)


# ---------------------------------------------------------------------------
# Run the real pipeline step by step (same parameters as ai-service/src/ocr.py)
# ---------------------------------------------------------------------------
original = cv2.imread(str(SAMPLE))
gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
page_crop = ocr._notebook_page(gray)
h, w = page_crop.shape[:2]
upscaled = page_crop
if max(h, w) < 1400:
    scale = 1400 / max(h, w)
    upscaled = cv2.resize(page_crop, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8)).apply(upscaled)
adaptive = cv2.adaptiveThreshold(clahe, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 41, 14)
closed = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (28, 3)))

page, thr = ocr._prepare_page(gray)
bands = ocr._merged_bands(thr)[:12]

rows = []
for i, (y1, y2) in enumerate(bands, 1):
    crop = ocr._line_crop(page, thr, y1, y2)
    tess = ocr._tess_line(crop)
    trocr = ocr._trocr_line(crop)
    chosen, score = ocr._pick_line_text(tess, trocr)
    rows.append(dict(i=i, y1=int(y1), y2=int(y2), crop=crop, tess=tess, trocr=trocr,
                     chosen=chosen, score=round(float(score), 2)))
    print(f"band {i}: tess={tess!r} trocr={trocr!r} -> {chosen!r} ({score:.2f})")

all_lines = ocr.run_ocr(original)
fields = extract_fields(all_lines)
report = {
    "sample": str(SAMPLE.relative_to(ROOT)),
    "bands": [{k: v for k, v in r.items() if k != "crop"} for r in rows],
    "fields": {k: v for k, v in fields.items() if k != "ocrLines"},
}
(FIG_DIR / "ocr_run_sample2.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str))


# ---------------------------------------------------------------------------
# Figure: preprocessing stages
# ---------------------------------------------------------------------------
def fig_preprocessing():
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.6))
    panels = [
        (rgb(original), "(a) Original phone photograph", None),
        (clahe, "(b) Paper crop + upscale + CLAHE contrast", "gray"),
        (adaptive, "(c) Adaptive Gaussian threshold (inverted)", "gray"),
        (closed, "(d) Morphological closing (28 x 3 kernel)", "gray"),
    ]
    for ax, (img, title, cmap) in zip(axes.flat, panels):
        ax.imshow(img, cmap=cmap)
        ax.set_title(title, fontsize=12, color=TEXT_DARK, fontweight="bold", pad=8)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_edgecolor(LAYER_EDGE)
    fig.tight_layout()
    save(fig, "ch4_fig_4_04_preprocessing_stages.png")


# ---------------------------------------------------------------------------
# Figure: horizontal projection profile + detected line bands
# ---------------------------------------------------------------------------
def draw_profile_figure(page_img, thr_img, band_list, titles, name):
    profile = thr_img.sum(axis=1).astype(float)
    smooth = np.convolve(profile, np.ones(17) / 17.0, mode="same")
    cut = max(smooth.max() * 0.12, 1.0)
    ys = np.arange(len(smooth))
    ph, pw = page_img.shape[:2]

    img_h = 6.4
    img_w = img_h * pw / ph
    fig, (ax_img, ax_prof) = plt.subplots(
        1, 2, figsize=(img_w + 4.6, img_h + 1.0),
        gridspec_kw=dict(width_ratios=[img_w, 3.6], wspace=0.04),
    )
    ax_img.imshow(page_img, cmap="gray", extent=(0, pw, ph, 0))
    for k, (y1, y2) in enumerate(band_list, 1):
        c = BAND_COLORS[(k - 1) % len(BAND_COLORS)]
        ax_img.add_patch(Rectangle((4, y1), pw - 8, y2 - y1, fill=False, edgecolor=c, linewidth=2.4))
        ax_img.text(14, y1 + 4, f"Band {k}", color="white", fontsize=10, fontweight="bold",
                    va="top", bbox=dict(boxstyle="round,pad=0.25", facecolor=c, edgecolor="none"))
    ax_img.set_title(titles[0], fontsize=12, fontweight="bold", color=TEXT_DARK)
    ax_img.set_xticks([])
    ax_img.set_yticks([])

    ax_prof.plot(smooth / smooth.max(), ys, color=NAVY, lw=1.6)
    ax_prof.axvline(cut / smooth.max(), color=RED, lw=1.4, linestyle="--")
    ax_prof.text(cut / smooth.max() + 0.02, 0.04 * ph, "12% cut-off", color=RED,
                 fontsize=9.5, fontweight="bold")
    for k, (y1, y2) in enumerate(band_list, 1):
        ax_prof.axhspan(y1, y2, color=BAND_COLORS[(k - 1) % len(BAND_COLORS)], alpha=0.2)
    ax_prof.set_ylim(ph, 0)
    ax_prof.set_xlim(0, 1.05)
    ax_prof.set_yticks([])
    ax_prof.set_xlabel("Normalised ink density per row", fontsize=10)
    ax_prof.set_title(titles[1], fontsize=12, fontweight="bold", color=TEXT_DARK)
    save(fig, name)


def fig_segmentation():
    draw_profile_figure(
        page, thr, [(r["y1"], r["y2"]) for r in rows],
        ("(a) Line bands detected on the page", "(b) Horizontal projection profile"),
        "ch4_fig_4_05_line_segmentation.png",
    )


def fig_segmentation_failure():
    img = cv2.imread(str(FAILURE_SAMPLE))
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    p, t = ocr._prepare_page(g)
    draw_profile_figure(
        t, t, ocr._merged_bands(t),
        ("(a) Binary page: texture and bleed-through become 'ink'",
         "(b) Profile never drops below cut-off"),
        "ch4_fig_4_06_segmentation_failure.png",
    )


# ---------------------------------------------------------------------------
# Figure: per-line Tesseract vs TrOCR vs selected text
# ---------------------------------------------------------------------------
def fig_ocr_comparison():
    n = len(rows)
    fig = plt.figure(figsize=(14, 1.25 * n + 1.3))
    col_x = [0.0, 0.34, 0.56, 0.78]
    headers = ["Line crop (input to OCR)", "Tesseract (LSTM)", "TrOCR (Transformer)", "Selected text"]
    head_colors = [NAVY, PURPLE, GREEN, RED]
    top = 1.0 - 0.9 / (1.25 * n + 1.3)
    row_h = (top - 0.02) / n
    for x, label, c in zip(col_x, headers, head_colors):
        fig.text(x + 0.005, top + 0.012, label, fontsize=12, fontweight="bold", color=c)
    for k, r in enumerate(rows):
        y0 = top - (k + 1) * row_h
        ax = fig.add_axes([col_x[0], y0 + row_h * 0.1, 0.32, row_h * 0.8])
        ax.imshow(r["crop"], cmap="gray", aspect="auto")
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_edgecolor(BAND_COLORS[(r["i"] - 1) % len(BAND_COLORS)])
            s.set_linewidth(2)
        texts = [r["tess"] or "(empty)", r["trocr"] or "(empty)",
                 f"{r['chosen'] or '(none)'}\nscore {r['score']:.2f}"]
        for x, t, bold in zip(col_x[1:], texts, (False, False, True)):
            fig.text(x + 0.005, y0 + row_h * 0.5, t[:34], fontsize=10.5, va="center",
                     color=TEXT_DARK, fontweight="bold" if bold else "normal",
                     family=MONO)
        fig.add_artist(plt.Line2D([0, 1], [y0, y0], color="#D5DCE6", lw=0.8))
    save(fig, "ch4_fig_4_08_ocr_comparison.png")


# ---------------------------------------------------------------------------
# Figure: TrOCR architecture applied to one real line crop
# ---------------------------------------------------------------------------
def box(ax, x, y, w, h, text, fill=NAVY, fs=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.18",
                                facecolor=fill, edgecolor=NAVY_EDGE, lw=1.0, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color="white", fontsize=fs,
            zorder=4)


def arrow(ax, p, q, label=None):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=ARROW, lw=1.4,
                                                    mutation_scale=14, shrinkA=0, shrinkB=0))
    if label:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 0.22, label, ha="center", fontsize=8.5,
                color=TEXT_DARK, fontweight="bold")


def pick_demo_row():
    for r in rows:
        if "khasra" in (r["chosen"] or "").lower() or "88" in (r["chosen"] or ""):
            return r
    return rows[0]


def fig_trocr():
    r = pick_demo_row()
    crop = r["crop"]
    resized = cv2.resize(crop, (384, 384), interpolation=cv2.INTER_AREA)

    fig = plt.figure(figsize=(15, 6.6))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 9)
    ax.axis("off")

    a1 = fig.add_axes([0.01, 0.42, 0.17, 0.2])
    a1.imshow(crop, cmap="gray", aspect="auto")
    a1.set_title("1. Line crop from band", fontsize=10.5, fontweight="bold", color=TEXT_DARK)
    a1.set_xticks([]); a1.set_yticks([])

    a2 = fig.add_axes([0.215, 0.3, 0.17, 0.42])
    a2.imshow(resized, cmap="gray")
    for g in range(0, 385, 16):
        a2.axhline(g, color="#E53E3E", lw=0.35, alpha=0.7)
        a2.axvline(g, color="#E53E3E", lw=0.35, alpha=0.7)
    a2.set_title("2. Resize 384x384,\nsplit into 24x24 = 576 patches", fontsize=10.5,
                 fontweight="bold", color=TEXT_DARK)
    a2.set_xticks([]); a2.set_yticks([])

    arrow(ax, (3.65, 4.8), (4.25, 4.8))
    arrow(ax, (7.75, 4.8), (8.35, 4.8), "patch\nembeddings")

    ax.add_patch(FancyBboxPatch((8.4, 2.0), 4.2, 5.6, boxstyle="round,pad=0,rounding_size=0.3",
                                facecolor="#F3F8F6", edgecolor=LAYER_EDGE, linestyle=(0, (5, 3)),
                                lw=1.3))
    ax.text(10.5, 7.25, "3. ViT Image Encoder", ha="center", fontsize=11.5, fontweight="bold",
            color=GREEN)
    box(ax, 8.8, 5.6, 3.4, 0.9, "Patch + position\nembedding (768-d)", fill=GREEN, fs=9.5)
    box(ax, 8.8, 4.2, 3.4, 0.9, "Multi-head\nself-attention (12 heads)", fill=GREEN, fs=9.5)
    box(ax, 8.8, 2.8, 3.4, 0.9, "Feed-forward\nx 12 layers", fill=GREEN, fs=9.5)
    arrow(ax, (10.5, 5.6), (10.5, 5.1))
    arrow(ax, (10.5, 4.2), (10.5, 3.7))

    arrow(ax, (12.6, 4.8), (13.3, 4.8), "visual\nfeatures")

    ax.add_patch(FancyBboxPatch((13.35, 2.0), 4.3, 5.6, boxstyle="round,pad=0,rounding_size=0.3",
                                facecolor="#F7F5FB", edgecolor=LAYER_EDGE, linestyle=(0, (5, 3)),
                                lw=1.3))
    ax.text(15.5, 7.25, "4. Transformer Text Decoder", ha="center", fontsize=11.5,
            fontweight="bold", color=PURPLE)
    box(ax, 13.75, 5.6, 3.5, 0.9, "Masked self-attention\non previous tokens", fill=PURPLE, fs=9.5)
    box(ax, 13.75, 4.2, 3.5, 0.9, "Cross-attention to\nimage features (16 heads)", fill=PURPLE, fs=9.5)
    box(ax, 13.75, 2.8, 3.5, 0.9, "Softmax over 50,265\nBPE tokens x 12 layers", fill=PURPLE, fs=9.5)
    arrow(ax, (15.5, 5.6), (15.5, 5.1))
    arrow(ax, (15.5, 4.2), (15.5, 3.7))

    arrow(ax, (17.65, 4.8), (18.2, 4.8))
    out = r["trocr"] or "(no text)"
    ax.text(19.1, 5.6, "5. Output text", ha="center", fontsize=10.5, fontweight="bold",
            color=TEXT_DARK)
    ax.text(19.1, 4.8, out[:22], ha="center", va="center", fontsize=11, fontweight="bold",
            color="white", family=MONO,
            bbox=dict(boxstyle="round,pad=0.4", facecolor=RED, edgecolor="none"))
    ax.text(10.0, 0.9, "Tokens are generated one at a time (autoregressive, max 64 tokens); "
            "each new token attends to the image features and the tokens already produced.",
            ha="center", fontsize=10, style="italic", color="#334155")
    save(fig, "ch4_fig_4_07_trocr_architecture.png")


# ---------------------------------------------------------------------------
# Figure: YOLO field-block detection design + target annotation on our page
# ---------------------------------------------------------------------------
def guess_class(text: str) -> str:
    t = (text or "").lower()
    for key, cls in (("ulpin", "ulpin"), ("khasra", "khasra"), ("khata", "khata"),
                     ("khewat", "khewat"), ("owner", "owner"), ("village", "village")):
        if key in t:
            return cls
    return "other_text"


def fig_yolo():
    fig = plt.figure(figsize=(15, 7.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 10)
    ax.axis("off")

    a_img = fig.add_axes([0.01, 0.12, 0.33, 0.72])
    a_img.imshow(page, cmap="gray")
    class_colors = {"ulpin": "#1D4E89", "khasra": "#1E6B52", "khata": "#9A5B13",
                    "khewat": "#5B3F8C", "owner": "#9B2C2C", "village": "#2C7A7B",
                    "other_text": "#4A5568"}
    for r in rows:
        cls = guess_class(r["chosen"])
        c = class_colors[cls]
        a_img.add_patch(Rectangle((4, r["y1"]), page.shape[1] - 8, r["y2"] - r["y1"],
                                  fill=False, edgecolor=c, linewidth=2.4))
        a_img.text(12, r["y1"] + 3, cls, color="white", fontsize=9.5, fontweight="bold",
                   va="top", bbox=dict(boxstyle="round,pad=0.2", facecolor=c, edgecolor="none"))
    a_img.set_title("Target labelling of a jamabandi page\n(classes YOLO is trained to detect)",
                    fontsize=11, fontweight="bold", color=TEXT_DARK)
    a_img.set_xticks([]); a_img.set_yticks([])

    steps = [
        ("Input page\nresized 640x640", NAVY),
        ("Backbone (CSP-Darknet)\nextracts visual features", GREEN),
        ("Neck (FPN / PAN)\nfuses multi-scale features", GREEN),
        ("Detection head\nbox + class + confidence", PURPLE),
        ("Filter: conf >= 0.25\n+ non-max suppression", AMBER),
        ("Crop each block\nTrOCR, else Tesseract", RED),
        ("Prefix label\ne.g. \"Khasra 88/1\"", NAVY),
    ]
    x0, w_box, h_box = 7.4, 5.2, 0.95
    y = 8.6
    centers = []
    for text, fill in steps:
        box(ax, x0, y - h_box / 2, w_box, h_box, text, fill=fill, fs=9.8)
        centers.append(y)
        y -= 1.22
    for a, b in zip(centers, centers[1:]):
        arrow(ax, (x0 + w_box / 2, a - h_box / 2), (x0 + w_box / 2, b + h_box / 2))

    ax.add_patch(FancyBboxPatch((13.3, 2.6), 6.4, 5.6, boxstyle="round,pad=0,rounding_size=0.3",
                                facecolor="#F4F7FB", edgecolor=LAYER_EDGE, linestyle=(0, (5, 3)),
                                lw=1.3))
    ax.text(16.5, 7.8, "Seven field classes", ha="center", fontsize=11.5, fontweight="bold",
            color="#1D4E89")
    yy = 7.1
    for cls, c in class_colors.items():
        ax.add_patch(Rectangle((13.8, yy - 0.22), 0.5, 0.44, facecolor=c, edgecolor="none"))
        ax.text(14.5, yy, cls, va="center", fontsize=10.5, color=TEXT_DARK,
                family=MONO)
        yy -= 0.62
    ax.text(16.5, 1.9, "Weights: models/jamabandi_blocks.pt (optional).\n"
            "If absent, the projection-profile line bands are used instead.",
            ha="center", fontsize=9.5, style="italic", color="#334155")
    save(fig, "ch4_fig_4_09_yolo_design.png")


# ---------------------------------------------------------------------------
# Figure: OCR lines -> parsed JSON (real output)
# ---------------------------------------------------------------------------
def fig_json():
    keys = ["ulpin", "khasraNumber", "khewatNumber", "khataNumber", "areaAcres", "state",
            "parcelIdType", "matchTier", "latitude", "longitude"]
    shown = {k: fields.get(k) for k in keys if k in fields}
    lines_txt = "\n".join(f"{k:>2}. {l.text[:40]}" for k, l in enumerate(all_lines, 1))
    json_txt = json.dumps(shown, indent=2, ensure_ascii=False, default=str)

    fig = plt.figure(figsize=(15, 5.6))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 7.5)
    ax.axis("off")
    for x0, title, body, tint in ((0.3, "Raw OCR lines (line OCR + full-page safety net)", lines_txt, "#F7F5FB"),
                                  (11.4, "Parsed JSON returned by /extract", json_txt, "#F3F8F6")):
        ax.add_patch(FancyBboxPatch((x0, 0.3), 8.3, 6.9, boxstyle="round,pad=0,rounding_size=0.3",
                                    facecolor=tint, edgecolor=LAYER_EDGE, linestyle=(0, (5, 3)),
                                    lw=1.3))
        ax.text(x0 + 4.15, 6.8, title, ha="center", fontsize=12, fontweight="bold", color=TEXT_DARK)
        ax.text(x0 + 0.35, 6.3, body, ha="left", va="top", fontsize=10, color=TEXT_DARK,
                family=MONO, linespacing=1.35)
    arrow(ax, (8.8, 3.8), (11.2, 3.8))
    ax.text(10.0, 4.2, "parsers + OCR\nrepairs", ha="center", fontsize=9.5, fontweight="bold",
            color=TEXT_DARK)
    save(fig, "ch4_fig_4_10_ocr_to_json.png")


if __name__ == "__main__":
    fig_preprocessing()
    fig_segmentation()
    fig_segmentation_failure()
    fig_ocr_comparison()
    fig_trocr()
    fig_yolo()
    fig_json()
    print(json.dumps(report["fields"], indent=2, default=str))
