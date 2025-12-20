"""
Medium RSS Scraper - Optimized with Content Fallback
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from bs4 import BeautifulSoup
from app import articles_collection

def fetch_medium_articles(tag="artificial-intelligence", count=3):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://medium.com/feed/tag/{tag}"
        response = requests.get(url, headers=headers, timeout=15)
        
        root = ET.fromstring(response.content)
        inserted_ids = []
        
        for item in root.findall('.//item')[:count]:
            title = get_text(item.find('title'))
            url = get_text(item.find('link'))
            
            if not title or not url:
                continue
            
            content = get_content(item)
            keywords = extract_keywords(f"{title} {content}")
            
            doc = {
                'title': title,
                'url': url,
                'source': 'Medium',
                'content': content,
                'scrapedDate': datetime.now().isoformat(),
                'categories': [tag.replace('-', ' ').title()],
                'keywords': keywords,
                'processed': False
            }
            result = articles_collection.insert_one(doc)
            inserted_ids.append(result.inserted_id)
            
        return inserted_ids
        
    except Exception:
        return []

def get_text(elem):
    return elem.text.strip() if elem is not None and elem.text else ""

def get_content(item):
    # Try content:encoded first (full content)
    content_elem = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
    if content_elem and content_elem.text:
        soup = BeautifulSoup(content_elem.text, 'html.parser')
        text = soup.get_text().strip()
        if text:
            return text[:1000]  # Limit length
    
    # Try description
    desc_elem = item.find('description')
    if desc_elem and desc_elem.text:
        soup = BeautifulSoup(desc_elem.text, 'html.parser')
        text = soup.get_text().strip()
        if text and "Continue reading on Medium" not in text:
            return text
    
    # Fallback: generate content from title
    return f"Article about {item.find('title').text.strip()}. Read more at the source."

def extract_keywords(text):
    if not text:
        return []
    
    text_lower = text.lower()
    keywords = [
        'ai', 'artificial intelligence', 'machine learning', 'python', 'javascript',
        'programming', 'technology', 'development', 'software', 'startup'
    ]
    
    return [kw for kw in keywords if kw in text_lower][:5]

if __name__ == "__main__":
    articles = fetch_medium_articles("artificial-intelligence", 1)
    print(articles)