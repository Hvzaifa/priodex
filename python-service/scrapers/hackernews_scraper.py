"""
Hacker News Scraper - Inserts Into MongoDB
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from app import articles_collection

def get_hacker_news_articles(count=3):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get('https://news.ycombinator.com', headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        inserted_ids = []
        
        titlelines = soup.find_all('span', class_='titleline')

        for titleline in titlelines[:count]:
            link = titleline.find('a')
            if not link:
                continue

            title = link.get_text(strip=True)
            url = link.get('href', '')

            if not url.startswith('http'):
                url = f"https://news.ycombinator.com/{url}"

            # Duplicate check
            if articles_collection.find_one({"url": url}):
                continue

            # Attempt to fetch a short snippet
            snippet = get_snippet_or_summary(url, title)

            doc = {
                'title': title,
                'url': url,
                'source': 'Hacker News',
                'content': snippet,       # <--- small preview only
                'scrapedDate': datetime.now().isoformat(),
                'categories': [],
                'keywords': [],
                'processed': False,
                'fullContentAvailable': False
            }

            result = articles_collection.insert_one(doc)
            inserted_ids.append(result.inserted_id)

        return inserted_ids

    except Exception as e:
        print("HN scraper error:", e)
        return []


def get_snippet_or_summary(url, title):
    """Return a short preview/snippet instead of full content."""
    try:
        if 'news.ycombinator.com' in url:
            return "Discussion on Hacker News. Click the link to read more."

        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')

        # Try meta description
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content']

        # Try first paragraph
        p = soup.find('p')
        if p and p.get_text(strip=True):
            return p.get_text(strip=True)

    except:
        pass

    # Final fallback: AI-style short summary
    return f"A story titled '{title}'. Click the link to read the full article from the source."


# Manual test
if __name__ == "__main__":
    ids = get_hacker_news_articles(1)
    print("Inserted:", ids)
