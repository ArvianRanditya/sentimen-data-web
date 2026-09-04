import os
import json
import urllib.request
import urllib.error
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "temp_data")

# ============================================================
# RETRIEVAL: TF-IDF & Cosine Similarity
# ============================================================

def retrieve_context(session_id: str, query: str, top_n: int = 15):
    """
    Mencari ulasan paling relevan dari dataset sesi menggunakan TF-IDF & Cosine Similarity.
    """
    # Cari berkas sesi dari tahap paling akhir ke paling awal
    stages = ["clustered", "labeled", "preprocessed", "clean", "raw"]
    file_path = None
    stage_found = None
    
    for stage in stages:
        path = os.path.join(TEMP_DIR, f"{session_id}_{stage}.csv")
        if os.path.exists(path):
            file_path = path
            stage_found = stage
            break
            
    if not file_path:
        return "Info: Tidak ada dataset aktif untuk sesi ini. Silakan unggah atau scrape data terlebih dahulu.", []

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return f"Error: Gagal membaca data ulasan ({str(e)})", []

    # Pastikan ada kolom Review
    review_col = "Review"
    if review_col not in df.columns:
        # Cari alternatif kolom
        for col in df.columns:
            if col.lower() in ["review", "ulasan", "text", "teks", "komentar"]:
                df = df.rename(columns={col: review_col})
                break
                
    if review_col not in df.columns:
        return "Error: Kolom ulasan tidak ditemukan di dataset.", []

    # Hapus baris kosong
    df = df.dropna(subset=[review_col])
    if df.empty:
        return "Info: Dataset ulasan kosong.", []

    # Tentukan teks yang akan di-vektorisasi (gunakan teks clean jika ada)
    vectorize_col = "clean" if "clean" in df.columns else review_col
    df[vectorize_col] = df[vectorize_col].fillna("").astype(str)
    
    # Hapus baris yang teks clean-nya kosong setelah pembersihan
    valid_df = df[df[vectorize_col].str.strip() != ""].copy()
    if valid_df.empty:
        # Jika semua teks clean kosong, gunakan review asli
        valid_df = df.copy()
        vectorize_col = review_col

    valid_df.reset_index(drop=True, inplace=True)

    # Preproses query agar cocok dengan teks 'clean' di dataset
    from utils.preprocessing import preprocess_pipeline
    query_clean = preprocess_pipeline(query)
    if not query_clean.strip():
        query_clean = query

    # Lakukan TF-IDF
    try:
        vectorizer = TfidfVectorizer(max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(valid_df[vectorize_col])
        query_vec = vectorizer.transform([query_clean])
    except Exception as e:
        # Fallback jika TF-IDF gagal (misal data terlalu pendek/karakter aneh)
        return "Error: Gagal memproses pencarian teks.", []

    # Hitung Cosine Similarity
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # Ambil indeks top_n dengan skor kemiripan tertinggi
    top_indices = similarities.argsort()[::-1][:top_n]
    
    # Cek apakah skor kemiripannya sangat rendah (opsional, tapi sebaiknya tetap kirim ulasan teratas)
    retrieved_items = []
    sentiment_map = {0: "Negatif", 1: "Netral", 2: "Positif"}
    
    for idx in top_indices:
        row = valid_df.iloc[idx]
        review_text = row[review_col]
        score = float(similarities[idx])
        
        # Cari metadata tambahan (sentimen & cluster)
        meta_parts = []
        
        # Sentimen
        label_col = "sentiment_label" if "sentiment_label" in row else ("label" if "label" in row else None)
        if label_col is not None and not pd.isna(row[label_col]):
            label_val = int(row[label_col])
            meta_parts.append(f"Sentimen: {sentiment_map.get(label_val, str(label_val))}")
            
        # Cluster
        if "cluster" in row and not pd.isna(row["cluster"]):
            cluster_val = int(row["cluster"])
            meta_parts.append(f"Cluster: {cluster_val}")
            
        # Topik Cluster
        if "topik_cluster" in row and not pd.isna(row["topik_cluster"]):
            meta_parts.append(f"Topik: {row['topik_cluster']}")
        elif "topic" in row and not pd.isna(row["topic"]):
            meta_parts.append(f"Topik: {row['topic']}")
            
        meta_str = " | ".join(meta_parts)
        meta_info = f" ({meta_str})" if meta_parts else ""
        
        retrieved_items.append(f"- \"{review_text}\"{meta_info} [Similarity: {score:.3f}]")

    context_str = "\n".join(retrieved_items)
    return context_str, retrieved_items

# ============================================================
# LLM: Call Gemini API with Chat History
# ============================================================

def call_gemini_rag_chat(query: str, context: str, history: list):
    """
    Memanggil API Gemini 1.5 Flash dengan konteks ulasan dan riwayat obrolan.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: API Key Gemini (`GEMINI_API_KEY`) belum dikonfigurasi di file `.env` backend."

    model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    # Definisikan instruksi sistem (System Instruction)
    system_instruction = (
        "Anda adalah Chatbot Asisten AI Universitas Wahid Hasyim (Unwahas) yang membantu menganalisis ulasan/review mahasiswa/pengguna. "
        "Tugas Anda adalah menjawab pertanyaan pengguna secara ramah, profesional, dan akurat berdasarkan data ulasan relevan yang disediakan di bagian CONTEXT. "
        "Gunakan data statistik sentimen atau cluster jika ditanyakan.\n\n"
        "Aturan menjawab:\n"
        "1. Jika pertanyaan di luar konteks ulasan (pertanyaan umum/sapaan), jawablah dengan sopan dan ramah.\n"
        "2. Jika user bertanya tentang ulasan tapi tidak ada informasi yang cocok di CONTEXT, beri tahu dengan sopan bahwa Anda tidak menemukan informasi tersebut di data ulasan yang diunggah, namun tetap berikan jawaban logis/saran umum jika memungkinkan.\n"
        "3. Tulis jawaban Anda dalam Bahasa Indonesia yang baik dan terstruktur."
    )

    # Format riwayat chat ke format Gemini API (role: "user" atau "model")
    gemini_contents = []
    
    # 1. Masukkan riwayat chat sebelumnya jika ada
    for msg in history:
        role = "user" if msg.get("role") == "user" else "model"
        gemini_contents.append({
            "role": role,
            "parts": [{"text": msg.get("content", "")}]
        })
        
    # 2. Masukkan prompt baru (pesan terbaru + konteks ulasan) sebagai pesan terakhir dari user
    new_prompt = (
        f"CONTEXT (Data Ulasan Relevan):\n{context}\n\n"
        f"PERTANYAAN PENGGUNA:\n{query}"
    )
    
    gemini_contents.append({
        "role": "user",
        "parts": [{"text": new_prompt}]
    })

    # Siapkan payload body
    payload = {
        "contents": gemini_contents,
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 4000
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        data_json = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_json, headers=headers)
        
        # Panggil API dengan timeout 90 detik (mencegah timeout di koneksi lambat)
        with urllib.request.urlopen(req, timeout=90) as response:
            res = json.loads(response.read().decode("utf-8"))
            
            # Ekstrak teks dari respons Gemini
            if "candidates" in res and len(res["candidates"]) > 0:
                candidate = res["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0].get("text", "").strip()
            
            return "Maaf, asisten AI tidak dapat merumuskan jawaban saat ini."
            
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode("utf-8")
            error_json = json.loads(error_body)
            error_msg = error_json.get("error", {}).get("message", str(e))
        except:
            error_msg = str(e)
        return f"Koneksi ke Gemini API Gagal: {error_msg}"
    except Exception as e:
        return f"Terjadi kesalahan koneksi AI: {str(e)}"
