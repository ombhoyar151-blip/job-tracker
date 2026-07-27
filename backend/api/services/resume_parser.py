from pathlib import Path

import PyPDF2
import docx


def extract_text_from_pdf(file_path: str | Path) -> str:
    text_parts = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_path: str | Path) -> str:
    doc = docx.Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(file_path: str | Path, file_type: str) -> str:
    if file_type == "application/pdf":
        return extract_text_from_pdf(file_path)
    elif file_type in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
