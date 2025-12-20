"""
Indie Hackers RSS Scraper - Clean Content
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from bs4 import BeautifulSoup
from app import articles_collection

def fetch_indiehackers_articles(count=2):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get('https://feed.indiehackers.world/posts.rss', headers=headers, timeout=15)
        
        root = ET.fromstring(response.content)
        inserted_ids = []
        
        channel = root.find('channel')
        if channel is None:
            return []
        
        for item in channel.findall('item')[:count]:
            title = get_text(item.find('title'))
            url = get_text(item.find('link'))
            
            if not title or not url:
                continue
            
            content = get_clean_content(item, url)
            categories = [cat.text.strip() for cat in item.findall('category') if cat.text] or ['Indie Business']
            keywords = extract_keywords(f"{title} {content}")
            
            doc = {
                'title': title,
                'url': url,
                'source': 'Indie Hackers',
                'content': content,
                'scrapedDate': datetime.now().isoformat(),
                'categories': categories,
                'keywords': keywords,
                'processed': False
            }
            result = articles_collection.insert_one(doc)
            inserted_ids.append(result.inserted_id)

        return inserted_ids
        
    except Exception as e:
        return []

def get_text(elem):
    if elem is not None and elem.text:
        return elem.text.strip()
    return ""

def get_clean_content(item, url):
    """Get clean, properly formatted content"""
    # Try RSS content:encoded first
    content_elem = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
    if content_elem and content_elem.text:
        soup = BeautifulSoup(content_elem.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        if len(text) > 100:
            return text
    
    # Try RSS description
    desc = item.find('description')
    if desc and desc.text:
        soup = BeautifulSoup(desc.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        if len(text) > 50:
            return text
    
    # Try to fetch from page
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=8)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        content_elem = soup.select_one('article, .post-content, .content')
        if content_elem:
            # Get text with proper spacing
            text = content_elem.get_text(separator=' ', strip=True)
            if len(text) > 100:
                return text
    except:
        pass
    
    return f"Indie Hackers article: {get_text(item.find('title'))}"

def extract_keywords(text):
    """Extract relevant keywords"""
    if not text:
        return []
    
    text_lower = text.lower()
    keywords = ['ai', 'startup', 'product', 'business', 'indie', 'saas', 'revenue', 'growth']
    
    return [kw for kw in keywords if kw in text_lower][:5]

if __name__ == "__main__":
    articles = fetch_indiehackers_articles(3)
    print(articles)