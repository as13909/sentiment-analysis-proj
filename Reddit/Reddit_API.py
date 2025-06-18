import requests
import praw
import csv
from textblob import TextBlob
import time
import datetime
import os
from dotenv import load_dotenv

# ---- Sentiment function ----
def get_sentiment(text):
    return round(TextBlob(text).sentiment.polarity, 4)

# Replace these with your app's info
load_dotenv()  # Load from .env file

client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")
user_agent = os.getenv("REDDIT_USER_AGENT")
username = os.getenv("REDDIT_USERNAME")
password = os.getenv("REDDIT_PASSWORD")

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    username=username,
    password=password,
    user_agent=user_agent
)

# ---- Parameters ----
cwd = os.getcwd()
cwd = cwd.split("\\")
cwd = cwd[1:-1]
path = "C:/"

for item in cwd:
    path = os.path.join(path, item)
path = os.path.join(path,r'movieInfo.csv')
first_movie = True
with open(path, "r", encoding='utf-8',newline="") as f1:
    reader = csv.reader(f1)
    next(reader)  # Skip header row
    for row in reader:
        keyword = row[0]
        release_date = row[2]
        subreddit_name = "movies"
        limit = 200
        count = 0
        # ---- CSV setup ----
        output_file = "RedditMovieData/reddit_movie_posts.csv"
        header = ["subreddit", "movie_name", "post_title", "post_url", "post_text", "sentiment_score"]

        with open(output_file, mode="a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            if first_movie:
                writer.writerow(header)

            for post in reddit.subreddit(subreddit_name).search(keyword, limit=limit, params={"before": release_date}):
                if keyword.lower() in post.title.lower() or keyword.lower() in (post.selftext or "").lower():
                    # Save this post to CSV
                    post_title = post.title
                    post_text = post.selftext or ""
                    sentiment = get_sentiment(post_title + ": " + post_text)
                    post_url = f"https://reddit.com{post.permalink}"
                    writer.writerow([post.subreddit.display_name, keyword, post_title, post_url, sentiment])
                    count+=1
        print(f"✅ Saved {count} posts to {output_file} from {keyword} in r/{subreddit_name}")
        first_movie = False