# This file contains functions for extracting text from PDF documents. It includes the function get_pdf_text which reads PDF files and extracts their text content.

from PyPDF2 import PdfReader

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text