#!/usr/bin/env python3
"""Build a detailed MCA project report for Bhumi, modelled on the Traffic Violation report quality."""

from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor, Cm

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "Project_Report_Template  MCA-V-Sem.docx"
OUT = ROOT / "Bhumi_Land_Registry_Marketplace_Project_Report.docx"
FIG = ROOT / "report_assets" / "figures"

PROJECT = "Bhumi: AI-Assisted Land Registry and Marketplace System"
STUDENT = "Abhishek Mishra"
ROLL = "24223002"
SESSION = "2024-2027"
SUPERVISOR = "Dr. Dibakar Saha"
HOD = "Dr. Tripti Swarnkar"

ABSTRACT_PARAS = [
    (
        "Land ownership and transfer in India continue to rely heavily on paper jamabandi and "
        "related registry documents maintained at the village and tehsil level. These documents "
        "encode parcel identity through a combination of khasra or survey numbers (often with "
        "multi-segment subdivisions such as 123/4 or 127/1/1), khata, khewat, khatauni and, "
        "increasingly, the Unique Land Parcel Identification Number (ULPIN / Bhu-Aadhaar). "
        "Citizens who wish to sell agricultural land, houses or flats commonly advertise on "
        "informal digital channels where buyers cannot reliably check whether a photographed "
        "paper corresponds to an authoritative government-side record. Officers in Patwari- or "
        "Tehsildar-style roles still perform essential verification, yet manually typing every "
        "field from a phone photograph is slow, error-prone and difficult to audit. There is "
        "therefore a clear need for an end-to-end system that accelerates intake of registry "
        "papers while keeping a human officer in control of publication and ownership transfer."
    ),
    (
        "This project presents Bhumi, an AI-assisted land registry and marketplace system "
        "designed and implemented as a three-tier web application. The browser hosts a React "
        "(Vite) single-page client that supports marketplace browse and search, role-based "
        "desks, listing creation with multi-file registry-paper upload, purchase request, "
        "sale confirmation, in-app notifications and chat. A Spring Boot backend exposes JWT-"
        "secured REST APIs for authentication, property lifecycle management, city-scoped "
        "authenticator queues, state-scoped administration, transfer finalization and "
        "certificate download. Persistence is abstracted through an AppStore, with a default "
        "in-memory seed suitable for classroom demos and an optional sqlite (H2 file) profile "
        "that stores government_record and related tables for teacher inspection. When a "
        "seller posts papers, AiClient forwards the first registry image to a FastAPI document "
        "agent at /extract, which returns structured JSON fields rather than free-form text alone."
    ),
    (
        "The document agent loads image or PDF bytes, applies OpenCV/Pillow preprocessing, "
        "optionally detects field blocks with YOLO (falling back to line banding when weights "
        "are unavailable), and runs OCR backends such as Tesseract or TrOCR. Parsers recover "
        "ULPIN, khasra/survey (including multi-segment paths), khata, khewat, khatauni, owner, "
        "village, district, state and area. ULPIN strings are normalised against common OCR "
        "glyph confusions and can be snapped to known demo ULPINs for handwriting evaluations. "
        "A shared Base-14 / Base-32 style codec in Python and Java encodes and decodes "
        "latitude–longitude so that a successful ULPIN yields a Google Maps Locate URL on the "
        "listing detail page. MatchingService then resolves a seeded GovernmentRecord by ULPIN, "
        "khasra or survey and routes the case to AI_VERIFIED_AWAITING_AUTHENTICATOR or "
        "NEEDS_PHYSICAL_VERIFICATION (or a dedicated registry queue). Numeric confidence is "
        "kept out of user-facing summaries so that buyers and sellers do not over-trust OCR scores."
    ),
    (
        "Authenticator desks are locked to the officer’s city: AI-matched listings can be "
        "approved or rejected with remarks, while physical cases require upload of a "
        "verification report before approve is enabled, mirroring field practice. On approval "
        "of a SALE listing the property becomes LIVE in marketplace search and an optional "
        "virtual jamabandi PNG with embedded metadata may be generated for later reuse. After "
        "purchase request and seller confirmation, the city authenticator finalizes transfer: "
        "the recorded government owner is updated to the buyer, status becomes SOLD, and "
        "CertificateService renders a Certificate of Transfer of Ownership PDF via OpenPDF. "
        "Admin workflows cover authenticator applications; recommended listings and Locate "
        "links improve discovery without replacing the verification desk."
    ),
    (
        "Evaluation used original handwritten jamabandi photographs captured by the student "
        "(not synthetically generated registry images) together with controlled printed demo "
        "sheets that carry reliable metadata for scripted viva runs. Seeded government rows "
        "such as khasra 123/4 with ULPIN HR06A1B2C3D4E5 (Ramesh Kumar, Sihi, Ballabgarh) "
        "consistently route to the AI-verified queue when form and extraction align, whereas "
        "unknown parcels (for example 777/7/1) correctly fall back to physical verification. "
        "Observed failure modes—glyph noise, slash–parenthesis confusion and reverse-side "
        "bleed—are mitigated by parser hardening and clearer capture guidance. Overall, Bhumi "
        "demonstrates a practical hybrid thesis for land-tech education and local deployment: "
        "machine extraction and matching accelerate intake and make queues explainable, while "
        "city authenticators retain accountability for publication and ownership transfer. "
        "The government store in this release is seeded application data for demonstration; "
        "integration with live statewide cadastral APIs and large-scale layout training remain "
        "explicit directions for future work."
    ),
]

ABSTRACT_KEYWORDS = (
    "Keywords—land registry, jamabandi, marketplace, OCR, ULPIN, Bhu-Aadhaar, khasra, "
    "FastAPI, Spring Boot, React, document verification, data flow diagram, ownership transfer"
)


def set_run(run, *, name="Calibri", size=11, bold=False, italic=False, color=None):
    run.font.name = name
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)


def p_body(doc, text, *, first_line=True):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if first_line:
        p.paragraph_format.first_line_indent = Cm(0.75)
    r = p.add_run(text)
    set_run(r, name="Calibri", size=11)
    return p


def p_head(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text)
    if level == 1:
        set_run(r, name="Calibri Light", size=18, bold=True, color=(0x1B, 0x3A, 0x4B))
    elif level == 2:
        set_run(r, name="Calibri Light", size=16, bold=True, color=(0x1B, 0x3A, 0x4B))
    else:
        set_run(r, name="Calibri Light", size=14, bold=True, color=(0x2F, 0x5D, 0x8C))
    return p


def p_caption(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    set_run(r, name="Calibri", size=10, italic=True, color=(0x5A, 0x6A, 0x7A))
    return p


def p_algo(doc, title, lines):
    p_head(doc, title, 3)
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Cm(0.5)
        p.paragraph_format.line_spacing = 1.1
        r = p.add_run(line)
        set_run(r, name="Consolas", size=9, color=(0x1B, 0x3A, 0x4B))
    doc.add_paragraph()


def p_bullet(doc, text):
    try:
        p = doc.add_paragraph(style="List Paragraph")
    except KeyError:
        p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.left_indent = Cm(0.75)
    r = p.add_run("• " + text)
    set_run(r, name="Calibri", size=11)
    return p


def add_fig(doc, filename, caption, width=6.2):
    path = FIG / filename
    if not path.exists():
        p_body(doc, f"[Figure missing: {filename}]", first_line=False)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    run = p.add_run()
    run.add_picture(str(path), width=Inches(width))
    p_caption(doc, caption)


def add_table(doc, headers, rows, caption):
    p_caption(doc, caption)
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    try:
        table.style = "Normal Table"
    except KeyError:
        pass
    for j, h in enumerate(headers):
        cell = table.rows[0].cells[j]
        cell.text = ""
        r = cell.paragraphs[0].add_run(h)
        set_run(r, name="Calibri", size=10, bold=True, color=(0xFF, 0xFF, 0xFF))
        tcPr = cell._tc.get_or_add_tcPr()
        shd = tcPr.makeelement(
            qn("w:shd"),
            {qn("w:val"): "clear", qn("w:color"): "auto", qn("w:fill"): "1B3A4B"},
        )
        tcPr.append(shd)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.rows[i + 1].cells[j]
            cell.text = ""
            r = cell.paragraphs[0].add_run(str(val))
            set_run(r, name="Calibri", size=10)
    doc.add_paragraph()


def _set_para_text(p, text):
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(text)


def replace_cover(doc):
    mapping = {
        "Title of the Project": PROJECT,
        "Student Name": STUDENT,
        "Roll No: xxxxxxxxxxx": f"Roll No: {ROLL}",
        "(Session: 20XX-20XX)": f"(Session: {SESSION})",
        "(Session: 2021-2022)": f"(Session: {SESSION})",
        "Name of HoD": HOD,
        "Faculty Name": SUPERVISOR,
        "<Project title>": PROJECT,
        "<Project Title>": PROJECT,
        "Project title": PROJECT,
        "<Mentor name, Designation, Organization name>": (
            f"{SUPERVISOR}, Assistant Professor, Department of Computer Applications, "
            f"National Institute of Technology Raipur"
        ),
        "( Supervisor name )": f"( {SUPERVISOR} )",
        "Student name": STUDENT,
    }
    for p in doc.paragraphs:
        full = p.text
        new = full
        for a, b in mapping.items():
            if a in new:
                new = new.replace(a, b)
        if new != full:
            _set_para_text(p, new)

    # Fill Roll No line under declaration if still empty
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == "Roll No:" or p.text.strip() == "Roll No: ":
            _set_para_text(p, f"Roll No: {ROLL}")
        if p.text.strip().startswith("Keywords—component"):
            _set_para_text(p, ABSTRACT_KEYWORDS)

    # Write acknowledgement into the blank page after DECLARATION (before main TOC)
    nit_i = None
    toc_i = None
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == "NIT Raipur":
            nit_i = i
        if p.text.strip() == "Table of Content (INDEX)":
            toc_i = i  # keep last occurrence (body TOC after declaration)
    if nit_i is not None and toc_i is not None and nit_i < toc_i:
        slot = None
        for i in range(nit_i + 1, toc_i):
            if not doc.paragraphs[i].text.strip():
                slot = i
                break
        if slot is not None and slot + 2 < toc_i:
            _set_para_text(doc.paragraphs[slot], "ACKNOWLEDGEMENT")
            ack = (
                f"I express my sincere gratitude to my project supervisor, {SUPERVISOR}, "
                f"Department of Computer Applications, National Institute of Technology Raipur, "
                f"for his valuable guidance, constructive criticism and constant encouragement "
                f"throughout the project “{PROJECT}”. I am thankful to {HOD}, Head of the "
                f"Department of Computer Applications, for providing academic support and "
                f"laboratory facilities. I also thank the faculty members of the department, "
                f"my classmates and my family for their support during the course of this work."
            )
            _set_para_text(doc.paragraphs[slot + 2], ack)

    # Prefill template Abstract area with the full multi-paragraph abstract
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() != "Abstract:":
            continue
        blanks = []
        j = i + 1
        while j < len(doc.paragraphs):
            t = doc.paragraphs[j].text.strip()
            if t.startswith("Keywords"):
                break
            if not t:
                blanks.append(j)
            j += 1
        # Prefer every-other blank so paragraphs are visually spaced on the template page
        targets = blanks[::2][: len(ABSTRACT_PARAS)]
        if len(targets) < len(ABSTRACT_PARAS):
            targets = blanks[: len(ABSTRACT_PARAS)]
        for k, para_i in enumerate(targets):
            _set_para_text(doc.paragraphs[para_i], ABSTRACT_PARAS[k])
        break


def page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


def build():
    shutil.copyfile(TEMPLATE, OUT)
    doc = Document(str(OUT))
    replace_cover(doc)

    page_break(doc)

    # ===== Lists =====
    p_head(doc, "LIST OF TABLES", 1)
    for line in [
        "Table 1.1: Land identifiers handled by Bhumi",
        "Table 1.2: Comparison with related approaches",
        "Table 3.1: System modules and responsibilities",
        "Table 3.2: Software requirements",
        "Table 3.3: Hardware requirements",
        "Table 3.4: Libraries and frameworks",
        "Table 4.1: Extracted JSON fields from /extract",
        "Table 4.2: Matching decision outcomes",
        "Table 5.1: Core API endpoint groups",
        "Table 6.1: Demo scenarios and observed outcomes",
        "Table 6.2: Failure modes and mitigations",
    ]:
        p_body(doc, line, first_line=False)

    p_head(doc, "LIST OF FIGURES", 1)
    for line in [
        "Figure 3.1: Layered architecture of Bhumi",
        "Figure 3.2: Collage of original handwritten jamabandi sheets used for testing",
        "Figure 3.3: Original jamabandi sheet 1 (photographed handwritten registry paper)",
        "Figure 3.4: Original jamabandi sheet 2 (photographed handwritten registry paper)",
        "Figure 3.5: Original jamabandi sheet 3 (photographed handwritten registry paper)",
        "Figure 4.1: Overall processing pipeline",
        "Figure 4.2: Government matching decision",
        "Figure 4.3: ULPIN encode–decode–Locate path",
        "Figure 5.1: Flowchart of listing, sale and transfer",
        "Figure 5.2: Level-0 Data Flow Diagram (context)",
        "Figure 5.3: Level-1 Data Flow Diagram",
        "Figure 5.4: Use case diagram",
        "Figure 5.5: Entity–Relationship diagram",
        "Figure 6.1: Property status lifecycle",
    ]:
        p_body(doc, line, first_line=False)

    page_break(doc)

    # ===== Abstract =====
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(PROJECT)
    set_run(r, name="Calibri Light", size=16, bold=True, color=(0x1B, 0x3A, 0x4B))

    p_head(doc, "Abstract:", 2)
    for idx, para in enumerate(ABSTRACT_PARAS):
        p_body(doc, para, first_line=(idx > 0))
    p_body(doc, ABSTRACT_KEYWORDS, first_line=False)

    page_break(doc)

    # ===== 1 =====
    p_head(doc, "1. Introduction", 1)
    p_head(doc, "1.1 Background", 2)
    p_body(
        doc,
        "Secure transfer of land rights is a foundation of economic activity. In the Indian "
        "context, evidence of rights is commonly recorded in jamabandi and related registry "
        "documents maintained at the village and tehsil level. A typical agricultural sheet "
        "mentions the owner, village, district, area and parcel identifiers. Northern states "
        "often use khasra with subdivisions such as 123/4 or 127/1/1, while several southern "
        "states use survey numbers. The Unique Land Parcel Identification Number (ULPIN), also "
        "called Bhu-Aadhaar, encodes a parcel location into a fourteen-character string and is "
        "being promoted as a nationwide digital identifier.",
    )
    p_body(
        doc,
        "Despite digitisation efforts, citizens who wish to sell land, houses or flats often "
        "advertise on informal channels where buyers cannot quickly check whether a photographed "
        "paper matches a government-side record. Officers (Patwari or Tehsildar style roles) still "
        "perform essential verification, but typing every field from a phone photograph is slow "
        "and error-prone. An end-to-end system that extracts fields, proposes a match and keeps "
        "the officer in control of publication and transfer therefore addresses a real operational gap.",
    )

    add_table(
        doc,
        ["Identifier", "Typical region", "Role in Bhumi"],
        [
            ["ULPIN / Bhu-Aadhaar", "Nationwide push", "Primary match key; decode to lat/lng + Locate"],
            ["Khasra (e.g. 123/4)", "North / Central", "Parcel key; multi-segment paths supported"],
            ["Survey number", "South India", "Alternate parcel key via governmentBySurvey"],
            ["Khata / Khewat / Khatauni", "Many states", "Supporting fields for display and OCR demos"],
        ],
        "Table 1.1: Land identifiers handled by Bhumi",
    )

    p_head(doc, "1.2 Related Work", 2)
    p_body(
        doc,
        "Related systems fall into three groups. First, state land-record portals expose citizen "
        "services but are not marketplaces. Second, commercial property portals emphasise "
        "photographs and prices, usually without binding registry verification. Third, academic "
        "OCR work on printed and handwritten Indic documents shows that form fields can be "
        "recovered from images, yet rarely connects extraction to role-based approval and "
        "ownership-transfer artefacts. Bhumi sits between these groups: it is a marketplace with "
        "an explicit verification desk and a document agent.",
    )
    add_table(
        doc,
        ["Approach", "Strength", "Limitation relative to Bhumi"],
        [
            ["State land portals", "Authoritative records", "No peer sale / transfer workflow"],
            ["Property marketplaces", "Discovery and chat", "Weak binding to registry papers"],
            ["Standalone OCR demos", "Field reading", "No officer queue or certificate"],
            ["Bhumi (this project)", "Extract + match + desk + transfer", "Demo gov store, not live NIC API"],
        ],
        "Table 1.2: Comparison with related approaches",
    )

    p_head(doc, "1.3 Motivation", 2)
    p_body(doc, "Three observations motivated the work:", first_line=False)
    p_bullet(doc, "Buyers need evidence that a listing’s paper corresponds to a known parcel record.")
    p_bullet(doc, "Officers need separate queues for AI-matched cases and physical visits.")
    p_bullet(doc, "A classroom-complete stack must run locally (React, Spring Boot, FastAPI) without cloud lock-in.")

    p_head(doc, "1.4 Organisation of the Report", 2)
    p_body(
        doc,
        "Chapter 2 defines the problem, objectives, scope and contributions. Chapter 3 presents "
        "the system model, architecture, modules and requirements. Chapter 4 describes the "
        "methodology: extraction, ULPIN handling and matching. Chapter 5 covers implementation, "
        "flowcharts, DFDs, use cases and the ER model. Chapter 6 discusses results and errors. "
        "Chapter 7 concludes and lists future work. Chapter 8 gives the bibliography.",
    )

    page_break(doc)

    # ===== 2 =====
    p_head(doc, "2. Project Overview", 1)
    p_head(doc, "2.1 Problem Definition", 2)
    p_body(
        doc,
        "Given a seller who uploads one or more registry-paper images together with a listing "
        "form (type, location, price, optional ULPIN/khasra), the system must (i) extract land "
        "identifiers, (ii) look up a government-style record, (iii) route the case to an "
        "AI-verified or physical authenticator queue in the seller’s city, (iv) publish the "
        "listing only after approval, and (v) support purchase, confirmation and transfer "
        "finalization that updates the recorded owner and issues a PDF certificate.",
    )

    p_head(doc, "2.2 Objectives", 2)
    p_bullet(doc, "Build a three-tier web system for land/house/flat marketplace workflows.")
    p_bullet(doc, "Implement a document agent that returns structured JSON from paper images.")
    p_bullet(doc, "Match ULPIN/khasra/survey against a local government record store.")
    p_bullet(doc, "Provide city-scoped authenticator and state-scoped admin desks.")
    p_bullet(doc, "Complete sale-to-transfer with notifications and a transfer certificate.")

    p_head(doc, "2.3 Scope and Assumptions", 2)
    p_body(
        doc,
        "The government store is seeded application data (approximately one hundred records), "
        "not a live statewide cadastral API. OCR quality depends on lighting and handwriting. "
        "The optional sqlite profile uses an H2 file database and Base64 password encoding "
        "labelled as classroom-only. Full nationwide YOLO training on real jamabandis is out of scope.",
    )

    p_head(doc, "2.4 Contributions", 2)
    p_bullet(doc, "End-to-end Bhumi stack with JWT roles USER, AUTHENTICATOR and ADMIN.")
    p_bullet(doc, "ULPIN codec with Locate URL generation and OCR noise hardening.")
    p_bullet(doc, "Physical verification report gate and virtual jamabandi on approval.")
    p_bullet(doc, "Recommended listings and marketplace lockdown for desk roles.")

    p_head(doc, "2.5 Expected Outcomes", 2)
    p_body(
        doc,
        "A demonstrable system where posting seeded khasra 123/4 (or ULPIN HR06A1B2C3D4E5) in "
        "Ballabgarh reaches the AI-verified queue; unknown parcels reach physical verification; "
        "officer approval yields LIVE search visibility; finalize yields SOLD status, updated "
        "owner and a downloadable certificate.",
    )

    page_break(doc)

    # ===== 3 =====
    p_head(doc, "3. System Model", 1)
    p_head(doc, "3.1 System Architecture", 2)
    p_body(
        doc,
        "Bhumi follows a layered client–server architecture. The browser hosts a React "
        "application. API calls under /api are handled by Spring Boot. When registry papers are "
        "uploaded, AiClient forwards the first paper to the FastAPI agent at /extract. "
        "MatchingService writes status and summary fields; NotifyService alerts officers. "
        "Persistence is abstracted by AppStore.",
    )
    add_fig(doc, "fig_3_1_architecture.png", "Figure 3.1: Layered architecture of Bhumi", 6.0)

    p_head(doc, "3.2 Module Description", 2)
    add_table(
        doc,
        ["Module", "Input", "Output", "Main tool"],
        [
            ["Frontend Shell/Routes", "User actions", "Screens + JWT session", "React Router"],
            ["AuthService", "Credentials / apply", "JWT, applications", "Spring Security"],
            ["PropertyService", "Draft + files", "Listing views", "Spring MVC"],
            ["AiClient + Matching", "Paper bytes", "Status + fields", "HTTP + rules"],
            ["AI /extract", "Image", "JSON fields", "FastAPI, OCR"],
            ["CertificateService", "Transfer data", "PDF bytes", "OpenPDF"],
            ["NotifyService", "Events", "IN_APP + logs", "AppStore"],
            ["AppStore", "Domain objects", "Persistence", "InMemory / JDBC"],
        ],
        "Table 3.1: System modules and responsibilities",
    )

    p_head(doc, "3.3 Software Requirements", 2)
    add_table(
        doc,
        ["Component", "Specification"],
        [
            ["OS", "macOS / Linux / Windows with WSL"],
            ["JDK", "21+"],
            ["Node.js", "20+"],
            ["Python", "3.9+ with ai-service venv"],
            ["Browser", "Chromium / Firefox / Safari recent"],
        ],
        "Table 3.2: Software requirements",
    )

    p_head(doc, "3.4 Hardware Requirements", 2)
    add_table(
        doc,
        ["Component", "Minimum", "Recommended"],
        [
            ["CPU", "4 cores", "8 cores"],
            ["RAM", "8 GB", "16 GB (OCR models)"],
            ["Disk", "5 GB free", "15 GB with models"],
            ["Camera", "Phone camera for handwriting demos", "Good lighting, flat paper"],
        ],
        "Table 3.3: Hardware requirements",
    )

    p_head(doc, "3.5 Libraries and Platform", 2)
    add_table(
        doc,
        ["Library / platform", "Role"],
        [
            ["React 18 + Vite 5", "SPA UI"],
            ["Spring Boot 3.3", "REST API, security, services"],
            ["JJWT", "JSON Web Tokens"],
            ["OpenPDF", "Transfer certificate PDF"],
            ["FastAPI + Uvicorn", "Document extract service"],
            ["OpenCV + Pillow", "Image load / preprocess"],
            ["Tesseract / TrOCR", "OCR backends"],
            ["H2 (sqlite profile)", "Classroom file database"],
        ],
        "Table 3.4: Libraries and frameworks",
    )

    p_head(doc, "3.6 Sample Inputs Used for Evaluation", 2)
    p_body(
        doc,
        "Evaluation used original handwritten jamabandi sheets photographed by the student "
        "and printed demo papers under samples/printed/ for controlled metadata demos. The "
        "handwritten sheets are real paper photographs—not synthetically generated registry "
        "images. Seeded government rows include khasra 123/4 with ULPIN HR06A1B2C3D4E5 "
        "(Ramesh Kumar, Sihi, Ballabgarh) and related parcels such as 88/1.",
    )
    add_fig(
        doc,
        "fig_3_2_sample_jamabandi_inputs.png",
        "Figure 3.2: Collage of original handwritten jamabandi sheets used for testing",
        6.3,
    )
    p_body(
        doc,
        "Figures 3.3–3.5 present the same original sheets individually so that examiners can "
        "inspect handwriting quality, ink bleed and layout. These photographs are the primary "
        "inputs used when exercising the FastAPI /extract endpoint during viva-oriented demos.",
        first_line=False,
    )
    add_fig(
        doc,
        "fig_3_3_jamabandi_original_1.jpg",
        "Figure 3.3: Original jamabandi sheet 1 (photographed handwritten registry paper)",
        5.4,
    )
    add_fig(
        doc,
        "fig_3_4_jamabandi_original_2.jpg",
        "Figure 3.4: Original jamabandi sheet 2 (photographed handwritten registry paper)",
        5.4,
    )
    add_fig(
        doc,
        "fig_3_5_jamabandi_original_3.jpg",
        "Figure 3.5: Original jamabandi sheet 3 (photographed handwritten registry paper)",
        5.4,
    )

    page_break(doc)

    # ===== 4 =====
    p_head(doc, "4. Methodology", 1)
    p_head(doc, "4.1 Overview of the Proposed Method", 2)
    p_body(
        doc,
        "The proposed method is a hybrid pipeline: computer vision and parsers propose "
        "structured fields; deterministic matching proposes a queue; a human authenticator "
        "approves publication and later finalizes ownership transfer. Figure 4.1 summarises the flow.",
    )
    add_fig(doc, "fig_4_1_pipeline.png", "Figure 4.1: Overall processing pipeline", 6.3)

    p_head(doc, "4.2 Document Acquisition and Preprocessing", 2)
    p_body(
        doc,
        "Sellers upload image or PDF registry papers. The AI service loads bytes with Pillow/"
        "OpenCV, builds grayscale and binary variants, and optionally detects field blocks with "
        "YOLO. If weights are absent, horizontal line bands are used. Printed PNGs may carry a "
        "bhumi_meta text chunk that short-circuits OCR for reliable classroom demos.",
    )

    p_head(doc, "4.3 Field Extraction", 2)
    p_body(
        doc,
        "OCR lines are filtered to reduce reverse-side bleed. Parsers recover ULPIN, khasra/"
        "survey (including multi-segment paths), khata, khewat, khatauni, owner, village, "
        "district, state and area. ULPIN normalisation repairs common glyph confusions and can "
        "snap near-miss strings to known demo ULPINs for handwriting tests.",
    )
    add_table(
        doc,
        ["JSON field", "Meaning"],
        [
            ["ulpin", "14-char parcel id"],
            ["khasraNumber / surveyNumber", "Parcel numbers"],
            ["khataNumber / khewatNumber", "Holding identifiers"],
            ["ownerName, village, district, state", "Descriptive fields"],
            ["latitude, longitude, locateUrl", "From ULPIN decode when possible"],
            ["matchTier, confidence, ocrLines", "Diagnostics (confidence hidden in user UI)"],
        ],
        "Table 4.1: Extracted JSON fields from /extract",
    )

    p_head(doc, "4.4 ULPIN Codec and Locate", 2)
    p_body(
        doc,
        "Encoding pads latitude/longitude, converts integer parts with Base-14 (latitude) and "
        "Base-19 digit alphabet (longitude), fractional triplets with Base-32, and applies "
        "I→Y and O→Z substitutions. Decoding reverses the process to support Google Maps Locate links. "
        "The same codec is implemented in Python (ai-service) and Java (backend) so that OCR "
        "output and Locate links remain consistent across tiers.",
    )
    p_algo(
        doc,
        "Algorithm 4.1: ULPIN Decode to Locate (conceptual)",
        [
            "Input: ulpin string U (length 14 after normalisation)",
            "Output: (lat, lng) and locateUrl, or failure",
            "1:  U ← normalise(U)   // uppercase; fix O/0, I/1 confusions; optional demo snap",
            "2:  if |U| ≠ 14 then return failure",
            "3:  (lat, lng) ← decode_base14_base32(U)",
            "4:  if out_of_india_bounds(lat, lng) then return failure",
            "5:  locateUrl ← \"https://www.google.com/maps?q=\" + lat + \",\" + lng",
            "6:  return (lat, lng, locateUrl)",
        ],
    )
    add_fig(doc, "fig_4_3_ulpin.png", "Figure 4.3: ULPIN encode–decode–Locate path", 6.0)

    p_head(doc, "4.5 Government Matching", 2)
    p_body(
        doc,
        "MatchingService applies extraction to the listing, then resolves a GovernmentRecord by "
        "ULPIN, khasra or survey. Alignment of city/owner/identifiers and confidence selects "
        "AI_VERIFIED_AWAITING_AUTHENTICATOR versus NEEDS_PHYSICAL_VERIFICATION. REGISTRY purpose "
        "uses a dedicated registry queue. User-facing summaries omit numeric confidence phrases.",
    )
    p_algo(
        doc,
        "Algorithm 4.2: ApplyExtractionAndMatch (conceptual)",
        [
            "Input: listing L with registry paper bytes P",
            "Output: updated status, extracted fields, officer notification",
            "1:  J ← AiClient.extract(P)                 // FastAPI /extract JSON",
            "2:  merge J into L (ULPIN, khasra, survey, owner, village, …)",
            "3:  G ← lookup GovernmentRecord by ULPIN else khasra else survey",
            "4:  if purpose(L) = REGISTRY then",
            "5:      status ← PENDING_REGISTRY; notify registry officers; return",
            "6:  if G = ∅ or weak_alignment(L, G, J) then",
            "7:      status ← NEEDS_PHYSICAL_VERIFICATION",
            "8:  else",
            "9:      status ← AI_VERIFIED_AWAITING_AUTHENTICATOR",
            "10: notify authenticators scoped to city(L)",
            "11: persist L via AppStore",
        ],
    )
    add_fig(doc, "fig_4_2_matching.png", "Figure 4.2: Government matching decision", 5.5)
    add_table(
        doc,
        ["Condition", "Status", "Officer action"],
        [
            ["Strong match", "AI_VERIFIED_AWAITING_AUTHENTICATOR", "Approve / reject with remarks"],
            ["No/weak match", "NEEDS_PHYSICAL_VERIFICATION", "Upload report, then approve"],
            ["Purpose REGISTRY", "PENDING_REGISTRY", "Registration review"],
            ["Approved SALE", "LIVE", "Visible in marketplace search"],
        ],
        "Table 4.2: Matching decision outcomes",
    )

    p_head(doc, "4.6 Sale and Transfer Method", 2)
    p_body(
        doc,
        "After LIVE publication, a buyer may request purchase. The seller confirms from Track. "
        "The city authenticator finalizes transfer: government owner becomes the buyer, OpenPDF "
        "renders a Certificate of Transfer of Ownership, and status becomes SOLD. On approve, "
        "a virtual jamabandi PNG with bhumi_meta may be generated for later reuse.",
    )

    page_break(doc)

    # ===== 5 =====
    p_head(doc, "5. Implementation", 1)
    p_head(doc, "5.1 Project Structure", 2)
    p_body(doc, "The repository is organised as follows:", first_line=False)
    p_bullet(doc, "frontend/ — React UI (marketplace, desks, post, track, chat)")
    p_bullet(doc, "backend/ — Spring Boot services, security, store, Flyway migrations")
    p_bullet(doc, "ai-service/ — FastAPI extract, OCR, ULPIN codec, sample scripts")
    p_bullet(doc, "samples/ — printed demos and handwritten/manual_tests originals")
    p_bullet(doc, "docs/ — report, presentation and guides")

    p_head(doc, "5.2 Flowchart", 2)
    p_body(
        doc,
        "Figure 5.1 shows control flow from posting through matching, officer decision, "
        "purchase, confirmation and finalization.",
    )
    add_fig(doc, "fig_5_1_flowchart.png", "Figure 5.1: Flowchart of listing, sale and transfer", 5.2)

    p_head(doc, "5.3 Data Flow Diagrams", 2)
    p_body(
        doc,
        "Figure 5.2 is the context diagram. External entities are USER, AUTHENTICATOR, ADMIN and "
        "the AI service. Figure 5.3 refines processing into authentication, post/extract, "
        "match/queue, approve/publish, purchase/transfer and notify/chat, with stores for users, "
        "government records, listings, certificates and notifications.",
    )
    add_fig(doc, "fig_5_2_dfd0.png", "Figure 5.2: Level-0 Data Flow Diagram (context)", 5.8)
    add_fig(doc, "fig_5_3_dfd1.png", "Figure 5.3: Level-1 Data Flow Diagram", 6.2)

    p_head(doc, "5.4 Use Case Diagram", 2)
    p_body(
        doc,
        "Primary use cases include browse/buy, post property, track/chat, extract fields, match "
        "records, approve listing, finalize transfer and approve authenticator applications.",
    )
    add_fig(doc, "fig_5_4_usecase.png", "Figure 5.4: Use case diagram", 5.8)

    p_head(doc, "5.5 Data Model (ER Diagram)", 2)
    p_body(
        doc,
        "Logical entities include UserAccount, PropertyListing, GovernmentRecord, "
        "TransferCertificate, Notification, AuthenticatorApplication and ChatMessage. "
        "Government records are keyed by khasra and indexed by ULPIN and survey for matching.",
    )
    add_fig(doc, "fig_5_5_er.png", "Figure 5.5: Entity–Relationship diagram", 6.2)

    p_head(doc, "5.6 Important API Groups", 2)
    add_table(
        doc,
        ["Area", "Examples"],
        [
            ["Auth", "POST /api/auth/login, /register, /authenticator-apply"],
            ["Public marketplace", "GET /api/public/properties, /recommended, locations"],
            ["Seller flows", "POST /api/properties, purchase-request, confirm-sale"],
            ["Authenticator", "/queues, /decision, /verification-report, /finalize-transfer"],
            ["AI", "POST http://localhost:8000/extract"],
        ],
        "Table 5.1: Core API endpoint groups",
    )

    p_head(doc, "5.7 Government Record Storage", 2)
    p_body(
        doc,
        "SeedData inserts government rows at first boot. Default InMemoryAppStore keeps maps "
        "governmentByKhasra, governmentByUlpin and governmentBySurvey. Under Spring profile "
        "sqlite, JdbcAppStore persists table government_record in backend/data/bhumi-demo.mv.db "
        "for teacher inspection via the H2 console. This design makes matching explainable in "
        "class: a teacher can open the H2 console, query government_record for khasra 123/4, "
        "and correlate the row with the AI-verified queue entry after a post.",
    )

    p_head(doc, "5.8 Role-Based Access and Desks", 2)
    p_body(
        doc,
        "JWT claims carry role and geography. USER accounts browse the marketplace, post "
        "listings and track sales. AUTHENTICATOR accounts are locked to city desks "
        "(AI-verified, physical and registry queues) and cannot use the public homepage as a "
        "consumer. ADMIN accounts approve authenticator applications and operate at state scope. "
        "Physical verification requires uploading a verification report before approve is enabled, "
        "which mirrors real field practice where paper evidence accompanies the decision.",
    )

    p_head(doc, "5.9 Certificate and Virtual Jamabandi", 2)
    p_body(
        doc,
        "On finalize-transfer, CertificateService renders a Certificate of Transfer of Ownership "
        "PDF with buyer, seller, parcel identifiers and timestamps. On approve of a SALE listing, "
        "the backend may also emit a virtual jamabandi PNG embedding bhumi_meta so that a later "
        "resale can reuse structured fields without retyping. These artefacts close the loop "
        "between paper intake and digital handover.",
    )

    page_break(doc)

    # ===== 6 =====
    p_head(doc, "6. Results and Discussion", 1)
    p_head(doc, "6.1 Experimental Setup", 2)
    p_body(
        doc,
        "Services were run locally: AI on port 8000 with BHUMI_OCR_ENGINE=labels, backend on "
        "8090, frontend on 5173. Demo accounts included user@bhumi.test and "
        "auth.ballabgarh@bhumi.gov.in. Tests used handwritten sheets in "
        "samples/handwritten/manual_tests/ and printed papers such as jamabandi_123_4.png.",
    )

    p_head(doc, "6.2 Qualitative Results", 2)
    add_table(
        doc,
        ["Scenario", "Input", "Observed outcome"],
        [
            ["Golden match", "Khasra 123/4 + ULPIN HR06A1B2C3D4E5", "AI_VERIFIED queue in Ballabgarh"],
            ["Khasra-only", "88/1 Anita Sharma sheet", "AI verified when OCR/form align"],
            ["Unknown parcel", "777/7/1 or random ULPIN", "NEEDS_PHYSICAL_VERIFICATION"],
            ["Physical approve", "Report uploaded", "Approve enabled; LIVE + virtual jamabandi"],
            ["Transfer", "Purchase + confirm + finalize", "SOLD + certificate PDF"],
        ],
        "Table 6.1: Demo scenarios and observed outcomes",
    )
    add_fig(doc, "fig_6_1_status_lifecycle.png", "Figure 6.1: Property status lifecycle", 6.2)

    p_head(doc, "6.3 Error Analysis", 2)
    add_table(
        doc,
        ["Failure mode", "Cause", "Mitigation"],
        [
            ["ULPIN null in JSON", "OCR glyph noise", "Normalisation + demo ULPIN snap; clearer writing"],
            ["Khasra 88) )", "Slash read as parenthesis", "Khasra OCR repair rules"],
            ["Bleed Hindi lines", "Writing on reverse side", "Bleed-line filter"],
            ["Wrong city officer", "Listing city ≠ officer city", "City-scoped queues (by design)"],
        ],
        "Table 6.2: Failure modes and mitigations",
    )

    p_head(doc, "6.4 Discussion", 2)
    p_body(
        doc,
        "The results support the hybrid thesis of the project: automation accelerates intake, "
        "while officers retain authority over publication and transfer. Printed metadata samples "
        "are most stable for scripted demos; original handwriting is more realistic for viva "
        "evaluation and benefits from parser hardening. Keeping confidence out of user-facing "
        "summaries avoids over-trusting OCR scores.",
    )

    page_break(doc)

    # ===== 7 =====
    p_head(doc, "7. Conclusion and Future Work", 1)
    p_head(doc, "7.1 Conclusion", 2)
    p_body(
        doc,
        "This project designed and implemented Bhumi, an AI-assisted land registry and "
        "marketplace that connects document extraction, government-record matching, "
        "authenticator approval and ownership-transfer certification. The system shows how a "
        "modern web and OCR stack can support transparent property discovery without removing "
        "the accountability of local verification officers.",
    )

    p_head(doc, "7.2 Future Work", 2)
    p_bullet(doc, "Train layout detectors on diverse real jamabandi formats across states.")
    p_bullet(doc, "Integrate legally accessible live land-record services where available.")
    p_bullet(doc, "Replace classroom Base64 password mode with production hashing and secrets management.")
    p_bullet(doc, "Improve Devanagari handwriting OCR and guided mobile capture.")
    p_bullet(doc, "Add bilingual UI and richer audit analytics for administrators.")

    page_break(doc)

    # ===== 8 =====
    p_head(doc, "8. Bibliography", 1)
    refs = [
        "[1] Department of Land Resources, Government of India, Unique Land Parcel Identification Number (ULPIN) / Bhu-Aadhaar programme notes.",
        "[2] Ministry of Rural Development / DoLR, Digital India Land Records Modernisation Programme (DILRMP) overview materials.",
        "[3] Spring Boot Reference Documentation, v3.3, VMware/Broadcom.",
        "[4] Sebastián Ramírez et al., FastAPI Documentation.",
        "[5] Meta Open Source, React Documentation.",
        "[6] R. Smith, “An Overview of the Tesseract OCR Engine,” ICDAR, 2007.",
        "[7] M. Li et al., “TrOCR: Transformer-based Optical Character Recognition with Pre-trained Models,” AAAI, 2023.",
        "[8] G. Jocher et al., Ultralytics YOLOv8 Documentation.",
        "[9] OpenPDF Project Documentation.",
        "[10] H2 Database Engine Documentation (PostgreSQL compatibility mode).",
        "[11] National Institute of Technology Raipur, Department of Computer Applications, MCA-V Semester Project Report Template and Guidelines.",
    ]
    for ref in refs:
        p_body(doc, ref, first_line=False)

    doc.save(str(OUT))
    print("Wrote", OUT)


if __name__ == "__main__":
    build()
