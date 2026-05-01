import logging
import argparse
from src.utils.logger import setup_logger
from src.ingestion.tmdb_client import ingest_movies, save_raw
from src.ingestion.genres_client import fetch_genres, save_genres
from src.processing.movies_transform import (
    process_movies,
    load_raw,
    load_genres_map,
    save_processed
)
from src.features.tfidf_vectorizer import (
    load_processed,
    build_tfidf,
    save_artifacts
)

setup_logger()
logger = logging.getLogger(__name__)

def run_ingestion():
    logger.info("Iniciando ingestão de filmes...")
    movies = ingest_movies(250) # 250 x 20 = 5000 filmes
    genres = fetch_genres()

    save_raw(movies)
    save_genres(genres)
    logger.info("Ingestão finalizada.")


def run_processing():
    logger.info("Iniciando processamento...")

    raw_data = load_raw()
    genre_map = load_genres_map()

    df = process_movies(raw_data, genre_map)
    save_processed(df)

    logger.info("Processamento finalizado.")


def run_features():
    logger.info("Iniciando geração de features (TF-IDF)...")

    df = load_processed()
    tfidf_matrix, vectorizer = build_tfidf(df)

    save_artifacts(tfidf_matrix, vectorizer)

    logger.info("Features geradas com sucesso.")


def main(ingest: bool = True):
    logger.info("===== INÍCIO DO PIPELINE =====")

    if ingest:
        run_ingestion()
    run_processing()
    run_features()

    logger.info("===== PIPELINE FINALIZADO =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CineAI pipeline runner")
    parser.add_argument(
        "--no-ingest",
        action="store_true",
        help="Pula ingestão e usa os arquivos raw já existentes",
    )
    args = parser.parse_args()
    main(ingest=not args.no_ingest)
