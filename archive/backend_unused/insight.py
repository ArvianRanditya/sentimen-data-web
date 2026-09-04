import pandas as pd


# ============================================================
# HITUNG DISTRIBUSI SENTIMEN
# ============================================================

def get_sentiment_summary(df):
    return df['sentimen'].value_counts()


# ============================================================
# SENTIMEN DOMINAN
# ============================================================

def get_dominant_sentiment(df):
    counts = df['sentimen'].value_counts()
    return counts.idxmax()


# ============================================================
# SENTIMEN PER CLUSTER
# ============================================================

def get_sentiment_per_cluster(df):
    return pd.crosstab(df['cluster_label'], df['sentimen'])

def get_cluster_sentiment_distribution(df):

    table = pd.crosstab(df['cluster_label'], df['sentimen'])

    result = []

    for cluster in table.index:

        result.append({
            "cluster": cluster,
            "positif": int(table.loc[cluster].get('positif', 0)),
            "netral": int(table.loc[cluster].get('netral', 0)),
            "negatif": int(table.loc[cluster].get('negatif', 0)),
        })

    return result

# ============================================================
# TOPIK PER CLUSTER
# ============================================================

def get_cluster_topics(df, top_n=5):

    topics = []

    for cluster in sorted(df['cluster_label'].unique()):

        subset = df[df['cluster_label'] == cluster]

        # gabungkan semua text clean
        text = ' '.join(subset['clean'].astype(str))

        words = text.split()

        # hitung kata paling sering
        freq = pd.Series(words).value_counts().head(top_n)

        topics.append({
            "cluster": cluster,
            "keywords": freq.index.tolist()
        })

    return topics


# ============================================================
# RINGKASAN GLOBAL
# ============================================================

def generate_global_insight(df):

    total = len(df)
    dominant = get_dominant_sentiment(df)
    most_pos = get_most_positive_cluster(df)
    most_neg = get_most_negative_cluster(df)

    cluster_distribution = get_cluster_sentiment_distribution(df)
    cluster_topics = get_cluster_topics(df)

    insight = {
        "total_data": total,
        "sentimen_dominan": dominant,
        "cluster_terbaik": most_pos,
        "cluster_terburuk": most_neg,

        # TAMBAHAN BARU
        "cluster_distribution_detail": cluster_distribution
        "cluster_topics": cluster_topics
    }

    return insight