import streamlit as st
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score

import matplotlib.pyplot as plt

# ============================================================
# HALAMAN CLUSTERING K-MEANS
# ============================================================

def show():

    st.title("📊 Clustering K-Means (Exploration → Clustering)")
    st.markdown("Tahap: Elbow + Silhouette → pilih K → clustering final")

    # ========================================================
    # AMBIL DATA
    # ========================================================

    df = st.session_state.get("preprocessed")

    if df is None:
        st.warning("⚠️ Lakukan preprocessing terlebih dahulu")
        return

    if "clean" not in df.columns:
        st.write(df.columns)
        st.error("Kolom 'clean' tidak ditemukan")
        return

    # ========================================================
    # TF-IDF
    # ========================================================

    st.subheader("🔤 TF-IDF Transform")

    tfidf = TfidfVectorizer(max_features=1000)
    X = tfidf.fit_transform(df["clean"])

    st.session_state["tfidf_cluster"] = tfidf
    st.session_state["X_cluster"] = X

    n_samples = X.shape[0]

    if n_samples < 3:
        st.error("Data terlalu sedikit untuk clustering (minimal 3 data)")
        return

    # ========================================================
    # RANGE K AMAN
    # ========================================================

    max_k = min(10, n_samples - 1)
    K_range = range(2, max_k + 1)

    # ========================================================
    # ELBOW & SILHOUETTE (VISUAL + TABLE)
    # ========================================================

    st.subheader("📉 Elbow Method & Silhouette Score")

    inertia = []
    sil_scores = []
    ch_scores = []

    for k in K_range:

        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)

        #ellbow
        inertia.append(km.inertia_)

        #silhouette
        if len(set(labels)) > 1:
            sil = silhouette_score(X, labels)
        else:
            sil = 0

        sil_scores.append(sil)

        # CALINSKI HARABASZ
        ch = calinski_harabasz_score(X.toarray(), labels)
        ch_scores.append(ch)

    # ========================================================
    # TABEL HASIL
    # ========================================================

    result_df = pd.DataFrame({
        "K": list(K_range),
        "Inertia (Elbow)": inertia,
        "Silhouette Score": sil_scores,
        "Calinski Harabasz": ch_scores
    })

    st.dataframe(result_df, use_container_width=True)

    # ========================================================
    # PLOT ELBOW
    # ========================================================

    fig1, ax1 = plt.subplots()
    ax1.plot(list(K_range), inertia, marker="o")
    ax1.set_xlabel("K")
    ax1.set_ylabel("Inertia")
    ax1.set_title("Elbow Method")
    st.pyplot(fig1)

    # ========================================================
    # PLOT SILHOUETTE
    # ========================================================

    fig2, ax2 = plt.subplots()
    ax2.plot(list(K_range), sil_scores, marker="o")
    ax2.set_xlabel("K")
    ax2.set_ylabel("Silhouette Score")
    ax2.set_title("Silhouette Score")
    st.pyplot(fig2)

    # ========================================================
    # PLOT CALINSKI HARABASZ
    # ========================================================

    fig3, ax3 = plt.subplots()

    ax3.plot(list(K_range), ch_scores, marker="o")

    ax3.set_xlabel("K")
    ax3.set_ylabel("Calinski-Harabasz Score")
    ax3.set_title("Calinski-Harabasz Index")

    st.pyplot(fig3)
    

    # ========================================================
    # PILIH K
    # ========================================================

    st.subheader("🎯 Pilih Jumlah Cluster")

    best_k = st.slider("Pilih K", 2, max_k, 3)

    st.info(f"Anda memilih K = {best_k}")

    # ========================================================
    # CLUSTERING FINAL (BARU JALAN SETELAH CLICK)
    # ========================================================

    if st.button("🚀 Lakukan Clustering"):

        km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        df["cluster"] = km.fit_predict(X)

        st.session_state["kmeans_model"] = km
        st.session_state["final"] = df

        joblib.dump(km, "models/kmeans_model.pkl")
        joblib.dump(tfidf, "models/tfidf_cluster.pkl")

        st.success("✅ Clustering berhasil!")

        # ====================================================
        # HASIL
        # ====================================================

        st.subheader("📊 Hasil Cluster")
        st.dataframe(df, use_container_width=True)

        # ====================================================
        # DISTRIBUSI
        # ====================================================

        st.subheader("📦 Distribusi Cluster")
        st.bar_chart(df["cluster"].value_counts())

        st.info(f"""
        - Total data: {n_samples}
        - Cluster terbentuk: {best_k}
        - Cluster terbesar: {df["cluster"].value_counts().idxmax()}
        """)