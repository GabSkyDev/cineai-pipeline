import pandas as pd
import joblib
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from src.utils.logger import setup_logger

PROCESSED_PATH = Path("data/processed/movies.parquet")
FEATURES_PATH = Path("data/features/tfidf_matrix.joblib")
VECTORIZER_PATH = Path("data/features/tfidf_vectorizer.joblib")

setup_logger()
logger = logging.getLogger(__name__)

def load_processed():
    return pd.read_parquet(PROCESSED_PATH)

def build_tfidf(df):
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000, 
        ngram_range=(1, 2)
    )

    tfidf_matrix = vectorizer.fit_transform(df["content"])

    return tfidf_matrix, vectorizer

def save_artifacts(matrix, vectorizer):
    FEATURES_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(matrix, FEATURES_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

if __name__ == "__main__":
    df = load_processed()

    tfidf_matrix, vectorizer = build_tfidf(df)

    save_artifacts(tfidf_matrix, vectorizer)

    logger.info("TF-IDF gerado com sucesso!")
    logger.info(f"Local de arquivo matrix: {FEATURES_PATH}.")
    logger.info(f"Local de arquivo vectorizer: {VECTORIZER_PATH}.")