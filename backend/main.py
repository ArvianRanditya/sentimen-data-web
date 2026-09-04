from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import uuid
import os
import shutil
import joblib
import json
import numpy as np
from dotenv import load_dotenv

# Muat variabel environment dari berkas .env
load_dotenv()


# Sklearn tools for training
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score, classification_report, confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Internal utils
from utils.scraper import scrape_multiple_urls
from utils.preprocessing import preprocess_pipeline
from utils.predictor import predict_sentiment, predict_cluster
from utils.topic_rules import TOPIC_RULES
from utils.nlg import generate_nlg_recommendation
from utils.rag_chat import retrieve_context, call_gemini_rag_chat

app = FastAPI(title="Sentiment Analysis API")

@app.get("/tes")
def tes():
    return {"ok": True}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMP_DIR = os.path.join(BASE_DIR, "temp_data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


# ==========================================
# Pydantic Models
# ==========================================
class ScrapeRequest(BaseModel):
    urls: str
    max_reviews: int = 50

class SessionRequest(BaseModel):
    session_id: str

class ClusterEvaluateRequest(BaseModel):
    session_id: str
    max_k: int = 10

class ClusterApplyRequest(BaseModel):
    session_id: str
    k: int = 3

class TrainRequest(BaseModel):
    session_id: str
    max_features: int = 1000
    test_size: float = 0.2

class PredictRequest(BaseModel):
    text: str

class DownloadRequest(BaseModel):
    session_id: str
    notes: dict

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: list[ChatMessage] = []


# ==========================================
# Helper to read/write dataset
# ==========================================
def get_file_path(session_id: str, stage: str = "raw"):
    return os.path.join(TEMP_DIR, f"{session_id}_{stage}.csv")


# ==========================================
# ROUTES
# ==========================================

@app.get("/")
def read_root():
    return {"message": "Welcome to Sentiment Analysis API"}


# 1. INPUT DATA (UPLOAD)
@app.post("/api/data/upload")
async def upload_file(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    file_path = get_file_path(session_id, "raw")
    
    # Read file content into memory first
    content = await file.read()
    
    # Determine file type from filename
    filename = file.filename.lower()
    
    try:
        if filename.endswith(".csv"):
            import io
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith((".xlsx", ".xls")):
            import io
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Format file tidak didukung. Gunakan .csv atau .xlsx")
        
        # Validate required columns
        if "Review" not in df.columns:
            # Try common alternatives
            for col in df.columns:
                if col.lower() in ["review", "ulasan", "text", "teks", "komentar", "comment"]:
                    df = df.rename(columns={col: "Review"})
                    break
        
        if "Review" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Kolom 'Review' tidak ditemukan. Kolom yang tersedia: {list(df.columns)}"
            )
        
        # Save as CSV for consistent processing downstream
        df.to_csv(file_path, index=False)
        
        preview = df.head(20).to_dict(orient="records")
        
        return {
            "session_id": session_id,
            "message": "File berhasil diupload",
            "total_rows": len(df),
            "columns": list(df.columns),
            "preview": preview
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal membaca file: {str(e)}")



# 1. INPUT DATA (SCRAPING)
@app.post("/api/data/scrape")
async def scrape_data(request: ScrapeRequest):

    session_id = str(uuid.uuid4())

    url_list = [
        u.strip()
        for u in request.urls.split("\n")
        if u.strip()
    ]

    try:

        df = scrape_multiple_urls(
            url_list,
            request.max_reviews
        )

        # simpan csv
        df.to_csv(
            get_file_path(session_id, "raw"),
            index=False
        )

        # preview data
        preview = df.head(20).to_dict(orient="records")

        return {
            "session_id": session_id,
            "message": "Scraping successful",
            "total_rows": len(df),
            "columns": list(df.columns),
            "preview": preview
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# ==========================================
# DOWNLOAD RAW DATA
# ==========================================
@app.get("/api/data/download/{session_id}")
async def download_raw_data(session_id: str):

    file_path = get_file_path(session_id, "raw")

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File tidak ditemukan"
        )

    return FileResponse(
        path=file_path,
        filename=f"raw_data_{session_id}.csv",
        media_type='text/csv'
    )

# 2.5. CLEANING DATA
@app.post("/api/data/clean")
async def clean_data(request: SessionRequest):
    raw_path = get_file_path(request.session_id, "raw")
    if not os.path.exists(raw_path):
        raise HTTPException(status_code=404, detail="Data mentah tidak ditemukan")
        
    df = pd.read_csv(raw_path)
    
    if "Review" not in df.columns:
        raise HTTPException(status_code=400, detail="Kolom 'Review' tidak ditemukan")
        
    original_len = len(df)
    df = df.dropna(subset=["Review"])
    df = df.drop_duplicates(subset=["Review"])
    df.reset_index(drop=True, inplace=True)
    clean_len = len(df)
    
    clean_path = get_file_path(request.session_id, "clean")
    df.to_csv(clean_path, index=False)
    
    preview = df.head(20).to_dict(orient="records")
    
    return {
        "message": "Cleaning selesai",
        "original_rows": original_len,
        "clean_rows": clean_len,
        "preview": preview
    }


# 3. PREPROCESSING
@app.post("/api/process/preprocess")
async def preprocess_data(request: SessionRequest):
    # Load data
    clean_path = get_file_path(request.session_id, "clean")
    raw_path = get_file_path(request.session_id, "raw")
    
    if os.path.exists(clean_path):
        df = pd.read_csv(clean_path)
    elif os.path.exists(raw_path):
        df = pd.read_csv(raw_path)
        # Drop NA and duplicates just in case clean step was skipped
        df = df.dropna(subset=["Review"])
        df = df.drop_duplicates(subset=["Review"])
    else:
        raise HTTPException(status_code=404, detail="Data not found")
    
    if "Review" not in df.columns:
        raise HTTPException(status_code=400, detail="Column 'Review' not found in dataset")
        
    df = df.dropna(subset=["Review"])
    df = df.drop_duplicates(subset=["Review"])
    df["Review"] = df["Review"].fillna("")
    
    # Run pipeline
    df["clean"] = df["Review"].apply(preprocess_pipeline)
    
    # Save to dedicated preprocessed stage (not overwriting the clean/raw data)
    preprocessed_path = get_file_path(request.session_id, "preprocessed")
    df.to_csv(preprocessed_path, index=False)
    
    preview = df.head(10).to_dict(orient="records")
    return {"message": "Preprocessing finished", "total_rows": len(df), "preview": preview}

#   DOWNLOAD PRE PROCESS
@app.get("/api/preprocess/download/{session_id}")
async def download_preprocessed(session_id: str):

    file_path = get_file_path(
        session_id,
        "preprocessed"
    )

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File preprocessing tidak ditemukan"
        )

    return FileResponse(
        path=file_path,
        filename="data_preprocessing.csv",
        media_type="text/csv"
    )

# 3. CLUSTERING EVALUATION
@app.post("/api/cluster/evaluate")
async def evaluate_cluster(request: ClusterEvaluateRequest):
    # Try preprocessed first, then clean, then raw
    preprocessed_path = get_file_path(request.session_id, "preprocessed")
    clean_path = get_file_path(request.session_id, "clean")
    
    if os.path.exists(preprocessed_path):
        df = pd.read_csv(preprocessed_path)
    elif os.path.exists(clean_path):
        df = pd.read_csv(clean_path)
    else:
        raise HTTPException(status_code=404, detail="Data preprocessed tidak ditemukan. Lakukan preprocessing terlebih dahulu.")
        
    if "clean" not in df.columns:
        raise HTTPException(status_code=400, detail="Kolom 'clean' tidak ada. Lakukan preprocessing terlebih dahulu.")
    
    # Drop NaN, empty strings, fill remaining NaN with empty string
    df = df.dropna(subset=["clean"])
    df = df[df["clean"].astype(str).str.strip() != ""]
    df["clean"] = df["clean"].fillna("").astype(str)
    df.reset_index(drop=True, inplace=True)
    
    if len(df) < 3:
        raise HTTPException(status_code=400, detail="Data terlalu sedikit untuk clustering (minimal 3 baris valid).")
        
    tfidf = TfidfVectorizer(max_features=1000)
    X = tfidf.fit_transform(df["clean"])
    
    n_samples = X.shape[0]
    max_k = min(request.max_k, n_samples - 1)
    
    results = []
    for k in range(2, max_k + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        
        ch = calinski_harabasz_score(X.toarray(), labels)
        
        results.append({
            "k": k,
            "calinski": float(ch)
        })
        
    return {"evaluation": results, "max_k": max_k}


# 3.5 DATA INFO
@app.post("/api/data/info")
async def data_info(request: SessionRequest):
    """Return basic stats about the labeled dataset for Training page"""
    labeled_path = get_file_path(request.session_id, "labeled")
    preprocessed_path = get_file_path(request.session_id, "preprocessed")
    clean_path = get_file_path(request.session_id, "clean")

    if os.path.exists(labeled_path):
        df = pd.read_csv(labeled_path)
    elif os.path.exists(preprocessed_path):
        df = pd.read_csv(preprocessed_path)
    elif os.path.exists(clean_path):
        df = pd.read_csv(clean_path)
    else:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")

    label_col = "sentiment_label" if "sentiment_label" in df.columns else "label"
    missing_label = int(df[label_col].isna().sum()) if label_col in df.columns else 0

    dist = {}
    if label_col in df.columns:
        dist = {int(k): int(v) for k, v in df[label_col].value_counts().to_dict().items()}

    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_label": missing_label,
        "label_distribution": dist,
        "columns": list(df.columns)
    }


# 4. CLUSTERING APPLY
@app.post("/api/cluster/apply")
async def apply_cluster(request: ClusterApplyRequest):
    # Try preprocessed first, then clean
    labeled_path = get_file_path(request.session_id, "labeled")

    if os.path.exists(labeled_path):
        df = pd.read_csv(labeled_path)
    else:
        raise HTTPException(
            status_code=404,
            detail="Data sentiment belum tersedia"
        )

    
    if "clean" not in df.columns:
        raise HTTPException(status_code=400, detail="Kolom 'clean' tidak ada. Lakukan preprocessing terlebih dahulu.")

    # Drop NaN, empty strings, ensure string type before TF-IDF
    df = df.dropna(subset=["clean"])
    df = df[df["clean"].astype(str).str.strip() != ""]
    df["clean"] = df["clean"].fillna("").astype(str)
    df.reset_index(drop=True, inplace=True)

    if len(df) < request.k:
        raise HTTPException(status_code=400, detail=f"Data terlalu sedikit ({len(df)} baris) untuk K={request.k} cluster.")

    tfidf = TfidfVectorizer(max_features=1000)
    X = tfidf.fit_transform(df["clean"])
    
    km = KMeans(n_clusters=request.k, random_state=42, n_init=10)
    df["cluster"] = km.fit_predict(X)
    
    # Save artifacts
    joblib.dump(km, os.path.join(MODEL_DIR, "kmeans_model.pkl"))
    joblib.dump(tfidf, os.path.join(MODEL_DIR, "tfidf_cluster.pkl"))
    
    df.to_csv(get_file_path(request.session_id, "clustered"), index=False)
    
    dist = df["cluster"].value_counts().to_dict()
    preview = df.head(10).to_dict(orient="records")
    return {"message": "Clustering applied", "distribution": dist, "preview": preview}


# 4.5. CLUSTER TOPIC
@app.post("/api/cluster/topic")
async def cluster_topic(request: SessionRequest):
    clustered_path = get_file_path(request.session_id, "clustered")
    if not os.path.exists(clustered_path):
        raise HTTPException(status_code=404, detail="Clustered data not found")
        
    df = pd.read_csv(clustered_path)
    if "cluster" not in df.columns:
        raise HTTPException(status_code=400, detail="Data is not clustered yet")
    if "clean" not in df.columns:
        raise HTTPException(status_code=400, detail="Kolom 'clean' tidak ditemukan")

    # Sanitize clean column — drop NaN, ensure str type
    df = df.dropna(subset=["clean"])
    df["clean"] = df["clean"].fillna("").astype(str)
    df = df[df["clean"].str.strip() != ""]
    df.reset_index(drop=True, inplace=True)
        
    try:
        tfidf = joblib.load(os.path.join(MODEL_DIR, "tfidf_cluster.pkl"))
    except Exception:
        raise HTTPException(status_code=404, detail="TF-IDF model for clustering not found")
        
    X = tfidf.transform(df["clean"])
    feature_names = np.array(tfidf.get_feature_names_out())
    unique_clusters = sorted(df["cluster"].unique())
    
    topics = {}
    for cluster_id in unique_clusters:
        cluster_data = df[df["cluster"] == cluster_id]
        if cluster_data.empty:
            continue
            
        idx = cluster_data.index
        cluster_vec = X[idx].mean(axis=0).A1
        top_idx = cluster_vec.argsort()[::-1][:10]
        
        top_words = feature_names[top_idx].tolist()
        top_scores = cluster_vec[top_idx].tolist()
        
        topics[int(cluster_id)] = [{"word": w, "score": float(s)} for w, s in zip(top_words, top_scores)]
        
    return {"topics": topics}


# 4.6. INSIGHT
@app.post("/api/insight")
async def get_insight(request: SessionRequest):
    clustered_path = get_file_path(request.session_id, "clustered")
    labeled_path = get_file_path(request.session_id, "labeled")

    if os.path.exists(clustered_path):
        data_path = clustered_path
    elif os.path.exists(labeled_path):
        data_path = labeled_path
    else:
        raise HTTPException(status_code=404, detail="Data not found for insight")
    df = pd.read_csv(data_path)
    
    insight = {
    "total_data": len(df),
    "cluster_distribution": {},
    "sentiment_distribution": {},
    "cluster_sentiment_mean": {},
    "cluster_topics": {},
    "cluster_distribution_detail": []
    }   
    
    if "cluster" in df.columns:
        insight["total_clusters"] = int(df["cluster"].nunique())
        # Convert keys to int for JSON serialization
        insight["cluster_distribution"] = {int(k): int(v) for k, v in df["cluster"].value_counts().to_dict().items()}
        
    label_col = None

    if "sentiment_label" in df.columns:
        label_col = "sentiment_label"
    elif "label" in df.columns:
        label_col = "label"
    if label_col in df.columns:
        insight["sentiment_distribution"] = {int(k): int(v) for k, v in df[label_col].value_counts().to_dict().items()}
        
    if "cluster" in df.columns and label_col:
        try:
            cluster_sent = df.groupby("cluster")[label_col].mean()
            insight["cluster_sentiment_mean"] = {int(k): float(v) for k, v in cluster_sent.to_dict().items()}
            insight["best_cluster"] = int(cluster_sent.idxmax())
            insight["worst_cluster"] = int(cluster_sent.idxmin())
        except Exception:
            pass

    # ==========================================
    # DISTRIBUSI SENTIMEN PER CLUSTER
    # ==========================================
    if "cluster" in df.columns and label_col:

        detail = []

        for cluster_id in sorted(df["cluster"].unique()):

            subset = df[df["cluster"] == cluster_id]

            positif = int((subset[label_col] == 2).sum())
            netral = int((subset[label_col] == 1).sum())
            negatif = int((subset[label_col] == 0).sum())

            detail.append({
                "cluster": int(cluster_id),
                "positif": positif,
                "netral": netral,
                "negatif": negatif
            })

        insight["cluster_distribution_detail"] = detail
            
    # ==========================================
    # TOPIK CLUSTER
    # ==========================================
    if "cluster" in df.columns and "clean" in df.columns:

        topics = {}

        for cluster_id in sorted(df["cluster"].unique()):

            subset = df[df["cluster"] == cluster_id]

            text = " ".join(subset["clean"].astype(str))

            stopwords_extra = {
                "yang", "dan", "di", "ke", "dari", "untuk",
                "dengan", "pada", "karena", "atau", "juga",
                "itu", "ini", "ada", "saya", "kami", "yg", "nya"
            }

            words = [
                w for w in text.split()
                if (
                    w not in stopwords_extra
                    and not w.endswith("nya")
                    and len(w) > 2
                )
            ]
            if len(words) == 0:
                top_words = ["tidak ada topik"]
            else:
                freq = pd.Series(words).value_counts().head(10)
                top_words = freq.index.tolist()
            freq = pd.Series(words).value_counts().head(10)

            top_words = freq.index.tolist()

            # ======================================
            # AUTO TOPIC NAME
            # ======================================

            topic_name = f"Cluster {cluster_id}"

            best_score = 0

            for topic, keywords in TOPIC_RULES.items():

                score = sum(1 for word in top_words if word in keywords)

                if score > best_score:
                    best_score = score
                    topic_name = topic

            topics[int(cluster_id)] = {
                "name": topic_name,
                "keywords": top_words
            }

        insight["cluster_topics"] = topics   

    with open(
        os.path.join(TEMP_DIR, "cluster_topics.json"),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            insight["cluster_topics"],
            f,
            ensure_ascii=False
        )

    # Load NLG recommendations if they exist
    nlg_path = os.path.join(TEMP_DIR, f"{request.session_id}_nlg.json")
    if os.path.exists(nlg_path):
        try:
            with open(nlg_path, "r", encoding="utf-8") as f:
                insight["nlg_recommendations"] = json.load(f)
        except Exception:
            insight["nlg_recommendations"] = {}
    else:
        insight["nlg_recommendations"] = {}

    return insight


# 4.7. NLG RECOMMENDATIONS
class NLGRequest(BaseModel):
    session_id: str

@app.post("/api/nlg/recommend")
async def generate_nlg(request: NLGRequest):
    clustered_path = get_file_path(request.session_id, "clustered")
    labeled_path = get_file_path(request.session_id, "labeled")
    
    if os.path.exists(clustered_path):
        data_path = clustered_path
    elif os.path.exists(labeled_path):
        data_path = labeled_path
    else:
        raise HTTPException(status_code=404, detail="Data hasil clustering/labeling tidak ditemukan")
        
    df = pd.read_csv(data_path)
    
    if "cluster" not in df.columns:
        raise HTTPException(status_code=400, detail="Data belum di-cluster. Lakukan clustering terlebih dahulu.")
        
    label_col = None
    if "sentiment_label" in df.columns:
        label_col = "sentiment_label"
    elif "label" in df.columns:
        label_col = "label"
        
    if not label_col:
        raise HTTPException(status_code=400, detail="Data belum dilabeli sentimen. Lakukan labeling terlebih dahulu.")

    df = df.dropna(subset=["clean"])
    df["clean"] = df["clean"].fillna("").astype(str)
    
    unique_clusters = sorted(df["cluster"].unique())
    nlg_results = {}
    
    for cluster_id in unique_clusters:
        subset = df[df["cluster"] == cluster_id]
        if subset.empty:
            continue
            
        text = " ".join(subset["clean"].astype(str))
        stopwords_extra = {
            "yang", "dan", "di", "ke", "dari", "untuk",
            "dengan", "pada", "karena", "atau", "juga",
            "itu", "ini", "ada", "saya", "kami", "yg", "nya"
        }
        words = [
            w for w in text.split()
            if (
                w not in stopwords_extra
                and not w.endswith("nya")
                and len(w) > 2
            )
        ]
        
        if len(words) == 0:
            top_words = ["tidak ada topik"]
        else:
            freq = pd.Series(words).value_counts().head(10)
            top_words = freq.index.tolist()
            
        topic_name = f"Cluster {cluster_id}"
        best_score = 0
        for topic, keywords in TOPIC_RULES.items():
            score = sum(1 for word in top_words if word in keywords)
            if score > best_score:
                best_score = score
                topic_name = topic
                
        positif = int((subset[label_col] == 2).sum())
        netral = int((subset[label_col] == 1).sum())
        negatif = int((subset[label_col] == 0).sum())
        total = len(subset)
        
        recommendation = generate_nlg_recommendation(
            topic_name=topic_name,
            keywords=top_words,
            positif=positif,
            netral=netral,
            negatif=negatif,
            total=total
        )
        
        nlg_results[str(cluster_id)] = {
            "topic_name": topic_name,
            "keywords": top_words,
            "recommendation": recommendation
        }
        
    nlg_path = os.path.join(TEMP_DIR, f"{request.session_id}_nlg.json")
    with open(nlg_path, "w", encoding="utf-8") as f:
        json.dump(nlg_results, f, ensure_ascii=False)
        
    return {"nlg_recommendations": nlg_results}


# 4.8. RAG CHATBOT ASSISTANT
@app.post("/api/chat")
async def chat_with_reviews(request: ChatRequest):
    # 1. Cari ulasan yang paling relevan
    context, retrieved_items = retrieve_context(request.session_id, request.message, top_n=15)
    
    # Konversi model pydantic ke dictionary untuk diolah di utils
    history_list = [{"role": msg.role, "content": msg.content} for msg in request.history]
    
    # 2. Panggil API Gemini
    answer = call_gemini_rag_chat(
        query=request.message,
        context=context,
        history=history_list
    )
    
    return {
        "answer": answer,
        "retrieved_context": retrieved_items
    }


# 5. PREDIKSI SENTIMENT
@app.post("/api/sentiment/predict")
async def label_sentiment(request: SessionRequest):

    clustered_path = get_file_path(request.session_id, "clustered")
    preprocessed_path = get_file_path(request.session_id, "preprocessed")
    clean_path = get_file_path(request.session_id, "clean")

    if os.path.exists(clustered_path):
        data_path = clustered_path
    elif os.path.exists(preprocessed_path):
        data_path = preprocessed_path
    elif os.path.exists(clean_path):
        data_path = clean_path
    else:
        raise HTTPException(
            status_code=404,
            detail="Data tidak ditemukan"
        )

    df = pd.read_csv(data_path)

    if "clean" not in df.columns:
        raise HTTPException(
            status_code=400,
            detail="Kolom 'clean' tidak ditemukan. Silakan lakukan proses preprocessing terlebih dahulu."
        )

    df = df.dropna(subset=["clean"])

    print("====================================")
    print("DATA YANG MASUK KE MODEL")
    print(df["clean"].head(20).tolist())
    print("====================================")

    sentiments = predict_sentiment(
        df["clean"].tolist()
    )

    df["sentiment_label"] = sentiments

    print("====================================")
    print("DISTRIBUSI HASIL PREDIKSI")
    print(df["sentiment_label"].value_counts())
    print("====================================")

    df.to_csv(
        get_file_path(request.session_id, "labeled"),
        index=False
    )

    dist = df["sentiment_label"].value_counts().to_dict()

    preview = df.head(10).to_dict(orient="records")

    return {
        "message": "Prediction applied",
        "distribution": dist,
        "preview": preview
    }


# 6. MODEL TRAINING
@app.post("/api/model/train")
async def train_model(request: TrainRequest):
    print("TEST SIZE :", request.test_size)

    df = pd.read_excel(
        os.path.join(BASE_DIR, "data_training", "data_training.xlsx")
    )

    label_map = {
        "negatif": 0,
        "netral": 1,
        "positif": 2
    }

    df["label"] = df["label"].map(label_map)

    df = df.dropna(subset=["label"])

    df["clean"] = df["text"].apply(preprocess_pipeline)
    print(df["clean"].head(10).tolist())

    label_col = "label"

    df = df.dropna(subset=[label_col, "clean"])

    y = df[label_col]

    X_train_text, X_test_text, y_train, y_test = train_test_split(
        df["clean"],
        y,
        test_size=request.test_size,
        random_state=42,
        stratify=y
    )

    tfidf = TfidfVectorizer(
        max_features=2000,
        ngram_range=(1, 2),
        min_df=2
    )

    X_train = tfidf.fit_transform(X_train_text)
    X_test = tfidf.transform(X_test_text)

    rf = RandomForestClassifier(
        n_estimators=150,
        min_samples_split=5,
        random_state=42,
        class_weight="balanced"
    )
   

    print(rf.get_params())

    rf.fit(X_train, y_train)

    print("CLASSES :", rf.classes_)

    print("LABEL TRAINING")
    print(pd.Series(y_train).value_counts())

    y_pred = rf.predict(X_test)

    report = classification_report(
        y_test,
        y_pred,
        output_dict=True
    )

    labels_sorted = sorted(y.unique())

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=labels_sorted
    )

    cm_list = cm.tolist()

    test_acc = float(
        accuracy_score(y_test, y_pred)
    )

    train_acc = float(
        rf.score(X_train, y_train)
    )

    joblib.dump(
        rf,
        os.path.join(MODEL_DIR, "rf_model.pkl")
    )

    joblib.dump(
        tfidf,
        os.path.join(MODEL_DIR, "tfidf_sentiment.pkl")
    )
    print("TOTAL DATA :", len(df))
    print("TRAIN DATA :", len(X_train_text))
    print("TEST DATA :", len(X_test_text))
    
    return {
        "message": "Model trained successfully",

        "total_dataset": len(df),
        "train_size_count": len(X_train_text),
        "test_size_count": len(X_test_text),

        "classification_report": report,
        "confusion_matrix": cm_list,
        "confusion_matrix_labels": [int(l) for l in labels_sorted],
        "test_accuracy": test_acc,
        "train_accuracy": train_acc
    }
    



# 7. PREDICTION INFERENCE (single)
@app.post("/api/model/predict")
async def predict_single(request: PredictRequest):
    try:
        clean_text = preprocess_pipeline(request.text)

        sent = predict_sentiment([clean_text])

        clus = predict_cluster([clean_text])

        cluster_id = int(clus[0])
        topic_name = f"Cluster {cluster_id}"

        topic_file = os.path.join(
            TEMP_DIR,
            "cluster_topics.json"
        )

        if os.path.exists(topic_file):

            with open(
                topic_file,
                "r",
                encoding="utf-8"
            ) as f:

                topic_data = json.load(f)

            if str(cluster_id) in topic_data:

                topic_name = topic_data[
                    str(cluster_id)
                ]["name"]

        return {
            "text": request.text,
            "sentiment": int(sent[0]),
            "cluster": cluster_id,
            "topic": topic_name
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# 8. BATCH PREDICTION (file upload)
@app.post("/api/model/predict_batch")
async def predict_batch(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename.lower()
    
    try:
        import io
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Format tidak didukung. Gunakan .csv atau .xlsx")
        
        if "Review" not in df.columns:
            raise HTTPException(status_code=400, detail="File harus memiliki kolom 'Review'")
        
        df = df.dropna(subset=["Review"])
        df["clean"] = df["Review"].apply(preprocess_pipeline)
        
        sentiments = predict_sentiment(df["clean"].tolist())
        clusters = predict_cluster(df["clean"].tolist())
        
        df["sentiment_label"] = [int(s) for s in sentiments]
        df["cluster"] = [int(c) for c in clusters]
        
        topic_file = os.path.join(
            TEMP_DIR,
            "cluster_topics.json"
        )

        topic_mapping = {}

        if os.path.exists(topic_file):

            with open(
                topic_file,
                "r",
                encoding="utf-8"
            ) as f:

                topic_data = json.load(f)

            topic_mapping = {
                int(k): v["name"]
                for k, v in topic_data.items()
            }

        df["topic"] = df["cluster"].map(
            lambda x: topic_mapping.get(
                x,
                f"Cluster {x}"
            )
        )

        label_map = {0: "Negatif", 1: "Netral", 2: "Positif"}
        df["sentimen"] = df["sentiment_label"].map(label_map)
        
        predictions = df[["Review","clean","sentiment_label","sentimen","cluster","topic"]].head(100).to_dict(orient="records")
        
        return {
            "total": len(df),
            "unique_clusters": int(df["cluster"].nunique()),
            "sentiment_distribution": {int(k): int(v) for k, v in df["sentiment_label"].value_counts().to_dict().items()},
            "predictions": predictions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal memproses file: {str(e)}")

# ==========================================
# DOWNLOAD HASIL ANALISIS
# ==========================================
@app.post("/api/download-analysis")
async def download_analysis(request: DownloadRequest):

    clustered_path = get_file_path(request.session_id, "clustered")
    labeled_path = get_file_path(request.session_id, "labeled")

    if os.path.exists(clustered_path):
        file_path = clustered_path
    elif os.path.exists(labeled_path):
        file_path = labeled_path
    else:
        raise HTTPException(
            status_code=404,
            detail="File hasil analisis tidak ditemukan"
        )
    df = pd.read_csv(file_path)

    # Mapping label angka -> teks
    label_map = {
        0: "Negatif",
        1: "Netral",
        2: "Positif"
    }

    if "sentiment_label" in df.columns:
        df["sentimen"] = df["sentiment_label"].map(label_map)

    # ==========================================
    # TOPIK CLUSTER
    # ==========================================

    if "cluster" not in df.columns:
        raise HTTPException(
            status_code=400,
            detail="Data clustering belum tersedia. Lakukan clustering terlebih dahulu."
        )
    cluster_topics = {}

    for cluster_id in sorted(df["cluster"].unique()):

        subset = df[df["cluster"] == cluster_id]

        text = " ".join(subset["clean"].astype(str))

        stopwords_extra = {
            "yang", "dan", "di", "ke", "dari", "untuk",
            "dengan", "pada", "karena", "atau", "juga",
            "itu", "ini", "ada", "saya", "kami", "yg", "nya"
        }

        words = [
            w for w in text.split()
            if w not in stopwords_extra and len(w) > 2
        ]
        if len(words) == 0:
            top_words = ["tidak ada topik"]
        else:
            freq = pd.Series(words).value_counts().head(10)
            top_words = freq.index.tolist()

        topic_name = f"Cluster {cluster_id}"

        best_score = 0

        for topic, keywords in TOPIC_RULES.items():

            score = sum(
                1 for word in top_words
                if word in keywords
            )

            if score > best_score:
                best_score = score
                topic_name = topic

        cluster_topics[cluster_id] = topic_name

    if cluster_topics:
        df["topik_cluster"] = df["cluster"].map(cluster_topics)
    else:
        df["topik_cluster"] = "Tidak ada topik"

    # Load NLG recommendations if they exist
    nlg_path = os.path.join(TEMP_DIR, f"{request.session_id}_nlg.json")
    nlg_recommendations = {}
    if os.path.exists(nlg_path):
        try:
            with open(nlg_path, "r", encoding="utf-8") as f:
                nlg_data = json.load(f)
                nlg_recommendations = {int(k): v["recommendation"] for k, v in nlg_data.items()}
        except Exception:
            pass

    df["rekomendasi_nlg"] = df["cluster"].map(
        lambda x: nlg_recommendations.get(x, "")
    )

    df["catatan_analisis"] = df["cluster"].map(
        lambda x: request.notes.get(str(x), "")
    )

    columns = [
        col for col in [
            "Review",
            "clean",
            "cluster",
            "topik_cluster",
            "sentimen",
            "rekomendasi_nlg",
            "catatan_analisis"
        ]
        if col in df.columns
    ]

    export_df = df[columns]

    rename_map = {
        "Review": "Review",
        "clean": "Clean Text",
        "cluster": "Cluster",
        "topik_cluster": "Topik Cluster",
        "sentimen": "Sentimen",
        "rekomendasi_nlg": "Rekomendasi Pintar (NLG)",
        "catatan_analisis": "Catatan Analisis"
    }


    export_df = export_df.rename(columns=rename_map)

    output_path = os.path.join(
        TEMP_DIR,
        f"{request.session_id}_hasil_analisis.xlsx"
    )

    print(export_df.head())
    print(export_df.columns.tolist())
    print(export_df.shape)

    export_df.to_excel(output_path, index=False)
    print("FILE BERHASIL DIBUAT")
    print("SIZE:", os.path.getsize(output_path))

    return FileResponse(
        path=output_path,
        filename="hasil_analisis.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
