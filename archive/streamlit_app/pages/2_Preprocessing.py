import streamlit as st
import io
import pandas as pd
from utils.preprocessing import preprocess_pipeline

# ============================================================
# PREPROCESSING PAGE (MANUAL ONLY - NO AUTO EXECUTION)
# ============================================================

def show():

    st.title("⚙️ Preprocessing Data")

    # ========================================================
    # AMBIL DATA
    # ========================================================

    df = st.session_state.get("data")

    if df is None:
        st.warning("⚠️ Data belum tersedia")
        return

    # ========================================================
    # RESET OPTIONAL (BIAR TIDAK AUTO KEPAKE HASIL LAMA)
    # ========================================================

    if st.button("🔄 Reset Hasil Preprocessing"):
        st.session_state["clean"] = None
        st.success("Reset berhasil")
        st.rerun()

    # ========================================================
    # PREVIEW RAW DATA
    # ========================================================

    st.subheader("📊 Dataset Awal")
    st.dataframe(df, use_container_width=True)

    # ========================================================
    # BUTTON PREPROCESSING (ONLY EXECUTE HERE)
    # ========================================================

    run = st.button("⚙️ Jalankan Preprocessing")

    if run:

        with st.spinner("Processing text..."):

            df_processed = df.copy()

            df_processed["clean"] = df_processed["Review"].apply(preprocess_pipeline)

            st.session_state["clean"] = df_processed

        st.success("✅ Preprocessing selesai!")

    # ========================================================
    # OUTPUT (HANYA JIKA SUDAH DIPROSES)
    # ========================================================

    if st.session_state.get("clean") is not None:

        df_clean = st.session_state["clean"]

        st.subheader("🧠 Hasil Preprocessing")
        st.dataframe(df_clean[["Review", "clean"]], use_container_width=True)

        # ====================================================
        # DOWNLOAD
        # ====================================================

        buffer = io.BytesIO()
        df_clean.to_excel(buffer, index=False)

        st.download_button(
            "⬇️ Download Hasil Preprocessing",
            data=buffer.getvalue(),
            file_name="data_preprocessing.xlsx"
        )