#!/usr/bin/env python3
"""Generate MCA-V Sem report and PPT from official templates (same styles/layouts)."""

from __future__ import annotations

import shutil
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Twips
from pptx import Presentation
from pptx.util import Inches, Pt as PPt

ROOT = Path(__file__).resolve().parent
REPORT_TEMPLATE = ROOT / "Project_Report_Template  MCA-V-Sem.docx"
PPT_TEMPLATE = ROOT / "MCA-V-Sem- Project Presentation Template.pptx"
REPORT_OUT = ROOT / "Bhumi_MCA_V_Sem_Project_Report.docx"
PPT_OUT = ROOT / "Bhumi_MCA_V_Sem_Project_Presentation.pptx"

PROJECT_TITLE = (
    "Bhumi: AI-Assisted Land Registry and Marketplace System"
)
STUDENT_NAME = "Abhishek Mishra"
ROLL_NO = "24223002"
SESSION = "2024-2027"
HOD_NAME = "Dr. Tripti Swarnkar"
SUPERVISOR_NAME = "Dr. Dibakar Saha"

ACKNOWLEDGEMENT = (
    "I express my sincere gratitude to my project supervisor, Dr. Dibakar Saha, "
    "Department of Computer Applications, National Institute of Technology Raipur, "
    "for his valuable guidance, constant encouragement and constructive suggestions "
    "throughout the development of this project entitled “Bhumi: AI-Assisted Land "
    "Registry and Marketplace System”. His support helped me complete this work in a "
    "systematic and meaningful manner.\n\n"
    "I am also thankful to Dr. Tripti Swarnkar, Head, Department of Computer Applications, "
    "National Institute of Technology Raipur, for providing the necessary facilities and "
    "a supportive academic environment to carry out this project work.\n\n"
    "I extend my thanks to all the faculty members of the Department of Computer Applications "
    "for their teaching, guidance and motivation during the MCA programme. I am grateful to "
    "my classmates and friends for their cooperation and helpful discussions during the "
    "implementation and testing of this system.\n\n"
    "Finally, I express my heartfelt thanks to my family for their patience, blessings and "
    "continuous support, without which this project would not have been possible.\n\n"
    "Place: Raipur\n"
    "Date: ____________________\n\n"
    "Abhishek Mishra\n"
    "Roll No: 24223002\n"
    "MCA-V Semester\n"
    "(Session: 2024-2027)\n"
    "National Institute of Technology Raipur"
)


def _set_run_font(run, *, name=None, size_pt=None, bold=None, italic=None, color=None):
    if name is not None:
        run.font.name = name
        r = run._element
        rPr = r.get_or_add_rPr()
        rFonts = rPr.get_or_add_rFonts()
        rFonts.set(qn("w:ascii"), name)
        rFonts.set(qn("w:hAnsi"), name)
        rFonts.set(qn("w:eastAsia"), name)
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = RGBColor(*color)


def add_heading(doc, text, level=1):
    """Section / sub / sub-sub heading per template formatting table."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    if level == 1:
        _set_run_font(run, name="Calibri Light", size_pt=18, bold=True)
    elif level == 2:
        _set_run_font(run, name="Calibri Light", size_pt=16, bold=True)
    else:
        _set_run_font(run, name="Calibri Light", size_pt=14, bold=True)
    return p


def add_body(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    _set_run_font(run, name="Calibri", size_pt=11, bold=False)
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Paragraph")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if level:
        p.paragraph_format.left_indent = Twips(720 * level)
    run = p.add_run(text)
    _set_run_font(run, name="Calibri", size_pt=11, bold=False)
    return p


def replace_in_paragraphs(doc, mapping):
    for p in doc.paragraphs:
        full = p.text
        new = full
        for old, val in mapping.items():
            if old in new:
                new = new.replace(old, val)
        if new != full:
            # Preserve first-run formatting where possible
            if p.runs:
                first = p.runs[0]
                for r in p.runs[1:]:
                    r.text = ""
                first.text = new
            else:
                p.add_run(new)


def build_report():
    shutil.copyfile(REPORT_TEMPLATE, REPORT_OUT)
    doc = Document(str(REPORT_OUT))

    mapping = {
        "Title of the Project": PROJECT_TITLE,
        "Student Name": STUDENT_NAME,
        "Roll No: xxxxxxxxxxx": f"Roll No: {ROLL_NO}",
        "(Session: 20XX-20XX)": f"(Session: {SESSION})",
        "(Session: 2021-2022)": f"(Session: {SESSION})",
        "Name of HoD": HOD_NAME,
        "Faculty Name": SUPERVISOR_NAME,
        "<Project title>": PROJECT_TITLE,
        "<Project Title>": PROJECT_TITLE,
        "Project title": PROJECT_TITLE,
    }
    replace_in_paragraphs(doc, mapping)

    # Keywords only on the Abstract keywords line (not the Contents list entry)
    for p in doc.paragraphs:
        if p.text.strip().startswith("Keywords—") or p.text.strip().startswith("Keywords-"):
            new_kw = (
                "Keywords—land registry, marketplace, OCR, ULPIN, FastAPI, Spring Boot, React, "
                "document verification, ownership transfer"
            )
            if p.runs:
                p.runs[0].text = new_kw
                for r in p.runs[1:]:
                    r.text = ""
            else:
                p.add_run(new_kw)
        if "Abstract (Keywords—" in p.text:
            # Restore contents index line style from template intent
            if p.runs:
                p.runs[0].text = "Abstract (Keywords—land registry, marketplace, OCR, ULPIN, React, Spring Boot)"
                for r in p.runs[1:]:
                    r.text = ""

    # Fill Acknowledgement after its heading
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == "Acknowledgement":
            # Prefer next empty paragraph(s); otherwise insert body after heading via add later
            filled = False
            if i + 1 < len(doc.paragraphs) and not doc.paragraphs[i + 1].text.strip():
                target = doc.paragraphs[i + 1]
                if target.runs:
                    target.runs[0].text = ACKNOWLEDGEMENT
                    for r in target.runs[1:]:
                        r.text = ""
                    _set_run_font(target.runs[0], name="Calibri", size_pt=11)
                else:
                    r = target.add_run(ACKNOWLEDGEMENT)
                    _set_run_font(r, name="Calibri", size_pt=11)
                filled = True
            if not filled:
                # Append a dedicated acknowledgement block near end of front matter by body add
                pass
            break

    # Always also write a clean Acknowledgement section in the main body style before Introduction
    # (ensures the text exists even if template had no empty slot)
    # Insert by adding at end then we already add Introduction — so add ack just before section 1
    # Handled below: prepend acknowledgement heading+body before "1. Introduction" content by
    # writing it first in the appended body.
    ack_written_flag = True

    # Fill Abstract paragraph that follows "Abstract:"
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == "Abstract:":
            # Write abstract into following empty / short paragraphs if any; else append after
            abstract = (
                "Bhumi is an AI-assisted land registry and marketplace system designed to make "
                "buying and selling of land, houses and flats more transparent and verifiable. "
                "Sellers upload jamabandi or registry papers; a FastAPI document agent extracts "
                "structured fields such as ULPIN (Bhu-Aadhaar), khasra or survey number, khata, "
                "khewat, owner name and location. The Spring Boot backend matches these fields "
                "against seeded government land records and routes the case either to an "
                "AI-verified authenticator queue or to a physical verification queue. City "
                "authenticators (Patwari or Tehsildar style officers) approve listings for the "
                "public marketplace. After a buyer requests purchase and the seller confirms, "
                "the officer finalizes ownership transfer, updates the government owner record "
                "and issues a Certificate of Transfer of Ownership PDF. The system also supports "
                "location-aware Locate links from ULPIN decoding, role-based desks for admin and "
                "authenticator users, optional classroom SQLite/H2 persistence with demo Base64 "
                "password encoding, and virtual jamabandi generation on approval. This report "
                "presents the problem, architecture, methodology, implementation and results of "
                "the MCA fifth-semester project."
            )
            # Insert abstract as next body paragraph by editing next empty para if present
            if i + 1 < len(doc.paragraphs) and not doc.paragraphs[i + 1].text.strip():
                r = doc.paragraphs[i + 1].add_run(abstract) if not doc.paragraphs[i + 1].runs else None
                if doc.paragraphs[i + 1].runs:
                    doc.paragraphs[i + 1].runs[0].text = abstract
                    _set_run_font(doc.paragraphs[i + 1].runs[0], name="Calibri", size_pt=11)
                elif r:
                    _set_run_font(r, name="Calibri", size_pt=11)
            else:
                # Fall through: abstract will also appear in section content
                pass
            break

    # ---- Acknowledgement (formal page content) ----
    add_heading(doc, "Acknowledgement", 1)
    for para in ACKNOWLEDGEMENT.split("\n\n"):
        add_body(doc, para)

    # ---- Main report body (sections required by template) ----
    add_heading(doc, "1. Introduction", 1)

    add_heading(doc, "1.1 Introduction to the Problem", 2)
    add_body(
        doc,
        "Land records in India are maintained through jamabandi and related registry documents "
        "that mention identifiers such as khasra (or survey number in some states), khata, "
        "khewat, khatauni and, increasingly, ULPIN (Unique Land Parcel Identification Number / "
        "Bhu-Aadhaar). Citizens who wish to sell property often list assets on informal channels "
        "where buyers cannot easily verify whether the paper matches an authoritative record. "
        "Manual verification by local officers is essential, but it is slow when every paper must "
        "be typed and compared by hand. The problem addressed by this project is to build a "
        "practical web system that (a) accepts property listings with scanned or photographed "
        "registry papers, (b) extracts land identifiers automatically, (c) matches them to a "
        "government-style record store, and (d) involves a city authenticator before a listing "
        "becomes publicly searchable, followed by a controlled sale and ownership transfer flow.",
    )

    add_heading(doc, "1.2 Related Work and Motivation", 2)
    add_body(
        doc,
        "Related work includes digital land-record portals of various states, DigiLocker-style "
        "document wallets, and commercial property portals. Pure marketplace sites usually show "
        "photos and prices without binding registry verification. Pure government portals focus "
        "on citizen services rather than peer-to-peer sale workflows. Academic and industry OCR "
        "work on printed and handwritten Indic documents shows that form fields can be recovered "
        "from images, but end-to-end products still need role-based approval, notifications and "
        "legal-style transfer artefacts. Bhumi is motivated by combining these pieces: OCR or "
        "metadata-backed extraction, deterministic matching to khasra or ULPIN, city-scoped "
        "officer desks, and an auditable path from listing to transfer certificate.",
    )
    add_bullet(doc, "Buyers need confidence that the listed parcel matches a known record.")
    add_bullet(doc, "Officers need queues that separate AI-matched cases from physical visits.")
    add_bullet(doc, "Sellers need a clear track of status from post to sold.")
    add_bullet(doc, "Classroom demonstration needs runnable local services without cloud lock-in.")

    add_heading(doc, "1.3 Scope of the Project", 2)
    add_body(
        doc,
        "The implemented scope covers guest marketplace search, user signup and login, seller "
        "posting of SALE and REGISTRY listings with mandatory papers, FastAPI extraction of "
        "land fields, Spring Boot matching and notifications, authenticator and admin desks, "
        "purchase request, sale confirmation, transfer finalization with OpenPDF certificate, "
        "Locate links from ULPIN or fallback coordinates, optional virtual jamabandi on "
        "approval, and an optional sqlite profile for a local file database. Full nationwide "
        "cadastral YOLO training and production-grade password hashing for the classroom "
        "sqlite profile are acknowledged as out of scope for the demo configuration.",
    )

    add_heading(doc, "2. Project Overview", 1)

    add_heading(doc, "2.1 Problem Definition", 2)
    add_body(
        doc,
        "Given a seller who uploads registry paper images and a form describing a land, house "
        "or flat listing in a chosen city, the system must extract identifiers, compare them "
        "with government records, and decide whether an authenticator can treat the case as "
        "AI-verified or must perform physical verification. After approval, the listing must "
        "appear in public search. A buyer must be able to request purchase; after seller "
        "confirmation, the city authenticator must finalize transfer, update ownership and "
        "issue a certificate. Admins must approve authenticator applications for their state.",
    )

    add_heading(doc, "2.2 Contributions", 2)
    add_bullet(
        doc,
        "Designed and implemented a three-tier stack: React frontend, Spring Boot API, FastAPI AI extract service.",
    )
    add_bullet(
        doc,
        "Implemented ULPIN-first and khasra/survey matching with OCR noise hardening for handwritten demos.",
    )
    add_bullet(
        doc,
        "Built role-based workflows for USER, AUTHENTICATOR and ADMIN with city and state scoping.",
    )
    add_bullet(
        doc,
        "Delivered end-to-end sale-to-transfer flow with in-app, email and SMS notification stubs.",
    )
    add_bullet(
        doc,
        "Added Locate URL generation, physical verification report gate, virtual jamabandi and optional H2 file DB profile.",
    )

    add_heading(doc, "2.3 Outcomes", 2)
    add_body(
        doc,
        "A locally runnable demonstration where posting jamabandi for khasra 123/4 (or seeded "
        "ULPIN) routes to the Ballabgarh AI-verified queue; mismatched papers route to physical "
        "verification; officer approval publishes the listing; purchase and finalize produce a "
        "SOLD status, updated government owner name and a downloadable transfer certificate. "
        "Direct curl to /extract returns JSON fields for teacher evaluation of OCR quality.",
    )

    add_heading(doc, "3. System Model", 1)

    add_heading(doc, "3.1 Software Architecture", 2)
    add_body(
        doc,
        "Bhumi uses a modular client–server architecture. The browser loads the Vite React "
        "application. API calls under /api are proxied to Spring Boot on port 8090. When a "
        "seller uploads registry papers, the backend AiClient sends the first paper as "
        "multipart to the AI service on port 8000. MatchingService updates the PropertyListing "
        "status and aiSummary, then NotifyService alerts city authenticators. Persistence is "
        "abstracted behind AppStore: InMemoryAppStore is primary by default; JdbcAppStore is "
        "wired under the sqlite Spring profile to an H2 file database.",
    )

    add_heading(doc, "3.2 Platforms, Libraries and Tools", 2)
    add_bullet(doc, "Frontend: React 18, TypeScript, Vite 5, React Router 6.")
    add_bullet(doc, "Backend: Spring Boot 3.3, Java 21, Spring Security, JJWT, OpenPDF, Flyway, JDBC.")
    add_bullet(doc, "AI: FastAPI, Uvicorn, OpenCV, Pillow, optional Tesseract/TrOCR/PaddleOCR/YOLO (ultralytics).")
    add_bullet(doc, "Data demo: In-memory maps; optional H2 file at backend/data/bhumi-demo.mv.db.")
    add_bullet(doc, "Build/run: Maven, npm, Python venv.")

    add_heading(doc, "3.3 Hardware and Deployment Assumptions", 2)
    add_body(
        doc,
        "Development assumes a developer laptop (macOS or Linux) with JDK 21, Node 20+, and "
        "Python 3.9+. No cloud deployment is required for evaluation. Ports 5173 (UI), 8090 "
        "(API) and 8000 (AI) must be free. OCR models may download on first use; a BHUMI_OCR_ENGINE=labels "
        "mode is used for faster classroom demos with line-band OCR.",
    )

    add_heading(doc, "3.4 Roles in the System Model", 2)
    add_bullet(doc, "USER: signup, browse LIVE sales, post property, track, chat, purchase request, confirm sale.")
    add_bullet(doc, "AUTHENTICATOR: city-scoped queues, decide approve/reject, upload physical report when required, finalize transfer.")
    add_bullet(doc, "ADMIN: login-only seeded accounts; approve authenticator applications for one state/UT.")

    add_heading(doc, "4. Methodology", 1)

    add_heading(doc, "4.1 Proposed Method Overview", 2)
    add_body(
        doc,
        "The proposed method is a pipeline of document understanding, record matching and "
        "human-in-the-loop approval. Automation extracts and proposes a match; a city officer "
        "remains responsible for final publication and ownership change. This hybrid design "
        "reflects real land administration practice where AI assists but does not replace the Patwari.",
    )

    add_heading(doc, "4.2 Document Extraction Algorithm", 2)
    add_body(doc, "Algorithm ExtractFields(image):")
    add_bullet(doc, "Step 1: Load image bytes; if PNG contains bhumi_meta text chunk, parse JSON/META trailer and return high-confidence fields.")
    add_bullet(doc, "Step 2: Else preprocess (grayscale / binary variants).")
    add_bullet(doc, "Step 3: Optionally run YOLO field-block detection; else split into horizontal line bands.")
    add_bullet(doc, "Step 4: OCR each crop with Tesseract/TrOCR (or Paddle if enabled).")
    add_bullet(doc, "Step 5: Filter bleed-through noise lines; normalize ULPIN (OCR repairs + demo snap), khasra (multi-segment), khata, khewat.")
    add_bullet(doc, "Step 6: If ULPIN valid, decode Base-14/19/32 codec to latitude/longitude and build Locate URL.")
    add_bullet(doc, "Step 7: Return JSON with matchTier, parcelIdType, confidence and ocrLines for debugging.")

    add_heading(doc, "4.3 Government Matching Algorithm", 2)
    add_body(doc, "Algorithm MatchListing(listing, extraction):")
    add_bullet(doc, "Step 1: Apply extracted ULPIN/khasra/survey/khata fields onto the listing.")
    add_bullet(doc, "Step 2: Lookup government record by ULPIN, else khasra, else survey.")
    add_bullet(doc, "Step 3: If no record → status NEEDS_PHYSICAL_VERIFICATION.")
    add_bullet(doc, "Step 4: If record found and city/owner/identifiers align with sufficient confidence → AI_VERIFIED_AWAITING_AUTHENTICATOR.")
    add_bullet(doc, "Step 5: Else → NEEDS_PHYSICAL_VERIFICATION with sanitized summary (no confidence leak to end-user UI).")
    add_bullet(doc, "Step 6: For REGISTRY purpose, route to PENDING_REGISTRY without requiring AI match.")

    add_heading(doc, "4.4 Sale and Transfer Method", 2)
    add_bullet(doc, "Officer approves → LIVE (physical queue requires uploaded verification report).")
    add_bullet(doc, "On approve, generate virtual jamabandi PNG with bhumi_meta and upsert government reuse keys.")
    add_bullet(doc, "Buyer purchase-request → PURCHASE_REQUESTED.")
    add_bullet(doc, "Seller confirm-sale → PENDING_TRANSFER.")
    add_bullet(doc, "Officer finalize-transfer → update government owner, render OpenPDF certificate, status SOLD.")

    add_heading(doc, "5. Implementation", 1)

    add_heading(doc, "5.1 Repository Layout", 2)
    add_bullet(doc, "frontend/ — React UI (Shell, routes, marketplace, officer, admin, post, track).")
    add_bullet(doc, "backend/ — Spring Boot modules: auth, property, verification, certificate, notify, chat, store, location.")
    add_bullet(doc, "ai-service/ — FastAPI app, ocr.py, extract.py, ulpin_codec.py, scripts for sample jamabandis.")
    add_bullet(doc, "samples/ — printed and handwritten test images; WRITE_ON_PAPER.md for classroom sheets.")
    add_bullet(doc, "docs/ — this report, presentation and deep guide.")

    add_heading(doc, "5.2 Data Flow Description", 2)
    add_body(
        doc,
        "Figure-style flow (textual): Paper image → AI /extract JSON → PropertyService.create → "
        "MatchingService → AppStore.saveProperty → NotifyService → Authenticator desk → decision "
        "→ LIVE → purchase → confirm → finalize → TransferCertificate PDF. Public search only "
        "lists LIVE SALE properties. Admin and authenticator roles are redirected away from the "
        "marketplace homepage to their desks.",
    )

    add_heading(doc, "5.3 Entity Relationship (Logical)", 2)
    add_body(
        doc,
        "Core entities: UserAccount (role, state, district, city), GovernmentRecord (khasra PK, "
        "ulpin, survey, owner, measurements), PropertyListing (status, papers, photos, lat/lng, "
        "verificationReport, virtualJamabandi), AuthenticatorApplication, Notification, "
        "ChatMessage, TransferCertificate, AuditEvent, StateAdmin. Relationships: seller and "
        "buyer users reference listings; papers and photos are stored files on the listing; "
        "certificate links to property id; government records are keyed for match lookups.",
    )

    add_heading(doc, "5.4 Important API Groups", 2)
    add_bullet(doc, "Auth: /api/auth/register, /login, /authenticator-apply, /me")
    add_bullet(doc, "Public: /api/public/properties, /recommended, locations, photos")
    add_bullet(doc, "Seller: POST /api/properties, /mine, purchase/confirm endpoints")
    add_bullet(doc, "Authenticator: /api/authenticator/queues, decision, verification-report, finalize-transfer")
    add_bullet(doc, "AI: POST http://localhost:8000/extract")

    add_heading(doc, "5.5 Frontend Implementation Notes", 2)
    add_body(
        doc,
        "Routes enforce MarketplaceOnly for guests/users and Guard roles for desks. Session JWT "
        "is stored under localStorage key bhumi.session. PostPropertyPage accepts optional "
        "latitude/longitude and multi-segment khasra help text. OfficerPage disables approve on "
        "physical queue until a report file is uploaded. PropertyDetailPage shows a Locate link "
        "when locateUrl is present.",
    )

    add_heading(doc, "5.6 Government Record Storage", 2)
    add_body(
        doc,
        "Government records are application data, not a live state NIC API. SeedData inserts "
        "about one hundred records at first boot, including golden rows such as khasra 123/4 "
        "with ULPIN HR06A1B2C3D4E5 (Ramesh Kumar, Sihi, Ballabgarh). Default storage is "
        "InMemoryAppStore maps (governmentByKhasra, governmentByUlpin, governmentBySurvey). "
        "Under profile sqlite, the same logical rows live in table government_record inside "
        "backend/data/bhumi-demo.mv.db and can be inspected with the H2 console.",
    )

    add_heading(doc, "5.7 Security Implementation", 2)
    add_bullet(doc, "JWT bearer authentication via JwtAuthFilter.")
    add_bullet(doc, "Default PasswordEncoder: BCrypt; sqlite profile: Base64 encoder labeled demo-only.")
    add_bullet(doc, "Service-layer checks for city (authenticator) and state (admin).")
    add_bullet(doc, "AI confidence numbers are stripped from user-facing aiSummary text.")

    add_heading(doc, "6. Results and Discussion", 1)

    add_heading(doc, "6.1 Functional Outcomes", 2)
    add_bullet(doc, "Successful AI match path with seeded jamabandi / handwritten sheets for 123/4 and related ids.")
    add_bullet(doc, "Physical path for unknown khasra/ULPIN; approve blocked until verification report uploaded.")
    add_bullet(doc, "Marketplace search filters by type, state, district, city and price; recommended listings for logged-in users.")
    add_bullet(doc, "Transfer certificate PDF generated and downloadable after finalize.")
    add_bullet(doc, "curl /extract returns structured JSON including ocrLines for debugging handwriting OCR.")

    add_heading(doc, "6.2 Experimental Observations on OCR", 2)
    add_body(
        doc,
        "Printed sample PNGs with embedded bhumi_meta yield stable, high-quality extraction without "
        "heavy OCR. Handwritten phone photos produce noisy lines (character confusion such as O/0, "
        "I/1, and slash read as parenthesis). After parser hardening (ULPIN demo snap, khasra slash "
        "repair, bleed-line filtering), classroom sheets for seeded ULPINs recover expected "
        "identifiers more reliably. Confidence remains an internal AI metric; the UI emphasizes "
        "match tier and officer decision.",
    )

    add_heading(doc, "6.3 Discussion", 2)
    add_body(
        doc,
        "The hybrid AI-plus-officer model is appropriate for land workflows where legal "
        "responsibility cannot be fully automated. In-memory mode maximizes demo speed; the "
        "sqlite profile supports teacher inspection of tables. Limitations include OCR brittleness "
        "on poor lighting, incomplete nationwide location trees beyond demo scale, and the "
        "explicitly non-production Base64 password mode for classroom databases.",
    )

    add_heading(doc, "7. Conclusion and Future Work", 1)

    add_heading(doc, "7.1 Conclusion", 2)
    add_body(
        doc,
        "This project delivered Bhumi, a working AI-assisted land registry and marketplace that "
        "connects document extraction, government-record matching, authenticator approval and "
        "ownership transfer certification. The system demonstrates how modern web and ML tooling "
        "can support—but not replace—local land verification officers.",
    )

    add_heading(doc, "7.2 Future Work", 2)
    add_bullet(doc, "Train a larger YOLO detector on real jamabandi layouts across states.")
    add_bullet(
        doc,
        "Train the model on real stamp paper images to detect official seals, the national emblem "
        "and other security features, verifying that the document is printed on valid, genuine stamp paper.",
    )
    add_bullet(doc, "Integrate real SMS/email gateways and production password hashing.")
    add_bullet(doc, "Connect to live state land-record APIs where legally available.")
    add_bullet(doc, "Improve Devanagari handwriting recognition and mobile capture guidance.")
    add_bullet(doc, "Add richer audit dashboards and bilingual UI.")

    add_heading(doc, "8. Bibliography", 1)
    add_body(
        doc,
        "[1] Department of Land Resources, Government of India, Unique Land Parcel Identification Number (ULPIN) / Bhu-Aadhaar programme documentation.",
    )
    add_body(
        doc,
        "[2] Spring Boot Reference Documentation, Version 3.3, VMware / Broadcom.",
    )
    add_body(
        doc,
        "[3] FastAPI Documentation, Sebastián Ramírez et al.",
    )
    add_body(
        doc,
        "[4] React Documentation, Meta Open Source.",
    )
    add_body(
        doc,
        "[5] Smith, R., An Overview of the Tesseract OCR Engine, ICDAR, 2007.",
    )
    add_body(
        doc,
        "[6] Li, M. et al., TrOCR: Transformer-based Optical Character Recognition with Pre-trained Models, AAAI, 2023.",
    )
    add_body(
        doc,
        "[7] Jocher, G. et al., Ultralytics YOLOv8 Documentation.",
    )
    add_body(
        doc,
        "[8] OpenPDF Project Documentation (fork of iText for PDF generation).",
    )
    add_body(
        doc,
        "[9] H2 Database Engine Documentation (PostgreSQL compatibility mode).",
    )
    add_body(
        doc,
        "[10] National Institute of Technology Raipur, Department of Computer Applications, MCA Project Guidelines and Templates (MCA-V Semester).",
    )

    # Extra explanatory pages to approach the 30-page guideline with same styles
    add_heading(doc, "Appendix A. Module-wise Description", 1)
    add_heading(doc, "A.1 Authentication Module", 2)
    add_body(
        doc,
        "AuthService registers USER accounts, rejects ADMIN signup, and accepts authenticator "
        "applications that create inactive users until a state admin approves. Login returns JWT "
        "claims including role, city, district and state used by the frontend greeting and "
        "recommendation APIs.",
    )
    add_heading(doc, "A.2 Property Module", 2)
    add_body(
        doc,
        "PropertyService validates papers and photo counts for SALE listings, invokes matching, "
        "exposes public search and recommended listings, and implements purchase, confirm, "
        "officer decision, report upload and virtual jamabandi download endpoints.",
    )
    add_heading(doc, "A.3 AI Client Module", 2)
    add_body(
        doc,
        "AiClient builds a multipart HTTP request to the AI base URL and maps JSON into an "
        "ExtractionResult record including optional latitude, longitude and locateUrl.",
    )
    add_heading(doc, "A.4 Notification and Chat Modules", 2)
    add_body(
        doc,
        "NotifyService writes IN_APP rows and logs EMAIL/SMS to the console for demos. ChatService "
        "allows buyer–seller messaging on live or in-progress deals and blocks phone-number style "
        "off-platform contact patterns in a simple filter.",
    )

    add_heading(doc, "Appendix B. How to Run for Evaluation", 1)
    add_body(doc, "AI service:")
    add_bullet(doc, "cd ai-service && source .venv/bin/activate && export BHUMI_OCR_ENGINE=labels")
    add_bullet(doc, "python -m uvicorn src.app:app --host 127.0.0.1 --port 8000")
    add_body(doc, "Backend:")
    add_bullet(doc, "cd backend && mvn spring-boot:run")
    add_bullet(doc, "Optional DB: mvn spring-boot:run -Dspring-boot.run.profiles=sqlite")
    add_body(doc, "Frontend:")
    add_bullet(doc, "cd frontend && npm install && npm run dev")
    add_body(doc, "Extract JSON from a handwritten photo:")
    add_bullet(
        doc,
        'curl -s -F "file=@samples/handwritten/manual_tests/1.jpg" http://127.0.0.1:8000/extract | ai-service/.venv/bin/python -m json.tool',
    )

    add_heading(doc, "Appendix C. Demo Accounts", 1)
    add_bullet(doc, "User: user@bhumi.test / User@123")
    add_bullet(doc, "Authenticator (Ballabgarh): auth.ballabgarh@bhumi.gov.in / Auth@123")
    add_bullet(doc, "State admin (Haryana): HR12345RH@bhumi.gov.in / AdminHR123@")

    add_heading(doc, "Appendix D. Status Dictionary", 1)
    add_bullet(doc, "PENDING_AI — brief initial status before matching completes in create().")
    add_bullet(doc, "AI_VERIFIED_AWAITING_AUTHENTICATOR — strong match; officer final approval.")
    add_bullet(doc, "NEEDS_PHYSICAL_VERIFICATION — weak/no match; report required before approve.")
    add_bullet(doc, "PENDING_REGISTRY — registry-only purpose.")
    add_bullet(doc, "LIVE — visible on marketplace.")
    add_bullet(doc, "PURCHASE_REQUESTED / PENDING_TRANSFER / SOLD / REJECTED — sale lifecycle.")

    doc.save(str(REPORT_OUT))
    print("Wrote", REPORT_OUT)


def _clear_and_bullets(shape, lines):
    tf = shape.text_frame
    # Keep existing paragraph formatting as much as possible
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.level = 0
    # Remove leftover paragraphs if template had more
    # (python-pptx cannot easily delete; overwrite extras with empty)
    extras = len(tf.paragraphs) - len(lines)
    # If fewer lines than existing, blank the rest
    if len(lines) < len(tf.paragraphs):
        for p in tf.paragraphs[len(lines) :]:
            p.text = ""


def _content_shape(slide):
    for shape in slide.shapes:
        if shape.has_text_frame and shape != slide.shapes.title:
            # Prefer placeholder idx 1
            if hasattr(shape, "is_placeholder") and shape.is_placeholder:
                if shape.placeholder_format.idx == 1:
                    return shape
    for shape in slide.shapes:
        if shape.has_text_frame and shape != slide.shapes.title:
            return shape
    return None


def _add_content_slide(prs, title, bullets, after_index=None):
    layout = prs.slide_layouts[1]  # Title and Content — same as template body slides
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = title
    body = _content_shape(slide)
    if body is not None:
        _clear_and_bullets(body, bullets)
    return slide


def build_ppt():
    shutil.copyfile(PPT_TEMPLATE, PPT_OUT)
    prs = Presentation(str(PPT_OUT))

    # Slide 1 — title
    s0 = prs.slides[0]
    s0.shapes.title.text = PROJECT_TITLE
    # subtitle placeholder
    for shape in s0.shapes:
        if shape.has_text_frame and shape != s0.shapes.title:
            if "Presented by" in shape.text_frame.text or shape.is_placeholder:
                lines = [
                    "Presented by",
                    STUDENT_NAME,
                    f"Roll No: {ROLL_NO}",
                    "MCA- V Semester",
                    f"(Session: {SESSION})",
                ]
                _clear_and_bullets(shape, lines)
                break
    # supervisor text box
    for shape in s0.shapes:
        if shape.has_text_frame and "Supervisor" in shape.text_frame.text:
            _clear_and_bullets(
                shape,
                [
                    SUPERVISOR_NAME,
                    "Supervisor",
                    "Department of Computer Applications",
                    "National Institute of Technology Raipur",
                ],
            )

    # Slide 2 sequence — keep instructional list from template (already correct)
    # Slide 3 contents — already correct structure

    # Slide 4 Declaration
    body = _content_shape(prs.slides[3])
    if body:
        _clear_and_bullets(
            body,
            [
                f"I hereby declare that the project “{PROJECT_TITLE}” is submitted in partial fulfillment for the award of the degree of Master of Computer Applications, MCA-V Semester, NIT Raipur.",
                "The work is original to the best of my knowledge and has not been submitted elsewhere for any degree or diploma.",
                f"Place: Raipur",
                f"Student: {STUDENT_NAME}",
                f"Roll No: {ROLL_NO}",
                f"Session: {SESSION}",
            ],
        )

    # Slide 5 Problem
    body = _content_shape(prs.slides[4])
    if body:
        _clear_and_bullets(
            body,
            [
                "Problem: Property listings rarely verify jamabandi papers against government land identifiers.",
                "Buyers cannot easily trust khasra / ULPIN claims on informal marketplaces.",
                "Officers need structured queues separating AI-matched cases from physical visits.",
                "Definition: Build a web system that extracts land fields from papers, matches government records, publishes only after city authenticator approval, and completes sale-to-transfer with a certificate.",
            ],
        )

    # Slide 6 Motivation
    body = _content_shape(prs.slides[5])
    if body:
        _clear_and_bullets(
            body,
            [
                "Need for transparent land transactions with verifiable registry papers.",
                "ULPIN / Bhu-Aadhaar adoption makes machine-readable parcel ids practical.",
                "OCR and form parsing can reduce typing effort for officers and sellers.",
                "Classroom-friendly local stack (React + Spring Boot + FastAPI) for end-to-end demos.",
            ],
        )

    # Slide 7 Contributions
    body = _content_shape(prs.slides[6])
    if body:
        _clear_and_bullets(
            body,
            [
                "Three-service architecture with JWT roles: USER, AUTHENTICATOR, ADMIN.",
                "AI extract JSON: ULPIN, khasra/survey, khata, khewat, owner, Locate lat/lng.",
                "MatchingService routes AI-verified vs physical verification vs registry.",
                "Sale flow: request → confirm → finalize → government owner update + PDF certificate.",
                "Extras: Locate link, recommended listings, virtual jamabandi, optional sqlite DB profile.",
            ],
        )

    # Slide 8 Methodology
    body = _content_shape(prs.slides[7])
    if body:
        _clear_and_bullets(
            body,
            [
                "Hybrid method: automate extraction/matching; human officer gives final approval.",
                "Extract: PNG bhumi_meta short-circuit OR preprocess → OCR → field normalize.",
                "ULPIN codec: Base-14 / Base-19-long / Base-32 with I→Y, O→Z substitutions.",
                "Match order: ULPIN → khasra → survey against AppStore government indexes.",
                "Physical queue: verification report required before approve.",
            ],
        )

    # Slide 9 Methodology cont
    body = _content_shape(prs.slides[8])
    if body:
        _clear_and_bullets(
            body,
            [
                "Status path: PENDING_AI → AI_VERIFIED… or NEEDS_PHYSICAL… → LIVE / REJECTED.",
                "Then PURCHASE_REQUESTED → PENDING_TRANSFER → SOLD.",
                "Notifications: IN_APP + console EMAIL/SMS stubs for demo.",
                "Security: JWT filter; BCrypt default; Base64 only for sqlite classroom profile.",
                "OCR hardening: repair slash/parenthesis noise; snap near-miss demo ULPINs.",
            ],
        )

    # Slide 10 Architecture
    body = _content_shape(prs.slides[9])
    if body:
        _clear_and_bullets(
            body,
            [
                "Frontend (5173): React marketplace, desks, track, chat.",
                "Backend (8090): PropertyService, MatchingService, CertificateService, NotifyService.",
                "AI (8000): FastAPI POST /extract → JSON fields + ocrLines.",
                "Store: InMemoryAppStore (default) or JdbcAppStore + H2 file (sqlite profile).",
                "Government records: SeedData → maps or government_record table.",
            ],
        )

    # Slide 11 Results
    body = _content_shape(prs.slides[10])
    if body:
        _clear_and_bullets(
            body,
            [
                "Simulation setup: local AI + backend + frontend; demo accounts from README.",
                "Seeded paper/khasra 123/4 → AI verified queue for Ballabgarh officer.",
                "Unknown ids → physical queue; report gate before approve.",
                "Finalize transfer → SOLD, owner updated, certificate downloadable.",
                "Handwritten /extract demos return structured JSON for evaluation.",
            ],
        )

    # Slide 12 Conclusion
    body = _content_shape(prs.slides[11])
    if body:
        _clear_and_bullets(
            body,
            [
                "Conclusion: Bhumi demonstrates AI-assisted verification with officer accountability.",
                "Future: larger YOLO training, live land APIs, production messaging and hashing.",
                "Future: stronger Indic handwriting OCR and bilingual UI.",
            ],
        )

    # Slide 13 References
    body = _content_shape(prs.slides[12])
    if body:
        _clear_and_bullets(
            body,
            [
                "[1] DoLR, Government of India — ULPIN / Bhu-Aadhaar documentation.",
                "[2] Spring Boot 3.3 Reference Documentation.",
                "[3] FastAPI Documentation.",
                "[4] React Documentation.",
                "[5] Tesseract OCR; TrOCR; Ultralytics YOLOv8 docs.",
                "[6] NIT Raipur MCA-V Project Templates and Guidelines.",
            ],
        )

    # Add continuation slides then reorder: Title…Results Cont…, Conclusion, References, Thank You
    _add_content_slide(
        prs,
        "Design/ Architecture/ Workflow Cont..",
        [
            "Workflow: Post papers → extract → match → officer → LIVE → buy → confirm → finalize.",
            "DFD-style: External users ↔ Frontend ↔ Backend ↔ AI; Backend ↔ Government store.",
            "ER-style: User, PropertyListing, GovernmentRecord, Certificate, Notification.",
            "Government records: SeedData into InMemory maps or government_record (sqlite/H2 file).",
        ],
    )
    _add_content_slide(
        prs,
        "Results and Discussion Cont..",
        [
            "Observation: printed bhumi_meta samples are most reliable for demos.",
            "Observation: handwriting needs clear block letters; parsers mitigate OCR noise.",
            "Limitation: demo DB/passwords are for classroom inspection, not production security.",
        ],
    )
    _add_content_slide(
        prs,
        "Methodology/ Proposed Algorithm Cont..",
        [
            "Algorithm MatchListing: apply AI fields → lookup gov → set queue status.",
            "Algorithm FinalizeTransfer: update owner → OpenPDF certificate → SOLD.",
            "Locate: decode ULPIN else form lat/lng else city centroid → Google Maps URL.",
        ],
    )

    # Reorder slides to follow template sequence (Cont slides before Conclusion)
    desired_titles = [
        PROJECT_TITLE,
        "Sequence of slides to be followed",
        "Contents:",
        "Declaration",
        "Problem Formulation and Definition",
        "Motivation",
        "Contributions",
        "Methodology/ Proposed Algorithm",
        "Methodology/ Proposed Algorithm",  # existing Cont slide from template
        "Methodology/ Proposed Algorithm Cont..",  # added
        "Design/ Architecture/ Workflow",
        "Design/ Architecture/ Workflow Cont..",
        "Results and Discussion",
        "Results and Discussion Cont..",
        "Conclusion and Future scope",
        "References",
        "Thank You!",
    ]

    def _norm(t: str) -> str:
        return " ".join((t or "").replace("\x0b", " ").split()).strip().lower()

    sldIdLst = prs.slides._sldIdLst
    id_nodes = list(sldIdLst)
    slides = list(prs.slides)
    # Map normalized title -> sldId element (first unused match)
    pairs = []
    for sid, slide in zip(id_nodes, slides):
        title = slide.shapes.title.text if slide.shapes.title else ""
        pairs.append((_norm(title), sid, title))

    used = set()
    new_order = []
    for want in desired_titles:
        wn = _norm(want)
        found = None
        for i, (tn, sid, raw) in enumerate(pairs):
            if i in used:
                continue
            if tn.startswith(wn) or wn.startswith(tn) or wn in tn or tn in wn:
                found = i
                break
        if found is None:
            continue
        used.add(found)
        new_order.append(pairs[found][1])
    # Append any unused (should be none)
    for i, (_, sid, _) in enumerate(pairs):
        if i not in used:
            new_order.append(sid)

    for sid in list(sldIdLst):
        sldIdLst.remove(sid)
    for sid in new_order:
        sldIdLst.append(sid)

    prs.save(str(PPT_OUT))
    print("Wrote", PPT_OUT)


def main():
    build_report()
    build_ppt()


if __name__ == "__main__":
    main()
