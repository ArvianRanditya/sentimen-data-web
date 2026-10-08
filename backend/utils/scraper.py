import re
import os
import traceback
import pandas as pd
from serpapi import GoogleSearch
from dotenv import load_dotenv

# ============================================================
# Load API KEY dari file .env (JANGAN hardcode di sini!)
# ============================================================

def get_api_key():
    load_dotenv(override=True)
    return os.getenv("SERPAPI_KEY", "").strip()


# ============================================================
# AMBIL NAMA TEMPAT DARI URL GOOGLE MAPS
# ============================================================

def extract_query(url):
    try:
        match = re.search(r'/place/([^/@]+)', url)
        if match:
            return match.group(1).replace('+', ' ').strip()
    except Exception:
        pass
    return None


# ============================================================
# AMBIL PLACE_ID (PALING STABIL)
# ============================================================

def get_place_id(query):
    api_key = get_api_key()
    if not api_key:
        raise ValueError("SERPAPI_KEY belum dikonfigurasi di file .env")

    params = {
        "engine": "google_maps",
        "q": query,
        "api_key": api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "error" in results:
        raise ValueError(f"SerpAPI Error: {results['error']}")

    # PRIORITAS 1
    if "place_results" in results:
        return results["place_results"].get("place_id")

    # PRIORITAS 2
    if "local_results" in results and len(results["local_results"]) > 0:
        return results["local_results"][0].get("place_id")

    return None


# ============================================================
# SCRAPE 1 TEMPAT (DENGAN PAGINATION)
# ============================================================

def scrape_reviews_from_url(url, max_reviews=50):
    api_key = get_api_key()
    if not api_key:
        raise ValueError("SERPAPI_KEY belum dikonfigurasi di file .env backend")

    clean_url = url.strip()
    query = extract_query(clean_url)

    if not query:
        if not clean_url.startswith("http"):
            query = clean_url
        else:
            raise ValueError("Tidak bisa membaca nama tempat dari URL Google Maps")

    place_id = get_place_id(query)

    if not place_id:
        raise ValueError(f"Gagal mendapatkan data lokasi di Google Maps untuk '{query}'")

    data = []
    next_page_token = None

    while len(data) < max_reviews:
        params = {
            "engine": "google_maps_reviews",
            "place_id": place_id,
            "api_key": api_key,
            "hl": "id"
        }

        # Kalau ada token halaman berikutnya, tambahkan ke params
        if next_page_token:
            params["next_page_token"] = next_page_token

        search = GoogleSearch(params)
        results = search.get_dict()

        if "error" in results:
            raise ValueError(f"SerpAPI Reviews Error: {results['error']}")

        reviews = results.get("reviews", [])

        if not reviews:
            break  # Tidak ada ulasan lagi, hentikan loop

        for r in reviews:
            if len(data) >= max_reviews:
                break
            data.append({
                "Review": r.get("snippet", ""),
                "Rating": r.get("rating", ""),
                "User": r.get("user", {}).get("name", ""),
                "Source": clean_url
            })

        # Cek apakah ada halaman berikutnya
        pagination = results.get("serpapi_pagination", {})
        next_page_token = pagination.get("next_page_token")

        # Kalau tidak ada token lanjutan, berarti sudah habis
        if not next_page_token:
            break

    if not data:
        raise ValueError(f"Tidak ada review ditemukan untuk lokasi '{query}'")

    return pd.DataFrame(data)


# ============================================================
# MULTI URL
# ============================================================

def scrape_multiple_urls(url_list, max_reviews=50):
    all_data = []
    errors = []

    for url in url_list:
        if not url.strip():
            continue
        try:
            print(f"Scraping: {url.strip()}")
            df = scrape_reviews_from_url(url.strip(), max_reviews)
            all_data.append(df)
        except Exception as e:
            print(f"Gagal di {url}: {e}")
            traceback.print_exc()
            errors.append(str(e))

    if not all_data:
        err_msg = "; ".join(errors) if errors else "Semua URL gagal diproses"
        raise ValueError(f"Gagal scraping: {err_msg}")

    final_df = pd.concat(all_data, ignore_index=True)
    return final_df