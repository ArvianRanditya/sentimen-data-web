import streamlit as st
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# ============================================================
# HALAMAN TOPIK CLUSTER
# ============================================================

def show():

    st.title("📌 Topik Tiap Cluster")
    st.markdown("Menampilkan kata dominan pada setiap cluster (berdasarkan TF-IDF)")

    # ========================================================
    # AMBIL DATA
    # ========================================================

    df = st.session_state.get("final")

    if df is None or "cluster" not in df.columns:
        st.warning("⚠️ Jalankan clustering terlebih dahulu")
        return

    if "clean" not in df.columns:
        st.error("Kolom 'clean' tidak ditemukan")
        return

    # ========================================================
    # AMBIL TF-IDF DARI SESSION (BIAR KONSISTEN)
    # ========================================================

    tfidf = st.session_state.get("tfidf_cluster")

    if tfidf is None:
        st.warning("TF-IDF tidak ditemukan, menggunakan fallback")

        tfidf = TfidfVectorizer(max_features=1000)
        X = tfidf.fit_transform(df["clean"])
    else:
        X = tfidf.transform(df["clean"])

    feature_names = np.array(tfidf.get_feature_names_out())

    # ========================================================
    # CLUSTER LIST
    # ========================================================

    unique_clusters = sorted(df["cluster"].unique())

    # ========================================================
    # LOOP CLUSTER
    # ========================================================

    for cluster_id in unique_clusters:

        st.subheader(f"📍 Cluster {cluster_id}")

        cluster_data = df[df["cluster"] == cluster_id]

        if cluster_data.empty:
            continue

        # ambil index yang valid
        idx = cluster_data.index

        # rata-rata TF-IDF
        cluster_vec = X[idx].mean(axis=0).A1

        top_idx = cluster_vec.argsort()[::-1][:10]

        top_words = feature_names[top_idx]
        top_scores = cluster_vec[top_idx]

        # ====================================================
        # TABEL TOP WORDS
        # ====================================================

        top_df = pd.DataFrame({
            "Kata": top_words,
            "Skor": top_scores
        })

        st.dataframe(top_df, use_container_width=True)

        # ====================================================
        # BAR CHART
        # ====================================================

        st.bar_chart(top_df.set_index("Kata"))

        # ====================================================
        # WORDCLOUD (SAFE MODE)
        # ====================================================

        word_freq = dict(zip(top_words, top_scores))

        if len(word_freq) > 0 and sum(top_scores) > 0:

            wc = WordCloud(
                width=800,
                height=400,
                background_color="white"
            ).generate_from_frequencies(word_freq)

            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")

            st.pyplot(fig)

        else:
            st.info("WordCloud tidak tersedia untuk cluster ini")

    # ========================================================
    # INSIGHT GLOBAL
    # ========================================================

    st.subheader("🧠 Insight Cluster")

    cluster_counts = df["cluster"].value_counts()

    st.dataframe(cluster_counts)

    st.info(f"""
    - Total cluster: **{len(unique_clusters)}**
    - Cluster terbesar: **{cluster_counts.idxmax()}**
    - Cluster terkecil: **{cluster_counts.idxmin()}**
    """)