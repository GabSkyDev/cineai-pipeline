import pandas as pd
from fastapi import HTTPException
import numpy as np

def get_recommendations(title, top_n, df = None, tfidf_matrix = None):
    title = title.lower()

    if title not in df["title_lower"].values:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    idx = df[df["title_lower"] == title].index[0]

    # similaridade sem recalcular tudo
    from sklearn.metrics.pairwise import cosine_similarity
    scores = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()

    # pega top N sem ordenar tudo
    top_indices = np.argsort(scores)[::-1][1:top_n+1]

    results = []
    for i in top_indices:
        results.append({
            "title": df.iloc[i]["title"],
            "score": round(float(scores[i]) * 100, 2)
        })

    return results