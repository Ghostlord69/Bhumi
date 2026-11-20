#!/usr/bin/env python3
"""Methodology-chapter figures for the Bhumi report (same visual style as Figure 3.1)."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Ellipse

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
DECISION_FILL = "#E8EEF7"

TINTS = {
    "blue": ("#F4F7FB", "#1D4E89"),
    "green": ("#F3F8F6", "#1E6B52"),
    "purple": ("#F7F5FB", "#5B3F8C"),
    "amber": ("#FBF6F0", "#9A5B13"),
    "red": ("#FBF3F3", "#9B2C2C"),
    "grey": ("#F5F5F5", "#3B4A5E"),
}


def new_canvas(w_in, h_in, xmax, ymin, ymax):
    fig, ax = plt.subplots(figsize=(w_in, h_in))
    ax.set_xlim(0, xmax)
    ax.set_ylim(ymin, ymax)
    ax.axis("off")
    return fig, ax


def layer(ax, x0, y0, x1, y1, title, tint):
    fill, title_color = TINTS[tint]
    ax.add_patch(FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.3",
        linewidth=1.3, edgecolor=LAYER_EDGE, facecolor=fill, linestyle=(0, (5, 3)), zorder=1,
    ))
    ax.text((x0 + x1) / 2, y1 - 0.36, title, ha="center", va="center", fontsize=11.5,
            color=title_color, fontweight="bold", zorder=5,
            bbox=dict(boxstyle="square,pad=0.15", facecolor=fill, edgecolor="none"))


def box(ax, cx, cy, w, h, text, fill=NAVY, fs=10, color="white", bold=False):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.22",
        linewidth=1.0, edgecolor=NAVY_EDGE, facecolor=fill, zorder=4,
    ))
    ax.text(cx, cy, text, ha="center", va="center", color=color, fontsize=fs,
            fontweight="bold" if bold else "normal", zorder=6)
    return dict(cx=cx, cy=cy, w=w, h=h)


def oval(ax, cx, cy, w, h, text):
    ax.add_patch(Ellipse((cx, cy), w, h, facecolor="#0B1A33", edgecolor=NAVY_EDGE, zorder=4))
    ax.text(cx, cy, text, ha="center", va="center", color="white", fontsize=10,
            fontweight="bold", zorder=6)
    return dict(cx=cx, cy=cy, w=w, h=h)


def diamond(ax, cx, cy, w, h, text, fs=9.5):
    pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=DECISION_FILL, edgecolor=NAVY,
                         linewidth=1.3, zorder=4))
    ax.text(cx, cy, text, ha="center", va="center", color=TEXT_DARK, fontsize=fs, zorder=6)
    return dict(cx=cx, cy=cy, w=w, h=h)


def T(n, dx=0.0):
    return (n["cx"] + dx, n["cy"] + n["h"] / 2)


def B(n, dx=0.0):
    return (n["cx"] + dx, n["cy"] - n["h"] / 2)


def L(n, dy=0.0):
    return (n["cx"] - n["w"] / 2, n["cy"] + dy)


def R(n, dy=0.0):
    return (n["cx"] + n["w"] / 2, n["cy"] + dy)


def path(ax, pts, label=None, label_at=0, label_dx=0.12, label_dy=0.0, ha="left"):
    """Polyline with an arrowhead on the final segment."""
    for (x1, y1), (x2, y2) in zip(pts[:-2], pts[1:-1]):
        ax.plot([x1, x2], [y1, y2], color=ARROW, lw=1.25, zorder=3, solid_capstyle="butt")
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=ARROW, lw=1.25, mutation_scale=13,
                                shrinkA=0, shrinkB=0), zorder=3)
    if label:
        (x1, y1), (x2, y2) = pts[label_at], pts[label_at + 1]
        ax.text((x1 + x2) / 2 + label_dx, (y1 + y2) / 2 + label_dy, label, fontsize=8.6,
                color=TEXT_DARK, ha=ha, va="center", fontweight="bold", zorder=7,
                bbox=dict(boxstyle="square,pad=0.08", facecolor="white", edgecolor="none"))


def save(fig, name):
    out = FIG_DIR / name
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Wrote", out)


# ---------------------------------------------------------------------------
# Figure 4.1 - Proposed method overview (automated stages + human-in-the-loop)
# ---------------------------------------------------------------------------
def fig_overview():
    fig, ax = new_canvas(15, 6.4, 20, -0.4, 8.4)

    cols = [
        (0.2, "1. Intake", "blue", ["Seller Login", "Listing Form", "Upload Jamabandi"]),
        (4.2, "2. Extraction", "green", ["Preprocess Image", "OCR Text Lines", "Parse Fields"]),
        (8.2, "3. Matching", "purple", ["Gov Record Lookup", "Rule-based Check", "Queue Routing"]),
        (12.2, "4. Verification", "red", ["City Officer Review", "Field Report", "Approve / Reject"]),
        (16.2, "5. Transfer", "amber", ["Purchase Request", "Seller Confirms", "Certificate PDF"]),
    ]
    tops, bots = [], []
    for x0, title, tint, items in cols:
        layer(ax, x0, 0.6, x0 + 3.6, 6.4, title, tint)
        nodes = []
        for i, label in enumerate(items):
            nodes.append(box(ax, x0 + 1.8, 5.0 - i * 1.55, 3.0, 0.82, label))
        for a, b in zip(nodes, nodes[1:]):
            path(ax, [B(a), T(b)])
        tops.append(nodes[0])
        bots.append(nodes[-1])

    for a, b in zip(bots, tops[1:]):
        x_mid = R(a)[0] + 0.2
        path(ax, [R(a), (x_mid, R(a)[1]), (x_mid, L(b)[1]), L(b)])

    ax.annotate("", xy=(11.85, 7.3), xytext=(4.25, 7.3),
                arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.6))
    ax.text(8.05, 7.65, "AUTOMATED  (FastAPI agent + MatchingService)", ha="center",
            fontsize=10, color=GREEN, fontweight="bold")
    ax.annotate("", xy=(19.85, 7.3), xytext=(12.25, 7.3),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=1.6))
    ax.text(16.05, 7.65, "HUMAN-IN-THE-LOOP  (City Authenticator)", ha="center",
            fontsize=10, color=RED, fontweight="bold")
    ax.text(10.0, 0.05, "AI proposes a match; the officer decides publication and ownership change",
            ha="center", fontsize=9.5, style="italic", color="#334155")
    save(fig, "ch4_fig_4_01_method_overview.png")


# ---------------------------------------------------------------------------
# Figure 4.2 - Document extraction algorithm (FastAPI /extract)
# ---------------------------------------------------------------------------
def fig_extraction():
    fig, ax = new_canvas(9.0, 19.0, 12, 1.6, 22.2)
    W = 5.0
    start = oval(ax, 5.0, 21.4, 2.6, 0.85, "Start: /extract")
    load = box(ax, 5.0, 20.1, W, 0.82, "Load image bytes (PNG / JPG / PDF)")
    d_meta = diamond(ax, 5.0, 18.5, 4.4, 1.5, "bhumi_meta\nchunk present?")
    meta = box(ax, 10.3, 18.5, 2.9, 0.95, "Parse embedded\nmetadata JSON", fill=GREEN)
    prep = box(ax, 5.0, 16.8, W, 0.82, "Preprocess: grayscale + binary")
    d_yolo = diamond(ax, 5.0, 15.1, 4.4, 1.5, "YOLO weights\navailable?")
    yolo = box(ax, 2.2, 13.4, 3.6, 0.95, "Detect field blocks\n(YOLO)")
    bands = box(ax, 7.8, 13.4, 3.6, 0.95, "Split into horizontal\nline bands")
    ocr = box(ax, 5.0, 11.8, W, 0.82, "OCR each crop (Tesseract / TrOCR)")
    bleed = box(ax, 5.0, 10.6, W, 0.82, "Filter reverse-side bleed lines")
    parse = box(ax, 5.0, 9.3, W + 0.6, 0.95,
                "Parse ULPIN, khasra (multi-segment),\nkhata, khewat, owner, village")
    d_ulpin = diamond(ax, 5.0, 7.6, 4.4, 1.5, "ULPIN valid\n(14 chars)?")
    decode = box(ax, 5.0, 5.9, W, 0.95, "Decode Base-14/19/32 to lat/lng\n+ build Locate URL")
    build = box(ax, 5.0, 4.4, W + 0.6, 0.95,
                "Build JSON: fields, matchTier,\nparcelIdType, confidence, ocrLines")
    end = oval(ax, 5.0, 2.9, 2.6, 0.85, "Return JSON")

    path(ax, [B(start), T(load)])
    path(ax, [B(load), T(d_meta)])
    path(ax, [R(d_meta), L(meta)], label="Yes", label_dx=-0.15, label_dy=0.22)
    path(ax, [B(meta), (10.3, 4.4), R(build)])
    path(ax, [B(d_meta), T(prep)], label="No")
    path(ax, [B(prep), T(d_yolo)])
    path(ax, [L(d_yolo), (2.2, 15.1), T(yolo)], label="Yes", label_dy=0.22)
    path(ax, [R(d_yolo), (7.8, 15.1), T(bands)], label="No", label_dx=-0.15, label_dy=0.22)
    path(ax, [B(yolo), (2.2, 12.6), (4.0, 12.6), T(ocr, -1.0)])
    path(ax, [B(bands), (7.8, 12.6), (6.0, 12.6), T(ocr, 1.0)])
    path(ax, [B(ocr), T(bleed)])
    path(ax, [B(bleed), T(parse)])
    path(ax, [B(parse), T(d_ulpin)])
    path(ax, [B(d_ulpin), T(decode)], label="Yes")
    path(ax, [L(d_ulpin), (1.2, 7.6), (1.2, 4.4), L(build)], label="No", label_dy=0.22)
    path(ax, [B(decode), T(build)])
    path(ax, [B(build), T(end)])
    save(fig, "ch4_fig_4_03_extraction_flowchart.png")


# ---------------------------------------------------------------------------
# Figure 4.3 - Government matching algorithm (MatchingService)
# ---------------------------------------------------------------------------
def fig_matching():
    fig, ax = new_canvas(9.5, 17.5, 12.4, 3.6, 22.2)
    W = 5.4
    start = oval(ax, 6.0, 21.4, 3.0, 0.85, "Listing submitted")
    d_reg = diamond(ax, 6.0, 19.8, 4.6, 1.5, "Purpose =\nREGISTRY?")
    reg = box(ax, 10.6, 19.8, 3.2, 0.95, "PENDING_REGISTRY", fill=PURPLE, bold=True, fs=9.5)
    extract = box(ax, 6.0, 18.1, W, 0.82, "AiClient.extract(first registry paper)")
    merge = box(ax, 6.0, 16.9, W, 0.95, "Merge fields into listing\n(form ULPIN kept if AI misses it)")
    lookup = box(ax, 6.0, 15.6, W, 0.95, "Lookup government record\n(ULPIN, then khasra, then survey)")
    d_found = diamond(ax, 6.0, 13.9, 4.6, 1.5, "Government\nrecord found?")
    d_ulpin = diamond(ax, 6.0, 11.9, 5.0, 1.6, "ULPIN equal and\nconfidence >= 0.75?")
    d_align = diamond(ax, 6.0, 9.7, 5.6, 1.9,
                      "City, owner, khata/khewat\nand parcel all agree,\nconfidence >= 0.75?", fs=9)
    ai = box(ax, 2.8, 7.3, 4.6, 0.95, "AI_VERIFIED_AWAITING_\nAUTHENTICATOR", fill=GREEN,
             bold=True, fs=9.5)
    phys = box(ax, 9.6, 7.3, 4.6, 0.95, "NEEDS_PHYSICAL_\nVERIFICATION", fill=AMBER,
               bold=True, fs=9.5)
    notify = box(ax, 6.0, 5.5, W, 0.82, "Notify authenticators of the listing's city")
    end = oval(ax, 6.0, 4.3, 3.2, 0.85, "Case in city queue")

    path(ax, [B(start), T(d_reg)])
    path(ax, [R(d_reg), L(reg)], label="Yes", label_dx=-0.12, label_dy=0.22)
    path(ax, [B(d_reg), T(extract)], label="No")
    path(ax, [B(extract), T(merge)])
    path(ax, [B(merge), T(lookup)])
    path(ax, [B(lookup), T(d_found)])
    path(ax, [R(d_found), (11.3, 13.9), T(phys, 1.7)], label="No", label_dy=0.22)
    path(ax, [B(d_found), T(d_ulpin)], label="Yes")
    path(ax, [L(d_ulpin), (1.2, 11.9), T(ai, -1.6)], label="Yes", label_dy=0.22)
    path(ax, [B(d_ulpin), T(d_align)], label="No")
    path(ax, [L(d_align), (2.8, 9.7), T(ai, 0.0)], label="Yes", label_dy=0.22)
    path(ax, [R(d_align), (9.6, 9.7), T(phys, 0.0)], label="No", label_dx=-0.1, label_dy=0.22)
    path(ax, [R(reg, -0.0), (12.3, 19.8), (12.3, 5.5), R(notify)])
    path(ax, [B(ai), (2.8, 5.5), L(notify)])
    path(ax, [B(phys), (9.6, 6.3), (7.5, 6.3), T(notify, 1.5)])
    path(ax, [B(notify), T(end)])
    save(fig, "ch4_fig_4_12_matching_flowchart.png")


# ---------------------------------------------------------------------------
# Figure 4.4 - Property status lifecycle (state machine)
# ---------------------------------------------------------------------------
def fig_lifecycle():
    fig, ax = new_canvas(15, 8.2, 20, -0.6, 10.2)
    layer(ax, 0.2, 4.6, 19.8, 10.0, "Verification Phase", "red")
    layer(ax, 0.2, -0.4, 19.8, 4.0, "Sale & Transfer Phase", "amber")

    pend = box(ax, 2.0, 7.1, 2.9, 0.95, "PENDING_AI", bold=True)
    ai = box(ax, 8.8, 8.5, 4.6, 0.85, "AI_VERIFIED_AWAITING_AUTH.", fill=GREEN, bold=True, fs=9.5)
    phys = box(ax, 8.8, 7.1, 4.6, 0.85, "NEEDS_PHYSICAL_VERIFICATION", fill=AMBER, bold=True, fs=9.5)
    reg = box(ax, 8.8, 5.7, 4.6, 0.85, "PENDING_REGISTRY", fill=PURPLE, bold=True, fs=9.5)
    live = box(ax, 16.3, 8.0, 2.8, 0.95, "LIVE", fill=GREEN, bold=True)
    rej = box(ax, 16.3, 6.0, 2.8, 0.95, "REJECTED", fill=RED, bold=True)

    buy = box(ax, 3.0, 1.6, 4.0, 0.95, "PURCHASE_REQUESTED", bold=True, fs=9.5)
    pt = box(ax, 10.0, 1.6, 4.0, 0.95, "PENDING_TRANSFER", bold=True, fs=9.5)
    sold = box(ax, 17.0, 1.6, 3.0, 0.95, "SOLD", fill=NAVY_EDGE, bold=True)

    path(ax, [R(pend, 0.3), (4.0, 7.4), (4.0, 8.5), L(ai)], label="strong match", label_at=2,
         label_dx=0.0, label_dy=0.24, ha="center")
    path(ax, [R(pend), L(phys)], label="weak / none", label_dx=0.75, label_dy=-0.26, ha="center")
    path(ax, [R(pend, -0.3), (4.0, 6.8), (4.0, 5.7), L(reg)], label="registry", label_at=2,
         label_dx=0.0, label_dy=-0.26, ha="center")

    path(ax, [R(ai), (12.4, 8.5), (12.4, 8.2), L(live, 0.2)], label="officer approves",
         label_at=0, label_dx=0.6, label_dy=0.24, ha="center")
    path(ax, [R(phys, 0.15), (13.0, 7.25), (13.0, 7.9), L(live, -0.1)],
         label="report + approve", label_at=0, label_dx=0.4, label_dy=0.24, ha="center")
    path(ax, [R(reg, 0.15), (13.6, 5.85), (13.6, 7.7), L(live, -0.3)],
         label="registered", label_at=0, label_dx=0.0, label_dy=0.24, ha="center")
    path(ax, [R(reg, -0.15), (14.2, 5.55), (14.2, 6.0), L(rej)], label="officer rejects",
         label_at=0, label_dx=0.0, label_dy=-0.26, ha="center")

    path(ax, [R(live), (19.2, 8.0), (19.2, 4.3), (3.0, 4.3), T(buy)],
         label="buyer requests purchase", label_at=2, label_dy=0.25, ha="center")
    path(ax, [R(buy), L(pt)], label="seller confirms", label_dx=-0.75, label_dy=0.28)
    path(ax, [R(pt), L(sold)], label="officer finalizes", label_dx=-0.8, label_dy=0.28)
    ax.text(17.0, 0.5, "owner updated + certificate PDF", ha="center", fontsize=8.6,
            color=TEXT_DARK, style="italic")
    save(fig, "ch4_fig_4_13_status_lifecycle.png")


# ---------------------------------------------------------------------------
# Figure 4.5 - Module interaction sequence (post -> match -> approve)
# ---------------------------------------------------------------------------
def fig_sequence():
    actors = [
        ("Seller\n(React UI)", "blue"),
        ("PropertyService", "blue"),
        ("MatchingService", "purple"),
        ("AI Agent\n/extract", "green"),
        ("AppStore", "grey"),
        ("Authenticator\nDesk", "red"),
    ]
    n = len(actors)
    gap = 3.0
    top_y, bottom_y = 15.0, 0.6
    fig, ax = new_canvas(14, 12.5, gap * n, 0.0, 16.2)
    xs = [gap / 2 + i * gap for i in range(n)]
    for x, (name, tint) in zip(xs, actors):
        color = TINTS[tint][1]
        box(ax, x, top_y, 2.5, 1.0, name, fill=color, fs=9.5, bold=True)
        ax.plot([x, x], [top_y - 0.5, bottom_y], color=LAYER_EDGE, lw=1.1,
                linestyle=(0, (5, 3)), zorder=1)

    msgs = [
        (0, 1, "1. POST /api/properties (form + papers)"),
        (1, 2, "2. run(listing)  [status PENDING_AI]"),
        (2, 3, "3. multipart registry paper"),
        (3, 2, "4. JSON fields + matchTier", True),
        (2, 4, "5. lookup ULPIN / khasra / survey"),
        (4, 2, "6. GovernmentRecord or empty", True),
        (2, 1, "7. queue status + summary", True),
        (1, 4, "8. save listing"),
        (1, 5, "9. notify city queue"),
        (5, 1, "10. approve (+ report if physical)", True),
        (1, 4, "11. LIVE + virtual jamabandi + gov upsert"),
        (1, 0, "12. 'Your property is now live'", True),
    ]
    y = 13.6
    step = 1.05
    for msg in msgs:
        a, b, label = msg[0], msg[1], msg[2]
        reply = len(msg) > 3
        x1, x2 = xs[a], xs[b]
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="-|>", color=ARROW, lw=1.2, mutation_scale=12,
                                    linestyle="--" if reply else "-", shrinkA=0, shrinkB=0))
        ax.text((x1 + x2) / 2, y + 0.2, label, ha="center", va="bottom", fontsize=8.8,
                color=TEXT_DARK, bbox=dict(boxstyle="square,pad=0.05", facecolor="white",
                                           edgecolor="none"))
        y -= step
    ax.text(gap * n / 2, 0.15, "Solid arrow = request, dashed arrow = response",
            ha="center", fontsize=9, style="italic", color="#334155")
    save(fig, "ch4_fig_4_02_module_sequence.png")


if __name__ == "__main__":
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig_overview()
    fig_extraction()
    fig_matching()
    fig_lifecycle()
    fig_sequence()
