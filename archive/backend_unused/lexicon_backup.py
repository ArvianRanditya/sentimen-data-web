import pandas as pd
import os

# ============================================================
# LOAD LEXICON CSV (SAFE PATH + FIX DELIMITER)
# ============================================================

def load_lexicon():

    base_path = os.path.dirname(os.path.abspath(__file__))
    lex_path = os.path.join(base_path, "..", "lexicon")

    pos_path = os.path.join(lex_path, "positive.csv")
    neg_path = os.path.join(lex_path, "negative.csv")

    # ========================================================
    # VALIDASI FILE
    # ========================================================

    if not os.path.exists(pos_path):
        raise FileNotFoundError(f"File tidak ditemukan: {pos_path}")

    if not os.path.exists(neg_path):
        raise FileNotFoundError(f"File tidak ditemukan: {neg_path}")

    # ========================================================
    # FIX: CSV PAKAI DELIMITER ;
    # ========================================================

    pos_df = pd.read_csv(pos_path, sep=";")
    neg_df = pd.read_csv(neg_path, sep=";")

    # rapikan kolom
    pos_df.columns = pos_df.columns.str.lower().str.strip()
    neg_df.columns = neg_df.columns.str.lower().str.strip()

    lexicon = {}

    # ========================================================
    # POSITIVE
    # ========================================================
    for _, row in pos_df.iterrows():
        word = str(row["word"]).strip().lower()
        weight = float(row["weight"])
        lexicon[word] = weight

    # ========================================================
    # NEGATIVE
    # ========================================================
    for _, row in neg_df.iterrows():
        word = str(row["word"]).strip().lower()
        weight = float(row["weight"])
        lexicon[word] = weight

    return lexicon


# ============================================================
# HITUNG SKOR SENTIMEN
# ============================================================

def calculate_sentiment_score(text, lexicon):

    if pd.isna(text):
        return 0

    words = str(text).split()

    score = 0

    negation_words = [
        "tidak",
        "tak",
        "bukan",
        "kurang",
        "ga",
        "gak",
        "nggak"
    ]

    for i, w in enumerate(words):

        if w in lexicon:

            word_score = lexicon[w]

            # cek negasi
            if i > 0 and words[i - 1] in negation_words:
                word_score *= -1

            score += word_score

    return score


# ============================================================
# KONVERSI SCORE → LABEL
# ============================================================

def score_to_label(score):
    print("LEXICON BARU AKTIF")

    if score >= 1.5:
        return 2  # positif

    elif score <= -1.5:
        return 0  # negatif

    else:
        return 1  # netral


# ============================================================
# PIPELINE LABELING
# ============================================================

def label_sentiment_lexicon(df, text_column="clean"):

    lexicon = load_lexicon()
    df = df.copy()

    scores = []
    labels = []

    for text in df[text_column]:
        score = calculate_sentiment_score(text, lexicon)
        label = score_to_label(score)

        scores.append(score)
        labels.append(label)

    df["sentiment_score"] = scores
    df["sentiment_label"] = labels

    return df