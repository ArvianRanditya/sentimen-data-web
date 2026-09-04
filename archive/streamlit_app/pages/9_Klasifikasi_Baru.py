import streamlit as st
import pandas as pd

from utils.preprocessing import preprocess_pipeline
from utils.predictor import predict_sentiment, predict_cluster

# ============================================================
# HALAMAN KLASIFIKASI DATA BARU (FIXED FINAL)
# ============================================================

def show():

    st.title("🔮 Klasifikasi Data Baru")
    st.markdown("Prediksi sentimen & cluster untuk data baru")

    # ========================================================
    # LOAD MODEL
    # ========================================================

    rf_model = st.session_state.get("rf_model")
    tfidf_sent = st.session_state.get("tfidf_sentiment")
    kmeans_model = st.session_state.get("kmeans_model")
    tfidf_cluster = st.session_state.get("tfidf_cluster")

    if rf_model is None or kmeans_model is None:
        st.warning("⚠️ Model belum dilatih")
        return

    if tfidf_sent is None or tfidf_cluster is None:
        st.warning("⚠️ TF-IDF belum tersedia")
        return

    # ========================================================
    # MODE INPUT
    # ========================================================

    mode = st.radio("Pilih Mode Input", ["Teks Manual", "Upload File"])

    sentiment_map = {
        0: "Negatif",
        1: "Netral",
        2: "Positif"
    }

    # ========================================================
    # MODE 1: TEKS MANUAL
    # ========================================================

    if mode == "Teks Manual":

        text = st.text_area("Masukkan review")

        if st.button("🚀 Prediksi"):

            if not text.strip():
                st.warning("Masukkan teks terlebih dahulu")
                return

            clean = preprocess_pipeline(text)

            sent = predict_sentiment([clean], tfidf_sent, rf_model)[0]
            cluster = predict_cluster([clean], tfidf_cluster, kmeans_model)[0]

            st.success("Hasil Prediksi")

            col1, col2 = st.columns(2)

            with col1:
                st.info("Input")
                st.write(text)

            with col2:
                st.info("Hasil")
                st.write(f"Clean: {clean}")
                st.write(f"Sentimen: {sentiment_map.get(sent, sent)}")
                st.write(f"Cluster: {cluster}")

    # ========================================================
    # MODE 2: FILE
    # ========================================================

    else:

        file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])

        if file is not None:

            df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)

            if "Review" not in df.columns:
                st.error("File harus punya kolom 'Review'")
                return

            if st.button("🚀 Proses Data"):

                df = df.copy()

                df["clean"] = df["Review"].apply(preprocess_pipeline)

                df["sentiment_label"] = predict_sentiment(
                    df["clean"], tfidf_sent, rf_model
                )

                df["cluster"] = predict_cluster(
                    df["clean"], tfidf_cluster, kmeans_model
                )

                df["sentimen"] = df["sentiment_label"].map(sentiment_map)

                st.session_state["prediksi_baru"] = df

                st.success("Prediksi selesai!")

                st.dataframe(df, use_container_width=True)

                st.metric("Total Data", len(df))
                st.metric("Cluster Unik", df["cluster"].nunique())

                st.download_button(
                    "⬇️ Download",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="prediksi.csv",
                    mime="text/csv"
                )