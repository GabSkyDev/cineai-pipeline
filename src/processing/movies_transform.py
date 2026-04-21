import pandas as pd
import json
import logging
from pathlib import Path
from datetime import datetime
from src.processing.text_cleaning import clean_text
from src.utils.logger import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

RAW_PATH = Path(f"data/raw/movies_raw_{datetime.now().strftime("%Y-%m-%d")}.json")
GENRE_PATH = Path(f"data/raw/genres_{datetime.now().strftime("%Y-%m-%d")}.json")
PROCESSED_PATH = Path("data/processed/movies.parquet")

def load_raw():
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    

def load_genres_map():
    with open(GENRE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        int(k): v
        for k, v in data.items()
    }

def process_movies(data, genre_map):
    df = pd.DataFrame(data)

    df = df[[
        "id",
        "title",
        "overview",
        "genre_ids",
        "popularity",
        "vote_average",
        "release_date",
        "adult"
    ]]

    df = df.dropna(subset=["title", "overview", "release_date"])

    df["genres"] = df["genre_ids"].apply(
        lambda ids: [genre_map.get(genre_id, "Unknown") for genre_id in ids] 
    )

    df["overview"] = df["overview"].apply(clean_text)

    df["content"] = df["overview"] + " " + df["genres"].apply(lambda x: " ".join([g.lower() for g in x]) if isinstance(x, list) else "")

    df = df.drop_duplicates(subset="id")

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    return df

def save_processed(df):
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_PATH, index=False)

if __name__ == "__main__":
    raw_data = load_raw()

    genre_map = load_genres_map()

    df = process_movies(raw_data, genre_map)
    save_processed(df)

    logger.info(f"Dados processados salvos. Local: {PROCESSED_PATH}.")
    print("Dados processados salvos.")