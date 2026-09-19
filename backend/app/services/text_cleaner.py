import re
import unicodedata


def clean_extracted_text(raw_text: str) -> str:
    """
    Sanitizes raw text extracted from PDF or DOCX documents:
    - Normalizes Unicode characters and common ligature bullets (e.g., \uf0b7, \u2022)
    - Replaces non-breaking spaces with standard spaces
    - Collapses excessive horizontal whitespace (tabs, multiple spaces)
    - Standardizes consecutive newlines while preserving structural paragraph breaks
    - Strips leading and trailing whitespace
    """
    if not raw_text:
        return ""

    # 1. Normalize Unicode (NFKC handles characters, accents, ligatures)
    text = unicodedata.normalize("NFKC", raw_text)

    # 2. Replace common non-standard bullet symbols with standard bullet '-'
    bullet_patterns = r'[\uf0b7\uf0a7\u2022\u2023\u25e6\u2043\u2219▪►●•*]'
    text = re.sub(bullet_patterns, '\n- ', text)

    # 3. Replace non-breaking spaces, form feeds, and carriage returns
    text = text.replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')

    # 4. Remove unprintable control characters except newline and tab
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # 5. Collapse multiple horizontal spaces and tabs into a single space per line
    lines = []
    for line in text.split('\n'):
        clean_line = re.sub(r'[ \t]+', ' ', line).strip()
        lines.append(clean_line)

    # 6. Collapse 3 or more consecutive empty lines into a maximum of 2 newlines (paragraph boundary)
    text = '\n'.join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def estimate_word_count(text: str) -> int:
    """Returns approximate word count of clean text"""
    if not text:
        return 0
    return len(text.split())
