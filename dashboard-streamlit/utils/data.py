import json

import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split

from utils.paths import DATA_PATH, METADATA_PATH
from utils.supabase_config import get_supabase_connection


LABEL_TO_ID = {"negative": 0, "neutral": 1, "positive": 2}
# Kolom teks akhir hasil preprocessing notebook (setelah stopword removal)
TEXT_FEATURE_COL = "text_akhir"
# Kolom label sentimen di CSV
TARGET_COL = "polarity"
SUPABASE_DATASET_TABLE = "zenlytics_reviews"
SUPABASE_DATASET_COLUMNS = {
    "review_id",
    "review_text_stemmed",
    "sentiment_label",
    "sentiment_encoded",
    "rating",
    "rating_group_encoded",
    "product_category",
    "price_category_encoded",
    "log_sold_count",
    "review_length_char",
    "review_word_count",
    "review_year",
    "review_month",
    "is_price_outlier",
    "is_anomaly",
}


def _first_existing_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for column in candidates:
        if column in df.columns:
            return column
    return None


def prepare_notebook02_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Standarisasi nama kolom agar konsisten di seluruh dashboard.

    Dataset asli: text_akhir (teks sudah diproses), polarity (label sentimen)
    Dashboard: review_text_stemmed (alias), sentiment_label (alias)
    """
    df = df.copy()
    sentiment_col = _first_existing_column(df, [TARGET_COL, "sentiment_label", "sentiment", "label"])
    text_col = _first_existing_column(
        df,
        [TEXT_FEATURE_COL, "review_text_stemmed", "processed_text", "review_text", "text"],
    )

    if sentiment_col is None:
        raise ValueError(
            "Dataset Supabase belum punya kolom sentimen. "
            "Butuh salah satu dari: polarity, sentiment_label, sentiment, label."
        )

    if text_col is None:
        raise ValueError(
            "Dataset Supabase belum punya kolom teks. "
            "Butuh salah satu dari: text_akhir, review_text_stemmed, processed_text, review_text, text."
        )

    df["sentiment_label"] = df[sentiment_col].astype(str).str.strip().str.lower()
    df["sentiment_encoded"] = df["sentiment_label"].map(LABEL_TO_ID).astype("Int64")

    df["review_text_stemmed"] = df[text_col].fillna("").astype(str)

    category_col = _first_existing_column(df, ["product_category", "category", "kategori_produk"])
    if category_col is None:
        df["product_category"] = "Unknown"
    elif category_col != "product_category":
        df["product_category"] = df[category_col].fillna("Unknown").astype(str)

    if "review_word_count" not in df.columns:
        df["review_word_count"] = df["review_text_stemmed"].str.split().str.len()
    return df


@st.cache_data(show_spinner=False)
def load_local_dataset() -> pd.DataFrame:
    return prepare_notebook02_dataset(pd.read_csv(DATA_PATH))


@st.cache_data(show_spinner=False)
def load_supabase_dataset() -> pd.DataFrame:
    conn = get_supabase_connection()
    try:
        df = pd.read_sql_query(f'SELECT * FROM "{SUPABASE_DATASET_TABLE}";', conn)
    finally:
        conn.close()

    return prepare_notebook02_dataset(df)


@st.cache_data(show_spinner=False)
def load_dataset(required_columns: tuple[str, ...] = ()) -> pd.DataFrame:
    missing_from_supabase = set(required_columns) - SUPABASE_DATASET_COLUMNS
    if missing_from_supabase:
        return load_local_dataset()

    return load_supabase_dataset()


@st.cache_data(show_spinner=False)
def load_modeling_dataset() -> pd.DataFrame:
    return load_dataset().reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_train_test() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = load_modeling_dataset()
    train, test = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["sentiment_label"],
    )
    return train.reset_index(drop=True), test.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_metadata() -> dict:
    if not METADATA_PATH.exists():
        return {}
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def sentiment_summary(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["sentiment_label"].value_counts().rename_axis("sentiment").reset_index(name="count")
    counts["percentage"] = counts["count"] / counts["count"].sum() * 100
    order = {"positive": 0, "neutral": 1, "negative": 2}
    return counts.sort_values("sentiment", key=lambda s: s.map(order)).reset_index(drop=True)
