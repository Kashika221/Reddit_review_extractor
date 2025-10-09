import os
import json
from glob import glob
from datetime import datetime
from dotenv import load_dotenv

# Import your scrapers
from news_scraper import scrape_news
from twitter_scraper import scrape_twitter
from reddit_scraper import RedditCompanyScraper

load_dotenv()

def load_json_files(folder_path):
    all_data = []
    for file_path in glob(os.path.join(folder_path, "*.json")):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                all_data.extend(data)
            except json.JSONDecodeError:
                print(f"⚠️ Skipping invalid JSON file: {file_path}")
    return all_data

def normalize_twitter(tweet):
    return {
        "source": "twitter",
        "author": tweet.get("user"),
        "text": tweet.get("text"),
        "created_at": tweet.get("created_at"),
        "likes": tweet.get("likes", 0),
        "retweets": tweet.get("retweets", 0),
        "replies": tweet.get("replies", 0),
        "engagement": tweet.get("engagement", 0),
        "url": tweet.get("url"),
    }

def normalize_reddit(post):
    return {
        "source": "reddit",
        "author": post.get("author"),
        "text": post.get("selftext") or post.get("title"),
        "created_at": post.get("created_utc"),
        "score": post.get("score", 0),
        "type": post.get("type"),
        "url": post.get("permalink"),
        "subreddit": post.get("subreddit", ""),
    }

def normalize_news(article):
    return {
        "source": "news",
        "author": article.get("source"),
        "text": article.get("title") + (f" - {article.get('description')}" if article.get("description") else ""),
        "created_at": article.get("publishedAt"),
        "url": article.get("url"),
    }

def scrape_and_compile(brand_name: str, twitter_max=50, news_max=50, reddit_limit=25):
    """
    Scrapes Twitter, News, Reddit for a brand, saves raw files,
    and compiles a normalized dataset.
    """
    brand_dir = f"data/compiled/{brand_name.lower().replace(' ', '_')}"
    os.makedirs(brand_dir, exist_ok=True)

    # --- Twitter ---
    print(f"\n🐦 Scraping Twitter for '{brand_name}'...")
    twitter_data = scrape_twitter(brand_name, mode="by", max_items=twitter_max)
    twitter_path = f"{brand_dir}/twitter.json"
    with open(twitter_path, "w", encoding="utf-8") as f:
        json.dump(twitter_data, f, indent=4, ensure_ascii=False)

    # --- News ---
    print(f"\n📰 Scraping News for '{brand_name}'...")
    news_data = scrape_news(brand_name, max_articles=news_max)
    news_path = f"{brand_dir}/news.json"
    with open(news_path, "w", encoding="utf-8") as f:
        json.dump(news_data, f, indent=4, ensure_ascii=False)

    # --- Reddit ---
    print(f"\n👥 Scraping Reddit for '{brand_name}'...")
    reddit_scraper = RedditCompanyScraper(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_SECRET_KEY"),
        user_agent="CompanyReviewScraper/1.0"
    )
    reddit_data = reddit_scraper.scrape_company_reviews(brand_name, limit=reddit_limit, time_filter='year')
    reddit_path = f"{brand_dir}/reddit.json"
    with open(reddit_path, "w", encoding="utf-8") as f:
        json.dump(reddit_data, f, indent=4, ensure_ascii=False)

    # --- Compile & Normalize ---
    compiled = []
    compiled.extend([normalize_twitter(t) for t in twitter_data])
    compiled.extend([normalize_reddit(r) for r in reddit_data])
    compiled.extend([normalize_news(n) for n in news_data])

    compiled_file = f"{brand_dir}/compiled_normalized.json"
    with open(compiled_file, "w", encoding="utf-8") as f:
        json.dump(compiled, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Compiled {len(compiled)} items into {compiled_file}")
    return compiled

if __name__ == "__main__":
    brand = input("Enter the company/brand name: ").strip()
    scrape_and_compile(brand)
