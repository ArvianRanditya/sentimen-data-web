import streamlit as st
import os
import importlib.util
import pandas as pd

from utils.scraper import scrape_reviews_from_url
from utils.preprocessing import preprocess_pipeline
from streamlit_option_menu import option_menu


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Sentiment & Clustering",
    layout="wide",
    page_icon="🤖"
)

# ============================================================
# CSS
# ============================================================

def load_css():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Sembunyikan navigasi otomatis Streamlit dari folder pages/
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# TITLE
# ============================================================

st.title(" Clustering & Sentiment System")

# ============================================================
# SESSION STATE INIT
# ============================================================

default_state = {
    "data": None,
    "clean": None,
    "labeled": None,
    "final": None,
    "preprocessed": None,

    "rf_model": None,
    "tfidf_sentiment": None,
    "kmeans_model": None,
    "tfidf_cluster": None
}

for key, value in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# LOAD PAGE
# ============================================================

def load_page(file_name):
    path = os.path.join("pages", file_name)
    spec = importlib.util.spec_from_file_location("module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.show()

# ============================================================
# SIDEBAR WORKFLOW (🔥 SINGLE MENU)
# ============================================================

with st.sidebar:
    step = option_menu(
        menu_title="Dashboard",
        options=[
            "Input Data",
            "Preprocessing",
            "Clustering K-Means",
            "Topik Cluster",
            "Labeling Sentimen",
            "Training Model",
            "Evaluasi Model",
            "Insight",
            "Klasifikasi Baru"
        ],
        icons=[
            "database",
            "gear",
            "diagram-3",
            "tags",
            "bookmark-check",
            "cpu",
            "bar-chart",
            "graph-up",
            "search"
        ],
        menu_icon="robot",
        default_index=0,
        styles={
            "container": {
                "padding": "5px",
                "background-color": "#fce4ec",
                "box-shadow": "none",
                "border": "none"
            },
            "icon": {
                "color": "#c2185b",
                "font-size": "18px"
            },
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "6px 0",
                "border-radius": "14px",
                "color": "#4a2c3a",
                "background-color": "rgba(255,255,255,0.55)"
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #f06292, #ba68c8)",
                "color": "white",
                "font-weight": "600"
            }
        }
    )
# ============================================================
# STEP 1: INPUT DATA
# ============================================================

if step == "Input Data":

    st.markdown("## 📥 Data Input")

    input_mode = st.radio(
        "Pilih Sumber Data",
        ["Scraping Google Maps", "Upload File"]
    )

    if input_mode == "Scraping Google Maps":

        urls = st.text_area("Masukkan URL (1 baris 1 link)")

        max_reviews = st.number_input(
            "Jumlah review per link",
            min_value=10,
            max_value=9999,
            value=50,
            step=1,
        )


        if st.button("🚀 Scraping"):

            if not urls:
                st.warning("URL belum diisi")
            else:
                url_list = [u.strip() for u in urls.split("\n") if u.strip()]
                all_data = []

                with st.spinner("Scraping..."):
                    for url in url_list:
                        try:
                            df = scrape_reviews_from_url(url, max_reviews=max_reviews)
                            all_data.append(df)
                        except Exception as e:
                            st.error(f"Gagal {url}: {e}")

                if all_data:
                    df_input = pd.concat(all_data, ignore_index=True)
                    st.session_state["data"] = df_input
                    st.success("Scraping selesai!")

    else:

        file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])

        if file is not None:

            if file.name.endswith(".csv"):
                df_input = pd.read_csv(file)
            else:
                df_input = pd.read_excel(file)

            st.session_state["data"] = df_input
            st.success("File berhasil diupload")

    # preview + download
    if st.session_state["data"] is not None:

        df_raw = st.session_state["data"]

        st.markdown("### 📊 Data Raw")
        st.dataframe(df_raw, use_container_width=True)

        st.markdown("### ⬇️ Download Data Mentah")

        csv = df_raw.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download Data Mentah CSV",
            data=csv,
            file_name="data_mentah.csv",
            mime="text/csv",
            key="download_data_mentah_app"
        )

    # ======================
    # CLEANING
    # ======================

    if st.session_state.get("data") is not None:

        st.markdown("### 🧹 Cleaning Data")

        if st.button("Cleaning Missing & Duplikat"):

            df_clean = df_raw.copy()

            if "Review" in df_clean.columns:

                # hapus missing
                df_clean = df_clean.dropna(subset=["Review"])

                # hapus duplikat
                df_clean = df_clean.drop_duplicates(subset=["Review"])

                df_clean.reset_index(drop=True, inplace=True)

                st.session_state["clean"] = df_clean

                st.success("Cleaning selesai!")

            else:
                st.error("Kolom 'Review' tidak ditemukan")

    # ============================================================
    # PREVIEW CLEAN DATA (IF EXISTS)
    # ============================================================

    if st.session_state.get("clean") is not None:

        st.subheader("🧼 Data Setelah Cleaning")

        st.dataframe(st.session_state["clean"], use_container_width=True)

        csv = st.session_state["clean"].to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download Data Clean",
            data=csv,
            file_name="data_clean.csv",
            mime="text/csv"
        )

# ============================================================
# STEP 2: PREPROCESSING
# ============================================================

elif step == "Preprocessing":

    if st.session_state["clean"] is None:
        st.warning("Belum ada data")
    else:
        df = st.session_state["clean"].copy()

        df["Review"] = df["Review"].fillna("")
        df["clean"] = df["Review"].apply(preprocess_pipeline)

        st.session_state["preprocessed"] = df
        st.write(df.columns)

        st.success("Preprocessing selesai")
        st.dataframe(df, use_container_width=True)

# ============================================================
# STEP 3+
# ============================================================

elif step == "Clustering K-Means":
    load_page("6_Clustering.py")

elif step == "Topik Cluster":
    load_page("7_Topik_Cluster.py")

elif step == "Labeling Sentimen":

    if st.session_state["clean"] is None:
        st.warning("Lakukan preprocessing dulu")
    else:
        load_page("3_Labeling.py")

elif step == "Training Model":
    load_page("4_Training.py")

elif step == "Evaluasi Model":
    load_page("5_Evaluasi.py")

elif step == "Insight":
    load_page("8_Insight.py")

elif step == "Klasifikasi Baru":
    load_page("9_Klasifikasi_Baru.py")