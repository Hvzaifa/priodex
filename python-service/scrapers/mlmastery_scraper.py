"""
Machine Learning Mastery RSS Scraper
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from bs4 import BeautifulSoup
import re
from app import articles_collection

def fetch_mlmastery_articles(count=3):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get('https://machinelearningmastery.com/feed/', headers=headers, timeout=15)
        
        # Parse RSS feed
        root = ET.fromstring(response.content)
        inserted_ids = []
        
        # Find channel
        channel = root.find('channel')
        if channel is None:
            return []
        
        for item in channel.findall('item')[:count]:
            title_elem = item.find('title')
            link_elem = item.find('link')
            description_elem = item.find('description')
            pub_date_elem = item.find('pubDate')
            creator_elem = item.find('{http://purl.org/dc/elements/1.1/}creator')
            
            if title_elem is not None and link_elem is not None:
                title = get_text(title_elem)
                url = get_text(link_elem)
                
                if not title or not url:
                    continue
                
                # Extract content from description
                content = extract_content(description_elem)
                
                # Extract categories/keywords from content and title
                keywords = extract_keywords(f"{title} {content}")
                
                # Determine if sponsored content
                categories = ['Machine Learning']
                if 'sponsored' in title.lower() or 'sponsored' in content.lower():
                    categories.append('Sponsored')
                
                doc = {
                    'title': title,
                    'url': url,
                    'source': 'Machine Learning Mastery',
                    'content': content,
                    'scrapedDate': datetime.now().isoformat(),
                    'categories': categories,
                    'keywords': keywords,
                    'processed': False,
                    'fullContentAvailable': False
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

def extract_content(desc_elem):
    """Extract clean content from CDATA description"""
    if desc_elem is None or desc_elem.text is None:
        return ""
    
    # The content is wrapped in CDATA, so we need to extract it
    content = desc_elem.text.strip()
    
    # Remove CDATA markers if present
    if content.startswith('<![CDATA[') and content.endswith(']]>'):
        content = content[9:-3].strip()
    
    # Clean HTML tags if any
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text().strip()
    
    # Clean up whitespace
    text = ' '.join(text.split())
    
    return text[:1500] if len(text) > 1500 else text

def extract_keywords(text):
    """Extract relevant ML/AI keywords from text"""
    if not text:
        return []
    
    text_lower = text.lower()
    
    # ML/AI specific keywords
    ml_keywords = [
        'machine learning', 'ai', 'artificial intelligence', 'deep learning',
        'neural network', 'llm', 'gpt', 'llama', 'transformer',
        'nlp', 'natural language processing', 'data science',
        'python', 'tensorflow', 'pytorch', 'scikit-learn',
        'model', 'training', 'inference', 'tokenizer',
        'prompt engineering', 'agentic', 'agents',
        'data leakage', 'feature engineering', 'validation',
        'pydantic', 'time series', 'cost reduction', 'optimization'
    ]
    
    found_keywords = []
    for keyword in ml_keywords:
        if keyword in text_lower and keyword not in found_keywords:
            found_keywords.append(keyword)
            if len(found_keywords) >= 8:
                break
    
    return found_keywords

# Run it
if __name__ == "__main__":
    articles = fetch_mlmastery_articles(2)
    print(articles)