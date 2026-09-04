import re
import string
import nltk
from functools import lru_cache

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords

# ============================================================
# DOWNLOAD NLTK (AMAN)
# ============================================================

try:
    nltk.data.find('corpora/stopwords')
except:
    nltk.download('stopwords')

# ============================================================
# INIT
# ============================================================

stop_words = set(stopwords.words('indonesian'))
custom_stopwords = {
    "universitas", "wahid", "hasyim", "unwahas", "kampus", "semarang",
    "unwahasnya", "wahidhasyim", "unisma", "kampusnya"
}
stop_words.update(custom_stopwords)

factory = StemmerFactory()
stemmer = factory.create_stemmer()

# ============================================================
# NORMALISASI KATA TIDAK BAKU
# ============================================================

slang_dict = {
    "yg": "yang",
    "gk": "tidak",
    "ga": "tidak",
    "nggak": "tidak",
    "dr": "dari",
    "utk": "untuk",
    "krn": "karena",
    "dgn": "dengan",
    "aja": "",
    "nya": "",
}


# ============================================================
# CLEANING TEXT
# ============================================================

def clean_text(text):

    text = str(text).lower()

    # hapus URL
    text = re.sub(r'http\S+', '', text)

    # hapus angka
    text = re.sub(r'\d+', '', text)

    # hapus tanda baca
    text = text.translate(str.maketrans('', '', string.punctuation))

    # hapus karakter aneh
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # hapus spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# ============================================================
# NORMALISASI SLANG
# ============================================================

def normalize_slang(text):

    tokens = text.split()

    normalized = [
        slang_dict[word]
        if word in slang_dict
        else word
        for word in tokens
    ]

    return " ".join(normalized)

# ============================================================
# TOKENIZE + STOPWORD
# ============================================================

def remove_stopwords(text):

    tokens = text.split()

    filtered = [word for word in tokens if word not in stop_words]

    return " ".join(filtered)


# ============================================================
# STEMMING DENGAN LRU CACHE
# ============================================================

@lru_cache(maxsize=10000)
def stem_word(word):
    return stemmer.stem(word)

def stemming(text):
    tokens = text.split()
    return " ".join([stem_word(token) for token in tokens])



# ============================================================
# PIPELINE UTAMA
# ============================================================
def preprocess_pipeline(text):

    text = clean_text(text)

    # normalisasi kata tidak baku
    text = normalize_slang(text)

    # hapus stopword
    text = remove_stopwords(text)

    # stemming
    text = stemming(text)

    return text