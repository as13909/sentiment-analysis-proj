import kagglehub
import pandas as pd
import os
import regex as re
from datetime import datetime
from textblob import TextBlob

#original fields: ['id', 'title', 'vote_average', 'vote_count', 'status', 'release_date',
    #    'revenue', 'runtime', 'adult', 'backdrop_path', 'budget', 'homepage',
    #    'imdb_id', 'original_language', 'original_title', 'overview',
    #    'popularity', 'poster_path', 'tagline', 'genres',
    #    'production_companies', 'production_countries', 'spoken_languages',
    #    'keywords']

def return_formatted_file() -> pd.DataFrame:
    #fields returned: title, release_date, vote_count, vote_average, genres, original_language
    path = kagglehub.dataset_download("asaniczka/tmdb-movies-dataset-2023-930k-movies")

    fullpath = os.path.join(path,os.listdir(path)[0])
    data = pd.read_csv(fullpath)
    data = data[['title','release_date','vote_count','vote_average', 'genres', 'original_language', 'keywords', 'popularity']]
    data.release_date = pd.to_datetime(data.release_date, errors='coerce')
    data = data[(data['release_date'] >= pd.to_datetime('2018-01-01')) & (data['original_language'] == 'en')]
    return data

#checks if tweet is about a movie and gives a similiartiy ranking
#Should expand the range to have a confidence score. True False is too limiting!!!!
def aboutMovie(post: str, keywords: list) -> int:
    movie_keywords = [
    r"\b(saw|watched|watching|seeing|screening|re-watch(ed)?)\b",
    r"\b(cinema|movie|film|theater|screen|showing|tickets?)\b",
    r"\b(good|bad|amazing|terrible|boring|great|funny|awesome|awful|underrated|overrated)\b",
    r"[🎥🍿👏]"
    ]
    # text = text.lower()
    # movie_words = ['movie', 'film', 'cinema', 'flick', 'show', 'watch', 'seen', 'actor', 'actress', 'director', 'scene', 'plot', 'story', 'character', 'trailer', 'screenplay', 'blockbuster', 'indie', 'documentary', 'animation', 'drama', 'comedy', 'horror', 'thriller', 'romance', 'sci-fi', 'fantasy']
    # score = 0
    # for word in movie_words:
    #     if word in text:
    #         score += 1
    # return score
    post_lower = post.lower()
    title_match = any(word in post_lower for word in keywords)

    # Check if any movie-related keyword matches
    keyword_match = any(re.search(pattern, post_lower) for pattern in movie_keywords)
    
    return title_match and keyword_match


#32 (space)
#48-57 (nums)
#65-90 (A-Z)
#97-122 (a-z)
def remove_non_ascii(text):
    out = ''.join(char for char in text if ord(char) in range(48, 58) or ord(char) in range(65, 91) or ord(char) in range(97, 123) or ord(char) == 32)
    out = out.replace('\n','')
    out = out.replace('  ',' ')
    return out

def parse_release_date(date_str):
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Date format not recognized: {date_str}")

def get_sentiment(text):
    return round(TextBlob(text).sentiment.polarity, 4)


KnownMovies = [
    "Black Panther: Wakanda Forever",
    "Avatar: The Way of Water",
    "Top Gun: Maverick",
    "Doctor Strange in the Multiverse of Madness",
    "Jurassic World: Dominion",
    "The Batman",
    "Spider"]