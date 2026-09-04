import numpy as np


# ============================================================
# AMBIL TOP WORDS PER CLUSTER (BERDASARKAN CENTROID KMEANS)
# ============================================================

def get_top_words_per_cluster(kmeans_model, tfidf_vectorizer, n_terms=10):
    """
    Output:
    {
        0: ['kelas', 'ruang', ...],
        1: ['bersih', 'nyaman', ...],
        ...
    }
    """

    terms = tfidf_vectorizer.get_feature_names_out()
    centroids = kmeans_model.cluster_centers_

    top_words = {}

    for i, center in enumerate(centroids):
        top_indices = center.argsort()[-n_terms:][::-1]
        top_words[i] = [terms[idx] for idx in top_indices]

    return top_words


# ============================================================
# KONVERSI KE FORMAT DATAFRAME (UNTUK TABEL UI)
# ============================================================

def top_words_to_df(top_words_dict):
    """
    Output dataframe:
    cluster | word_1 | word_2 | ...
    """

    data = []

    for cluster_id, words in top_words_dict.items():
        row = {"cluster": cluster_id}
        for i, w in enumerate(words):
            row[f"word_{i+1}"] = w
        data.append(row)

    return data


# ============================================================
# FORMAT UNTUK VISUALISASI BAR CHART
# ============================================================

def get_top_words_freq(top_words_dict):
    """
    Flatten untuk chart
    """

    data = []

    for cluster_id, words in top_words_dict.items():
        for w in words:
            data.append({
                "cluster": cluster_id,
                "word": w
            })

    return data