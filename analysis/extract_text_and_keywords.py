import os
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import re

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "downloaded_pdfs", "p.1183.pdf")  # Change to p.1189.pdf as needed
OUTPUT_TXT = os.path.join(PROJECT_ROOT, "data", "processed", "p.1183_extracted.txt")

# Keywords for context extraction
KEYWORDS = [
    "постановление",
    "распоряжение",
    "имущество",
    "бесхозяйное имущество",
    "муниципальная собственность",
    "признать бесхозяйным",
    "реестр бесхозяйного имущества",
    "изъятие",
    "снос",
    "ремонт",
    "восстановление",
    "адрес",
    "кадастровый номер",
    "жилой фонд",
    "компенсационное жилье",
    "программа",
    "собственность"
]

# Extraction function with OCR fallback
def extract_text(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text
    except Exception:
        pass
    # OCR fallback
    try:
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img, lang="rus") + "\n"
    except Exception as e:
        print(f"OCR failed for {pdf_path}: {e}")
    return text

def keyword_context(text, keywords, window=80):
    results = []
    for kw in keywords:
        for m in re.finditer(kw, text, re.IGNORECASE):
            start = max(0, m.start() - window)
            end = min(len(text), m.end() + window)
            snippet = text[start:end].replace('\n', ' ')
            results.append((kw, snippet))
    return results

def main():
    text = extract_text(PDF_PATH)
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Full text saved to {OUTPUT_TXT}")
    print("\n--- Keyword Contexts ---")
    results = keyword_context(text, KEYWORDS)
    for kw, snippet in results:
        print(f"[{kw}] ...{snippet}...")
    print(f"\nTotal keyword hits: {len(results)}")

if __name__ == "__main__":
    main()
