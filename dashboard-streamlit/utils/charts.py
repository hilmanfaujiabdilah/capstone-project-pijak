from collections import Counter
import json
from pathlib import Path

import numpy as np
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
# pyrefly: ignore [missing-import]
import streamlit as st

try:
    # pyrefly: ignore [missing-import]
    from wordcloud import WordCloud
except ImportError:
    WordCloud = None

from utils.ui import LABEL_COLORS

# Path ke pre-computed metrics JSON (di dalam folder dashboard-streamlit/model/)
_METRICS_JSON = Path(__file__).resolve().parents[1] / "model" / "model_metrics.json"


PLOTLY_TEMPLATE = "plotly_dark"


def sentiment_distribution_chart(df: pd.DataFrame) -> go.Figure:
    counts = df["sentiment_label"].value_counts().reset_index()
    counts.columns = ["sentiment", "count"]
    fig = px.bar(
        counts,
        x="sentiment",
        y="count",
        color="sentiment",
        color_discrete_map=LABEL_COLORS,
        template=PLOTLY_TEMPLATE,
        text_auto=True,
    )
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Jumlah Review")
    return fig


def sentiment_donut_chart(df: pd.DataFrame) -> go.Figure:
    counts = df["sentiment_label"].value_counts().reset_index()
    counts.columns = ["sentiment", "count"]
    fig = px.pie(
        counts,
        names="sentiment",
        values="count",
        hole=0.58,
        color="sentiment",
        color_discrete_map=LABEL_COLORS,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(showlegend=False)
    return fig


def text_length_histogram(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df,
        x="review_word_count",
        nbins=45,
        color="sentiment_label",
        color_discrete_map=LABEL_COLORS,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(xaxis_title="Jumlah Kata", yaxis_title="Jumlah Review")
    return fig


def category_chart(df: pd.DataFrame) -> go.Figure:
    top = df["product_category"].value_counts().head(10).reset_index()
    top.columns = ["category", "count"]
    fig = px.bar(
        top.sort_values("count"),
        x="count",
        y="category",
        orientation="h",
        template=PLOTLY_TEMPLATE,
        color="count",
        color_continuous_scale=["#1E293B", "#00ADB5"],
    )
    fig.update_layout(xaxis_title="Jumlah Review", yaxis_title="", coloraxis_showscale=False)
    return fig


@st.cache_data(show_spinner=False)
def word_frequencies(df: pd.DataFrame, label: str | None = None, top_n: int = 25) -> pd.DataFrame:
    source = df if label is None else df[df["sentiment_label"] == label]
    words = " ".join(source["review_text_stemmed"].dropna().astype(str)).split()
    counts = Counter(words).most_common(top_n)
    return pd.DataFrame(counts, columns=["word", "count"])


def frequency_chart(freq_df: pd.DataFrame, title: str) -> go.Figure:
    fig = px.bar(
        freq_df.sort_values("count"),
        x="count",
        y="word",
        orientation="h",
        template=PLOTLY_TEMPLATE,
        color="count",
        color_continuous_scale=["#1E293B", "#00ADB5"],
        title=title,
    )
    fig.update_layout(xaxis_title="Frekuensi", yaxis_title="", coloraxis_showscale=False)
    return fig


@st.cache_data(show_spinner=False)
def build_wordcloud(df: pd.DataFrame, label: str | None = None):
    if WordCloud is None:
        raise RuntimeError("Library wordcloud belum terpasang. Jalankan `pip install wordcloud`.")

    source = df if label is None else df[df["sentiment_label"] == label]
    text = " ".join(source["review_text_stemmed"].dropna().astype(str))
    if not text.strip():
        text = "sentimen review produk"
    return WordCloud(
        width=1200,
        height=520,
        background_color="#0F172A",
        colormap="viridis",
        max_words=120,
        collocations=False,
    ).generate(text).to_array()


@st.cache_data(show_spinner=False)
def model_performance(_df_clean: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Hitung metrik evaluasi secara otomatis dari data dan model.

    Menggunakan label normalization agar kompatibel dengan model yang
    di-train dengan label integer (0,1,2) maupun string (negative/neutral/positive).
    """
    # Mapping dari label integer ke string (untuk kompatibilitas)
    ID_TO_LABEL = {"0": "negative", "1": "neutral", "2": "positive"}
    ORDERED_LABELS = ["negative", "neutral", "positive"]

    model, vectorizer = load_model_assets()
    x = _df_clean["review_text_stemmed"].fillna("").astype(str).values
    y_raw = _df_clean["sentiment_label"].astype(str).str.strip().values
    # Normalisasi label ground truth: "0"->"negative", dll jika perlu
    y = np.array([ID_TO_LABEL.get(v, v) for v in y_raw])

    x_train, x_test, y_train, y_true = train_test_split(
        x, y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    x_train_vec = vectorizer.transform(x_train)
    x_test_vec = vectorizer.transform(x_test)

    y_train_pred_raw = model.predict(x_train_vec)
    y_pred_raw = model.predict(x_test_vec)

    # Normalisasi prediksi: handle integer (0,1,2) atau string label
    y_train_pred = np.array([ID_TO_LABEL.get(str(v).strip(), str(v).strip()) for v in y_train_pred_raw])
    y_pred = np.array([ID_TO_LABEL.get(str(v).strip(), str(v).strip()) for v in y_pred_raw])

    report = classification_report(y_true, y_pred, labels=ORDERED_LABELS, output_dict=True, zero_division=0)
    report_df = pd.DataFrame([
        {"metric": label, **metrics}
        for label, metrics in report.items()
        if isinstance(metrics, dict)
    ])

    matrix = confusion_matrix(y_true, y_pred, labels=ORDERED_LABELS)
    matrix_df = pd.DataFrame(matrix, index=ORDERED_LABELS, columns=ORDERED_LABELS)

    test_accuracy = float(report.get("accuracy", report["weighted avg"]["f1-score"]))
    metadata = {
        "train_size": int(len(x_train)),
        "test_size": int(len(x_test)),
        "test_accuracy": test_accuracy,
        "train_accuracy": float((y_train_pred == y_train).mean()),
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "svm_config": {
            "vectorizer": "TfidfVectorizer",
            "max_features": "default",
            "kernel": "linear",
        },
    }
    return report_df, matrix_df, metadata


def confusion_matrix_chart(matrix_df: pd.DataFrame) -> go.Figure:
    fig = px.imshow(
        matrix_df,
        text_auto=True,
        color_continuous_scale=["#1E293B", "#00ADB5"],
        template=PLOTLY_TEMPLATE,
        aspect="auto",
    )
    fig.update_layout(xaxis_title="Prediksi", yaxis_title="Aktual", coloraxis_showscale=False)
    return fig
