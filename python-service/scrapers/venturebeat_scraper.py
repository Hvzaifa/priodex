"""
VentureBeat RSS Scraper - Structured Output
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import re
from app import articles_collection

def fetch_venturebeat_articles(count=2):
    """Fetch articles from VentureBeat RSS feed in structured format"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get('https://venturebeat.com/feed', headers=headers, timeout=15)
        
        root = ET.fromstring(response.content)
        inserted_ids = []
        seen_urls = set()
        
        tech_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'startup',
            'fintech', 'cloud', 'saas', 'software', 'hardware', 'security',
            'cybersecurity', 'funding', 'robotics', 'blockchain', 'crypto',
            'enterprise', 'developer', 'infrastructure', 'mobile', 'app',
            'data', 'analytics', 'venture capital', 'vc', 'investment'
        ]
        
        for item in root.findall('.//item'):
            if len(inserted_ids) >= count:
                break
                
            title_elem = item.find('title')
            link_elem = item.find('link')
            description_elem = item.find('description')
            
            if title_elem is None or link_elem is None:
                continue
                
            title = title_elem.text.strip() if title_elem.text else ""
            url = link_elem.text.strip() if link_elem.text else ""
            
            if not title or not url or url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Skip duplicates in DB
            if articles_collection.find_one({"url": url}):
                continue
            
            # Extract categories from RSS
            categories = []
            for category in item.findall('category'):
                if category.text:
                    categories.append(category.text.strip())
            
            # Get content from description
            content = ""
            if description_elem is not None and description_elem.text:
                content = re.sub('<[^<]+?>', '', description_elem.text).strip()
            
            # Extract keywords
            combined_text = f"{title} {content}".lower()
            keywords = [kw for kw in tech_keywords if kw in combined_text][:8]
            
            # Ensure categories and keywords are never empty
            if not categories:
                categories = ["Tech"]
            
            if not keywords:
                keywords = ["technology"]
            
            doc = {
                'title': title,
                'url': url,
                'source': 'VentureBeat',
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

# Run it
if __name__ == "__main__":
    print(fetch_venturebeat_articles(1))