import streamlit as st

from utils.data import load_metadata
from utils.ui import page_hero, setup_page


setup_page("About Project", "ℹ️")
metadata = load_metadata()

page_hero(
    "About Zenlytics",
    "AI-based Sentiment Analytics for Tokopedia Product Reviews.",
)

st.subheader("Tujuan")
st.markdown(
    """
    Dashboard ini dibuat untuk membantu pembacaan insight sentimen review produk secara cepat,
    mulai dari ringkasan dataset, prediksi realtime, analitik kata, evaluasi model, sampai batch prediction.
    """
)

st.subheader("Pipeline")
st.markdown(
    """
    Website mengikuti notebook 02: data memakai `fix_tokopedia_reviews.csv`, fitur teks memakai
    `text_akhir`, target memakai `polarity`, dan model utama memakai artefak SVM Data Murni
    dari `modeling/model_save/model_svm.pkl` plus `modeling/tfidf_vectorizer.pkl`.
    """
)

st.subheader("Metadata")
st.json(
    {
        "project": metadata.get("project", "Zenlytics"),
        "version": metadata.get("versi", "v1.0"),
        "created_by": metadata.get("dibuat_oleh", "PJK - GM028"),
        "rows_clean": metadata.get("total_rows_clean"),
        "train_size": metadata.get("train_size"),
        "test_size": metadata.get("test_size"),
        "dataset": "data/fix_tokopedia_reviews.csv",
        "feature_column": "text_akhir",
        "target_column": "polarity",
        "model": "modeling/model_save/model_svm.pkl",
        "vectorizer": "modeling/tfidf_vectorizer.pkl",
    }
)
