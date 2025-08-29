import os
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from config import PROJECT_ROOT

KEYWORDS = [
    "о сносе",
    "бесхозяйного",
    "снос",
    "снести",
    "муниципальная собственность",
    "признать бесхозяйным",
    "реестр бесхозяйного имущества",
    "изъятие",
    "передать в собственность",
    "объект недвижимости",
    "акт осмотра",
    "постановление",
    "распоряжение",
    "имущество"
]

DOWNLOAD_DIR = f"{PROJECT_ROOT}/data/raw/downloaded_pdfs"

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

def search_keywords(text, keywords):
    found = []
    for kw in keywords:
        if kw.lower() in text.lower():
            found.append(kw)
    return found

def main():
    pdf_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith('.pdf')]
    results = {}
    for fname in pdf_files:
        path = os.path.join(DOWNLOAD_DIR, fname)
        print(f"\n--- Analyzing {fname} ---")
        text = extract_text(path)
        found = search_keywords(text, KEYWORDS)
        if found:
            results[fname] = found
            print(f"Keywords found: {', '.join(found)}")
        else:
            print("No keywords found.")
        # Optionally, print a preview
        print("Preview:")
        print(text[:1000])
        print("--- End Preview ---")
    print(f"\nTotal relevant documents: {len(results)}\n")
    for fname, kws in results.items():
        print(f"{fname}: {', '.join(kws)}")

if __name__ == "__main__":
    main()
