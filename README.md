# 📊 SentimenAI - Clustering & Sentiment Analysis Dashboard

![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)

SentimenAI adalah aplikasi dashboard komprehensif untuk menganalisis sentimen dan melakukan clustering pada data teks (seperti ulasan pelanggan). Sistem ini menggunakan arsitektur modern yang memisahkan antara **Frontend (Vue.js)** dan **Backend (FastAPI & Machine Learning Python)**.

Aplikasi ini sangat cocok untuk memproses data ulasan dari platform seperti Google Maps, mengelompokkannya (Clustering), dan memberikan label sentimen otomatis sebelum melatih model *Machine Learning* untuk prediksi tingkat lanjut.

---

## ✨ Fitur Utama

Aplikasi ini memiliki 9 langkah pipeline (alur pemrosesan) otomatis:
1. **Input Data**: Upload dataset (CSV/Excel) atau *scrape* otomatis dari Google Maps.
2. **Preprocessing**: Pembersihan teks otomatis (hapus tanda baca, angka, *stopword*, dan proses *stemming* Bahasa Indonesia).
3. **Clustering (K-Means)**: Pengelompokan data ke dalam beberapa cluster, lengkap dengan evaluasi otomatis (Metode *Elbow*, *Silhouette*, dan *Calinski-Harabasz*).
4. **Topik Cluster**: Melihat ekstraksi kata kunci paling dominan dari tiap cluster menggunakan perhitungan TF-IDF.
5. **Labeling Sentimen**: Pemberian label (Positif/Netral/Negatif) secara otomatis menggunakan pendekatan *Lexicon*.
6. **Training Model**: Pelatihan model *Random Forest* berdasarkan data yang telah dilabeli sebelumnya.
7. **Evaluasi Model**: Tampilan *Confusion Matrix* dan akurasi (Precision, Recall, F1-Score) dari model yang telah dilatih.
8. **Insight Data**: Ringkasan visual secara global tentang persebaran sentimen dan cluster.
9. **Klasifikasi Baru**: Prediksi teks tunggal secara langsung, atau prediksi masal (*batch prediction*) menggunakan file baru.

---

## 🛠️ Teknologi yang Digunakan

Aplikasi ini dibagi menjadi 2 bagian utama (*Decoupled Architecture*):

**1. Backend (Dapur Pengolah Data)**
Berjalan di **Port 8000** menggunakan:
- **FastAPI**: Framework web super cepat untuk membuat API.
- **Pandas**: Pengelolaan manipulasi data (*DataFrame*).
- **Scikit-Learn**: Library *Machine Learning* untuk K-Means, Random Forest, & Evaluasi.
- **PySastrawi**: Library NLP khusus untuk *stemming* kata Bahasa Indonesia.
- **Python-Dotenv**: Mengamankan *API Key* melalui file `.env`.

**2. Frontend (Tampilan Pengguna / UI)**
Berjalan di **Port 5173** menggunakan:
- **Vue.js 3**: Framework *Javascript* modern.
- **Pinia**: *State Management* modern untuk menyimpan data sesi (Session ID).
- **Chart.js & Vue-ChartJS**: Pembuatan grafik visual interaktif.
- **Tailwind CSS**: Styling tampilan *Dashboard* dan komponen *UI*.

---

## 🚀 Panduan Instalasi Lengkap (Untuk Pemula)

Aplikasi ini terdiri dari dua bagian yang berjalan secara bersamaan: **Backend** (pemroses data) dan **Frontend** (tampilan antarmuka). Kamu harus menjalankan keduanya agar aplikasi berfungsi penuh.

### Persiapan Awal (Wajib)
Sebelum mulai, pastikan komputermu sudah ter-install 2 aplikasi ini:
1. **Python** (Minimal versi 3.9)
   - Download di: [python.org/downloads](https://www.python.org/downloads/)
   - *Penting saat install Python di Windows: Pastikan kamu mencentang kotak **"Add Python to PATH"** di bagian paling bawah layar instalasi awal.*
2. **Node.js** (Minimal versi 18)
   - Download versi LTS (Long Term Support) di: [nodejs.org](https://nodejs.org/)
   - Install seperti aplikasi biasa (Next, Next, Install).

---

### Langkah 1: Siapkan Backend (Dapur Pengolah Data)

Backend ini menggunakan Python dan bertugas melakukan komputasi berat seperti *Machine Learning*.

1. **Buka Terminal / Command Prompt (CMD)**, lalu arahkan ke folder proyek ini.
2. Masuk ke dalam folder `backend`:
   ```bash
   cd backend
   ```
3. **Buat Virtual Environment (Lingkungan Virtual)**
   Ini bertujuan agar paket Python untuk aplikasi ini tidak bercampur dengan aplikasi lain di komputermu. Ketikkan:
   ```bash
   python -m venv venv
   ```
   *(Akan muncul folder baru bernama `venv` di dalam folder backend).*
4. **Aktifkan Virtual Environment**
   - Jika kamu pakai **Windows** (Command Prompt / PowerShell):
     ```bash
     venv\Scripts\activate
     ```
   - Jika kamu pakai **Mac / Linux**:
     ```bash
     source venv/bin/activate
     ```
   *(Tanda berhasil: akan muncul tulisan `(venv)` di paling kiri terminalmu).*
5. **Install Semua Library yang Dibutuhkan**
   Ketik perintah berikut untuk mengunduh semua library (seperti Pandas, Scikit-Learn, FastAPI) dari file `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   *(Tunggu beberapa saat sampai proses unduh selesai).*
6. **(Opsional) Siapkan API Key untuk Scraping**
   - Buat file baru bernama `.env` di dalam folder `backend`.
   - Buka file `.env` tersebut pakai Notepad/teks editor, lalu isi dengan:
     ```env
     SERPAPI_KEY=masukkan_api_key_kamu_disini
     ```
   *(Kamu bisa mendapatkannya secara gratis dengan mendaftar di [SerpApi.com](https://serpapi.com/) jika butuh fitur mengambil data otomatis dari Google Maps).*
7. **Nyalakan Server Backend!**
   Ketikkan:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   ✅ *Jika muncul pesan `Application startup complete`, artinya Backend sudah berhasil menyala dan siap menerima perintah! **Biarkan terminal ini tetap terbuka**.*

---

### Langkah 2: Siapkan Frontend (Tampilan Web Pengguna)

Karena terminal pertama tadi sudah dipakai untuk menjalankan Backend, sekarang kamu harus membuka **Terminal (CMD) yang KEDUA**.

1. Di terminal kedua yang baru saja dibuka, masuk ke folder `frontend`:
   ```bash
   cd frontend
   ```
2. **Install Library Bawaan Node.js**
   Ketik perintah ini untuk mengunduh library seperti Vue.js dan TailwindCSS:
   ```bash
   npm install
   ```
   *(Tunggu sampai proses loading selesai dan muncul tulisan `added xxx packages`).*
3. **Nyalakan Server Frontend!**
   Ketikkan:
   ```bash
   npm run dev
   ```
   ✅ *Jika berhasil, akan muncul tulisan `VITE v5.x.x ready in xxx ms` dan URL lokal (contoh: `http://localhost:5173/`).*

---

### Langkah 3: Mulai Gunakan Aplikasi! 🎉

1. Buka browser favoritmu (Google Chrome, Mozilla Firefox, atau Edge).
2. Ketikkan alamat URL berikut di bagian atas (address bar):
   👉 **`http://localhost:5173`**
3. Selesai! Kamu sekarang sudah bisa menggunakan aplikasi SentimenAI secara penuh.

> **Tips:** Ketika selesai menggunakan aplikasi, kamu bisa menutup server dengan cara menekan tombol `Ctrl + C` di masing-masing terminal.

---

## 📁 Struktur Direktori Singkat

```text
sentimen_analisis_master/
│
├── archive/                  # Arsip kode versi Streamlit lama & modul tidak terpakai
│   ├── streamlit_app/        # Aplikasi Streamlit (app.py, pages, assets, dll)
│   └── backend_unused/       # Berkas utilitas backend yang tidak digunakan
│
├── backend/                  # BACKEND (FastAPI & Machine Learning Python)
│   ├── main.py               # File utama server API
│   ├── requirements.txt      # Daftar library Python backend
│   ├── utils/                # Modul utilitas aktif (nlg, predictor, preprocessing, scraper, topic_rules)
│   ├── models/               # Tempat penyimpanan model terlatih (.pkl)
│   └── temp_data/            # Tempat penyimpanan dataset sementara per sesi
│
├── docs/                     # DOKUMENTASI PROYEK
│   ├── DOKUMENTASI.md        # Panduan backend & frontend lengkap
│   ├── penjelasan_sistem.txt # Alur sistem singkat
│   └── format_dataset.txt    # Panduan format data input
│
└── frontend/                 # FRONTEND (Vue.js 3 / Vite)
    ├── index.html            # File HTML utama
    ├── package.json          # Dependency frontend
    └── src/
        ├── components/       # Komponen UI (Navbar, dll)
        ├── views/            # Halaman views pipeline 9 langkah
        ├── store/            # State management sesi (Pinia)
        └── router/           # Router navigasi halaman
```

---

## 🤝 Catatan Tambahan

- Saat mengunggah dataset berformat CSV atau Excel, pastikan terdapat satu kolom utama bernama **`Review`** (dengan R besar) yang berisi teks untuk dianalisis.
- Data yang diunggah aman dan hanya diproses di komputer lokalmu di dalam folder `backend/temp_data/`.
- File model hasil pelatihan otomatis akan tersimpan di dalam folder `backend/models/`.

Dibuat dengan ❤️ untuk kemudahan Analisis Sentimen!
