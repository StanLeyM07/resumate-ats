"""
file_parser.py — Utility to extract raw text from uploaded files (PDF, DOCX).

=== JUST-IN-TIME LEARNING ===

WHY EXTRACT TEXT FIRST?
    LLMs (like Gemini Flash) are great at reading text. While Gemini CAN process
    raw PDF files directly via the File API, it's often faster, cheaper, and 
    more reliable for structured data extraction to just extract the raw text 
    first using lightweight Python libraries, then send that text to the LLM.

LIBRARIES USED:
    - pypdf: A pure-Python PDF library. Great for extracting text from digital PDFs.
             (Note: It doesn't do OCR. If someone uploads a scanned image PDF,
             it won't read the text. For a portfolio project, this limitation is fine,
             but worth mentioning in an interview!)
    - python-docx: Parses Microsoft Word (.docx) files natively by unzipping the
                   XML structure inside the docx file.
"""

import io
from pypdf import PdfReader
from docx import Document

"""
=============================================================================
LEARNING MODULE: Unstructured Data Extraction
=============================================================================
This file handles extracting raw text from various document formats so the LLM
can read them. LLMs cannot read raw binary files like PDFs directly; they need
plain text strings.

Key Concepts Used Here:
1. `pypdf`: A pure-Python library for reading PDF files. It extracts text 
   page-by-page.
2. `python-docx`: Parses Microsoft Word XML structures to extract paragraph text.
3. In-Memory Processing: We use `io.BytesIO` to read files directly from 
   memory (RAM) instead of saving them to the hard drive first. This makes
   the API much faster and safer.
=============================================================================
"""

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Takes raw file bytes and a filename, determines the type,
    and returns the extracted raw text.
    """
    extension = filename.lower().split('.')[-1]
    
    if extension == 'pdf':
        return _extract_from_pdf(file_bytes)
    elif extension in ['docx', 'doc']:
        return _extract_from_docx(file_bytes)
    elif extension in ['txt', 'md', 'csv']:
        # It's already plain text, just decode it
        return file_bytes.decode('utf-8', errors='replace')
    else:
        raise ValueError(f"Unsupported file type: .{extension}. Please upload PDF, DOCX, or TXT.")

def _extract_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from all pages of a PDF."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text.append(extracted)
        
        full_text = "\n".join(text).strip()
        if not full_text:
            raise ValueError("No text found in PDF. It might be a scanned image.")
        return full_text
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")

def _extract_from_docx(file_bytes: bytes) -> str:
    """Extracts text from all paragraphs and tables in a DOCX file."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = []
        
        # Extract paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
                
        # Extract tables (often used in invoices/contracts)
        for table in doc.tables:
            for row in table.rows:
                row_data = [cell.text.strip().replace('\n', ' ') for cell in row.cells if cell.text.strip()]
                if row_data:
                    text.append(" | ".join(row_data))
                    
        return "\n".join(text).strip()
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {str(e)}")
