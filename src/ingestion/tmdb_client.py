import requests
import time
import json
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

OUTPUT_PATH = Path("data/raw/movies_raw.json")


def fetch_movies(page: int):
    url = f"{BASE_URL}/movie/popular"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "page": page
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Erro na API: {response.status_code}")

    return response.json()


def ingest_movies(max_pages=5):
    all_movies = []

    for page in range(1, max_pages + 1):
        print(f"Coletando página {page}...")

        data = fetch_movies(page)
        results = data.get("results", [])

        all_movies.extend(results)

        time.sleep(0.3)  # evitar rate limit

    return all_movies


def save_raw(data):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("API_KEY:", API_KEY)
    print("BASE_URL:", BASE_URL)
    movies = ingest_movies(max_pages=10)
    save_raw(movies)

    print(f"{len(movies)} filmes salvos em RAW.")