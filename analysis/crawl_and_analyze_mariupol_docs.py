import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm
from datetime import datetime
from config import PROJECT_ROOT

DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "downloaded_pdfs")
BASE_URL = "https://mariupol-r897.gosweb.gosuslugi.ru/ofitsialno/dokumenty/"
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
START_DATE = datetime(2022, 5, 1)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_pdf_links(base_url):
    print("Crawling for PDF links...")
    resp = requests.get(base_url, timeout=20)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            full_url = urljoin(base_url, href)
            links.append(full_url)
    print(f"Found {len(links)} PDF links on the page.")
    return links

def filter_by_date(links):
    filtered = []
    for url in links:
        # Try to extract date from filename: look for dd.mm.yyyy or yyyy-mm-dd
        fname = os.path.basename(url)
        date_match = re.search(r'(\d{2}[.\-]\d{2}[.\-]\d{4})', fname)
        if date_match:
            try:
                date_str = date_match.group(1).replace('-', '.')
                file_date = datetime.strptime(date_str, "%d.%m.%Y")
                if file_date >= START_DATE:
                    filtered.append(url)
            except Exception:
                continue
        else:
            # If no date, keep it for manual review
            filtered.append(url)
    print(f"{len(filtered)} PDFs after filtering by date >= May 2022.")
    return filtered

def download_pdf(url, dest_dir):
    fname = os.path.join(dest_dir, os.path.basename(url))
    if not os.path.exists(fname):
        r = requests.get(url, stream=True, timeout=60)
        with open(fname, "wb") as f:
            for chunk in r.iter_content(1024*1024):
                f.write(chunk)
    return fname

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
    # If no text found, fallback to OCR
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
    links = get_pdf_links(BASE_URL)
    links = filter_by_date(links)
    results = {}
for url in tqdm(links, desc="Processing PDFs"):
    pdf_path = download_pdf(url, DOWNLOAD_DIR)
    text = extract_text(pdf_path)
    found = search_keywords(text, KEYWORDS)
    if found:
        if pdf_path in results:
            results[pdf_path].update(found)
        else:
            results[pdf_path] = set(found)
    print(f"\nTotal relevant documents: {len(results)}\n")
for path, kws in results.items():
    print(f"{os.path.basename(path)}: {', '.join(kws)}")

if __name__ == "__main__":
    main()
