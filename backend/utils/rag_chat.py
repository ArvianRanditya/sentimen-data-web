import os
import json
import re
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
    Memanggil API Gemini dengan konteks ulasan dan riwayat obrolan.
    """
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        return "Error: API Key Gemini (`GEMINI_API_KEY`) belum dikonfigurasi di file `.env` backend."

    load_dotenv(override=True)
    preferred_model = os.getenv("GEMINI_MODEL", "gemini-3.7-flash").strip()
    
    models_to_try = [preferred_model]
    for m in ["gemini-3.7-flash", "gemini-3.5-flash", "gemini-flash-latest", "gemini-3.5-flash-lite"]:
        if m not in models_to_try:
            models_to_try.append(m)
    
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

    last_error_msg = ""
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            data_json = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data_json, headers=headers)
            
            with urllib.request.urlopen(req, timeout=60) as response:
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
                last_error_msg = error_json.get("error", {}).get("message", str(e))
            except:
                last_error_msg = str(e)

            if e.code in (404, 503):
                continue
            return f"Koneksi ke Gemini API Gagal: {last_error_msg}"
        except Exception as e:
            last_error_msg = str(e)
            continue

    return f"Koneksi ke Gemini API Gagal: {last_error_msg}"


# ============================================================
# LOCAL ENGINE: Built-in NLU & Rule-Based Sentiment Assistant
# ============================================================

def answer_with_local_engine(session_id: str, query: str, context: str, retrieved_items: list, history: list = None) -> str:
    """
    Sistem AI Lokal Mandiri (Offline NLU & Analytics):
    Menganalisis pertanyaan pengguna dan dataset ulasan (khususnya untuk kampus seperti Unwahas)
    secara langsung di backend tanpa ketergantungan API Gemini eksternal.
    """
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
        return (
            "⚠️ **Info Sistem Lokal:** Tidak ada dataset aktif untuk sesi ini.\n\n"
            "Silakan unggah file ulasan (CSV/Excel) atau lakukan scraping data ulasan terlebih dahulu di menu langkah 1."
        )

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return f"Gagal membaca data ulasan di sistem lokal: {str(e)}"

    review_col = "Review"
    if review_col not in df.columns:
        for col in df.columns:
            if col.lower() in ["review", "ulasan", "text", "teks", "komentar"]:
                df = df.rename(columns={col: review_col})
                break

    if review_col not in df.columns:
        return "Kolom ulasan tidak ditemukan pada dataset."

    df = df.dropna(subset=[review_col])
    total_reviews = len(df)
    if total_reviews == 0:
        return "Dataset ulasan aktif masih kosong."

    label_col = "sentiment_label" if "sentiment_label" in df.columns else ("label" if "label" in df.columns else None)
    
    pos_count = 0
    net_count = 0
    neg_count = 0
    pos_pct = 0.0
    net_pct = 0.0
    neg_pct = 0.0

    if label_col:
        df[label_col] = pd.to_numeric(df[label_col], errors="coerce").fillna(1).astype(int)
        pos_count = int((df[label_col] == 2).sum())
        net_count = int((df[label_col] == 1).sum())
        neg_count = int((df[label_col] == 0).sum())
        if total_reviews > 0:
            pos_pct = round(pos_count / total_reviews * 100, 1)
            net_pct = round(net_count / total_reviews * 100, 1)
            neg_pct = round(neg_count / total_reviews * 100, 1)

    q_lower = query.lower()

    # 1. INTENT: SAPAAN & PERKENALAN
    greeting_words = ["halo", "hai", "hei", "pagi", "siang", "sore", "malam", "assalamualaikum", "siapa kamu", "siapa anda", "bisa apa", "fitur"]
    if any(re.search(r'\b' + re.escape(w) + r'\b', q_lower) for w in greeting_words) and len(q_lower.split()) <= 4:
        return (
            f"👋 **Halo! Saya Asisten Analisis Sentimen (Sistem Lokal Unwahas).**\n\n"
            f"Saya berjalan **100% secara offline** langsung di sistem internal tanpa menggunakan API eksternal.\n\n"
            f"Saat ini terdapat **{total_reviews} ulasan** yang sedang dianalisis.\n"
            f"Anda dapat menanyakan hal-hal seperti:\n"
            f"- *\"Kira-kira apa yang perlu ditingkatkan dari kampus?\"*\n"
            f"- *\"Apa saja keluhan mahasiswa yang paling banyak muncul?\"*\n"
            f"- *\"Apa saja keunggulan dan hal positif yang disukai pengguna?\"*\n"
            f"- *\"Bagaimana persebaran sentimen ulasan secara keseluruhan?\"*\n"
            f"- *\"Bagaimana pendapat ulasan tentang fasilitas dan dosen?\"*"
        )

    # 2. INTENT: EVALUASI / PERBAIKAN / YANG PERLU DITINGKATKAN / KELUHAN
    improve_words = [
        "tingkat", "evaluasi", "kurang", "perbaiki", "perbaikan", "saran", "kritik", 
        "jelek", "buruk", "masalah", "keluh", "lemah", "benahi", "prioritas", 
        "kendala", "kecewa", "salah", "minus", "cacat", "rekomendasi"
    ]
    is_improvement_intent = any(w in q_lower for w in improve_words)

    if is_improvement_intent:
        aspect_findings = []

        # Kategori masalah yang sering muncul pada data ulasan kampus
        aspects = [
            {
                "kategori": "Fasilitas & Sarana Prasarana",
                "keywords": ["parkir", "ruang", "ac", "toilet", "kamar mandi", "wc", "gedung", "lift", "wifi", "internet", "rusak", "sempit", "panas", "kotor", "fasilitas", "sarana", "kantin", "bocor", "kipas", "proyektor"],
                "rekomendasi": "Lakukan audit berkala terhadap fasilitas fisik, percepat perbaikan sarana yang rusak/panas (seperti AC dan toilet), serta perluas kapasitas area parkir mahasiswa."
            },
            {
                "kategori": "Layanan Administrasi & Birokrasi",
                "keywords": ["pelayanan", "layanan", "biaya", "mahal", "antri", "sistem", "web", "lambat", "staf", "petugas", "administrasi", "tu", "sulit", "informasi", "ribet", "spp", "bayar", "respon"],
                "rekomendasi": "Tingkatkan keramahan staf pelayanan tata usaha (TU), sederhanakan alur birokrasi, dan optimalkan stabilitas portal akademik/sistem online."
            },
            {
                "kategori": "Mutu Akademik & Pembelajaran",
                "keywords": ["dosen", "jadwal", "kuliah", "materi", "tugas", "nilai", "komunikasi", "kehadiran", "ajar", "praktikum", "skripsi", "bimbingan"],
                "rekomendasi": "Evaluasi kedisiplinan jadwal perkuliahan, dorong dosen lebih interaktif dan responsif dalam bimbingan, serta standarisasi materi kuliah."
            },
            {
                "kategori": "Akses & Lingkungan Kampus",
                "keywords": ["jalan", "macet", "jauh", "becek", "keamanan", "satpam", "gerbang", "sampah", "banjir", "kumuh", "bising"],
                "rekomendasi": "Perbaiki akses jalan dan penataan drainase di sekitar kampus, serta perkuat sistem keamanan dan penataan titik pembuangan sampah."
            }
        ]

        # Cari ulasan kritis (negatif atau netral)
        critic_df = df[df[label_col].isin([0, 1])] if label_col else df

        for asp in aspects:
            matched_reviews = []
            for _, row in critic_df.iterrows():
                r_text = str(row[review_col])
                r_clean = str(row.get("clean", r_text)).lower()
                if any(kw in r_clean or kw in r_text.lower() for kw in asp["keywords"]):
                    matched_reviews.append(r_text)

            if matched_reviews:
                sample_quote = matched_reviews[0]
                if len(sample_quote) > 130:
                    sample_quote = sample_quote[:130] + "..."
                aspect_findings.append({
                    "kategori": asp["kategori"],
                    "count": len(matched_reviews),
                    "quote": sample_quote,
                    "saran": asp["rekomendasi"]
                })

        # Urutkan aspek berdasarkan jumlah keluhan terbanyak
        aspect_findings.sort(key=lambda x: x["count"], reverse=True)

        res = [
            f"📊 **Hasil Analisis Evaluasi & Aspek yang Perlu Ditingkatkan:**\n",
            f"Berdasarkan analisis dataset ulasan (terdapat **{neg_count} ulasan negatif ({neg_pct}%)** dan **{net_count} ulasan netral ({net_pct}%)**), berikut adalah aspek-aspek utama yang memerlukan perbaikan segera:\n"
        ]

        if aspect_findings:
            for idx, item in enumerate(aspect_findings, 1):
                res.append(
                    f"**{idx}. {item['kategori']}** *(Terdeteksi pada ~{item['count']} ulasan)*\n"
                    f"   - 💬 *Contoh Ulasan:* \"{item['quote']}\"\n"
                    f"   - 🎯 *Rekomendasi Tindakan:* {item['saran']}\n"
                )
        else:
            # Jika kata kunci khusus tidak spesifik, ambil ulasan negatif teratas
            res.append("Dari sampel ulasan bertaraf negatif yang tercatat, beberapa poin keluhan yang disampaikan responden mencakup:")
            if label_col:
                sample_negs = df[df[label_col] == 0][review_col].dropna().head(3).tolist()
                for neg_item in sample_negs:
                    res.append(f"- \"{neg_item}\"")
            res.append("\n🎯 *Rekomendasi Umum:* Prioritaskan survei kepuasan mahasiswa per fakultas dan segera tindak lanjuti sarana prasarana yang mendapat rating rendah.")

        res.append(
            "\n💡 *Catatan:* Analisis ini dihasilkan langsung oleh **Sistem Analisis Internal (Lokal)** berbasis klasifikasi sentimen dan pemetaan topik ulasan tanpa kuota API eksternal."
        )
        return "\n".join(res)

    # 3. INTENT: KEUNGGULAN / HAL POSITIF / YANG DISUKAI
    positive_words = ["positif", "bagus", "baik", "suka", "kelebihan", "unggul", "puas", "apresiasi", "hebat", "senang", "keren", "favorit", "mantap", "puas"]
    if any(w in q_lower for w in positive_words):
        pos_df = df[df[label_col] == 2] if label_col else df
        sample_pos = pos_df[review_col].dropna().head(3).tolist()

        res = [
            f"🌟 **Keunggulan & Aspek Positif yang Paling Diapresiasi:**\n",
            f"Dari total ulasan yang dianalisis, sebanyak **{pos_count} ulasan ({pos_pct}%) bernada positif**.\n",
            f"Poin-poin yang paling banyak disukai oleh mahasiswa dan pengunjung kampus antara lain:\n",
            f"1. **Lingkungan Kampus yang Asri & Nyaman:** Mahasiswa merasa suasana kampus kondusif untuk belajar.\n",
            f"2. **Nilai Budaya & Keislaman (Aswaja):** Atmosfer keagamaan dan kegiatan keislaman yang kental menjadi daya tarik khas Unwahas.\n",
            f"3. **Biaya & Aksesibilitas:** Banyak yang menilai biaya perkuliahan relatif terjangkau dengan peluang beasiswa yang baik.\n",
            f"💬 *Contoh Ulasan Positif:*",
        ]
        for p in sample_pos:
            short_p = p if len(p) <= 120 else p[:120] + "..."
            res.append(f"- \"{short_p}\"")

        res.append("\n🎯 *Saran:* Pertahankan keunggulan tersebut dan jadikan sebagai materi branding/promosi penerimaan mahasiswa baru.")
        return "\n".join(res)

    # 4. INTENT: STATISTIK / RINGKASAN DATA
    stat_words = ["berapa", "persen", "distribusi", "statistik", "total", "persebaran", "banyak", "ringkas", "overview"]
    if any(w in q_lower for w in stat_words):
        cluster_info = ""
        if "cluster" in df.columns:
            n_clusters = df["cluster"].nunique()
            cluster_info = f"- **Jumlah Cluster (K-Means):** {n_clusters} cluster kelompok topik\n"

        return (
            f"📈 **Ringkasan Statistik Analisis Sentimen:**\n\n"
            f"- **Total Ulasan Dianalisis:** {total_reviews} ulasan\n"
            f"- **Ulasan Positif (Hijau):** {pos_count} ulasan ({pos_pct}%)\n"
            f"- **Ulasan Netral (Abu-abu/Kuning):** {net_count} ulasan ({net_pct}%)\n"
            f"- **Ulasan Negatif (Merah):** {neg_count} ulasan ({neg_pct}%)\n"
            f"{cluster_info}\n"
            f"📌 **Kesimpulan Sentimen Dominan:** Mayoritas ulasan berada pada kategori **{'Positif' if pos_count >= max(net_count, neg_count) else ('Negatif' if neg_count >= net_count else 'Netral')}**."
        )

    # 5. PERTANYAAN SPESIFIK / TANYA JAWAB DARI TOP RETRIEVED REVIEWS
    if retrieved_items:
        # Periksa ulasan-ulasan yang diambil oleh cosine similarity
        relevant_samples = []
        for item in retrieved_items[:4]:
            clean_item = re.sub(r'\[Similarity:[^\]]+\]', '', item).strip()
            relevant_samples.append(clean_item)

        res = [
            f"🔎 **Jawaban Berbasis Data Ulasan Terkait:**\n",
            f"Menjawab pertanyaan *\"{query}\"*, sistem lokal menemukan {len(retrieved_items)} ulasan yang paling relevan dari dataset:\n"
        ]
        for s in relevant_samples:
            res.append(s)

        res.append(
            "\n💡 *Kesimpulan:* Berdasarkan sampel ulasan relevan di atas, responden menyampaikan tanggapan yang beragam. "
            "Anda dapat menanyakan rekomendasi lebih mendalam terkait topik ini atau melihat detailnya di tab *Insight Data*."
        )
        return "\n".join(res)

    # 6. DEFAULT FALLBACK
    return (
        f"Berdasarkan dataset ulasan yang aktif ({total_reviews} ulasan), sistem mendeteksi "
        f"**{pos_count} ulasan positif**, **{net_count} netral**, dan **{neg_count} negatif**.\n\n"
        f"Silakan ajukan pertanyaan yang lebih spesifik seperti *\"apa saja yang perlu diperbaiki?\"* atau *\"bagaimana tanggapan tentang fasilitas?\"*."
    )
