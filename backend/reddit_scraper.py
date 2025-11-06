import os
import json
from datetime import datetime
from dotenv import load_dotenv
import praw

load_dotenv()

class RedditCompanyScraper:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id = client_id,
            client_secret = client_secret,
            user_agent = user_agent
        )

    def scrape_company_reviews(self, company_name, limit = 25, time_filter = 'year', min_score = 0, include_comments = True):
        reviews = []
        search_queries = [
            f"{company_name} Company customer review",
            f"{company_name} Company customer experience",
            f"{company_name} Company customer opinion",
            f"employees working at {company_name}"
        ]

        for query in search_queries:
            print(f"Searching: {query}")
            try:
                submissions = self.reddit.subreddit('all').search(
                    query, limit = limit, time_filter = time_filter
                )

                for submission in submissions:
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

                    submission.comments.replace_more(limit = 0)
                    for comment in submission.comments.list()[:2]:
                        if len(comment.body) > 50:
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
                print(f"Error searching '{query}': {str(e)}")

        unique_reviews = []
        seen = set()
        for review in reviews:
            if review['permalink'] not in seen:
                unique_reviews.append(review)
                seen.add(review['permalink'])

        print(f"Collected {len(unique_reviews)} items for '{company_name}'")
        filtered_reviews = self.filter_reviews(unique_reviews, min_score, include_comments)
        self.save_to_file(filtered_reviews, company_name, filtered = True)
        return unique_reviews

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