import os
import json
from datetime import datetime
from dotenv import load_dotenv
import praw
import re

load_dotenv()

class RedditCompanyScraper:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id = client_id,
            client_secret = client_secret,
            user_agent = user_agent
        )

    def is_relevant(self, submission, company_name):
        """Check if post is actually about the company"""
        combined_text = (submission.title + " " + submission.selftext).lower()
        company_lower = company_name.lower()
        
        # Must contain company name
        if company_lower not in combined_text:
            return False
        
        # Filter out irrelevant posts
        irrelevant_keywords = ["gpu", "graphics card", "nvidia", "golf", "game", "mmorpg", "minecraft"]
        for keyword in irrelevant_keywords:
            if keyword in combined_text and company_lower not in submission.title.lower():
                return False
        
        return True

    def scrape_company_reviews(self, company_name, limit = 25, time_filter = 'year', min_score = 50, include_comments = True):
        reviews = []
        
        # Relevant subreddits for company reviews
        relevant_subreddits = [
            'reviews',
            'Assistance',
            'mildlyinfuriating',
            'jobs',
            'AskReddit',
            'WorkReform',
            'antiwork',
            'personalfinance',
            'Scams'
        ]
        
        search_queries = [
            company_name,
            f"{company_name} review",
            f"{company_name} experience",
            f"{company_name} customer service"
        ]

        for subreddit_name in relevant_subreddits:
            for query in search_queries:
                print(f"Searching r/{subreddit_name} for: {query}")
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    submissions = subreddit.search(
                        query, limit = limit, time_filter = time_filter
                    )

                    for submission in submissions:
                        # Relevance check
                        if not self.is_relevant(submission, company_name):
                            continue
                        
                        # Skip if already collected
                        if any(r['permalink'] == f"https://reddit.com{submission.permalink}" for r in reviews):
                            continue

                        review_data = {
                            'title' : submission.title,
                            'author' : str(submission.author),
                            'subreddit' : str(submission.subreddit),
                            'score' : submission.score,
                            'upvote_ratio' : submission.upvote_ratio,
                            'num_comments' : submission.num_comments,
                            'created_utc' : datetime.fromtimestamp(
                                submission.created_utc
                            ).strftime('%Y-%m-%d %H:%M:%S'),
                            'url' : submission.url,
                            'permalink' : f"https://reddit.com{submission.permalink}",
                            'selftext' : submission.selftext,
                            'type' : 'post',
                            'search_query' : query
                        }
                        reviews.append(review_data)

                        if include_comments:
                            submission.comments.replace_more(limit = 0)
                            for comment in submission.comments.list()[:2]:
                                if len(comment.body) > 50 and company_name.lower() in comment.body.lower():
                                    comment_data = {
                                        'title' : f"Comment on: {submission.title}",
                                        'author' : str(comment.author),
                                        'subreddit' : str(submission.subreddit),
                                        'score' : comment.score,
                                        'created_utc' : datetime.fromtimestamp(
                                            comment.created_utc
                                        ).strftime('%Y-%m-%d %H:%M:%S'),
                                        'permalink' : f"https://reddit.com{comment.permalink}",
                                        'selftext' : comment.body,
                                        'type' : 'comment',
                                        'parent_post' : submission.title,
                                        'search_query' : query
                                    }
                                    reviews.append(comment_data)

                except Exception as e:
                    print(f"Error searching r/{subreddit_name} for '{query}': {str(e)}")

        print(f"Collected {len(reviews)} items for '{company_name}'")
        filtered_reviews = self.filter_reviews(reviews, min_score, include_comments)
        self.save_to_file(filtered_reviews, company_name, filtered = True)
        return filtered_reviews

    def filter_reviews(self, reviews, min_score = 0, include_comments = True):
        filtered = []
        for review in reviews:
            if review['score'] >= min_score:
                if include_comments or review['type'] == 'post':
                    filtered.append(review)
        print(f"Filtered down to {len(filtered)} items (min_score={min_score})")
        return filtered

    def save_to_file(self, reviews, company_name, filtered = False):
        os.makedirs("data/reddit", exist_ok = True)
        suffix = "_filtered" if filtered else ""
        file_path = f"data/reddit/{company_name.lower().replace(' ', '_')}{suffix}.json"

        with open(file_path, "w", encoding = "utf-8") as f:
            json.dump(reviews, f, ensure_ascii = False, indent = 4)

        print(f"Saved {len(reviews)} reviews to {file_path}")
        return file_path


if __name__ == "__main__":
    CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    CLIENT_SECRET = os.getenv("REDDIT_SECRET_KEY")
    USER_AGENT = "CompanyReviewScraper/1.0"

    scraper = RedditCompanyScraper(CLIENT_ID, CLIENT_SECRET, USER_AGENT)

    company_name = input("Enter the company name: ").strip()

    reviews = scraper.scrape_company_reviews(company_name, limit = 25, time_filter = 'year', min_score = 10, include_comments = True)