import requests
import time
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from src.utils.logger import setup_logger

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

OUTPUT_PATH = Path("data/raw/movies_raw.json")

setup_logger()
logger = logging.getLogger(__name__)

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
        logger.info(f"Coletando página {page}")

        try:
            data = fetch_movies(page)
            results = data.get("results", [])

            all_movies.extend(results)

        except Exception as e:
            logger.error(f"Erro ao coletar página {page}: {e}")

        time.sleep(0.3)  # evitar rate limit

    logger.info(f"Total de filmes coletados: {len(all_movies)}")
    
    return all_movies


def save_raw(data):
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_file = Path(f"data/raw/movies_raw_{timestamp}.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    movies = ingest_movies(max_pages=10)
    save_raw(movies)

    logger.info(f"Quantidade de filmes salvos em '{OUTPUT_PATH}': {len(movies)} filmes.")