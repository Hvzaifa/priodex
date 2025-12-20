"""
Engadget RSS Scraper - Full Content Extraction (FIXED)
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from bs4 import BeautifulSoup
from app import articles_collection


ENGADGET_FEED = "https://www.engadget.com/rss.xml"


def fetch_engadget_articles(count=1):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(ENGADGET_FEED, headers=headers, timeout=15)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        inserted_ids = []

        items = root.findall(".//item")

        for item in items[:count]:
            title = get_text(item.find("title"))
            url = get_text(item.find("link"))

            if not title or not url:
                continue

            # Duplicate check
            if articles_collection.find_one({"url": url}):
                continue

            content = extract_full_content(item, url)
            categories = extract_categories(item)
            keywords = extract_keywords(title + " " + content)

            doc = {
                "title": title,
                "url": url,
                "source": "Engadget",
                "content": content,
                "scrapedDate": datetime.utcnow().isoformat(),
                "categories": categories,
                "keywords": keywords,
                "processed": False
            }

            result = articles_collection.insert_one(doc)
            inserted_ids.append(result.inserted_id)

        return inserted_ids

    except Exception as e:
        print("Engadget scraper error:", e)
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
    return categories


# -----------------------------------------------------------
# FULL CONTENT EXTRACTION
# -----------------------------------------------------------
def extract_full_content(item, url):
    """
    Priority:
    1. content:encoded (FULL article)
    2. description
    3. Fetch article page (fallback)
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
        if len(cleaned.split()) > 40:
            return cleaned

    # ---------- PRIORITY 3: FETCH PAGE ----------
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"
        })
        soup = BeautifulSoup(response.content, "html.parser")

        article = soup.find("article")
        if article:
            cleaned = clean_html(article.get_text(" ", strip=True))
            if len(cleaned.split()) > 150:
                return cleaned

    except Exception as e:
        print("Page fetch error:", e)

    return f"Engadget article: {get_text(item.find('title'))}. Read the full article at the source."


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
def extract_keywords(text):
    if not text:
        return []

    text = text.lower()

    tech_keywords = [
        "ai", "machine learning", "cloud", "aws", "google", "apple",
        "microsoft", "android", "iphone", "hardware", "chip", "gpu",
        "nvidia", "intel", "qualcomm", "security", "privacy",
        "software", "open source", "startup", "robotics"
    ]

    found = []
    for kw in tech_keywords:
        if kw in text and kw not in found:
            found.append(kw)
            if len(found) >= 8:
                break

    return found


# -----------------------------------------------------------
# TEST
# -----------------------------------------------------------
if __name__ == "__main__":
    ids = fetch_engadget_articles(1)
    print("Inserted:", ids)
