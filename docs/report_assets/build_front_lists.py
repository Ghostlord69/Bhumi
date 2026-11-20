"""Build a copy-paste source for Contents, List of Tables and List of Figures with dot-leader tabs."""
from pathlib import Path

import docx
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.shared import Inches, Pt

OUT = Path(__file__).resolve().parents[1] / "Bhumi_Contents_Tables_Figures.docx"
TAB_POS = Inches(6.88)

CONTENTS = [
    ("Acknowledgement", 4, 0), ("List of Tables", 6, 0), ("List of Figures", 7, 0), ("Abstract", 8, 0),
    ("1. Introduction", 9, 0), ("1.1 Introduction to the Problem", 9, 1),
    ("1.2 Related Work and Motivation", 9, 1), ("1.3 Scope of the Project", 9, 1),
    ("2. Project Overview", 10, 0), ("2.1 Problem Definition", 10, 1), ("2.2 Objective", 10, 1),
    ("2.3 Scope and Assumptions", 10, 1), ("2.4 Outcome", 10, 1),
    ("3. System Model", 11, 0), ("3.1 Software Architecture", 11, 1),
    ("4. Methodology", 14, 0), ("4.1 Proposed Method Overview", 14, 1), ("4.2 Modules of the System", 14, 1),
    ("4.3 Document Extraction Algorithm", 15, 1), ("4.4 ULPIN Decoding and Locate", 15, 1),
    ("4.5 Government Matching Algorithm", 15, 1), ("4.6 Sale and Transfer Method", 17, 1),
    ("5. Implementation", 18, 0), ("5.1 Repository Layout", 18, 1), ("5.2 Data Flow Description", 19, 1),
    ("5.3 Entity Relationship", 19, 1), ("5.4 Important API Groups", 20, 1),
    ("5.5 Frontend Implementation Notes", 21, 1), ("5.6 Government Record Storage", 24, 1),
    ("5.7 Security Implementation", 25, 1),
    ("6. Results and Discussion", 25, 0), ("6.1 Functional Outcomes", 25, 1),
    ("6.2 Experimental Observations on OCR", 26, 1), ("6.3 Discussion", 26, 1),
    ("7. Conclusion and Future Work", 27, 0), ("7.1 Conclusion", 27, 1), ("7.2 Future Work", 27, 1),
    ("8. Bibliography", 28, 0),
]

TABLES = [
    ("Table 3.1: Architecture layers at a glance", 12),
    ("Table 3.2: Layer-wise components and their functions", 12),
    ("Table 3.3: End-to-end control flow", 13),
    ("Table 3.4: Actors and their access to system layers", 13),
    ("Table 4.1: Fields returned by the /extract endpoint", 15),
    ("Table 4.2: Status transitions in the sale and transfer method", 17),
    ("Table 5.1: Repository layout and responsibility of each module", 18),
    ("Table 5.2: REST API groups, access level and purpose", 20),
    ("Table 5.3: Frontend routes and role guards", 21),
    ("Table 5.4: Structure of the government_record table", 24),
    ("Table 5.5: Storage modes for government records", 24),
]

FIGURES = [
    ("Figure 3.1: Layered system architecture of Bhumi", 11),
    ("Figure 4.1: Proposed method overview: automated stages and human-in-the-loop", 14),
    ("Figure 4.2: Module interaction sequence for posting and verifying a listing", 14),
    ("Figure 4.3: ULPIN encode, decode and Locate path", 15),
    ("Figure 4.4: Government matching decision flowchart", 16),
    ("Figure 5.1: Level-1 Data Flow Diagram of Bhumi", 19),
    ("Figure 5.2: Entity Relationship Diagram of the Bhumi schema (Flyway V1-V4)", 19),
    ("Figure 5.3: Public home page with search and verified listings", 22),
    ("Figure 5.4: Seller's \"List your property\" form", 23),
    ("Figure 5.5: Authenticator desk with verification and transfer queues", 23),
    ("Figure 6.1: Listing and transfer outcomes (A) and OCR behaviour on input papers (B)", 27),
]


def heading(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(16)


def entry(doc, text, page, level=0, bold=False):
    p = doc.add_paragraph()
    fmt = p.paragraph_format
    fmt.tab_stops.add_tab_stop(TAB_POS, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    fmt.left_indent = Inches(0.3 * level)
    fmt.space_after = Pt(4)
    fmt.line_spacing = 1.15
    r = p.add_run(text)
    r.bold = bold
    p.add_run(f"\t{page}").bold = bold


def main():
    doc = docx.Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.268), Inches(11.693)
    sec.left_margin = sec.right_margin = Inches(0.669)
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(12)

    heading(doc, "TABLE OF CONTENTS")
    for text, page, level in CONTENTS:
        entry(doc, text, page, level, bold=level == 0)

    for title, rows in (("LIST OF TABLES", TABLES), ("LIST OF FIGURES", FIGURES)):
        doc.add_section(WD_SECTION.NEW_PAGE)
        heading(doc, title)
        for text, page in rows:
            entry(doc, text, page)

    doc.save(OUT)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
