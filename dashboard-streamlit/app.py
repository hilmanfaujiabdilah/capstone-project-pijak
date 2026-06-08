import streamlit as st

from utils.charts import category_chart, sentiment_distribution_chart, sentiment_donut_chart
from utils.data import load_dataset, load_metadata, sentiment_summary
from utils.ui import page_hero, setup_page


setup_page("Dashboard")

df = load_dataset(("sentiment_label", "product_category"))
metadata = load_metadata()
summary = sentiment_summary(df)

page_hero(
    "Sentiment Dashboard",
    "Dashboard analisis sentimen review produk Tokopedia.",
)

total_reviews = len(df)
positive = int((df["sentiment_label"] == "positive").sum())
neutral = int((df["sentiment_label"] == "neutral").sum())
negative = int((df["sentiment_label"] == "negative").sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Dataset", f"{total_reviews:,}")
col2.metric("Positif", f"{positive:,}", f"{positive / total_reviews:.1%}")
col3.metric("Netral", f"{neutral:,}", f"{neutral / total_reviews:.1%}")
col4.metric("Negatif", f"{negative:,}", f"{negative / total_reviews:.1%}")

st.divider()

left, right = st.columns([1.25, 1])
with left:
    st.subheader("Distribusi Sentimen")
    st.plotly_chart(sentiment_distribution_chart(df), use_container_width=True)

with right:
    st.subheader("Proporsi Sentimen")
    st.plotly_chart(sentiment_donut_chart(df), use_container_width=True)

st.subheader("Kategori Produk Terbanyak")
st.plotly_chart(category_chart(df), use_container_width=True)

st.subheader("Ringkasan Project")
col_a, col_b = st.columns([1.2, 1])
with col_a:
    st.markdown(
        """
        Dashboard membantu membaca pola sentimen dari ribuan review produk dengan tampilan
        yang lebih mudah dipahami untuk presentasi capstone. Model utama memakai teks yang
        tersimpan di Supabase dataset `zenlytics_reviews`, lalu TF-IDF dan SVM linear dari
        notebook 02 bagian Data Murni.
        """
    )
with col_b:
    st.dataframe(
        summary.assign(percentage=lambda x: x["percentage"].round(2)),
        hide_index=True,
        use_container_width=True,
    )

with st.expander("Detail dataset dan pipeline"):
    st.write(
        {
            "project": metadata.get("project", "VibeSight"),
            "version": metadata.get("versi", "v1.0"),
            "train_size": metadata.get("train_size"),
            "test_size": metadata.get("test_size"),
            "stemmer": metadata.get("stemmer", "PySastrawi"),
            "dataset": "Supabase: zenlytics_reviews",
            "feature_column": "review_text_stemmed",
            "target_column": "sentiment_label",
            "model_artifact": "modeling/model_save/model_svm.pkl",
            "vectorizer_artifact": "modeling/tfidf_vectorizer.pkl",
        }
    )
