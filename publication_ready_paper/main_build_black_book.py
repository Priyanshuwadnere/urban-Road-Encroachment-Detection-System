import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Import modular builders
from publication_ready_paper.dissertation_prelims import build_preliminary_pages
from publication_ready_paper.dissertation_ch1_ch2 import build_chapter_1, build_chapter_2
from publication_ready_paper.dissertation_ch3 import build_chapter_3
from publication_ready_paper.dissertation_ch4 import build_chapter_4
from publication_ready_paper.dissertation_ch5_ch6 import build_chapter_5_and_6

def set_page_number_field(run):
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

def main():
    print("Initializing Capstone Black Book Document Assembly...")
    doc = Document()
    
    # ---------------------------------------------------------
    # 1. Page Margins Setup (Template Page 20 Rules)
    # Left = 1.5 inches, Others = 1.0 inch
    # ---------------------------------------------------------
    section = doc.sections[0]
    section.left_margin = Inches(1.5)
    section.right_margin = Inches(1.0)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)

    # ---------------------------------------------------------
    # 2. Build Preliminary Pages (Roman Numbering)
    # ---------------------------------------------------------
    build_preliminary_pages(doc)

    # ---------------------------------------------------------
    # 3. New Section for Chapters (Arabic Numbering & Running Headers)
    # ---------------------------------------------------------
    ch_section = doc.add_section()
    ch_section.left_margin = Inches(1.5)
    ch_section.right_margin = Inches(1.0)
    ch_section.top_margin = Inches(1.0)
    ch_section.bottom_margin = Inches(1.0)

    # Configure Running Header (Left: Project Title, Right: Academic Year)
    ch_section.header.is_linked_to_previous = False
    p_hdr = ch_section.header.paragraphs[0]
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr_l = p_hdr.add_run("Urban Road Encroachment Detection Using Computer Vision and GIS")
    r_hdr_l.font.name = "Times New Roman"
    r_hdr_l.font.size = Pt(8.5)
    r_hdr_l.font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)
    
    r_hdr_tab = p_hdr.add_run("\t\tAcademic Year: 2026–2027")
    r_hdr_tab.font.name = "Times New Roman"
    r_hdr_tab.font.size = Pt(8.5)
    r_hdr_tab.font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)

    # Configure Running Footer (Right: Page Number)
    ch_section.footer.is_linked_to_previous = False
    p_ftr = ch_section.footer.paragraphs[0]
    p_ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_ftr = p_ftr.add_run("Page ")
    r_ftr.font.name = "Times New Roman"
    r_ftr.font.size = Pt(9.5)
    set_page_number_field(r_ftr)

    # ---------------------------------------------------------
    # 4. Build Chapters 1 to 6, References, Appendices
    # ---------------------------------------------------------
    figures_dir = r"E:\Urban Road Encroachment Detection System\publication_ready_paper\figures"

    print("Assembling Chapter 1...")
    build_chapter_1(doc)

    print("Assembling Chapter 2...")
    build_chapter_2(doc)

    print("Assembling Chapter 3...")
    build_chapter_3(doc, figures_dir)

    print("Assembling Chapter 4...")
    build_chapter_4(doc, figures_dir)

    print("Assembling Chapters 5, 6, References, and Appendices...")
    build_chapter_5_and_6(doc)

    # ---------------------------------------------------------
    # 5. Save Document
    # ---------------------------------------------------------
    out_docx = r"E:\Urban Road Encroachment Detection System\Urban_Road_Encroachment_Detection_Black_Book.docx"
    doc.save(out_docx)
    print(f"\nSUCCESS! Generated Academic Capstone Black Book:\n{out_docx}")

if __name__ == "__main__":
    main()
