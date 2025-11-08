# scraping/extractor.py
from newspaper import Article
from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
from urllib.parse import urlparse

def extract_text(url: str) -> str:
    """
    Extracts readable text from a URL.
    Handles both static and dynamic websites.
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    text = ""
    print(f"[1/4] Trying newspaper3k extraction...")

    try:
        article = Article(url, language="en")
        article.download()
        article.parse()
        text = article.text.strip()
        if len(text) >= 100:
            print(f"newspaper3k success: {len(text)} characters")
            return text
    except Exception as e:
        print(f"newspaper3k failed: {e}")

    print(f"[2/4] Trying requests + BeautifulSoup...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, timeout=15, headers=headers)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()
        
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        text = " ".join(paragraphs)
        
        if len(text) >= 100:
            print(f"BeautifulSoup success: {len(text)} chars")
            return text
    except Exception as e:
        print(f"BeautifulSoup failed: {e}")
    
    print(f"[3/4] Trying requests-html with JS rendering...")
    try:
        session = HTMLSession()
        r = session.get(url, timeout=30)
        r.html.render(timeout=30, sleep=2)
        
        paragraphs = [p.text.strip() for p in r.html.find("p")]
        text = " ".join(paragraphs)
        
        if len(text) >= 100:
            print(f"requests-html success: {len(text)} characters")
            return text
    except Exception as e:
        print(f"requests-html failed: {e}")
    
    print(f"[4/4] Fallback: Extracting all text from body...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, timeout=15, headers=headers)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "meta", "link", "nav", "footer"]):
            tag.decompose()
        
        text = soup.get_text(separator=" ", strip=True)
        
        text = " ".join(text.split())
        
        if len(text) >= 100:
            print(f"Fallback success: {len(text)} charactes")
            return text
    except Exception as e:
        print(f"Fallback failed: {e}")
    
    print(f"All methods failed. Retrieved text length: {len(text)}")
    return text


def get_logo(url: str) -> str:
    """
    Extracts the favicon/logo from a website.
    """
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        icon_selectors = [
            ("link", {"rel": "icon"}),
            ("link", {"rel": "shortcut icon"}),
            ("link", {"rel": "apple-touch-icon"}),
        ]
        
        for tag, attrs in icon_selectors:
            icon_link = soup.find(tag, attrs)
            if icon_link and icon_link.get("href"):
                href = icon_link.get("href")
                if href.startswith("http"):
                    return href
                elif href.startswith("/"):
                    parsed = urlparse(url)
                    return f"{parsed.scheme}://{parsed.netloc}{href}"
                else:
                    parsed = urlparse(url)
                    base_path = "/".join(parsed.path.split("/")[:-1]) or "/"
                    return f"{parsed.scheme}://{parsed.netloc}{base_path}/{href}"
    except Exception as e:
        print(f"Logo extraction error: {e}")
    
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"