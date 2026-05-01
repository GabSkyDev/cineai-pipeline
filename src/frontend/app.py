import streamlit as st
import requests
import subprocess
import sys
import os
from pathlib import Path

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Cine AI - Pipeline", layout="centered")

# ---------- SIDEBAR (DEMO SETUP) ----------
st.sidebar.header("Configuração")

api_key = st.sidebar.text_input("TMDB API Key", type="password", help="Cole sua chave da API do TMDB.")
base_url = st.sidebar.text_input("TMDB Base URL", value="https://api.themoviedb.org/3")

ingest_enabled = st.sidebar.toggle("Rebaixar dados (ingestão)", value=True, help="Se desligado, usa os raw já existentes.")

def _artifacts_ready() -> bool:
    root = Path(__file__).resolve().parents[2]
    return (
        (root / "data/processed/movies.parquet").exists()
        and (root / "data/features/tfidf_matrix.joblib").exists()
        and (root / "data/features/tfidf_vectorizer.joblib").exists()
    )

run_pipeline = st.sidebar.button("Rodar pipeline", type="primary", use_container_width=True)

if run_pipeline:
    if not api_key:
        st.sidebar.error("Informe a TMDB API Key para rodar a ingestão.")
    else:
        env = os.environ.copy()
        env["API_KEY"] = api_key
        env["BASE_URL"] = base_url.strip()

        cmd = [sys.executable, "-m", "app.run_pipeline"]
        if not ingest_enabled:
            cmd.append("--no-ingest")

        with st.spinner("Rodando pipeline (ingestão → processamento → features)..."):
            proc = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if proc.returncode == 0:
            st.sidebar.success("Pipeline concluída! Pode testar as buscas.")
        else:
            st.sidebar.error("Pipeline falhou. Veja os logs abaixo.")
            st.sidebar.code((proc.stdout or "") + "\n" + (proc.stderr or ""))

st.sidebar.divider()
if _artifacts_ready():
    st.sidebar.success("Artifacts prontos para recomendação.")
else:
    st.sidebar.warning("Artifacts ainda não gerados. Clique em 'Rodar pipeline'.")

# ---------- ESTILO ----------
st.markdown("""
<style>
.card {
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    color: white;
    font-weight: 500;
}
.title {
    font-size: 18px;
}
.score {
    font-size: 14px;
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("🩸 Cine AI 🩸")
st.caption("Sistema de recomendação de filmes baseado em similaridade!")

# ---------- INPUT ----------
movie_name = st.text_input("Digite o nome de um filme")

top_n = st.slider("Quantidade de recomendações", 1, 10, 5)

def get_tier_color(rank: int) -> str:
    # Cores por TIER (posição no ranking), não por %.
    # 1: destaque | 2-3: forte | 4-6: ok | 7+: fraco/ruído
    if rank == 1:
        return "#7c3aed"  # roxo
    if rank in (2, 3):
        return "#16a34a"  # verde
    if 4 <= rank <= 6:
        return "#ca8a04"  # amarelo
    return "#334155"  # cinza/azulado

def get_confidence_label(items: list[dict]) -> tuple[str, str]:
    # Confiança pelo “gap” entre o topo e o fim do top-N
    # (cosine similarity não é probabilidade, então evitamos dar “% de certeza”).
    scores = [float(x.get("score", 0.0)) for x in items]
    if len(scores) < 2:
        return ("Alta", "#16a34a")

    top = scores[0]
    tail = scores[-1]
    gap = top - tail

    if gap >= 20:
        return ("Alta", "#16a34a")
    if gap >= 10:
        return ("Média", "#ca8a04")
    return ("Baixa", "#dc2626")

# ---------- BOTÃO ----------
if st.button("Recomendar"):
    if not movie_name:
        st.warning("Digite um filme.")
    elif not _artifacts_ready():
        st.warning("Rode a pipeline primeiro (sidebar) para gerar os artifacts.")
    else:
        try:
            with st.spinner("Buscando recomendações..."):
                response = requests.get(
                    f"{API_URL}/recommend",
                    params={"movie": movie_name, "top_n": top_n}
                )

            if response.status_code == 200:
                data = response.json()

                st.markdown("---")
                rec = data.get("recommendation")
                if isinstance(rec, dict) and "matched_title" in rec:
                    st.subheader(f'Recomendações para "{data["input"]}"')
                    st.caption(f'Auto-correção: usando "{rec["matched_title"]}" ({rec.get("matched_score", 0)}%)')
                    items = rec.get("items", [])
                else:
                    st.subheader(f'Recomendações para "{data["input"]}"')
                    items = rec if isinstance(rec, list) else []

                if items:
                    label, color = get_confidence_label(items)
                    st.markdown(
                        f"<div style='margin: 6px 0 14px 0;'>"
                        f"<span style='background:{color}; color:white; padding:6px 10px; border-radius:999px; font-weight:600;'>"
                        f"Confiança: {label}"
                        f"</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                for i, rec_item in enumerate(items, start=1):
                    color = get_tier_color(i)

                    st.markdown(f"""
                    <div class="card" style="background-color:{color}">
                        <div class="title">{i}. {rec_item['title']}</div>
                        <div class="score">Similaridade: {rec_item['score']}%</div>
                    </div>
                    """, unsafe_allow_html=True)

            elif response.status_code == 404:
                st.error("Filme não encontrado.")
            else:
                st.error("Erro na API.")

        except requests.exceptions.ConnectionError:
            st.error("API não está rodando.")