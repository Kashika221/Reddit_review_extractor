import praw
from datetime import datetime
import re
from dotenv import load_dotenv
import os

load_dotenv()

class RedditCompanyScraper:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    def scrape_company_reviews(self, company_name, limit = 5, time_filter='all'):
        reviews = []
        search_queries = [
            f"{company_name}  review",
            f"{company_name} experience",
            f"{company_name} opinion",
            f"working at {company_name}"
        ]
        for query in search_queries:
            print(query)
            try:
                submissions = self.reddit.subreddit('all').search(
                    query,
                    limit=limit,
                    time_filter=time_filter
                )
                for submission in submissions:
                    review_data = {
                        'title': submission.title,
                        'author': str(submission.author),
                        'subreddit': str(submission.subreddit),
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'created_utc': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        'url': submission.url,
                        'permalink': f"https://reddit.com{submission.permalink}",
                        'selftext': submission.selftext,
                        'type': 'post',
                        'search_query': query
                    }
                    reviews.append(review_data)
                    submission.comments.replace_more(limit = 0)
                    for comment in submission.comments.list()[:2]: 
                        if len(comment.body) > 50: 
                            comment_data = {
                                'title': f"Comment on: {submission.title}",
                                'author': str(comment.author),
                                'subreddit': str(submission.subreddit),
                                'score': comment.score,
                                'created_utc': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                                'permalink': f"https://reddit.com{comment.permalink}",
                                'selftext': comment.body,
                                'type': 'comment',
                                'parent_post': submission.title,
                                'search_query': query
                            }
                            reviews.append(comment_data)
            except Exception as e:
                print(f"Error searching '{query}': {str(e)}")
        unique_reviews = []
        seen_permalinks = set()
        
        for review in reviews:
            if review['permalink'] not in seen_permalinks:
                unique_reviews.append(review)
                seen_permalinks.add(review['permalink'])
        return unique_reviews
    
    def filter_reviews(self, reviews, min_score=0, include_comments=True):
        filtered = []
        
        for review in reviews:
            if review['score'] >= min_score:
                if include_comments or review['type'] == 'post':
                    filtered.append(review)
        
        return filtered
    
    def save_to_file(self, reviews, filename='company_reviews.txt'):
        with open(filename, 'w', encoding='utf-8') as f:
            for i, review in enumerate(reviews, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"Review #{i}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Type: {review['type']}\n")
                f.write(f"Title: {review['title']}\n")
                f.write(f"Author: {review['author']}\n")
                f.write(f"Subreddit: r/{review['subreddit']}\n")
                f.write(f"Score: {review['score']}\n")
                f.write(f"Date: {review['created_utc']}\n")
                f.write(f"URL: {review['permalink']}\n")
                f.write(f"\nContent:\n{review['selftext']}\n")
            return

if __name__ == "__main__":
    CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    CLIENT_SECRET = os.getenv("REDDIT_SECRET_KEY")
    USER_AGENT = "CompanyReviewScraper/1.0"
    
    scraper = RedditCompanyScraper(CLIENT_ID, CLIENT_SECRET, USER_AGENT)

    company_name = input("Enter the company name :")  
    reviews = scraper.scrape_company_reviews(company_name = company_name, limit = 25, time_filter = 'year')
    filtered_reviews = scraper.filter_reviews(reviews, min_score = 5, include_comments=True)
    print(f"\n{'='*80}")
    print(f"Found {len(filtered_reviews)} reviews for {company_name}")
    print(f"{'='*80}\n")
    
    for i, review in enumerate(filtered_reviews[:5], 1): 
        print(f"{i}. [{review['type'].upper()}] {review['title']}")
        print(f"   Score: {review['score']} | r/{review['subreddit']} | {review['created_utc']}")
        print(f"   {review['selftext'][:200]}...")
        print()