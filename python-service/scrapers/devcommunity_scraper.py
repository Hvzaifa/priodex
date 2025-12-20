"""
Dev.to Article Scraper - Inserts Into MongoDB
"""

from app import articles_collection
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import re

class DevToScraper:
    def __init__(self):
        self.base_url = "https://dev.to"
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    
    def fetch_articles(self, count=2):
        """
        Scrape articles AND insert them into MongoDB.
        Returns a list of inserted document IDs.
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            inserted_ids = []
            seen_urls = set()
            
            for card in soup.find_all(['article', 'div']):
                if len(inserted_ids) >= count:
                    break
                    
                article_data = self._extract_article(card)
                if not article_data:
                    continue

                url = article_data['url']
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                # Check if article already exists (avoid duplicates)
                exists = articles_collection.find_one({"url": url})
                if exists:
                    continue

                # Insert into MongoDB
                result = articles_collection.insert_one(article_data)
                inserted_ids.append(result.inserted_id)

            return inserted_ids
            
        except Exception as e:
            print("Scraping error:", e)
            return []
    
    def _extract_article(self, card):
        try:
            title_link = card.find('a', href=lambda x: x and len(x) > 10 and not x.startswith('/t/'))
            if not title_link:
                return None
                
            title = title_link.get_text(strip=True)
            url = urljoin(self.base_url, title_link.get('href'))
            
            if len(title) < 30:
                return None
            
            content = self._get_content(url)
            if not content:
                return None
            
            return {
                'title': title,
                'url': url,
                'source': 'Dev.to',
                'content': content,
                'scrapedDate': datetime.now().isoformat(),
                'categories': self._extract_categories(card),
                'keywords': self._extract_keywords(content, title),
                'processed': False
            }
            
        except Exception as e:
            print("Extract error:", e)
            return None
    
    def _get_content(self, url):
        try:
            response = requests.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content_elem = soup.find('div', class_=['crayons-article__main', 'article-body']) or soup.find('article')
            if content_elem:
                for element in content_elem.find_all(['pre', 'code', 'script', 'style']):
                    element.decompose()
                
                paragraphs = content_elem.find_all('p')
                content = "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                return content if content else None
            
            return None
        except Exception:
            return None

    
    def _extract_categories(self, card):
        categories = []
        tag_links = card.find_all('a', href=lambda x: x and x.startswith('/t/'))
        for tag_link in tag_links[:5]:
            category = tag_link.get_text(strip=True).replace('#', '')
            if category and category not in categories:
                categories.append(category)
        return categories
    
    def _extract_keywords(self, content, title):
        text = f"{title} {content}".lower()
        tech_keywords = [
            'javascript', 'python', 'react', 'vue', 'angular', 'node', 'typescript',
            'java', 'docker', 'kubernetes', 'aws', 'cloud', 'devops',
            'machine learning', 'ai', 'web development', 'mobile development',
            'database', 'api', 'rest', 'graphql', 'security', 'testing'
        ]
        
        found_keywords = []
        for keyword in tech_keywords:
            if keyword in text and keyword not in found_keywords:
                found_keywords.append(keyword)
                if len(found_keywords) >= 8:
                    break
        return found_keywords


def get_articles(count=3):
    scraper = DevToScraper()
    inserted_ids = scraper.fetch_articles(count)
    print(f"Inserted {len(inserted_ids)} article from DEV Community.")
    return inserted_ids


if __name__ == "__main__":
    get_articles(1)
