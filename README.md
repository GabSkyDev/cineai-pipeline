## CineAI Pipeline

Pipeline de dados + sistema de recomendação de filmes baseado em similaridade textual (TF‑IDF), com interface em Streamlit e API em FastAPI.

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikitlearn&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-data-150458?logo=pandas&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

### Objetivo

Criar uma **pipeline de dados** que:

- Ingesta dados de filmes a partir de uma API (TMDB)
- Realiza limpeza/transformação e gera um dataset processado
- Treina um modelo de **TF‑IDF** para recomendação por similaridade
- Exponha recomendações via **FastAPI**
- Permita testes fáceis via **Streamlit** (modo demo)

O projeto é voltado para **portfólio/treino**, priorizando clareza de pipeline, reprodutibilidade e uma experiência simples para quem quer testar.

### Principais features

- **Recomendação por similaridade** com TF‑IDF (word + char n‑grams) e cosseno
- **Auto-correção de entrada**: o usuário pode digitar algo próximo do título, e o sistema tenta encontrar o melhor match antes de recomendar
- **UI pronta para demo**: sidebar para colar `API_KEY` e botão para rodar a pipeline (gera artifacts)

### Estrutura do projeto

```
cineai-pipeline/
├─ app/
│  └─ run_pipeline.py                # Orquestrador (ingestão → processamento → features)
├─ src/
│  ├─ api/
│  │  └─ main.py                     # FastAPI (/recommend)
│  ├─ features/
│  │  └─ tfidf_vectorizer.py         # Treino e persistência dos vetores TF‑IDF
│  ├─ ingestion/
│  │  ├─ tmdb_client.py              # Coleta de filmes (TMDB)
│  │  └─ genres_client.py            # Coleta de gêneros (TMDB)
│  ├─ model/
│  │  └─ recommender.py              # Similaridade + auto-correção
│  ├─ processing/
│  │  ├─ movies_transform.py         # Transformações e montagem do "content"
│  │  └─ text_cleaning.py            # Limpeza/normalização de texto
│  └─ frontend/
│     └─ app.py                      # Streamlit (UI)
├─ data/
│  ├─ raw/                           # JSON bruto (TMDB)
│  ├─ processed/                     # Parquet processado
│  └─ features/                      # Artifacts (.joblib)
└─ requirements.txt
```

### Fluxo da pipeline

1. **Ingestão**
   - Coleta filmes populares e o mapa de gêneros via TMDB
   - Salva em `data/raw/` (timestamped)
2. **Processamento**
   - Filtra, limpa e monta uma coluna `content` (título + gêneros + sinopse)
   - Salva em `data/processed/movies.parquet`
3. **Features (TF‑IDF)**
   - Gera matriz TF‑IDF híbrida:
     - TF‑IDF por palavras do `content`
     - TF‑IDF por caracteres do título (melhora match de nomes)
   - Salva artifacts em `data/features/`
4. **Serving**
   - FastAPI lê `movies.parquet` e a matriz TF‑IDF
   - Endpoint `/recommend` retorna o top‑N por similaridade
5. **UI**
   - Streamlit chama a API para recomendar
   - Sidebar permite rodar a pipeline com a `API_KEY` (modo demo)

### Como rodar

#### Pré‑requisitos

- **Python 3.12+**
- Uma chave de API do TMDB (você vai colar direto na UI)

#### 1) Criar e ativar o ambiente virtual

No Windows (PowerShell), na raiz do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Se o seu PowerShell bloquear o activate:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

#### 2) Rodar a pipeline (opcional)

> No modo demo, **não é necessário** criar `.env` nem exportar variável de ambiente.
> Você cola a `TMDB API Key` na sidebar do Streamlit e clica em **Rodar pipeline**.

Se quiser rodar manualmente via terminal:

```powershell
python -m app.run_pipeline
```

Ou pular ingestão (usa raw existente):

```powershell
python -m app.run_pipeline --no-ingest
```

#### 3) Subir a API (FastAPI)

Se a execução direta do `uvicorn.exe` estiver bloqueada por políticas do Windows, rode via módulo:

```powershell
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

#### 4) Rodar o frontend (Streamlit)

```powershell
python -m streamlit run src/frontend/app.py
```

No modo demo:

- Cole a `TMDB API Key` na sidebar
- Clique em **Rodar pipeline**
- Faça as buscas na tela principal

> Importante: por padrão, o Streamlit consome a API em `http://127.0.0.1:8000`.
> Então, para pesquisar/recomendar, mantenha o FastAPI rodando também.

### API

#### `GET /recommend`

Parâmetros:
- `movie` (str): texto do usuário (título ou aproximado)
- `top_n` (int): quantidade de recomendações

Resposta:
- Lista de recomendações **ou** um objeto com `matched_title` quando houve auto-correção.

### Decisões técnicas (resumo)

- **TF‑IDF + cosine similarity**: baseline simples, rápido e explicável para portfólio.
- **Word + char n‑grams**: melhora matching de títulos curtos, variações e pequenos typos.
- **Auto-correção**: quando o título digitado não existe no catálogo, escolhe o melhor match (com threshold) antes de recomendar.

### Limitações conhecidas

- TF‑IDF não entende semântica: pode haver recomendações por “palavra em comum” (ex.: títulos com o mesmo termo).
- Quanto mais rico o dataset (cast, diretor, keywords, etc.), melhor a qualidade de recomendação.

### Próximos passos (ideias)

- Enriquecer base com dados do endpoint de detalhes do TMDB (cast/diretor/keywords/tagline)
- Adicionar modo “semantic search” com embeddings (ex.: `sentence-transformers`) e comparação com o baseline TF‑IDF
- Cache e persistência de artifacts por versão/dia para demos mais rápidas

### Conclusão

O CineAI Pipeline organiza, de ponta a ponta, um fluxo real de dados (ingestão → tratamento → features → serving) e entrega uma aplicação pronta para ser testada por qualquer pessoa. É um projeto ótimo para demonstrar **engenharia de dados aplicada**, **ML clássico** e **deploy local** com API + UI.

