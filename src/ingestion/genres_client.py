import requests
import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from src.utils.logger import setup_logger
from pathlib import Path

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

setup_logger()
logger = logging.getLogger(__name__)

def fetch_genres():
    url = f"{BASE_URL}/genre/movie/list"
    params = {
        "api_key": API_KEY,
        "language": "en"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Erro na API: {response.status_code}")
    
    data = response.json()

    return {
        genre["id"]: genre["name"]
        for genre in data["genres"]
    }

def save_genres(genre_map):
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_file = Path(f"data/raw/genres_{timestamp}.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(genre_map, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    genre_map = fetch_genres()
    save_genres(genre_map)
    logger.info(f"Total de gêneros coletados: {len(genre_map)}")