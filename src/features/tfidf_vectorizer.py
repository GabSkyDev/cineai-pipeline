import pandas as pd
import joblib
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
from src.utils.logger import setup_logger

PROCESSED_PATH = Path("data/processed/movies.parquet")
FEATURES_PATH = Path("data/features/tfidf_matrix.joblib")
VECTORIZER_PATH = Path("data/features/tfidf_vectorizer.joblib")

setup_logger()
logger = logging.getLogger(__name__)

def load_processed():
    return pd.read_parquet(PROCESSED_PATH)

def build_tfidf(df):
    # Word TF-IDF (sinopse + gêneros + título repetido)
    word_vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=25000,
        ngram_range=(1, 2),
        max_df=0.85,
        min_df=2,
        sublinear_tf=True,
        norm="l2",
    )

    # Char TF-IDF no título: melhora muito matching de nomes curtos/variações
    char_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        sublinear_tf=True,
        norm="l2",
    )

    word_matrix = word_vectorizer.fit_transform(df["content"].fillna(""))
    title_col = df["title_clean"] if "title_clean" in df.columns else df["title"]
    char_matrix = char_vectorizer.fit_transform(title_col.fillna("").astype(str))

    # Dá um peso extra ao título (ajusta “proximidade por nome”)
    tfidf_matrix = hstack([word_matrix, 2.0 * char_matrix]).tocsr()

    return tfidf_matrix, {"word": word_vectorizer, "char": char_vectorizer}

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