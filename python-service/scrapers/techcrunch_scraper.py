"""
TechCrunch RSS Feed Scraper - Scrapes N Articles with Categories & Keywords
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import xml.etree.ElementTree as ET
from app import articles_collection

def fetch_tech_articles(count=2):
    """Fetch a specified number of TechCrunch articles from RSS feed and store with categories + keywords"""
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    rss_url = 'https://techcrunch.com/feed/'
    
    try:
        # Fetch RSS feed
        response = requests.get(rss_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse RSS XML
        root = ET.fromstring(response.content)
        
        tech_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'startup',
            'fintech', 'cloud', 'saas', 'software', 'hardware', 'security',
            'cybersecurity', 'funding', 'robotics', 'blockchain', 'crypto',
            'enterprise', 'developer', 'infrastructure', 'mobile', 'app',
            'data', 'analytics', 'venture capital', 'vc', 'investment'
        ]
        
        inserted_ids = []
        seen_urls = set()

        # Iterate through RSS items
        for item in root.findall('.//item'):
            if len(inserted_ids) >= count:
                break

            # Extract basic RSS fields
            title_elem = item.find('title')
            link_elem = item.find('link')
            description_elem = item.find('description')
            pub_date_elem = item.find('pubDate')
            
            title = title_elem.text if title_elem is not None else ""
            url = link_elem.text if link_elem is not None else ""
            description = description_elem.text if description_elem is not None else ""

            if not title or not url:
                continue
            
            if url in seen_urls:
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
            
            # Fetch full article content
            content = ""
            try:
                article_response = requests.get(url, headers=headers, timeout=10)
                article_soup = BeautifulSoup(article_response.content, 'html.parser')
                
                content_elem = article_soup.select_one('div.article-content, div.entry-content, article')
                if content_elem:
                    paragraphs = content_elem.find_all('p')
                    content = "\n".join([
                        p.get_text(strip=True) 
                        for p in paragraphs 
                        if len(p.get_text(strip=True)) > 50
                    ])
                
                # Extract additional categories from article page
                category_tags = article_soup.select('a[rel="category tag"]')
                page_categories = [tag.get_text(strip=True) for tag in category_tags]
                categories.extend(page_categories)
            except:
                pass
            
            # Use description as fallback
            if not content:
                content = BeautifulSoup(description, 'html.parser').get_text(strip=True)

            # Remove duplicates and limit categories
            categories = list(dict.fromkeys(categories))[:5]

            # -------- Extract Keywords --------
            combined_text = f"{title} {content}".lower()
            keywords = [
                kw for kw in tech_keywords if kw in combined_text
            ][:8]

            # Ensure they are never empty
            if not categories:
                categories = ["Tech"]

            if not keywords:
                keywords = ["technology"]

            # Build MongoDB document
            doc = {
                'title': title,
                'url': url,
                'source': 'TechCrunch',
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


# Run test
if __name__ == "__main__":
    print(fetch_tech_articles(1))