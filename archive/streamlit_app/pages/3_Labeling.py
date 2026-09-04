import streamlit as st
import pandas as pd

from utils.lexicon import label_sentiment_lexicon

# ============================================================
# LABELING SENTIMEN (PIPELINE FIXED)
# ============================================================

def show():

    st.title("🏷️ Labeling Sentimen (Lexicon)")

    # ========================================================
    # AMBIL DATA DARI PIPELINE
    # ========================================================

    df = st.session_state.get("clean")

    if df is None:
        df = st.session_state.get("data")

    if df is None:
        st.warning("⚠️ Tidak ada data, lakukan preprocessing dulu")
        return

    df = df.copy()

    # ========================================================
    # AUTO PREPROCESS IF BELUM ADA CLEAN
    # ========================================================

    if "clean" not in df.columns:
        st.info("🔄 Auto preprocessing dijalankan...")
        from utils.preprocessing import preprocess_pipeline
        df["clean"] = df["Review"].apply(preprocess_pipeline)

    # ========================================================
    # BUTTON LABELING
    # ========================================================

    if st.button("🚀 Jalankan Labeling Sentimen"):

        with st.spinner("Melabeli data..."):

            df = label_sentiment_lexicon(df, text_column="clean")

            st.session_state["labeled"] = df
            st.session_state["clean"] = df  # lanjut pipeline

        st.succeghfhfjhjss("✅ Labeling selesai!")

    # ========================================================
    # OUTPUT
    # ========================================================

    if st.session_state.get("labeled") is not None:

        df = st.session_state["labeled"]

        st.subheader("📊 Hasil Labeling")
        st.dataframe(df[["Review", "clean", "sentiment_label"]], use_container_width=True)

        # rename untuk UI lebih jelas
        label_map = {
            0: "Negatif",
            1: "Netral",
            2: "Positif"
        }

        df["sentimen"] = df["sentiment_label"].map(label_map)

        st.bar_chart(df["sentimen"].value_counts())

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download Labeling",
            data=csv,
            file_name="data_labeling.csv",
            mime="text/csv"
        )