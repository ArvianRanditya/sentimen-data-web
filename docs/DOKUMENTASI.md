# 📘 Dokumentasi Proyek SentimenAI
### Panduan untuk Pemula — Memahami Backend & Frontend

---

## 🤔 Apa itu Backend dan Frontend?

Bayangkan sebuah **restoran** 🍽️

| Bagian Restoran | Di Dunia Web |
|---|---|
| **Dapur** (tempat masak, tidak kelihatan tamu) | **Backend** — tempat data diolah |
| **Ruang makan** (yang dilihat & digunakan tamu) | **Frontend** — tampilan yang dilihat pengguna |
| **Pelayan** (pengantar pesanan dapur → tamu) | **API** — penghubung backend & frontend |

Jadi dalam proyek ini:
- **Frontend** = tampilan web yang kamu buka di browser (Vue.js)
- **Backend** = program Python yang mengolah data di balik layar (FastAPI)
- **API** = "jembatan" yang menghubungkan keduanya

---

## 🗂️ Struktur Folder Proyek

```
sentimen_analisis_master/
│
├── 📁 backend/              ← DAPUR (Python / FastAPI)
│   ├── main.py              ← File utama backend (semua "resep" dan route API ada di sini)
│   ├── requirements.txt     ← Daftar dependensi Python yang dibutuhkan
│   ├── .env                 ← Berkas konfigurasi kunci API (SERPAPI & GEMINI)
│   ├── models/              ← File model AI yang sudah dilatih (.pkl)
│   │   ├── rf_model.pkl         ← Model Random Forest untuk sentimen
│   │   ├── tfidf_sentiment.pkl  ← Vectorizer TF-IDF untuk sentimen
│   │   ├── kmeans_model.pkl     ← Model K-Means untuk clustering
│   │   └── tfidf_cluster.pkl    ← Vectorizer TF-IDF untuk clustering
│   ├── temp_data/           ← Penyimpanan sementara data pengguna (CSV, JSON, XLSX)
│   ├── data_training/       ← Berkas data latih bawaan
│   │   └── data_training.xlsx   ← Data berlabel untuk melatih Random Forest
│   ├── lexicon/             ← Kamus kata sentimen (Legacy / Tidak digunakan lagi)
│   │   ├── positive.csv
│   │   └── negative.csv
│   └── utils/               ← Fungsi-fungsi pembantu
│       ├── preprocessing.py ← Proses teks (tokenisasi, normalisasi slang, stemming Sastrawi)
│       ├── predictor.py     ← Fungsi prediksi sentimen & cluster (memuat model .pkl)
│       ├── scraper.py       ← Ambil data dari Google Maps via SerpApi
│       ├── topic_rules.py   ← Penamaan topik cluster berbasis kecocokan kata kunci
│       ├── nlg.py           ← Generator narasi rekomendasi (Gemini/OpenAI atau Template)
│       └── rag_chat.py      ← Logika pencarian ulasan (RAG) & chatbot Gemini
│
└── 📁 frontend/             ← RUANG MAKAN (Vue.js 3 / Vite)
    ├── package.json         ← Konfigurasi dependensi JavaScript
    └── src/
        ├── views/           ← Halaman-halaman utama website
        │   ├── Beranda.vue         ← Dasbor dengan ringkasan pipeline
        │   ├── DataInput.vue       ← Upload file CSV/Excel atau Scraping
        │   ├── Preprocessing.vue   ← Pembersihan teks NLP
        │   ├── Training.vue        ← Pelatihan model Random Forest
        │   ├── Evaluasi.vue        ← Performa model & Confusion Matrix
        │   ├── Labeling.vue        ← Prediksi sentimen dataset aktif
        │   ├── Clustering.vue      ← Pengelompokkan data via K-Means
        │   ├── TopikCluster.vue    ← Analisis kata kunci per cluster
        │   ├── Insight.vue         ← Statistik global, NLG, & catatan analisis
        │   └── KlasifikasiBaru.vue  ← Uji coba prediksi data baru (single/batch)
        ├── components/      ← Komponen Vue yang bisa dipakai ulang
        │   ├── Navbar.vue          ← Menu navigasi atas
        │   ├── Layout.vue          ← Wrapper utama + tata letak sidebar
        │   ├── Sidebar.vue         ← Menu navigasi kiri
        │   ├── PipelineNav.vue     ← Navigasi langkah berurutan di bawah halaman
        │   ├── ChatWidget.vue      ← Widget asisten chatbot AI (RAG)
        │   ├── AppIcon.vue         ← Komponen ikon-ikon SVG
        │   └── ShapeGrid.vue       ← Animasi dekoratif di latar belakang
        ├── router/
        │   └── index.js            ← Konfigurasi rute navigasi halaman
        └── store/
            └── index.js            ← State management Pinia (menyimpan session_id)
```

---

## ▶️ Cara Menjalankan Proyek (Step by Step)

> **Penting:** Kamu butuh 2 terminal terbuka sekaligus!

### Terminal 1 — Jalankan Backend (Dapur)

```powershell
# 1. Pastikan berada di folder utama proyek (sentimen_analisis_master)
# 2. Aktifkan Virtual Environment agar seluruh package python (seperti serpapi, dll) termuat:
#    Jika menggunakan PowerShell:
.\.venv\Scripts\Activate.ps1

#    Jika menggunakan Command Prompt (CMD) biasa:
#    .\.venv\Scripts\activate.bat

# 3. Masuk ke folder backend
cd backend

# 4. Jalankan server Python
uvicorn main:app --reload --port 8000
```

Kalau berhasil, akan muncul:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Artinya:** Dapur sudah buka! Backend siap menerima pesanan.

---

### Terminal 2 — Jalankan Frontend (Ruang Makan)

```bash
# Masuk ke folder frontend
cd frontend

# Jalankan website
npm run dev
```

Kalau berhasil, akan muncul:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

**Artinya:** Ruang makan sudah buka! Buka browser dan akses `http://localhost:5173`

---

## 🔑 Konfigurasi Variabel Lingkungan (`.env`)

Untuk mengaktifkan fitur pencarian data ulasan (Chatbot AI) dan penarikan ulasan (Google Maps scraper), buatlah berkas bernama `.env` di dalam folder `backend/` dan isi dengan konfigurasi berikut:

```env
# Key untuk Scraping Google Maps (dapatkan di https://serpapi.com)
SERPAPI_KEY=isi_dengan_serpapi_key_kamu

# Key untuk Chatbot AI & NLG (dapatkan di https://aistudio.google.com)
GEMINI_API_KEY=isi_dengan_gemini_api_key_kamu

# Konfigurasi model Gemini (Opsional, bawaan: gemini-1.5-flash)
GEMINI_MODEL=gemini-1.5-flash
```

---

## 🔄 Bagaimana Backend dan Frontend Berkomunikasi?

Analoginya seperti tamu memesan makanan:

```
[Browser / Frontend]          [Backend / Python]
       |                              |
       | 1. Klik tombol "Upload"      |
       |----------------------------->|
       |   Kirim file CSV             |
       |                              | 2. Python baca file,
       |                              |    simpan sementara
       |                              |    (temp_data/)
       | 3. Terima balasan:           |
       |    "Upload berhasil!         |<-------------|
       |     200 data ditemukan"      |
       |                              |
```

Komunikasi ini dilakukan lewat **HTTP Request** ke URL tertentu.

---

## 🗺️ Daftar API Endpoint (Semua "Pintu" ke Backend)

| Metode & Endpoint URL | Fungsi | Dipakai di halaman |
|---|---|---|
| `POST /api/data/upload` | Mengunggah file CSV/Excel ulasan | Input Data |
| `POST /api/data/scrape` | Scrape review Google Maps via SerpApi | Input Data |
| `POST /api/data/clean` | Hapus ulasan duplikat & nilai kosong | Input Data |
| `GET /api/data/download/{session_id}` | Unduh berkas data mentah (`_raw.csv`) | Input Data (Unduh) |
| `POST /api/process/preprocess` | Pembersihan teks (NLP Preprocessing) | Preprocessing |
| `GET /api/preprocess/download/{session_id}` | Unduh data hasil preprocessing | Preprocessing (Unduh) |
| `POST /api/model/train` | Melatih model klasifikasi Random Forest | Training |
| `POST /api/data/info` | Mendapatkan statistik data berlabel | Training / Dashboard |
| `POST /api/sentiment/predict` | Pelabelan sentimen otomatis dengan Random Forest | Labeling (Analisis Sentimen) |
| `POST /api/cluster/evaluate` | Menghitung indeks Calinski-Harabasz per nilai K | Clustering |
| `POST /api/cluster/apply` | Menerapkan clustering K-Means pada ulasan | Clustering |
| `POST /api/cluster/topic` | Mendapatkan kata kunci TF-IDF per cluster | Topik Cluster |
| `POST /api/insight` | Mengambil statistik global analisis | Insight |
| `POST /api/nlg/recommend` | Membuat narasi rekomendasi AI per cluster | Insight (NLG) |
| `POST /api/chat` | Chatbot tanya jawab berbasis dokumen ulasan (RAG) | Semua halaman (Widget Obrolan) |
| `POST /api/model/predict` | Prediksi sentimen & cluster 1 teks baru | Klasifikasi Baru (Single) |
| `POST /api/model/predict_batch` | Klasifikasi massal ulasan dari berkas unggahan | Klasifikasi Baru (Batch) |
| `POST /api/download-analysis` | Mengunduh berkas laporan akhir (.xlsx) | Insight (Export Laporan) |

---

## 🔢 Urutan Penggunaan Aplikasi (Pipeline 9 Langkah)

Aplikasi dirancang dengan alur logis yang berurutan. Setiap langkah memproses keluaran dari langkah sebelumnya.

```
LANGKAH 1: Input Data
  → Unggah file CSV/Excel dengan kolom berisi review (misal: "Review" atau "Ulasan").
  → Atau lakukan scraping data dari tautan Google Maps.
  → Klik "Hapus Duplikat & Kosong" untuk membersihkan data mentah.
        ↓
LANGKAH 2: Preprocessing
  → Pembersihan teks secara otomatis:
    - Case Folding: Mengubah huruf kapital menjadi huruf kecil.
    - Filtering: Menghapus angka, URL, tanda baca, dan karakter aneh.
    - Normalisasi: Mengubah singkatan/slang menjadi kata baku (misal: "yg" -> "yang").
    - Stopword Removal: Membuang kata hubung/tidak penting (misal: "dan", "di", "yang").
    - Stemming Sastrawi: Mengembalikan kata berimbuhan ke kata dasar (misal: "berlari" -> "lari").
        ↓
LANGKAH 3: Training Model
  → Melatih model Random Forest menggunakan data latih terstandar (data_training.xlsx).
  → Menghasilkan model klasifikasi (`rf_model.pkl`) dan TF-IDF Vectorizer (`tfidf_sentiment.pkl`).
        ↓
LANGKAH 4: Evaluasi Model
  → Melihat performa model Random Forest hasil training.
  → Menampilkan visualisasi Confusion Matrix serta tabel Classification Report (Akurasi, Presisi, Recall, F1-Score).
        ↓
LANGKAH 5: Analisis Sentimen
  → Menggunakan model Random Forest yang sudah dilatih untuk melabeli dataset aktif milik Anda.
  → Memberikan label sentimen otomatis: Positif (2), Netral (1), atau Negatif (0).
        ↓
LANGKAH 6: Clustering K-Means
  → Mengevaluasi jumlah kelompok (K) optimal menggunakan Calinski-Harabasz Index.
  → Klik "Lakukan Clustering" untuk mengelompokkan data berdasarkan kemiripan teks.
        ↓
LANGKAH 7: Topik Cluster
  → Menampilkan 10 kata kunci teratas per kelompok data menggunakan metode pembobotan TF-IDF.
        ↓
LANGKAH 8: Insight
  → Menampilkan grafik visual gabungan antara cluster dan sentimen.
  → Memanggil asisten generator rekomendasi (NLG) untuk menyusun rekomendasi naratif berbasis data.
  → Pengguna dapat menulis catatan analisis mandiri per cluster.
        ↓
LANGKAH 9: Klasifikasi Baru
  → Uji coba model secara instan dengan memasukkan satu ulasan baru.
  → Atau unggah berkas excel baru untuk memprediksi sentimen dan topik clusternya secara massal.
```

---

## 🧰 Teknologi yang Digunakan

### Backend (Python)
| Library | Fungsi |
|---|---|
| **FastAPI** | Pembuatan API yang cepat, asinkron, dan terstruktur |
| **Uvicorn** | Server eksekusi aplikasi FastAPI |
| **Pandas & NumPy** | Analisis struktur data dan komputasi matriks |
| **Scikit-learn** | Machine learning (Random Forest, K-Means, TF-IDF Vectorizer, Metrik Evaluasi) |
| **PySastrawi** | Stemming morfologi Bahasa Indonesia |
| **NLTK** | Tokenisasi dan penyaring kata henti (*stopwords*) |
| **Joblib** | Serialization/penyimpanan dan pemuatan model AI (`.pkl`) |
| **python-dotenv** | Pengelolaan variabel lingkungan dan API key |
| **google-search-results** | Integrasi dengan API SerpApi untuk scraping ulasan Google Maps |

### Frontend (JavaScript/Vue)
| Library | Fungsi |
|---|---|
| **Vue.js 3** | Framework reaktif modern untuk antarmuka pengguna (UI) |
| **Vite** | Build tool super cepat untuk pengembangan Vue |
| **Vue Router** | Manajemen navigasi rute halaman |
| **Pinia** | State management untuk menyimpan session_id antar halaman |
| **Axios** | Melakukan HTTP Request/komunikasi data ke API Backend |
| **Chart.js & vue-chartjs** | Membuat diagram dan grafik visualisasi data yang interaktif |
| **Tailwind CSS** | Kerangka kerja CSS untuk desain antarmuka modern yang estetik |

---

## 💾 Penyimpanan Data

### Di Backend (Sementara)
Data hasil pemrosesan disimpan pada folder `temp_data/` dengan format:
```
{session_id}_raw.csv          ← Data mentah dari hasil upload/scrape
{session_id}_clean.csv        ← Hasil penyaringan data kosong/duplikat
{session_id}_preprocessed.csv ← Hasil preprocessing NLP
{session_id}_labeled.csv      ← Hasil prediksi sentimen otomatis (Random Forest)
{session_id}_clustered.csv    ← Hasil clustering akhir (K-Means)
{session_id}_nlg.json         ← Berkas rekomendasi naratif per cluster
```

### Di Frontend (Browser)
Data disimpan di **LocalStorage** browser agar tidak hilang saat halaman dimuat ulang (refresh):
* `session_id`: Untuk melacak file pemrosesan aktif pengguna di server.

---

## ❓ FAQ (Pertanyaan Umum)

**Q: Kenapa harus menggunakan requirements.txt untuk instalasi?**  
A: Karena proyek ini membutuhkan beberapa pustaka pembantu lain (seperti `nltk`, `openpyxl`, `python-multipart`) agar fitur pengolahan Excel, pengunduhan kamus stopword, dan unggah berkas berjalan lancar. Cukup jalankan `pip install -r requirements.txt` untuk mengunduh semuanya secara otomatis.

---

**Q: Mengapa Training Model (Langkah 3) ditaruh di awal sebelum Analisis Sentimen (Langkah 5)?**  
A: Karena aplikasi memprediksi sentimen ulasan dataset Anda (Langkah 5) menggunakan model Random Forest. Model ini harus dilatih dulu menggunakan dataset latihan (`data_training.xlsx`) di Langkah 3 agar siap digunakan untuk mengklasifikasi ulasan baru.

---

**Q: Di mana kamus Lexicon digunakan?**  
A: Kamus Lexicon (`backend/lexicon`) adalah sisa kode/metode lama (Legacy) dan saat ini sudah digantikan sepenuhnya oleh model klasifikasi Random Forest yang terbukti jauh lebih akurat dan adaptif terhadap ulasan baru.

---

**Q: Bagaimana cara kerja Chatbot Asisten Ulasan (RAG)?**  
A: Ketika Anda bertanya di widget obrolan, sistem akan mencari ulasan paling relevan di berkas sesi Anda menggunakan kemiripan kosakata (TF-IDF & Cosine Similarity). Teks ulasan yang relevan tersebut lalu dikirimkan ke model Gemini API bersama pertanyaan Anda untuk dirumuskan menjadi jawaban yang ramah dan akurat.

---

**Q: Mengapa rekomendasi NLG di halaman Insight bisa muncul meskipun saya tidak mengisi GEMINI_API_KEY?**  
A: Jika API Key tidak dikonfigurasi, sistem akan beralih secara otomatis (fallback) ke generator rekomendasi berbasis aturan template dinamis Bahasa Indonesia yang disesuaikan dengan topik dominan, kata kunci, dan persentase sentimen cluster tersebut.

---

## 🚀 Cara Install dari Awal (Fresh Install)

### Syarat:
* Python 3.9 atau lebih baru
* Node.js 18 atau lebih baru

### Backend:
```bash
# Masuk ke folder backend
cd backend

# Buat environment virtual (Opsional tapi disarankan)
python -m venv venv
venv\Scripts\activate   # Untuk Windows

# Install semua dependensi
pip install -r requirements.txt

# Buat file .env dan isi API Key Anda
# Jalankan backend
uvicorn main:app --reload --port 8000
```

### Frontend:
```bash
# Masuk ke folder frontend
cd frontend

# Install dependensi JavaScript
npm install

# Jalankan server local
npm run dev
```

Buka browser dan buka alamat `http://localhost:5173`
