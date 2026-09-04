import re
import os
import traceback
import pandas as pd
from serpapi import GoogleSearch
from dotenv import load_dotenv

# ============================================================
# Load API KEY dari file .env (JANGAN hardcode di sini!)
# ============================================================

load_dotenv()
API_KEY = os.getenv("SERPAPI_KEY", "")


# ============================================================
# AMBIL NAMA TEMPAT DARI URL GOOGLE MAPS
# ============================================================

def extract_query(url):
    try:
        match = re.search(r'/place/([^/]+)', url)
        if match:
            return match.group(1).replace('+', ' ')
    except:
        pass
    return None



# ============================================================
# AMBIL PLACE_ID (PALING STABIL)
# ============================================================

def get_place_id(query):

    params = {
        "engine": "google_maps",
        "q": query,
        "api_key": API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

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

    query = extract_query(url)

    if not query:
        raise ValueError("Tidak bisa membaca nama tempat dari URL")

    place_id = get_place_id(query)

    if not place_id:
        raise ValueError("Gagal mendapatkan place_id")

    data = []
    next_page_token = None

    while len(data) < max_reviews:

        params = {
            "engine": "google_maps_reviews",
            "place_id": place_id,
            "api_key": API_KEY,
            "hl": "id"
        }

        # Kalau ada token halaman berikutnya, tambahkan ke params
        if next_page_token:
            params["next_page_token"] = next_page_token

        search = GoogleSearch(params)
        results = search.get_dict()

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
                "Source": url
            })

        # Cek apakah ada halaman berikutnya
        pagination = results.get("serpapi_pagination", {})
        next_page_token = pagination.get("next_page_token")

        # Kalau tidak ada token lanjutan, berarti sudah habis
        if not next_page_token:
            break

    if not data:
        raise ValueError("Tidak ada review ditemukan")

    return pd.DataFrame(data)


# ============================================================
# MULTI URL
# ============================================================

def scrape_multiple_urls(url_list, max_reviews=50):

    all_data = []

    for url in url_list:

        try:
            print(f"Scraping: {url}")

            df = scrape_reviews_from_url(url, max_reviews)

            all_data.append(df)

        except Exception as e:
            print(f"Gagal di {url}: {e}")
            traceback.print_exc()

    if not all_data:
        raise ValueError("Semua URL gagal")

    final_df = pd.concat(all_data, ignore_index=True)

    return final_df