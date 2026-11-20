#!/usr/bin/env python3
"""Layered system-architecture figure for the Bhumi report (traffic-report visual style)."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent / "figures" / "fig_3_1_system_architecture.png"

NODE_FILL = "#13294B"
NODE_EDGE = "#0B1A33"
ARROW = "#3B4A5E"
LAYER_EDGE = "#7C8BA1"
LABEL = "#1F2A3A"
BRANCH = "#1F2A3A"
NODE_H = 0.82

LAYERS = {
    "input": ("#F4F7FB", "#1D4E89"),
    "extract": ("#F3F8F6", "#1E6B52"),
    "parse": ("#F7F5FB", "#5B3F8C"),
    "geo": ("#FBF6F0", "#9A5B13"),
    "match": ("#F3F8F6", "#1E6B52"),
    "verify": ("#FBF3F3", "#9B2C2C"),
    "trade": ("#F4F7FB", "#1D4E89"),
    "store": ("#F5F5F5", "#3B4A5E"),
}

fig, ax = plt.subplots(figsize=(9.0, 23.5))
ax.set_xlim(0, 12)
ax.set_ylim(-1.9, 30.0)
ax.axis("off")


def layer(x0, y0, x1, y1, title, key):
    fill, title_color = LAYERS[key]
    ax.add_patch(
        FancyBboxPatch(
            (x0, y0), x1 - x0, y1 - y0,
            boxstyle="round,pad=0,rounding_size=0.35",
            linewidth=1.3, edgecolor=LAYER_EDGE, facecolor=fill, linestyle=(0, (5, 3)),
        )
    )
    ax.text((x0 + x1) / 2, y1 - 0.38, title, ha="center", va="center",
            fontsize=12.5, color=title_color, fontweight="bold", zorder=5,
            bbox=dict(boxstyle="square,pad=0.15", facecolor=fill, edgecolor="none"))


def node(cx, cy, w, text):
    ax.add_patch(
        FancyBboxPatch(
            (cx - w / 2, cy - NODE_H / 2), w, NODE_H,
            boxstyle="round,pad=0,rounding_size=0.28",
            linewidth=1.0, edgecolor=NODE_EDGE, facecolor=NODE_FILL,
        )
    )
    ax.text(cx, cy, text, ha="center", va="center", color="white", fontsize=10.5)
    return {"cx": cx, "cy": cy, "w": w}


def bottom(n, dx=0.0):
    return (n["cx"] + dx, n["cy"] - NODE_H / 2)


def top(n, dx=0.0):
    return (n["cx"] + dx, n["cy"] + NODE_H / 2)


def left(n):
    return (n["cx"] - n["w"] / 2, n["cy"])


def right(n):
    return (n["cx"] + n["w"] / 2, n["cy"])


def arrow(p, q, label=None, label_dx=0.12, label_frac=0.5, ha="left"):
    ax.annotate(
        "", xy=q, xytext=p,
        arrowprops=dict(arrowstyle="-|>", color=ARROW, lw=1.25,
                        mutation_scale=13, shrinkA=0, shrinkB=0),
        zorder=3,
    )
    if label:
        lx = p[0] + (q[0] - p[0]) * label_frac + label_dx
        ly = p[1] + (q[1] - p[1]) * label_frac
        ax.text(lx, ly, label, fontsize=8.6, color=BRANCH, ha=ha, va="center",
                fontweight="bold")


# 1. Input Layer
layer(3.3, 26.9, 8.7, 29.8, "Input Layer", "input")
n_upload = node(6.0, 28.6, 4.6, "Jamabandi Image + Listing Form")
n_prep = node(6.0, 27.5, 4.6, "Image Preprocessing")
arrow(bottom(n_upload), top(n_prep))

# 2. Extraction Layer
layer(3.0, 23.4, 9.0, 26.3, "Extraction Layer (FastAPI Agent)", "extract")
n_detect = node(6.0, 25.1, 5.0, "Field-Block Detection (YOLO)")
n_ocr = node(6.0, 24.0, 5.0, "OCR (Tesseract / TrOCR)")
arrow(bottom(n_prep), top(n_detect))
arrow(bottom(n_detect), top(n_ocr))

# 3. Field Parsing Layer
layer(0.3, 19.1, 11.7, 22.4, "Field Parsing Layer", "parse")
n_norm = node(6.0, 21.2, 4.6, "Noise Filter & Normalisation")
n_ulpin = node(2.2, 19.85, 3.3, "ULPIN Parser")
n_khasra = node(6.0, 19.85, 3.3, "Khasra / Survey Parser")
n_owner = node(9.8, 19.85, 3.3, "Owner & Location Parser")
arrow(bottom(n_ocr), top(n_norm), label="OCR TEXT LINES", label_frac=0.45)
arrow(bottom(n_norm, -0.9), top(n_ulpin))
arrow(bottom(n_norm), top(n_khasra))
arrow(bottom(n_norm, 0.9), top(n_owner))

# 4. Geo Layer (side branch, like the Recognition Layer in the reference)
layer(0.5, 15.2, 4.5, 18.4, "Geo Layer", "geo")
n_decode = node(2.5, 17.2, 3.6, "ULPIN Decode (Lat/Lng)")
n_locate = node(2.5, 16.1, 3.6, "Locate URL")
arrow(bottom(n_ulpin), top(n_decode))
arrow(bottom(n_decode), top(n_locate))

# 5. Matching Layer
layer(4.9, 11.9, 11.3, 14.8, "Matching Layer (Spring Boot)", "match")
n_lookup = node(8.1, 13.6, 4.8, "Government Record Lookup")
n_decide = node(8.1, 12.5, 4.8, "Match Decision")
arrow(bottom(n_locate), (n_lookup["cx"] - 1.9, n_lookup["cy"] + NODE_H / 2),
      label="ULPIN", label_frac=0.42, label_dx=0.15)
arrow(bottom(n_khasra), (n_lookup["cx"] - 0.6, n_lookup["cy"] + NODE_H / 2),
      label="KHASRA", label_frac=0.55, label_dx=0.12)
arrow(bottom(n_owner), (n_lookup["cx"] + 1.2, n_lookup["cy"] + NODE_H / 2),
      label="OWNER / CITY", label_frac=0.5, label_dx=0.12)
arrow(bottom(n_lookup), top(n_decide))

# 6. Verification Layer
layer(0.3, 6.8, 11.7, 11.2, "Verification Layer (City Authenticator)", "verify")
n_ai = node(3.6, 10.0, 4.0, "AI-Verified Queue")
n_phys = node(8.6, 10.0, 4.4, "Physical Verification Queue")
n_report = node(8.6, 8.9, 4.4, "Field Report Upload")
n_approve = node(6.0, 7.6, 4.8, "Approve / Reject")
arrow(bottom(n_decide, -1.4), top(n_ai), label="STRONG MATCH",
      label_frac=0.3, label_dx=-0.15, ha="right")
arrow(bottom(n_decide, 0.5), top(n_phys), label="WEAK / NO MATCH",
      label_frac=0.3, label_dx=0.12)
arrow(bottom(n_phys), top(n_report))
arrow(bottom(n_ai), (n_approve["cx"] - 1.5, n_approve["cy"] + NODE_H / 2))
arrow(bottom(n_report), (n_approve["cx"] + 1.5, n_approve["cy"] + NODE_H / 2))

# 7. Marketplace & Transfer Layer (horizontal sale chain)
layer(0.3, 2.6, 11.7, 6.2, "Marketplace & Transfer Layer", "trade")
n_live = node(6.0, 5.0, 4.0, "LIVE Listing")
n_buy = node(2.1, 3.4, 3.2, "Purchase Request")
n_confirm = node(6.0, 3.4, 3.2, "Seller Confirmation")
n_final = node(9.9, 3.4, 3.2, "Finalize Transfer")
arrow(bottom(n_approve), top(n_live), label="APPROVED", label_frac=0.4)
arrow(bottom(n_live, -1.2), top(n_buy))
arrow(right(n_buy), left(n_confirm))
arrow(right(n_confirm), left(n_final))

# 8. Storage & Presentation Layer
layer(2.0, -1.7, 10.0, 2.0, "Storage & Presentation Layer", "store")
n_store = node(6.0, 0.8, 4.6, "AppStore (InMemory / H2)")
n_pdf = node(3.9, -0.5, 3.4, "Transfer Certificate PDF")
n_ui = node(8.1, -0.5, 3.4, "React Dashboard")
arrow(bottom(n_final), right(n_store), label="SOLD", label_frac=0.35, label_dx=0.12)
arrow(bottom(n_store, -1.0), top(n_pdf))
arrow(bottom(n_store, 1.0), top(n_ui))

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
print("Wrote", OUT)
