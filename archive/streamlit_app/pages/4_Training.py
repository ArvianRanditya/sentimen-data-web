import streamlit as st
import pandas as pd
import joblib
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# ============================================================
# HALAMAN TRAINING MODEL
# ============================================================

def show():

    st.title("🤖 TF-IDF & Training Random Forest")
    st.markdown("Mengubah teks menjadi fitur numerik dan melatih model klasifikasi sentimen")

    # ========================================================
    # AMBIL DATA
    # ========================================================

    df = st.session_state.get("labeled")

    if df is None:
        st.warning("⚠️ Lakukan pelabelan sentimen terlebih dahulu")
        return

    if "clean" not in df.columns:
        st.error("Kolom 'clean' tidak ditemukan")
        return

    # ========================================================
    # 🔥 FIX UTAMA: label konsisten
    # ========================================================

    label_col = "sentiment_label" if "sentiment_label" in df.columns else "label"

    if label_col not in df.columns:
        st.error("Kolom label tidak ditemukan (sentiment_label / label)")
        return

    # ========================================================
    # 🔥 HANDLE MISSING LABEL (ANTI ERROR)
    # ========================================================

    df = df.dropna(subset=[label_col])

    # ========================================================
    # INFO DATA
    # ========================================================

    st.subheader("📊 Info Data")

    col1, col2, col3 = st.columns(3)

    col1.metric("Jumlah Data", len(df))
    col2.metric("Jumlah Kolom", len(df.columns))
    col3.metric("Missing Label", df[label_col].isna().sum())

    # ========================================================
    # DISTRIBUSI LABEL
    # ========================================================

    st.subheader("📊 Distribusi Label Sentimen")

    st.bar_chart(df[label_col].value_counts())

    # ========================================================
    # TF-IDF PARAMETER
    # ========================================================

    st.subheader("⚙️ Parameter TF-IDF")

    max_features = st.slider("Max Features", 100, 1000, 300, step=100)
    test_size = st.slider("Test Size (%)", 10, 40, 20) / 100

    # ========================================================
    # TRAIN MODEL
    # ========================================================

    if st.button("🚀 Latih Model Random Forest"):

        with st.spinner("Training model..."):

            # ====================================================
            # LABEL
            # ====================================================

            y = df[label_col]

            # ====================================================
            # SPLIT DATA DULU
            # ====================================================

            X_train_text, X_test_text, y_train, y_test = train_test_split(
                df["clean"],
                y,
                test_size=test_size,
                random_state=42,
                stratify=y
            )

            # ====================================================
            # TF-IDF SETELAH SPLIT (ANTI DATA LEAKAGE)
            # ====================================================

            tfidf = TfidfVectorizer(max_features=max_features)

            X_train = tfidf.fit_transform(X_train_text)

            X_test = tfidf.transform(X_test_text)

            # ====================================================
            # MODEL (AUTO HANDLE IMBALANCE)
            # ====================================================

            rf = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight="balanced"  # 🔥 AUTO IMBALANCE FIX
            )

            rf.fit(X_train, y_train)

            y_pred = rf.predict(X_test)

            # ====================================================
            # SIMPAN SESSION
            # ====================================================

            st.session_state["tfidf_sentiment"] = tfidf
            st.session_state["rf_model"] = rf
            st.session_state["X_sent"] = X
            st.session_state["y_sent"] = y

            # 🔥 TAMBAHAN WAJIB UNTUK EVALUASI
            st.session_state["X_test"] = X_test
            st.session_state["y_test"] = y_test

            # ====================================================
            # SIMPAN MODEL
            # ====================================================

            joblib.dump(rf, "models/rf_model.pkl")
            joblib.dump(tfidf, "models/tfidf_sentiment.pkl")

            # ====================================================
            # EVALUASI
            # ====================================================

            st.subheader("📊 Classification Report")

            st.text(classification_report(y_test, y_pred))

            st.subheader("📉 Confusion Matrix")

            cm = confusion_matrix(y_test, y_pred)

            fig, ax = plt.subplots()
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)

            st.pyplot(fig)

        st.success("✅ Model berhasil dilatih & disimpan!")

    # ========================================================
    # STATUS MODEL
    # ========================================================

    if st.session_state.get("rf_model") is not None:
        st.success("Model tersedia di session_state")
        st.info("Siap untuk evaluasi, clustering, dan prediksi")