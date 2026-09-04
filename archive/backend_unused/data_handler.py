import pandas as pd


# ============================================================
# VALIDASI DATA
# ============================================================

def validate_data(df):
    """
    Pastikan kolom 'Review' ada
    """
    if 'Review' not in df.columns:
        raise ValueError("Dataset harus memiliki kolom 'Review'")
    return df


# ============================================================
# GABUNG DATA
# ============================================================

def combine_data(existing_df, new_df):
    """
    Gabungkan data lama dan baru
    """
    if existing_df is None:
        return new_df

    combined = pd.concat([existing_df, new_df], ignore_index=True)
    return combined


# ============================================================
# INFO DATASET
# ============================================================

def get_dataset_info(df):

    total_data = len(df)
    missing = df['Review'].isna().sum()
    duplicate = df.duplicated().sum()

    info = {
        "total_data": total_data,
        "missing": missing,
        "duplicate": duplicate
    }

    return info


# ============================================================
# CLEANING DATA
# ============================================================

def clean_data(df):
    """
    - Hapus missing
    - Hapus duplicate
    """

    df = df.copy()

    df = df.dropna(subset=['Review'])
    df = df.drop_duplicates(subset=['Review'])

    df = df.reset_index(drop=True)

    return df


# ============================================================
# LOAD FILE (CSV / EXCEL)
# ============================================================

def load_file(uploaded_file):

    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)

    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)

    else:
        raise ValueError("Format file tidak didukung (gunakan CSV/XLSX)")

    return validate_data(df)


# ============================================================
# EXPORT FILE
# ============================================================

def convert_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')


def convert_to_excel(df):
    from io import BytesIO

    buffer = BytesIO()
    df.to_excel(buffer, index=False)

    return buffer.getvalue()