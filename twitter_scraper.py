import os
import json
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

if not APIFY_TOKEN:
    raise ValueError("Missing APIFY_TOKEN in environment variables.")

# Initialize Apify client
client = ApifyClient(APIFY_TOKEN)


def scrape_twitter(handle: str, mode: str = "by", max_items: int = 50, top_n: int = 20):
    """
    Scrape tweets either posted BY a brand or MENTIONING the brand using Apify's Twitter scraper.
    
    Args:
        handle (str): Twitter username without '@' (e.g., 'nike')
        mode (str): 'by' → tweets posted by the brand
                    'mentions' → tweets mentioning/tagging the brand
        max_items (int): Maximum number of tweets to fetch
        top_n (int): For mentions mode, only keep top_n tweets by public engagement
    
    Returns:
        list[dict]: List of normalized tweet data dictionaries
    """
    # Build search query based on mode
    if mode == "by":
        # Exclude replies and retweets
        query = f"from:{handle} -filter:replies -filter:retweets"
    elif mode == "mentions":
        query = f"@{handle}"
    else:
        raise ValueError("Invalid mode. Choose 'by' or 'mentions'.")

    # Prepare actor input for Apify
    run_input = {
        "twitterContent": query,
        "maxItems": max_items,
        "queryType": "Latest",
        "lang": "en",
    }

    try:
        # Run Apify Twitter scraper actor
        run = client.actor("CJdippxWmn9uRfooo").call(run_input=run_input)

        # Get dataset items (tweets)
        dataset = client.dataset(run["defaultDatasetId"])
        tweets = list(dataset.iterate_items())

        # Normalize key fields
        results = []
        for t in tweets:
            text = (
                t.get("full_text")
                or t.get("text")
                or t.get("tweet_text")
                or t.get("content")
                or ""
            )
            results.append({
                "user": t.get("user_screen_name"),
                "text": text.strip(),
                "created_at": t.get("created_at"),
                "likes": t.get("likeCount", 0),
                "retweets": t.get("retweetCount", 0),
                "replies": t.get("replyCount", 0),
                "engagement": t.get("likeCount", 0) + t.get("retweetCount", 0) + t.get("replyCount", 0),
                "url": t.get("url"),
            })

        # For mentions mode, keep only top_n tweets by engagement
        if mode == "mentions":
            results.sort(key=lambda x: x["engagement"], reverse=True)
            results = results[:top_n]

        # Create output directory
        os.makedirs("data/twitter", exist_ok=True)

        # Save results to file
        file_path = f"data/twitter/{handle.lower()}_{mode}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        print(f"✅ Fetched {len(results)} tweets ({mode} mode) for @{handle}")
        print(f"📁 Saved to: {file_path}")

        return results

    except Exception as e:
        print(f"❌ Error scraping Twitter: {e}")
        return []


# Example usage (for testing)
if __name__ == "__main__":
    brand_handle = "nike"  # change to any handle
    brand_tweets = scrape_twitter(brand_handle, mode="by", max_items=50)
    mentions = scrape_twitter(brand_handle, mode="mentions", max_items=100, top_n=20)

    print("\n--- Sample brand tweet ---")
    if brand_tweets:
        print(brand_tweets[0])

    print("\n--- Sample mention ---")
    if mentions:
        print(mentions[0])
