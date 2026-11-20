#!/usr/bin/env python3
"""Implementation-chapter figures (Level-1 DFD and ER diagram) in the Figure 3.1 style."""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from draw_methodology_figures import (
    ARROW, FIG_DIR, NAVY, NAVY_EDGE, TEXT_DARK, B, L, R, T, box, new_canvas, path, save,
)

ENTITY = "#1D4E89"
STORE_FILL = "#FBF6F0"
STORE_EDGE = "#9A5B13"


def store(ax, cx, cy, w, h, sid, text):
    ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, facecolor=STORE_FILL,
                           edgecolor=STORE_EDGE, linewidth=1.3, zorder=4))
    ax.plot([cx - w / 2 + 0.6] * 2, [cy - h / 2, cy + h / 2], color=STORE_EDGE, lw=1.3, zorder=5)
    ax.text(cx - w / 2 + 0.3, cy, sid, ha="center", va="center", fontsize=9.5,
            fontweight="bold", color=STORE_EDGE, zorder=6)
    ax.text(cx + 0.3, cy, text, ha="center", va="center", fontsize=9, color=TEXT_DARK, zorder=6)
    return dict(cx=cx, cy=cy, w=w, h=h)


# ---------------------------------------------------------------------------
# Figure 5.1 - Level-1 data flow diagram
# ---------------------------------------------------------------------------
def fig_dfd():
    fig, ax = new_canvas(17, 9.2, 23.2, 0.2, 12.2)
    ax.text(11.6, 11.85, "Level-1 Data Flow Diagram - Bhumi", ha="center", fontsize=14,
            fontweight="bold", color=NAVY)

    xs = [4.2, 7.6, 11.0, 14.4, 17.8, 21.2]
    labels = ["1.0\nAuthenticate\n& Authorise", "2.0\nPost Listing\n& Upload", "3.0\nExtract, Match\n& Route",
              "4.0\nVerify &\nApprove", "5.0\nPurchase &\nTransfer", "6.0\nNotify\n& Chat"]
    P = [box(ax, x, 6.2, 2.7, 1.7, t, fill=NAVY, fs=9.6, bold=True) for x, t in zip(xs, labels)]

    admin = box(ax, 1.15, 6.2, 1.9, 1.2, "State\nAdmin", fill=ENTITY, fs=9.5, bold=True)
    user = box(ax, 5.9, 10.4, 3.2, 1.0, "Citizen User (Seller)", fill=ENTITY, fs=9.5, bold=True)
    ai = box(ax, 9.3, 9.0, 2.3, 0.9, "AI Service :8000", fill="#1E6B52", fs=9.2, bold=True)
    officer = box(ax, 14.4, 10.4, 2.9, 1.0, "City Authenticator", fill=ENTITY, fs=9.5, bold=True)
    buyer = box(ax, 17.8, 10.4, 2.6, 1.0, "Buyer / Seller", fill=ENTITY, fs=9.5, bold=True)
    inbox = box(ax, 21.2, 10.4, 2.6, 1.0, "All Roles (Inbox)", fill=ENTITY, fs=9.5, bold=True)

    D1 = store(ax, 4.2, 1.4, 2.9, 0.8, "D1", "app_user")
    D2 = store(ax, 7.6, 1.4, 2.9, 0.8, "D2", "listing, papers,\nphotos")
    D3 = store(ax, 11.0, 1.4, 2.9, 0.8, "D3", "government_record")
    D4 = store(ax, 17.8, 1.4, 2.9, 0.8, "D4", "transfer_certificate")
    D5 = store(ax, 21.2, 1.4, 2.9, 0.8, "D5", "notification, chat")

    path(ax, [R(admin), L(P[0])])
    ax.text(admin["cx"], admin["cy"] + 1.05, "approves\nofficers", ha="center", va="center",
            fontsize=8.6, fontweight="bold", color=TEXT_DARK)
    path(ax, [B(user, -1.0), (4.9, T(P[0])[1])], "login", label_dx=0.1)
    path(ax, [B(user, 1.0), (6.9, T(P[1])[1])], "listing +\njamabandi", label_dx=-0.95)
    path(ax, [T(P[1], 0.9), (8.5, B(ai)[1])], "image", label_dx=0.1)
    path(ax, [B(ai, 0.8), (10.1, T(P[2])[1])], "fields\nJSON", label_dx=0.1)
    path(ax, [B(officer, -0.6), T(P[3], -0.6)], "decision,\nreport", label_dx=-1.15)
    path(ax, [T(P[3], 0.6), B(officer, 0.6)], "queues", label_dx=0.1)
    path(ax, [B(buyer), T(P[4])], "purchase /\nconfirm", label_dx=0.1)
    path(ax, [T(P[5]), B(inbox)], "alerts", label_dx=0.1)

    chain = ["JWT", "listing", "queued\ncase", "LIVE", "events"]
    for i, lab in enumerate(chain):
        path(ax, [R(P[i]), L(P[i + 1])], lab, label_dx=0, label_dy=-0.45, ha="center")

    path(ax, [B(P[0]), T(D1)], "user, role", label_dx=0.1)
    path(ax, [B(P[1]), T(D2)], "store files", label_dx=0.1)
    path(ax, [T(D3, -0.6), (10.4, B(P[2])[1])], "lookup", label_dx=-0.85)
    path(ax, [B(P[3], -0.7), (13.7, 3.9), (11.5, 3.9), (11.5, T(D3)[1])], "upsert record",
         label_at=1, label_dx=0, label_dy=0.22, ha="center")
    path(ax, [B(P[4], -0.8), (17.0, 3.2), (12.1, 3.2), (12.1, T(D3)[1])], "owner = buyer",
         label_at=1, label_dx=0, label_dy=0.22, ha="center")
    path(ax, [B(P[4], 0.5), (18.3, T(D4)[1])], "certificate\nPDF", label_dx=0.1)
    path(ax, [B(P[5]), T(D5)], "save", label_dx=0.1)

    for i, (fill, edge, lab) in enumerate([(NAVY, NAVY_EDGE, "Process"), (ENTITY, NAVY_EDGE, "External entity"),
                                           ("#1E6B52", NAVY_EDGE, "External system"),
                                           (STORE_FILL, STORE_EDGE, "Data store")]):
        x = 6.0 + i * 3.2
        ax.add_patch(Rectangle((x, 0.35), 0.45, 0.3, facecolor=fill, edgecolor=edge, zorder=4))
        ax.text(x + 0.6, 0.5, lab, va="center", fontsize=9, color=TEXT_DARK)
    save(fig, "ch5_fig_5_01_dfd_level1.png")


# ---------------------------------------------------------------------------
# Figure 5.2 - Entity relationship diagram (Flyway V1-V4)
# ---------------------------------------------------------------------------
ROW = 0.4
HEAD = 0.55
TAG_COLORS = {"PK": "#B7791F", "FK": "#1D4E89", "UQ": "#5B3F8C", "IX": "#3B4A5E"}


def table(ax, cx, top, name, rows, head=NAVY, w=4.2):
    h = HEAD + ROW * len(rows)
    x0 = cx - w / 2
    ax.add_patch(FancyBboxPatch((x0, top - h), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                facecolor="white", edgecolor=NAVY_EDGE, linewidth=1.2, zorder=4))
    ax.add_patch(Rectangle((x0, top - HEAD), w, HEAD, facecolor=head, edgecolor=NAVY_EDGE, zorder=5))
    ax.text(cx, top - HEAD / 2, name, ha="center", va="center", color="white", fontsize=10,
            fontweight="bold", zorder=6)
    for i, (tag, col) in enumerate(rows):
        y = top - HEAD - ROW * (i + 0.5)
        if i % 2:
            ax.add_patch(Rectangle((x0 + 0.02, y - ROW / 2), w - 0.04, ROW, facecolor="#F4F7FB",
                                   edgecolor="none", zorder=4.5))
        if tag:
            ax.text(x0 + 0.15, y, tag, va="center", fontsize=7.6, fontweight="bold",
                    color=TAG_COLORS[tag], zorder=6)
        ax.text(x0 + 0.75, y, col, va="center", fontsize=8.4, color=TEXT_DARK, zorder=6)
    return dict(cx=cx, cy=top - h / 2, w=w, h=h, top=top, bottom=top - h)


def rel(ax, pts, label, dashed=False, label_at=0, dx=0.0, dy=0.25):
    style = (0, (5, 3)) if dashed else "solid"
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=ARROW, lw=1.3, linestyle=style, zorder=3)
    for (x, y) in (pts[0], pts[-1]):
        ax.plot(x, y, "o", ms=4.5, color=ARROW, zorder=3)
    (x1, y1), (x2, y2) = pts[label_at], pts[label_at + 1]
    ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, label, ha="center", va="center", fontsize=8.4,
            fontweight="bold", color=TEXT_DARK, zorder=7,
            bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="none"))


def fig_er():
    fig, ax = new_canvas(17, 12.2, 23.6, -1.5, 16.2)
    ax.text(11.8, 15.85, "Entity Relationship Diagram - Bhumi schema (Flyway V1-V4)", ha="center",
            fontsize=14, fontweight="bold", color=NAVY)

    user = table(ax, 3.5, 15.0, "app_user", [
        ("PK", "id"), ("UQ", "email"), ("", "password_hash"), ("", "full_name, phone"),
        ("", "role (USER / AUTHENTICATOR / ADMIN)"), ("", "state, district, city"),
        ("", "active, official_login"), ("", "created_at")])
    app = table(ax, 3.5, 9.9, "authenticator_application", [
        ("PK", "id"), ("FK", "applicant_user_id"), ("", "official_id_number"),
        ("", "state, district, city"), ("", "status")], head="#5B3F8C")
    admin = table(ax, 3.5, 6.2, "state_admin", [
        ("PK", "admin_id"), ("FK", "user_id (unique)"), ("IX", "state_union_territory"),
        ("UQ", "email"), ("", "active")], head="#5B3F8C")
    audit = table(ax, 3.5, 1.9, "audit_event", [
        ("PK", "id"), ("", "actor_id (no FK)"), ("", "action"), ("", "detail, created_at")],
        head="#3B4A5E")

    notif = table(ax, 9.2, 15.0, "notification", [
        ("PK", "id"), ("FK", "user_id"), ("", "channel, subject, body"), ("", "is_read, created_at")],
        head="#3B4A5E")
    paper = table(ax, 9.2, 10.4, "property_paper", [
        ("PK", "id"), ("FK", "property_id"), ("", "file_id, original_name"),
        ("", "content_type"), ("", "bytes (BYTEA)")], head="#1E6B52")
    photo = table(ax, 9.2, 6.6, "property_photo", [
        ("PK", "id"), ("FK", "property_id"), ("", "file_id, content_type"),
        ("", "bytes (BYTEA)"), ("IX", "sort_order")], head="#1E6B52")
    chat = table(ax, 9.2, 1.9, "chat_message", [
        ("PK", "id"), ("FK", "property_id"), ("FK", "sender_id"), ("", "body, blocked")],
        head="#3B4A5E")

    listing = table(ax, 14.6, 11.3, "property_listing", [
        ("PK", "id"), ("FK", "seller_id"), ("FK", "buyer_id"), ("", "purpose, type"),
        ("IX", "status"), ("", "title, address, asking_price"), ("IX", "city"),
        ("", "state, district, measurements"), ("", "khasra_number, survey_number"),
        ("", "ulpin"), ("", "khata, khewat, khatauni"), ("", "ai_summary, officer_remarks"),
        ("", "certificate_id"), ("", "latitude, longitude (V4)"),
        ("", "verification_report_* (V4)"), ("", "virtual_jamabandi_* (V4)"),
        ("", "purchase / sale / transfer times")], head=NAVY, w=4.6)

    gov = table(ax, 21.0, 11.3, "government_record", [
        ("PK", "khasra_number"), ("UQ", "ulpin (V2)"), ("IX", "survey_number (V2)"),
        ("", "khata, khewat, khatauni (V2)"), ("", "village, city, district"),
        ("", "owner_name, owner_phone"), ("", "measurements"), ("", "updated_at")],
        head="#9A5B13", w=4.6)
    cert = table(ax, 21.0, 5.6, "transfer_certificate", [
        ("PK", "id"), ("FK", "property_id"), ("UQ", "certificate_number"), ("", "khasra_number"),
        ("", "old_owner_name, new_owner_name"), ("", "officer_id, officer_name"),
        ("", "pdf_bytes (BYTEA)")], head="#9A5B13", w=4.6)

    ux1 = user["cx"] + 2.1
    rel(ax, [(ux1, 14.0), (notif["cx"] - 2.1, 14.0)], "1 : N", dy=0.22)
    rel(ax, [(3.5, user["bottom"]), (3.5, app["top"])], "1 : N  applies", dx=0.95, dy=0)
    rel(ax, [(1.4, 12.0), (0.9, 12.0), (0.9, 5.4), (1.4, 5.4)], "1 : 1", label_at=1, dx=0, dy=0)
    rel(ax, [(ux1, 11.6), (14.6, 11.6), (14.6, listing["top"])],
        "1 : N  seller_id / buyer_id", dy=0.22)
    rel(ax, [(listing["cx"] - 2.3, 9.4), (paper["cx"] + 2.1, 9.4)], "1 : N", dy=0.22)
    rel(ax, [(listing["cx"] - 2.3, 5.6), (photo["cx"] + 2.1, 5.6)], "1 : N", dy=0.22)
    rel(ax, [(14.6, listing["bottom"]), (14.6, 0.9), (chat["cx"] + 2.1, 0.9)], "1 : N",
        label_at=1, dy=0.22)
    rel(ax, [(listing["cx"] + 2.3, 9.0), (gov["cx"] - 2.3, 9.0)],
        "matched on\nULPIN / khasra\n(logical, no FK)", dashed=True, dy=-0.75)
    rel(ax, [(listing["cx"] + 2.3, 4.6), (cert["cx"] - 2.3, 4.6)], "1 : 0..1\nissues", dy=0.42)

    for i, (tag, meaning) in enumerate([("PK", "primary key"), ("FK", "foreign key"),
                                        ("UQ", "unique"), ("IX", "indexed")]):
        x = 13.0 + i * 2.6
        ax.text(x, -0.6, tag, fontsize=9, fontweight="bold", color=TAG_COLORS[tag])
        ax.text(x + 0.55, -0.6, meaning, fontsize=9, color=TEXT_DARK)
    ax.text(18.2, -1.15, "Dashed line = application-level match by MatchingService", fontsize=8.6,
            style="italic", color="#334155", ha="center")
    save(fig, "ch5_fig_5_02_er_diagram.png")


if __name__ == "__main__":
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig_dfd()
    fig_er()
