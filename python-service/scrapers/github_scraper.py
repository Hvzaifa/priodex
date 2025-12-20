"""
GitHub Blog Scraper - Full Content Extraction (Fixed)
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from bs4 import BeautifulSoup
from app import articles_collection

def fetch_github_blog_articles(count=2):
    try:
        response = requests.get('https://github.blog/feed/', timeout=10)
        root = ET.fromstring(response.content)
        inserted_ids = []

        for item in root.findall('.//item')[:count]:
            title = get_text(item.find('title'))
            url = get_text(item.find('link'))

            if not title or not url:
                continue

            # FIX: New extraction logic
            content = extract_full_content(item, url)

            doc = {
                'title': title,
                'url': url,
                'source': 'GitHub Blog',
                'content': content,
                'scrapedDate': datetime.now().isoformat(),
                'categories': ['GitHub'],
                'keywords': get_keywords(title + " " + content),
                'processed': False
            }

            result = articles_collection.insert_one(doc)
            inserted_ids.append(result.inserted_id)

        return inserted_ids

    except Exception as e:
        print("GitHub scraper error:", e)
        return []


def get_text(elem):
    return elem.text.strip() if elem is not None and elem.text else ""


# -----------------------------------------------------------
# FIXED FULL ARTICLE CONTENT EXTRACTION
# -----------------------------------------------------------
def extract_full_content(item, url):
    """
    Priority:
    1. content:encoded (Full RSS content — BEST)
    2. Fetch article page HTML
    3. RSS description fallback
    """

    # ---------- PRIORITY 1: content:encoded ----------
    encoded = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
    if encoded is not None and encoded.text:
        cleaned = clean_html(encoded.text)
        if len(cleaned.split()) > 50:
            return cleaned

    # ---------- PRIORITY 2: FETCH FULL PAGE ----------
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # GitHub Blog's REAL selectors
        possible_selectors = [
            "article .entry-content",
            "article .post-content-container",
            "article .post-content",
            ".entry-content",
            ".post-content",
        ]

        for sel in possible_selectors:
            elem = soup.select_one(sel)
            if elem:
                cleaned = clean_html(elem.get_text(" ", strip=True))
                if len(cleaned.split()) > 50:
                    return cleaned

    except Exception as e:
        print("Error fetching page content:", e)

    # ---------- PRIORITY 3: Description fallback ----------
    desc = item.find("description")
    if desc is not None and desc.text:
        cleaned = clean_html(desc.text)
        if len(cleaned.split()) > 20:
            return cleaned

    # Final fallback
    return f"GitHub blog article about {get_text(item.find('title')).lower()}. Read the full article at the source link."


# -----------------------------------------------------------
# CLEAN HTML → CLEAN TEXT
# -----------------------------------------------------------
def clean_html(html_text):
    """Removes HTML tags, scripts, links cleanly and returns readable content."""
    soup = BeautifulSoup(html_text, "html.parser")

    for tag in soup.find_all(['script', 'style', 'img', 'svg', 'noscript']):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    return ' '.join(text.split())


def get_keywords(text):
    if not text:
        return []

    text_lower = text.lower()
    keywords = [
        'github', 'git', 'developer', 'code', 'programming',
        'open source', 'pull request', 'repository', 'workflow',
        'actions', 'security', 'devops'
    ]

    return [kw for kw in keywords if kw in text_lower][:8]


# -----------------------------------------------------------
# TEST RUN
# -----------------------------------------------------------
if __name__ == "__main__":
    ids = fetch_github_blog_articles(1)
    print("Inserted:", ids)
