"""
The New Stack Blog Scraper - Full Content Extraction
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from bs4 import BeautifulSoup
from app import articles_collection


FEED_URL = "https://thenewstack.io/blog/feed/"


def fetch_thenewstack_articles(count=2):
    try:
        response = requests.get(FEED_URL, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        inserted_ids = []

        # RSS feed → <item>
        items = root.findall(".//item")

        for item in items[:count]:
            title = get_text(item.find("title"))
            url = get_text(item.find("link"))

            if not title or not url:
                continue

            content = extract_full_content(item, url)
            categories = extract_categories(item)

            doc = {
                "title": title,
                "url": url,
                "source": "The New Stack",
                "content": content,
                "scrapedDate": datetime.utcnow().isoformat(),
                "categories": categories,
                "keywords": get_keywords(title + " " + content),
                "processed": False
            }

            result = articles_collection.insert_one(doc)
            inserted_ids.append(result.inserted_id)

        return inserted_ids

    except Exception as e:
        print("The New Stack scraper error:", e)
        return []


# -----------------------------------------------------------
# UTILITIES
# -----------------------------------------------------------
def get_text(elem):
    return elem.text.strip() if elem is not None and elem.text else ""


def extract_categories(item):
    categories = []
    for cat in item.findall("category"):
        if cat.text:
            categories.append(cat.text.strip())
    return categories or ["Tech"]


# -----------------------------------------------------------
# FULL CONTENT EXTRACTION
# -----------------------------------------------------------
def extract_full_content(item, url):
    """
    Priority:
    1. content:encoded (full article)
    2. description
    3. Fetch article page
    """

    # ---------- PRIORITY 1: content:encoded ----------
    encoded = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
    if encoded is not None and encoded.text:
        cleaned = clean_html(encoded.text)
        if len(cleaned.split()) > 100:
            return cleaned

    # ---------- PRIORITY 2: description ----------
    desc = item.find("description")
    if desc is not None and desc.text:
        cleaned = clean_html(desc.text)
        if len(cleaned.split()) > 50:
            return cleaned

    # ---------- PRIORITY 3: FETCH PAGE ----------
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"
        })
        soup = BeautifulSoup(response.content, "html.parser")

        # The New Stack article container
        possible_selectors = [
            "article",
            "div.article-content",
            "div.post-content",
            "main"
        ]

        for sel in possible_selectors:
            elem = soup.select_one(sel)
            if elem:
                cleaned = clean_html(elem.get_text(" ", strip=True))
                if len(cleaned.split()) > 150:
                    return cleaned

    except Exception as e:
        print("Page fetch error:", e)

    return f"The New Stack article: {get_text(item.find('title'))}. Read the full article at the source."


# -----------------------------------------------------------
# CLEAN HTML
# -----------------------------------------------------------
def clean_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")

    for tag in soup.find_all(["script", "style", "img", "svg", "noscript", "figure"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    return " ".join(text.split())


# -----------------------------------------------------------
# KEYWORDS
# -----------------------------------------------------------
def get_keywords(text):
    if not text:
        return []

    text = text.lower()
    keywords = [
        "cloud", "kubernetes", "devops", "software",
        "open source", "ai", "ml", "security",
        "platform", "infrastructure", "developer",
        "containers", "microservices"
    ]

    return [kw for kw in keywords if kw in text][:10]


# -----------------------------------------------------------
# TEST
# -----------------------------------------------------------
if __name__ == "__main__":
    ids = fetch_thenewstack_articles(1)
    print("Inserted:", ids)
