#!/usr/bin/env python3
from docx import Document
import sys

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    full_text = []
    
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    
    return '\n'.join(full_text)

if __name__ == "__main__":
    docx_path = "/home/ubuntu/upload/Especificacao_Site_Chamado_Manus.docx"
    text = extract_text_from_docx(docx_path)
    print(text)

