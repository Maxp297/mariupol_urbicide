import requests
from bs4 import BeautifulSoup

# Set a realistic user-agent and headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'close'
}

url = 'https://gisnpa-dnr.ru/'

try:
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    print(f"[+] Success: status {resp.status_code}")
    print(f"[+] First 500 bytes:\n{resp.text[:500]}")
    # Optionally parse with BeautifulSoup
    soup = BeautifulSoup(resp.text, 'html.parser')
    title = soup.title.string if soup.title else 'No title'
    print(f"[+] Page title: {title}")
except Exception as e:
    print(f"[-] Error: {e}")
