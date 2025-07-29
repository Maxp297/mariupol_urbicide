import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os
import json

BASE_URL = "https://mariupol-r897.gosweb.gosuslugi.ru/ofitsialno/dokumenty/"
VISITED = set()
SITE_TREE = {}
MAX_DEPTH = 6  # adjust as needed
SLEEP = 0.8   # polite crawling

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; EvidenceCollector/1.0)'
}

def crawl(url, tree, depth=0):
    if depth > MAX_DEPTH or url in VISITED:
        return
    print(f"Crawling: {url}")
    VISITED.add(url)
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return
        soup = BeautifulSoup(r.text, "html.parser")
        # Extract page title
        title = soup.title.text.strip() if soup.title else url
        tree['url'] = url
        tree['title'] = title
        tree['children'] = []
        # Find all internal links
        for a in soup.find_all('a', href=True):
            href = a['href']
            abs_url = urljoin(url, href)
            # Only follow links within the base domain and /ofitsialno/dokumenty/
            if abs_url.startswith(BASE_URL) and abs_url not in VISITED:
                child = {}
                tree['children'].append(child)
                crawl(abs_url, child, depth+1)
        time.sleep(SLEEP)
    except Exception as e:
        print(f"Error crawling {url}: {e}")

def main():
    global SITE_TREE
    SITE_TREE = {}
    crawl(BASE_URL, SITE_TREE)
    out_path = os.path.join(os.path.dirname(__file__), "mariupol_gosuslugi_structure.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(SITE_TREE, f, ensure_ascii=False, indent=2)
    print(f"Site structure saved to {out_path}")

if __name__ == "__main__":
    main()
