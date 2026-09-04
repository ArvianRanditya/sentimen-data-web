import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# HALAMAN INSIGHT OTOMATIS
# ============================================================

def show():

    st.title("🧠 Insight Otomatis")
    st.markdown("Ringkasan otomatis dari hasil clustering & sentimen")

    # ========================================================
    # AMBIL DATA
    # ========================================================

    df = st.session_state.get("final")

    if df is None:
        st.warning("⚠️ Jalankan clustering & sentimen terlebih dahulu")
        return

    # ========================================================
    # VALIDASI KOLOM CLUSTER
    # ========================================================

    if "cluster" not in df.columns:
        st.error("Kolom 'cluster' tidak ditemukan")
        return

    # ========================================================
    # FIX LABEL COLUMN (ANTI ERROR)
    # ========================================================

    label_col = "sentiment_label" if "sentiment_label" in df.columns else "label"

    # ========================================================
    # INSIGHT DASAR
    # ========================================================

    st.subheader("📊 Ringkasan Data")

    total_data = len(df)
    total_cluster = df["cluster"].nunique()

    col1, col2 = st.columns(2)

    col1.metric("Total Data", total_data)
    col2.metric("Jumlah Cluster", total_cluster)

    # ========================================================
    # DISTRIBUSI CLUSTER
    # ========================================================

    st.subheader("📦 Distribusi Cluster")

    cluster_count = df["cluster"].value_counts().sort_index()

    st.bar_chart(cluster_count)
    st.dataframe(cluster_count.rename("Jumlah Data"))

    # ========================================================
    # SENTIMEN INSIGHT (SAFE)
    # ========================================================

    st.subheader("😊 Insight Sentimen")

    if label_col in df.columns:

        sentiment_map = {
            0: "Negatif",
            1: "Netral",
            2: "Positif"
        }

        df["sentimen_label"] = df[label_col].map(sentiment_map)

        sent_count = df["sentimen_label"].value_counts()

        st.bar_chart(sent_count)
        st.dataframe(sent_count.rename("Jumlah"))

        dominant_sent = sent_count.idxmax()
        st.success(f"Sentimen dominan: **{dominant_sent}**")

    else:
        st.info("Sentimen belum tersedia (jalankan labeling + training)")

    # ========================================================
    # CLUSTER ANALYSIS
    # ========================================================

    st.subheader("📌 Analisis Cluster")

    cluster_summary = df["cluster"].value_counts().sort_index()

    st.dataframe(cluster_summary.rename("Jumlah Data"))

    # ========================================================
    # CLUSTER vs SENTIMEN (SAFE FIX)
    # ========================================================

    if label_col in df.columns:

        st.subheader("🏆 Cluster Terbaik & Terburuk")

        try:
            cluster_sent = df.groupby("cluster")[label_col].mean()

            best_cluster = cluster_sent.idxmax()
            worst_cluster = cluster_sent.idxmin()

            st.success(f"Cluster paling positif: **{best_cluster}**")
            st.error(f"Cluster paling negatif: **{worst_cluster}**")

        except Exception as e:
            st.warning(f"Tidak bisa menghitung cluster sentimen: {e}")
