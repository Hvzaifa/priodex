"""
Wired RSS Scraper - With Full Content
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import re
from app import articles_collection

def fetch_wired_articles(count=2):
    """Fetch articles from Wired RSS feed with full content"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Use Wired's main RSS feed
        response = requests.get('https://www.wired.com/feed/rss', headers=headers, timeout=15)
        
        # Parse RSS feed
        root = ET.fromstring(response.content)
        inserted_ids = []
        
        # Find channel
        channel = root.find('channel')
        if channel is None:
            return []
        
        items_processed = 0
        for item in channel.findall('item'):
            if items_processed >= count:
                break
                
            title_elem = item.find('title')
            link_elem = item.find('link')
            category_elems = item.findall('category')
            
            if title_elem is not None and link_elem is not None:
                title = title_elem.text.strip() if title_elem.text else ""
                url = link_elem.text.strip() if link_elem.text else ""
                
                # Filter for AI, Ideas, Science topics
                categories = []
                if category_elems:
                    categories = [cat.text for cat in category_elems if cat.text]
                
                # Check if article matches our topics
                relevant_topics = ['AI', 'Artificial Intelligence', 'Science', 'Ideas', 'Tech', 'Innovation']
                title_lower = title.lower()
                
                is_relevant = (
                    any(topic.lower() in title_lower for topic in relevant_topics) or
                    any(topic in categories for topic in relevant_topics)
                )
                
                if not is_relevant:
                    continue
                
                # Get FULL content from the article URL
                full_content = get_full_article_content(url)            
                
                # Extract keywords from title and full content
                keywords = extract_keywords(title + " " + full_content)
                
                doc = {
                    'title': title,
                    'url': url,
                    'source': 'Wired',
                    'content': full_content,
                    'scrapedDate': datetime.now().isoformat(),
                    'categories': categories[:3],
                    'keywords': keywords,
                    'processed': False
                }                
                items_processed += 1
                result = articles_collection.insert_one(doc)
                inserted_ids.append(result.inserted_id)
        
        return inserted_ids
        
    except Exception as e:
        return []

def get_full_article_content(url):
    """Fetch full article content from Wired URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Wired article content is typically in these selectors
        content_selectors = [
            'article',
            '.article-body',
            '.body-container',
            '.content-header__body',
            '[data-testid="ArticleBody"]',
            '.grid--item-body'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for element in content_elem.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'figure']):
                    element.decompose()
                
                # Get all paragraphs
                paragraphs = content_elem.find_all('p')
                content_text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                
                if content_text and len(content_text) > 200:
                    return content_text[:3000]  # Limit content length
        
        # Fallback: try to get any meaningful text
        body = soup.find('body')
        if body:
            text = body.get_text(strip=True)
            if len(text) > 300:
                return text[:3000]
        
        return "Full content not available"
        
    except Exception:
        return "Failed to fetch full content"

def extract_keywords(text):
    """Extract relevant keywords from text"""
    if not text:
        return []
    
    text_lower = text.lower()
    tech_keywords = [
        'ai', 'artificial intelligence', 'machine learning', 'science', 'technology',
        'innovation', 'research', 'data', 'algorithm', 'neural', 'robot',
        'quantum', 'climate', 'space', 'biology', 'physics', 'engineering',
        'future', 'discovery', 'breakthrough', 'study', 'scientists'
    ]
    
    found_keywords = []
    for keyword in tech_keywords:
        if keyword in text_lower and keyword not in found_keywords:
            found_keywords.append(keyword)
            if len(found_keywords) >= 6:
                break
    
    return found_keywords

# Import required
from bs4 import BeautifulSoup

# Run it
if __name__ == "__main__":
    articles = fetch_wired_articles(1)
    print(articles) 