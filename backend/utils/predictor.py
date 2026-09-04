import joblib
import os
import numpy as np

# ============================================================
# LOAD MODEL (SAFE PATH)
# ============================================================

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_PATH, "models")

MODEL_MTIMES = {}

def load_pkl_dynamic(filename):
    """
    Muat file .pkl secara dinamis dari folder models.
    Otomatis memuat ulang jika berkas di disk diperbarui (berdasarkan mod time).
    """
    global MODEL_MTIMES
    path = os.path.join(MODEL_PATH, filename)
    if not os.path.exists(path):
        return None
    
    mtime = os.path.getmtime(path)
    if filename not in MODEL_MTIMES or MODEL_MTIMES[filename]["mtime"] < mtime:
        try:
            model = joblib.load(path)
            MODEL_MTIMES[filename] = {"model": model, "mtime": mtime}
            print(f"🔄 Berhasil memuat ulang model secara dinamis: {filename}")
        except Exception as e:
            print(f"⚠️ Gagal memuat model {filename}: {e}")
            
    return MODEL_MTIMES.get(filename, {}).get("model")


# ============================================================
# PREDICT SENTIMEN
# ============================================================

def predict_sentiment(texts, tfidf=None, model=None):

    if model is None:
        model = load_pkl_dynamic("rf_model.pkl")
    if tfidf is None:
        tfidf = load_pkl_dynamic("tfidf_sentiment.pkl")

    if model is None or tfidf is None:
        raise ValueError("Model sentiment belum tersedia. Silakan lakukan training model terlebih dahulu.")

    print("====================================")
    print("MODEL :", model)

    print("===== 20 DATA YANG AKAN DIPREDIKSI =====")
    for i, t in enumerate(texts[:20]):
        print(i+1, ":", t)

    X = tfidf.transform(texts)

    pred = model.predict(X)

    print("20 HASIL PREDIKSI PERTAMA:")
    print(pred[:20])
    print("====================================")

    return pred


# ============================================================
# PREDICT CLUSTER
# ============================================================

def predict_cluster(texts, tfidf=None, model=None):

    if model is None:
        model = load_pkl_dynamic("kmeans_model.pkl")
    if tfidf is None:
        tfidf = load_pkl_dynamic("tfidf_cluster.pkl")

    if model is None or tfidf is None:
        raise ValueError("Model cluster belum tersedia. Silakan lakukan clustering terlebih dahulu.")

    X = tfidf.transform(texts)
    return model.predict(X)


# ============================================================
# TEST TERMINAL (SAFE)
# ============================================================

if __name__ == "__main__":

    print("✅ Predictor OK")

    sample = ["kampus ini bersih dan nyaman"]

    try:
        print("Sentiment:", predict_sentiment(sample))
        print("Cluster:", predict_cluster(sample))
    except Exception as e:
        print("⚠️ ERROR:", e)