import re
import unicodedata

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def _load_stopwords() -> set[str]:
    sw: set[str] = set(ENGLISH_STOP_WORDS)
    try:
        from nltk.corpus import stopwords  # type: ignore
        sw |= set(stopwords.words("english"))
        sw |= set(stopwords.words("portuguese"))
    except Exception:
        # Fallback leve (evita quebrar se o corpus do NLTK não estiver baixado)
        sw |= {
            "de", "da", "do", "das", "dos", "um", "uma", "uns", "umas",
            "e", "ou", "em", "no", "na", "nos", "nas",
            "para", "por", "com", "sem", "sobre", "entre",
            "que", "como", "mais", "menos", "muito", "pouco",
        }
    return sw

STOPWORDS = _load_stopwords()

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    # lowercase
    text = text.lower()

    # normaliza acentos (ex.: "ação" -> "acao") e remove caracteres não-alfabéticos
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # tokenização simples
    words = text.split()

    # remove stopwords
    words = [word for word in words if word not in STOPWORDS]

    # junta novamente
    return " ".join(words)
