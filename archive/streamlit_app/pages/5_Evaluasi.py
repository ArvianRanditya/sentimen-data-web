import streamlit as st
import pandas as pd
import numpy as np

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# HALAMAN EVALUASI MODEL
# ============================================================

def show():

    st.title("📊 Evaluasi Model Random Forest")
    st.markdown("Menampilkan performa model klasifikasi sentimen (berbasis data testing)")

    # ========================================================
    # AMBIL SESSION
    # ========================================================

    rf = st.session_state.get("rf_model")
    X_test = st.session_state.get("X_test")
    y_test = st.session_state.get("y_test")
    X_full = st.session_state.get("X_sent")
    y_full = st.session_state.get("y_sent")

    # ========================================================
    # VALIDASI
    # ========================================================

    if rf is None or X_test is None or y_test is None:
        st.warning("⚠️ Silakan lakukan training model terlebih dahulu")
        return

    # ========================================================
    # PREDIKSI DATA TEST (FIX UTAMA)
    # ========================================================

    y_pred = rf.predict(X_test)

    # ========================================================
    # ACCURACY
    # ========================================================

    test_acc = accuracy_score(y_test, y_pred)

    st.metric("🎯 Test Accuracy", f"{test_acc:.4f}")

    # ========================================================
    # BONUS: TRAIN vs TEST (BIAR ILMIAH)
    # ========================================================

    if X_full is not None and y_full is not None:
        train_acc = rf.score(X_full, y_full)

        col1, col2 = st.columns(2)
        col1.metric("Train Accuracy", f"{train_acc:.4f}")
        col2.metric("Test Accuracy", f"{test_acc:.4f}")

    # ========================================================
    # DISTRIBUSI LABEL TEST
    # ========================================================

    st.subheader("📊 Distribusi Label (Data Testing)")

    st.bar_chart(pd.Series(y_test).value_counts())

    # ========================================================
    # CLASSIFICATION REPORT
    # ========================================================

    st.subheader("📋 Classification Report")

    report = classification_report(y_test, y_pred, output_dict=True)
    df_report = pd.DataFrame(report).transpose()

    st.dataframe(df_report, use_container_width=True)

    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    st.subheader("🧩 Confusion Matrix (Test Data)")

    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots()

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Negatif", "Netral", "Positif"],
        yticklabels=["Negatif", "Netral", "Positif"],
        ax=ax
    )

    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")

    st.pyplot(fig)
