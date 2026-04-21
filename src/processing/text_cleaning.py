import re
from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words("english"))

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    # lowercase
    text = text.lower()

    # remove pontuação e números
    text = re.sub(r"[^a-z\s]", "", text)

    # tokenização simples
    words = text.split()

    # remove stopwords
    words = [word for word in words if word not in STOPWORDS]

    # junta novamente
    return " ".join(words)
