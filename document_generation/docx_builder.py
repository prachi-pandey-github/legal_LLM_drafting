# document_generation/docx_builder.py
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import tempfile
import os

class DocxBuilder:
    def __init__(self):
        self.doc = Document()
        
    def add_title(self, title):
        heading = self.doc.add_heading(title, level=0)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    def add_heading(self, text, level=1):
        self.doc.add_heading(text, level=level)
        
    def add_paragraph(self, text, bold=False, italic=False):
        p = self.doc.add_paragraph(text)
        if bold:
            p.runs[0].bold = True
        if italic:
            p.runs[0].italic = True
            
    def add_clause(self, clause_title, clause_body):
        self.add_heading(clause_title, level=2)
        self.add_paragraph(clause_body)
        
    def add_signature_block(self, party_name, role):
        self.add_paragraph(f"________________________")
        self.add_paragraph(f"{party_name}")
        self.add_paragraph(f"({role})")
        
    def save_to_temp(self, filename="legal_document.docx"):
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        self.doc.save(filepath)
        return filepath