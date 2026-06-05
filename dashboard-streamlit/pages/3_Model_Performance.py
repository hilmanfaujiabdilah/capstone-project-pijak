# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from utils.charts import confusion_matrix_chart
from utils.ui import page_hero, setup_page
from utils.data import load_train_test, LABEL_TO_ID
from utils.modeling import load_model_assets
from utils.preprocessing import preprocess_text


setup_page("Model Performance", "M")
page_hero(
    "Evaluasi Model SVM",
    "Performa model pada data testing"
)

try:
    # Load model & vectorizer
    model, vectorizer = load_model_assets()
    
    # Load train & test data
    train_df, test_df = load_train_test()
    
    # Preprocess test texts
    test_texts = test_df["review_text_stemmed"].apply(preprocess_text).tolist()
    
    # Vectorize test texts
    test_vectors = vectorizer.transform(test_texts)
    
    # Get predictions
    y_pred = model.predict(test_vectors)
    y_true = test_df["sentiment_label"].values
    
    # Calculate metrics
    test_accuracy = accuracy_score(y_true, y_pred)
    train_accuracy = model.score(
        vectorizer.transform(train_df["review_text_stemmed"].apply(preprocess_text).tolist()),
        train_df["sentiment_label"].values
    )
    
    # Classification report
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    report_df = pd.DataFrame(report).transpose().reset_index()
    report_df.rename(columns={"index": "metric"}, inplace=True)
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=["negative", "neutral", "positive"])
    matrix_df = pd.DataFrame(cm, index=["negative", "neutral", "positive"], columns=["negative", "neutral", "positive"])
    
    # Get macro F1
    macro_f1 = report["macro avg"]["f1-score"]
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Accuracy Testing", f"{test_accuracy:.2%}")
    col1.caption(f"Training: {train_accuracy:.2%}")
    
    macro_row = report_df[report_df["metric"] == "macro avg"].iloc[0]
    col2.metric("Precision Macro", f"{macro_row['precision']:.2%}")
    col3.metric("Recall Macro", f"{macro_row['recall']:.2%}")
    col4.metric("F1 Macro", f"{macro_row['f1-score']:.2%}")

    st.caption(
        f"Split modeling: {len(train_df):,} data training dan {len(test_df):,} data testing."
    )

    left, right = st.columns([1.05, 0.95])
    with left:
        st.subheader("Classification Report")
        display = report_df.copy()
        numeric_cols = ["precision", "recall", "f1-score", "support"]
        display[numeric_cols] = display[numeric_cols].round(4)
        st.dataframe(display, hide_index=True, use_container_width=True)

    with right:
        st.subheader("Confusion Matrix")
        st.plotly_chart(confusion_matrix_chart(matrix_df), use_container_width=True)

    st.subheader("Ringkasan Model")
    
    with st.expander("Konfigurasi model terbaik"):
        st.write({
            "model": "SVM",
            "vectorizer": "TfidfVectorizer",
            "macro_f1": round(float(macro_f1), 4),
        })

except Exception as e:
    st.error(f"Terjadi kesalahan saat memproses evaluasi model: {str(e)}")
    st.info("Pastikan model dan vectorizer tersedia di folder model.")
