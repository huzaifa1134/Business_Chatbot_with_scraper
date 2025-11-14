from newspaper import Article
from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
from urllib.parse import urlparse, urljoin
import time
import os
import pickle
import faiss

MAX_PAGES = 15

def extract_text(url: str) -> str:
    """Extracts readable text from a single URL (static/dynamic)"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    text = ""
    try:
        article = Article(url, language="en")
        article.download()
        article.parse()
        text = article.text.strip()
        if len(text) >= 100:
            return text
    except:
        pass

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for script in soup(["script", "style", "meta", "link", "noscript"]):
            script.decompose()
        text_parts = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p')]
        text = " ".join(text_parts)
        text = " ".join(text.split())
        if len(text) >= 100:
            return text
    except:
        pass

    return text


def get_logo(url: str) -> str:
    """Get favicon/logo"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        icon = soup.find("link", rel=lambda x: x and "icon" in x)
        if icon and icon.get("href"):
            href = icon['href']
            parsed = urlparse(url)
            if href.startswith("http"):
                return href
            elif href.startswith("/"):
                return f"{parsed.scheme}://{parsed.netloc}{href}"
            else:
                base_path = "/".join(parsed.path.split("/")[:-1]) or "/"
                return f"{parsed.scheme}://{parsed.netloc}{base_path}/{href}"
    except:
        pass
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"


def crawl_website(base_url: str, max_pages: int = MAX_PAGES):
    """Crawl multiple pages, return list of dicts with text + url"""
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url
    parsed_base = urlparse(base_url)
    domain = f"{parsed_base.scheme}://{parsed_base.netloc}"

    visited = set()
    to_visit = [base_url]
    all_pages = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        text = extract_text(url)
        if text:
            all_pages.append({"url": url, "text": text})
        visited.add(url)

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(domain, href)
                if full_url.startswith(domain) and full_url not in visited and full_url not in to_visit:
                    to_visit.append(full_url)
        except:
            pass

        time.sleep(1)

    return all_pages


def save_faiss_index(index, path):
    faiss.write_index(index, path)

def load_faiss_index(path):
    return faiss.read_index(path)

def save_chunks(chunks, path):
    with open(path, "wb") as f:
        pickle.dump(chunks, f)

def load_chunks(path):
    with open(path, "rb") as f:
        return pickle.load(f)
