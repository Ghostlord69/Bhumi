#!/usr/bin/env python3
"""Results-chapter figure for the Bhumi report (same visual style as the methodology figures)."""

from draw_methodology_figures import (
    AMBER, GREEN, RED, B, L, R, T, box, diamond, layer, new_canvas, path, save,
)


# ---------------------------------------------------------------------------
# Figure 6.1 - Observed outcomes: verification paths, transfer and OCR behaviour
# ---------------------------------------------------------------------------
def fig_outcomes():
    fig, ax = new_canvas(17, 9.4, 28.4, 0.2, 13.4)
    W, H = 3.3, 1.15

    layer(ax, 0.2, 5.4, 28.2, 13.2, "A. End-to-end listing and transfer outcomes", "blue")

    upload = box(ax, 1.95, 9.0, W, H, "Seller uploads\njamabandi paper", fs=9.5)
    extract = box(ax, 5.7, 9.0, W, H, "AI /extract\n(fields + ocrLines)", fs=9.5)
    match = diamond(ax, 9.9, 9.0, 4.0, 2.3, "Strong match with\ngovernment\nrecord?", fs=9.2)

    ai_ok = box(ax, 14.4, 11.0, W, H, "AI verified\n(officer notified)", fs=9.5)
    approve = box(ax, 18.4, 11.0, W, H, "Officer approves,\nlisting goes LIVE", fs=9.5)
    buy = box(ax, 22.4, 11.0, W, H, "Buyer requests,\nseller confirms", fs=9.5)
    final = box(ax, 26.2, 11.0, W, H, "Officer finalizes\ntransfer", fs=9.5)

    phys = box(ax, 14.4, 7.0, W, H, "Physical\nverification queue", fill=AMBER, fs=9.5)
    report = box(ax, 18.4, 7.0, W, H, "Approve locked until\nfield report uploaded",
                 fill=AMBER, fs=8.8)
    search = box(ax, 22.4, 7.0, W, H, "Marketplace search\n(type, place, price)",
                 fill="#1D4E89", fs=9.0)
    done = box(ax, 26.2, 7.4, W, 2.3,
               "SOLD\n\nRemoved from search\nOwner record = buyer\nCertificate PDF issued",
               fill=GREEN, fs=8.8)

    path(ax, [R(upload), L(extract)])
    path(ax, [R(extract), (match["cx"] - 2.0, 9.0)])
    path(ax, [(match["cx"], 10.15), (match["cx"], 11.0), L(ai_ok)],
         label="Yes (e.g. khasra 123/4)", label_at=1, label_dy=0.3, ha="center")
    path(ax, [(match["cx"], 7.85), (match["cx"], 7.0), L(phys)],
         label="No (unknown khasra / ULPIN)", label_at=1, label_dy=-0.3, ha="center")
    path(ax, [R(ai_ok), L(approve)])
    path(ax, [R(phys), L(report)])
    path(ax, [T(report, -0.7), B(approve, -0.7)], label="report\nattached", label_dx=0.12)
    path(ax, [B(approve, 0.7), (19.1, 9.0), (22.4, 9.0), T(search)], label="listed",
         label_at=1, label_dy=0.22, ha="center")
    path(ax, [R(approve), L(buy)])
    path(ax, [R(buy), L(final)])
    path(ax, [B(final), T(done)])

    ax.text(14.2, 5.85, "Both paths end with an officer decision: the AI proposes, the officer is accountable",
            ha="center", fontsize=9.5, style="italic", color="#334155")

    layer(ax, 0.2, 0.5, 28.2, 4.9, "B. OCR behaviour on the two kinds of input paper", "green")

    printed = box(ax, 2.3, 2.4, 3.6, 1.3, "Printed sample PNG\nwith bhumi_meta", fs=9.3)
    stable = box(ax, 6.6, 2.4, 3.4, 1.3, "Stable, accurate\nextraction", fill=GREEN, fs=9.3)
    hand = box(ax, 11.4, 2.4, 3.4, 1.3, "Handwritten\nphone photo", fs=9.3)
    noisy = box(ax, 15.6, 2.4, 3.8, 1.3, "Noisy lines: O/0, I/1,\n'/' read as '('", fill=RED, fs=9.0)
    harden = box(ax, 20.4, 2.4, 4.4, 1.3, "Parser hardening:\nULPIN snap, slash repair,\nbleed-line filter",
                 fill=AMBER, fs=8.8)
    recovered = box(ax, 25.5, 2.4, 3.8, 1.3, "Seeded identifiers\nrecovered reliably",
                    fill=GREEN, fs=9.3)

    path(ax, [R(printed), L(stable)])
    path(ax, [R(hand), L(noisy)])
    path(ax, [R(noisy), L(harden)])
    path(ax, [R(harden), L(recovered)])
    ax.plot([9.0, 9.0], [1.0, 4.0], color="#7C8BA1", lw=1.0, ls=(0, (4, 3)))

    save(fig, "fig_6_1_results_outcomes.png")


if __name__ == "__main__":
    fig_outcomes()
