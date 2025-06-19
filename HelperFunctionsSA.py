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
def aboutMovie(post: str, keywords: list) -> float:
    movie_keywords = [
        r"\b(saw|watched|watching|seeing|screening|re-watch(ed)?)\b",
        r"\b(sequel(s)?|prequel|franchise|remake|reboot)\b",
        r"\b(cinema|movie|film|theater|screen|showing|tickets?)\b",
        r"\b(good|bad|amazing|terrible|boring|great|funny|awesome|awful|underrated|overrated)\b",
        r"\b(actor|actress|director|scene|script|trailer|credits|runtime)\b",
        r"letterboxd|imdb",
        r"[🎥🍿👏]"
    ]
    
    post_lower = post.lower()
    title_match = any(word.lower() in post_lower for word in keywords)

    # Score from keyword patterns
    keyword_hits = sum(bool(re.search(pattern, post_lower)) for pattern in movie_keywords)
    total_patterns = len(movie_keywords)

    # Raw score based on matches
    score = keyword_hits / total_patterns  # Normalized between 0 and 1

    # Boost score slightly if title match is found
    if title_match:
        score = min(score + 0.2, 1.0)

    return round(score, 3)

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