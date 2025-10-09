import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

def scrape_news(brand_name : str, max_articles : int = 50):
    API_KEY = os.getenv("NEWS_API")  
    url = "https://newsapi.org/v2/everything"

    to_date = datetime.utcnow().date()
    from_date = to_date - timedelta(days = 7)

    params = {
        "q" : brand_name,
        "from" : from_date.isoformat(),
        "to" : to_date.isoformat(),
        "sortBy" : "relevancy",
        "language" : "en",
        "pageSize" : max_articles,
        "apiKey" : API_KEY,
    }

    response = requests.get(url, params = params)
    data = response.json()

    if response.status_code != 200:
        raise Exception(f"NewsAPI error: {data.get('message')}")

    articles = []
    for article in data.get("articles", []):
        articles.append({
            "title" : article["title"],
            "source" : article["source"]["name"],
            "publishedAt" : article["publishedAt"],
            "description" : article["description"],
            "url" : article["url"],
        })

    os.makedirs("data/news", exist_ok = True)
    file_path = f"data/news/{brand_name.lower().replace(' ', '_')}_news.json"

    with open(file_path, "w", encoding = "utf-8") as f:
        json.dump(articles, f, ensure_ascii = False, indent = 4)

    print(f"Saved {len(articles)} news articles for '{brand_name}' in {file_path}")
    return articles

if __name__ == "__main__":
    scrape_news("Nike")