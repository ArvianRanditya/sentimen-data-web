import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def generate_nlg_recommendation(topic_name, keywords, positif, netral, negatif, total, mode: str = "local"):
    """
    Generate narrative recommendation based on sentiment and keywords.
    mode can be "local" (built-in offline template) or "gemini" (cloud AI).
    """
    if mode == "local":
        return generate_template_based_nlg(topic_name, keywords, positif, netral, negatif, total)

    # Cloud AI mode (Gemini)
    load_dotenv(override=True)
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        fallback = generate_template_based_nlg(topic_name, keywords, positif, netral, negatif, total)
        return f"{fallback}\n\n*(Catatan: Menggunakan Sistem Lokal karena GEMINI_API_KEY belum dikonfigurasi di file .env)*"

    prompt = f"""
    Anda adalah seorang asisten AI akademis/universitas dan ahli analisis teks. 
    Buatlah sebuah narasi rekomendasi tindak lanjut singkat (1-2 paragraf, maksimal 120 kata) dalam Bahasa Indonesia yang profesional dan ramah pengguna berdasarkan data cluster ulasan mahasiswa berikut:
    - Kategori Bidang/Topik: {topic_name}
    - Kata Kunci Utama (TF-IDF): {', '.join(keywords)}
    - Distribusi Sentimen: Positif ({positif} ulasan), Netral ({netral} ulasan), Negatif ({negatif} ulasan)
    - Total Data Ulasan di Cluster ini: {total} ulasan

    Panduan menulis:
    1. Mulai dengan menyimpulkan sentimen dominan secara halus (misalnya: ulasan bernada sangat positif, atau banyak dikritik mahasiswa).
    2. Hubungkan dengan kata kunci utama yang sering disebut mahasiswa.
    3. Berikan saran/rekomendasi konkret berbasis tindakan (actionable recommendation) untuk pengelola kampus/universitas demi meningkatkan kepuasan mahasiswa.
    4. Tulis langsung narasinya saja tanpa embel-embel kalimat pembuka seperti "Tentu, ini rekomendasinya:" atau tanda kutip.
    """.strip()

    try:
        return call_gemini(gemini_key, prompt)
    except Exception as e:
        print(f"Gemini NLG failed: {str(e)}")
        fallback = generate_template_based_nlg(topic_name, keywords, positif, netral, negatif, total)
        return f"{fallback}\n\n*(Catatan: Menggunakan Sistem Lokal karena koneksi Gemini API gagal/terkendala: {str(e)})*"


def call_openai(api_key, prompt):
    url = "https://api.openai.com/v1/chat/completions"
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Anda adalah asisten AI yang memberikan rekomendasi naratif berbasis data secara profesional."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        res = json.loads(response.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"].strip()


def call_gemini(api_key, prompt):
    load_dotenv(override=True)
    preferred_model = os.getenv("GEMINI_MODEL", "gemini-3.7-flash").strip()
    
    # Model candidates in priority order
    models_to_try = [preferred_model]
    for m in ["gemini-3.7-flash", "gemini-3.5-flash", "gemini-flash-latest", "gemini-3.5-flash-lite"]:
        if m not in models_to_try:
            models_to_try.append(m)

    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2000
        }
    }
    
    last_err = None
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                res = json.loads(response.read().decode("utf-8"))
                if "candidates" in res and len(res["candidates"]) > 0:
                    return res["candidates"][0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            last_err = e
            # If model not found (404) or overloaded (503), try next fallback model
            if e.code in (404, 503):
                continue
            raise
        except Exception as e:
            last_err = e
            continue

    if last_err:
        raise last_err
    raise RuntimeError("Semua model Gemini tidak dapat dijangkau")



def call_groq(api_key, prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Anda adalah asisten AI yang memberikan rekomendasi naratif berbasis data secara profesional."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        res = json.loads(response.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"].strip()


def call_ollama(base_url, prompt):
    # Ensure url has trailing slash and appropriate port/path
    # Usually Ollama runs on port 11434, path /api/generate
    endpoint = f"{base_url.rstrip('/')}/api/generate"
    model = os.getenv("OLLAMA_MODEL", "llama3")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 300
        }
    }
    
    req = urllib.request.Request(endpoint, data=json.dumps(data).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        res = json.loads(response.read().decode("utf-8"))
        return res["response"].strip()


def generate_template_based_nlg(topic_name, keywords, positif, netral, negatif, total):
    """
    Fallback method that generates a high-quality Indonesian summary narrative
    using dynamic templates based on the cluster metrics.
    """
    if total == 0:
        return "Tidak ada data ulasan yang cukup dalam cluster ini untuk dianalisis."

    # Determine dominant sentiment
    sent_dict = {"Positif": positif, "Netral": netral, "Negatif": negatif}
    dominant_sent = max(sent_dict, key=sent_dict.get)
    dominant_count = sent_dict[dominant_sent]
    pct = round(dominant_count / total * 100, 1)
    
    # Capitalize keywords for display
    kw_str = ", ".join([f"'{w}'" for w in keywords[:5]])
    
    # Part 1: Sentiment Conclusion
    if dominant_sent == "Positif":
        p1 = f"Cluster **{topic_name}** menunjukkan tingkat kepuasan yang tinggi dari mahasiswa/pengguna. Sebanyak {positif} ulasan ({pct}%) bernada positif, yang menandakan bahwa program atau fasilitas terkait berjalan dengan sangat baik dan dirasakan manfaatnya secara nyata."
    elif dominant_sent == "Negatif":
        p1 = f"Cluster **{topic_name}** didominasi oleh umpan balik kritis dan keluhan. Sebanyak {negatif} ulasan ({pct}%) bernada negatif, yang mengindikasikan adanya kendala serius atau ketidakpuasan yang dirasakan secara langsung oleh responden."
    else:
        p1 = f"Cluster **{topic_name}** memiliki respon yang cenderung berimbang atau netral. Sebanyak {netral} ulasan ({pct}%) bernada netral, menandakan bahwa layanan atau aspek ini sudah cukup memenuhi ekspektasi dasar namun masih memiliki ruang yang luas untuk ditingkatkan."

    # Part 2: Keyword Contextual Analysis
    p2 = ""
    # Look for matching campus-related topics
    clean_topic = topic_name.lower()
    if "lingkungan" in clean_topic or "fasilitas" in clean_topic:
        if dominant_sent == "Positif":
            p2 = f"Mahasiswa mengapresiasi kenyamanan lingkungan fisik kampus yang tercermin dari kata kunci dominan seperti {kw_str}. Hal ini sangat menunjang suasana belajar mengajar yang kondusif."
        elif dominant_sent == "Negatif":
            p2 = f"Kritik mahasiswa terfokus pada kenyamanan sarana fisik serta kebersihan fasilitas, yang diwakili oleh kata {kw_str}. Permasalahan ini berpotensi mengganggu aktivitas harian di area kampus jika dibiarkan."
        else:
            p2 = f"Aspek lingkungan fisik dinilai fungsional secara umum. Namun, kemunculan kata kunci seperti {kw_str} menunjukkan perlunya pemeliharaan sarana secara berkala."
            
    elif "akademik" in clean_topic or "kuliah" in clean_topic or "dosen" in clean_topic:
        if dominant_sent == "Positif":
            p2 = f"Kualitas pengajaran, kompetensi dosen, dan kesiapan administrasi kelas mendapat respons positif dengan kata kunci seperti {kw_str}. Hal ini mencerminkan komitmen akademik yang kuat."
        elif dominant_sent == "Negatif":
            p2 = f"Terdapat keluhan signifikan mengenai penjadwalan, koordinasi materi perkuliahan, atau kejelasan komunikasi dosen yang diidentifikasi dari istilah {kw_str}."
        else:
            p2 = f"Proses administrasi dan perkuliahan dinilai standar. Akan tetapi, kata kunci {kw_str} memberikan isyarat bahwa metode pengajaran interaktif perlu lebih digalakkan."
            
    elif "budaya" in clean_topic or "nilai" in clean_topic or "aswaja" in clean_topic or "islam" in clean_topic:
        if dominant_sent == "Positif":
            p2 = f"Penerapan nilai keagamaan Aswaja, kegiatan ibadah di masjid, serta atmosfer kampus islami dirasa sangat kental dan diapresiasi tinggi, terbukti dari kata kunci {kw_str}."
        elif dominant_sent == "Negatif":
            p2 = f"Terdapat catatan mengenai perlunya penyesuaian kemasan kegiatan keagamaan atau nilai budaya agar lebih relevan dengan aspirasi mahasiswa masa kini, merujuk pada kata kunci {kw_str}."
        else:
            p2 = f"Internalisasi nilai budaya kampus berjalan konisten secara umum, tetapi kata kunci {kw_str} mengindikasikan perlunya variasi acara kerohanian yang lebih kreatif."
            
    else:
        # Generic fallback based on keywords
        p2 = f"Pembahasan utama di dalam kelompok ulasan ini berfokus pada istilah penting seperti {kw_str} yang menjadi poin pembicaraan krusial."

    # Part 3: Actionable Recommendation
    p3 = ""
    if dominant_sent == "Negatif" or dominant_sent == "Netral":
        p3 = f"**Rekomendasi Tindak Lanjut:** Pihak pengelola kampus disarankan segera melakukan audit internal dan mengevaluasi secara spesifik keluhan yang menyangkut {', '.join(keywords[:3])}. Melakukan diskusi terbuka atau survei kepuasan mendalam sangat penting untuk memperbaiki sarana/proses tersebut."
    else:
        p3 = f"**Rekomendasi Tindak Lanjut:** Manajemen kampus sebaiknya mempertahankan standar tinggi yang ada saat ini. Jadikan keunggulan di bidang {', '.join(keywords[:3])} sebagai materi promosi institusi, sembari melakukan pemantauan berkala agar kualitas pelayanan tidak menurun."

    return f"{p1}\n\n{p2} {p3}"
