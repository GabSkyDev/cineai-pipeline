import pandas as pd
from fastapi import HTTPException
import numpy as np

def get_recommendations(title, top_n, df = None, tfidf_matrix = None, vectorizers = None):
    raw_query = str(title)
    title = raw_query.lower().strip()

    # auto-correção: se não for match exato, busca o título mais provável
    matched_title = None
    matched_score = None

    if title not in df["title_lower"].values:
        if not vectorizers or "word" not in vectorizers or "char" not in vectorizers:
            raise HTTPException(status_code=404, detail="Filme não encontrado")

        from scipy.sparse import hstack
        from sklearn.metrics.pairwise import cosine_similarity
        from src.processing.text_cleaning import clean_text

        word_vectorizer = vectorizers["word"]
        char_vectorizer = vectorizers["char"]

        cleaned = clean_text(raw_query)
        query_word = word_vectorizer.transform([cleaned])
        query_char = char_vectorizer.transform([cleaned])
        query_vec = hstack([query_word, 2.0 * query_char]).tocsr()

        match_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
        best_idx = int(np.argmax(match_scores))
        best_score = float(match_scores[best_idx])

        # limite mínimo para evitar "chutes" ruins
        if best_score < 0.25:
            raise HTTPException(status_code=404, detail="Filme não encontrado")

        idx = best_idx
        matched_title = df.iloc[idx]["title"]
        matched_score = round(best_score * 100, 2)
    else:
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

    if matched_title is not None:
        # adiciona informação de auto-correção sem quebrar o frontend (campo extra)
        return {
            "matched_title": matched_title,
            "matched_score": matched_score,
            "items": results
        }

    return results