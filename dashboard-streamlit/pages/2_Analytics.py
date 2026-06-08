import matplotlib.pyplot as plt
import streamlit as st

from utils.charts import (
    build_wordcloud,
    frequency_chart,
    sentiment_distribution_chart,
    text_length_histogram,
    word_frequencies,
)
from utils.data import load_dataset
from utils.ui import page_hero, setup_page


setup_page("Analytics")
page_hero(
    "Analytics Review",
    "Eksplorasi kata, panjang review, dan distribusi sentimen dari Supabase `zenlytics_reviews`.",
)

df = load_dataset(("sentiment_label", "review_text_stemmed", "review_word_count"))

tab_overview, tab_words, tab_wordcloud = st.tabs(["Overview", "Frekuensi Kata", "Wordcloud"])

with tab_overview:
    left, right = st.columns(2)
    with left:
        st.subheader("Distribusi Sentimen")
        st.plotly_chart(sentiment_distribution_chart(df), use_container_width=True)
    with right:
        st.subheader("Distribusi Panjang Teks")
        st.plotly_chart(text_length_histogram(df), use_container_width=True)

with tab_words:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            frequency_chart(word_frequencies(df, None, 25), "Most Common Words"),
            use_container_width=True,
        )
        st.plotly_chart(
            frequency_chart(word_frequencies(df, "positive", 20), "Top Positive Words"),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            frequency_chart(word_frequencies(df, "negative", 20), "Top Negative Words"),
            use_container_width=True,
        )
        st.plotly_chart(
            frequency_chart(word_frequencies(df, "neutral", 20), "Top Neutral Words"),
            use_container_width=True,
        )

with tab_wordcloud:
    selected = st.selectbox("Filter sentimen", ["Semua", "positive", "neutral", "negative"])
    label = None if selected == "Semua" else selected
    try:
        cloud = build_wordcloud(df, label)
        fig, ax = plt.subplots(figsize=(14, 6), facecolor="#0F172A")
        ax.imshow(cloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)
    except RuntimeError as exc:
        st.warning(str(exc))
        st.plotly_chart(
            frequency_chart(word_frequencies(df, label, 30), "Frekuensi Kata sebagai fallback"),
            use_container_width=True,
        )
