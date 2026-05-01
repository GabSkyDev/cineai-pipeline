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

setup_logger()
logger = logging.getLogger(__name__)

def _get_config():
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL") or "https://api.themoviedb.org/3"
    if not api_key:
        raise RuntimeError("API_KEY não definido. Configure API_KEY no ambiente ou em um arquivo .env.")
    return api_key, base_url

def fetch_genres():
    api_key, base_url = _get_config()
    url = f"{base_url}/genre/movie/list"
    params = {
        "api_key": api_key,
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