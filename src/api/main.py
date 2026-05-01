from fastapi import FastAPI
from pathlib import Path
from src.model.recommender import get_recommendations
import joblib
import pandas as pd

app = FastAPI(title = "CineAI - Pipeline")

BASE_PATH = Path(__file__).resolve().parents[2] 

DATA_PATH = BASE_PATH / "data/processed/movies.parquet"
TFIDF_PATH = BASE_PATH / "data/features/tfidf_matrix.joblib"
VECTORIZER_PATH = BASE_PATH / "data/features/tfidf_vectorizer.joblib"

df = pd.read_parquet(DATA_PATH)
tfidf_matrix = joblib.load(TFIDF_PATH)
vectorizers = joblib.load(VECTORIZER_PATH)

df["title_lower"] = df["title"].str.lower()

# Endpoint principal
@app.get("/recommend")
def recommend(movie: str, top_n: int = 5):
    return {
        "input": movie,
        "recommendation": get_recommendations(movie, top_n, df, tfidf_matrix, vectorizers)
    }