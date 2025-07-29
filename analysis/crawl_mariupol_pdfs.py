import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import csv
import json
import time
import os

BASE_URL = "https://mariupol-r897.gosweb.gosuslugi.ru/ofitsialno/dokumenty/"
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "mariupol_pdf_links.json")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "mariupol_pdf_links.csv")
VISITED = set()
PDFS = []
MAX_DEPTH = 6
SLEEP = 0.7

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ru,en-US;q=0.9,en;q=0.8",
    "Referer": "https://mariupol-r897.gosweb.gosuslugi.ru/",
    "Connection": "keep-alive",
}

def crawl(url, session, depth=0, parent=None):
    if url in VISITED or depth > MAX_DEPTH:
        return
    VISITED.add(url)
    try:
        resp = session.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return
    soup = BeautifulSoup(resp.text, "html.parser")
    # Find all PDF links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            full_url = urljoin(url, href)
            link_text = a.get_text(strip=True)
            PDFS.append({
                "pdf_url": full_url,
                "parent_page": url,
                "link_text": link_text
            })
    # Find all internal links for further crawling
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#"):
            continue
        full_url = urljoin(url, href)
        if (full_url.startswith(BASE_URL) and
            urlparse(full_url).path != urlparse(url).path):
            crawl(full_url, session, depth + 1, parent=url)
    time.sleep(SLEEP)

if __name__ == "__main__":
    session = requests.Session()
    # Visit the homepage to get cookies
    try:
        session.get("https://mariupol-r897.gosweb.gosuslugi.ru/", headers=HEADERS, timeout=20)
    except Exception as e:
        print(f"Warning: Could not fetch homepage: {e}")

    print(f"Starting crawl at {BASE_URL}")
    crawl(BASE_URL, session)
    print(f"Found {len(PDFS)} unique PDF links.")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(PDFS, f, ensure_ascii=False, indent=2)
    print(f"PDF links saved to {OUTPUT_JSON}")

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["pdf_url", "parent_page", "link_text"])
        writer.writeheader()
        for row in PDFS:
            writer.writerow(row)
    print(f"PDF links saved to {OUTPUT_CSV}")
import requests

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "downloaded_pdfs")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

import hashlib

def download_pdf(url, dest_dir):
    # Create a unique filename: sha256(url)[:10] + '_' + basename
    url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()[:10]
    base = os.path.basename(url)
    fname = os.path.join(dest_dir, f"{url_hash}_{base}")
    if os.path.exists(fname):
        print(f"Already exists: {fname}")
        return True
    try:
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(fname, "wb") as f:
            for chunk in r.iter_content(1024*1024):
                f.write(chunk)
        print(f"Downloaded: {fname}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

if __name__ == "__main__":
    # ...existing crawling and JSON/CSV export code...
    import json
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        pdf_links = json.load(f)
    print(f"Starting batch download of {len(pdf_links)} PDFs...")
    success, fail = 0, 0
    for entry in pdf_links:
        url = entry["pdf_url"]
        if download_pdf(url, DOWNLOAD_DIR):
            success += 1
        else:
            fail += 1
    print(f"Batch download complete. Success: {success}, Failed: {fail}")    