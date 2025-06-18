from atproto import Client, models
import os
import csv
from dotenv import load_dotenv
import requests
from datetime import datetime
from textblob import TextBlob
from dateutil.relativedelta import relativedelta
import sys
import pandas as pd
curdir = os.getcwd()
curdir = curdir.split("\\")
curdir = curdir[1:-1]
path_shit = "C:/"
for item in curdir:
    path_shit = os.path.join(path_shit,item)
sys.path.append(path_shit)
import HelperFunctionsSA as hf
#Above is because Python doesn't know how to fucking file parse



load_dotenv()  # Load from .env file
# Initialize client
client = Client()
handle = os.getenv("BSKY_HANDLE")
password = os.getenv("BSKY_PASSWORD")

client.login(handle, password)

# Get your profile
profile = client.get_profile(handle)

#grab movie info for query
cwd = os.getcwd()
cwd = cwd.split("\\")
cwd = cwd[1:-1]
path = "C:/"
for item in cwd:
    path = os.path.join(path, item)
path = os.path.join(path,r'movieInfo.csv')

first_movie = True #makes sure we don't rewrite header

df = hf.return_formatted_file()

for index,row in df.iterrows():
    movie_title = row.title
    release_date = row.release_date
    keywords = row.keywords
    limit = 100
    count = 0
    # ---- CSV setup ----
    if movie_title in hf.KnownMovies:
        output_file = "BSky_moviedata/bsky_movie_posts3.csv"
        header = ["movie_name", "likes", "date_posted", "post_text", "sentiment_score","AboutMovie"]
        
        until_datetime = hf.parse_release_date(str(release_date).split(" ")[0])

        # Add one month
        plus_one_month = until_datetime + relativedelta(months=1)

        # Subtract one month
        minus_two_month = until_datetime - relativedelta(months=2)

        # Convert to ISO 8601 format with Zulu time (UTC)
        until_iso = until_datetime.isoformat() + "Z"
        plus_one_iso = plus_one_month.isoformat() + "Z"
        minus_two_iso = minus_two_month.isoformat() + "Z"

        # # Define your search query

        with open(output_file, mode="a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            if first_movie:
                writer.writerow(header)
            response = client.app.bsky.feed.search_posts(
                params=models.AppBskyFeedSearchPosts.Params(
                    q=movie_title,  # 'q' is the query string parameter
                    limit=limit,
                    until=plus_one_iso,
                    since = minus_two_iso
                    #lang='en' #may need to remove; filters out a lot for old movies before bsky was popular
                )
            )
            #Movie title no punctuation:
            cleaned_title = hf.remove_non_ascii(movie_title)
            response2 = client.app.bsky.feed.search_posts(
                params=models.AppBskyFeedSearchPosts.Params(
                    q=cleaned_title,  # 'q' is the query string parameter
                    limit=limit,
                    until=until_iso,
                    since=minus_two_iso
                    #lang='en' #may need to remove; filters out a lot for old movies before bsky was popular
                )
            )
            for post in response.posts:
                text = post.record.text
                kword = movie_title.replace(',','')
                text = text.replace(',','')
                text = text.replace('\n',' ')
                if str(keywords) == 'nan':
                    output_hfsa = 'No Keywords'
                else:
                    output_hfsa = hf.aboutMovie(text,keywords)
                writer.writerow([kword, post.like_count, post.record.created_at, text, hf.get_sentiment(post.record.text), output_hfsa])

                count+=1

            for post in response2.posts:
                text = post.record.text
                kword = movie_title.replace(',','')
                text = text.replace(',','')
                text = text.replace('\n',' ')
                if str(keywords) == 'nan':
                    output_hfsa = "No Keywords"
                else:
                    output_hfsa = hf.aboutMovie(text,keywords)
                writer.writerow([kword, post.like_count, post.record.created_at, text, hf.get_sentiment(post.record.text), output_hfsa])
                count+=1
            print(f"✅ Saved {count} posts to {output_file} from {movie_title} AND {cleaned_title} from date range {minus_two_iso} to {plus_one_iso}")
            first_movie = False