from dotenv import load_dotenv
load_dotenv()
import schedule
import time
from scrapers.ieee_scraper import fetch_ieee_spectrum_ai_articles
from scrapers.engadget_scraper import fetch_engadget_articles
from scrapers.github_scraper import fetch_github_blog_articles
from scrapers.ainews_scraper import fetch_ai_news_articles
from scrapers.techeu_scraper import fetch_tech_eu_articles
from scrapers.techcrunch_scraper import fetch_tech_articles
from scrapers.venturebeat_scraper import fetch_venturebeat_articles
from scrapers.wired_scraper import fetch_wired_articles
from scrapers.indiehackers_scraper import fetch_indiehackers_articles
from scrapers.crunchbase_scraper import fetch_crunchbase_articles
from scrapers.newsstack_scraper import fetch_thenewstack_articles
from scrapers.aitechpark_scraper import fetch_aitechpark_articles
from app import articles_collection
from ai_processor import summarize_with_groq
import os

def run_all_scrapers():
    scrapers = [
        fetch_ieee_spectrum_ai_articles,
        fetch_engadget_articles,
        fetch_indiehackers_articles,
        fetch_thenewstack_articles,
        fetch_aitechpark_articles,
        fetch_tech_articles,
        fetch_tech_eu_articles,
        fetch_venturebeat_articles,
        fetch_wired_articles,
        fetch_ai_news_articles,
        fetch_github_blog_articles,
        fetch_crunchbase_articles
    ]
    
    for scraper_func in scrapers:
        try:
            scraper_func()
        except Exception as e:
            print(f"Scraper failed: {e}")
    print("Ran all scrapers once.")

def summarize_all_fetched_articles():
    """Process all unprocessed articles"""
    try:
        unprocessed = articles_collection.find({"processed": False})
        for article in unprocessed:
            try:
                summarize_with_groq(article, os.getenv("GROQ_API_KEY"))
                articles_collection.update_one(
                    {"_id": article["_id"]},
                    {"$set": {"processed": True}}
                )
            except Exception as e:
                print(f"Summarization failed: {e}")
        print("Summarized all articles.")
                
    except Exception as e:
        print(f"Error processing articles: {e}")

# Schedule tasks every 24 hours
schedule.every(24).hours.do(run_all_scrapers)
schedule.every(24).hours.do(summarize_all_fetched_articles)

# Run immediately on startup
run_all_scrapers()
summarize_all_fetched_articles()

# Main loop
while True:
    try:
        schedule.run_pending()
        time.sleep(60)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Scheduler error: {e}")
        time.sleep(60)