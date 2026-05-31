# ZenLytics

AI-Based Sentiment Analytics for Tokopedia Product Reviews

Capstone Project – Pijak × IBM SkillsBuild  
Tema: AI for Business Intelligence and Market Insights

---

## 📌 Deskripsi Project

ZenLytics adalah aplikasi analisis sentimen ulasan produk Tokopedia berbasis Artificial Intelligence dan Machine Learning yang dibangun menggunakan Streamlit.

Aplikasi ini membantu pengguna memahami persepsi pelanggan terhadap suatu produk melalui analisis sentimen otomatis, visualisasi data, evaluasi model, dan prediksi sentimen secara realtime maupun batch.

ZenLytics mengimplementasikan pipeline Natural Language Processing (NLP) Bahasa Indonesia mulai dari preprocessing teks hingga klasifikasi sentimen menggunakan algoritma Support Vector Machine (SVM).

---

## 👥 Tim Pengembang

| ID Peserta | Nama | Peran |
|------------|------|--------|
| APC237D6Y0070 | Hilman Fauzi Abdilah | AI Engineer / Project Manager |
| APC246D6Y0164 | Ade Wahyu Warpudin | AI Engineer / ML Engineer |
| APC246D6Y0236 | Ade Suryadi | AI Engineer / ML Engineer |
| APC446D6Y0245 | Pajar | AI Engineer / UI/UX Designer |
| APC617D6X0220 | Nurhayati Kusumaning Ayu | AI Engineer / Data Engineer |

---

# 🎯 Tujuan Project

Project ini bertujuan untuk:

- Mengotomatisasi analisis sentimen ulasan produk Tokopedia.
- Membantu pelaku bisnis memahami opini pelanggan.
- Menyediakan dashboard analitik yang mudah digunakan.
- Menampilkan insight sentimen secara visual.
- Menyediakan sistem prediksi sentimen realtime berbasis AI.

---

# 🧠 Machine Learning Pipeline

ZenLytics menggunakan pipeline NLP Bahasa Indonesia sebagai berikut:

```text
Review Produk
      ↓
Text Cleaning
      ↓
Case Folding
      ↓
Slang Word Normalization
      ↓
Tokenization
      ↓
Stopword Removal
      ↓
Stemming (Sastrawi)
      ↓
TF-IDF Vectorization
      ↓
Support Vector Machine (SVM)
      ↓
Sentiment Prediction
```

---

# 📊 Dataset

Dataset yang digunakan berasal dari:

Tokopedia Product Reviews 2025 Dataset

Sumber:

https://www.kaggle.com/datasets/salmanabdu/tokopedia-product-reviews-2025

Dataset digunakan untuk membangun model analisis sentimen dengan label:

| Label | Sentimen |
|---------|----------|
| positive | Positif |
| neutral | Netral |
| negative | Negatif |

Kolom utama yang digunakan dalam proses modeling:

| Kolom | Fungsi |
|---------|---------|
| text_akhir | Feature text |
| polarity | Target label |

---

# ⚙️ Teknologi yang Digunakan

## Front-End Dashboard

- Streamlit

## Data Processing

- Pandas
- NumPy

## Machine Learning

- Scikit-Learn
- TF-IDF Vectorizer
- Support Vector Machine (SVM)

## NLP Bahasa Indonesia

- Sastrawi
- MPStemmer
- NLTK

## Visualisasi

- Plotly
- Matplotlib
- WordCloud

## Database

- MySQL Connector

---

# 📁 Struktur Project

```text
capstone-project-pijak-main/
│
├── README.md
│
├── dashboard-streamlit/
│   ├── app.py
│   ├── requirements.txt
│   ├── model/
│   │   ├── model_svm_best.pkl
│   │   └── tfidf_vectorizer.pkl
│   ├── pages/
│   ├── utils/
│   └── .streamlit/
│
├── dataset/
│   └── tokopedia_reviews.csv
│
├── model-result/
│   ├── tfidf_vectorizer.pkl
│   ├── lstm_tokenizer.pkl
│   ├── model_result_info.md
│   └── model_save/
│       ├── model_svm.pkl
│       ├── model_svm_tuning.pkl
│       └── model_lstm.h5
│
├── notebooks/
│   └── preprocessing-and-training-model.ipynb
│
├── reports/
│   ├── laporan_data_engineering_v1.0.md
│   ├── laporan_eda_v1.0_20260516_1145.md
│   └── seluruh file visualisasi EDA
│
└── database-connection/
    └── Databse Credential Zenlytics.txt
```

---

# 🚀 Instalasi

## 1. Clone Repository

```bash
git clone https://github.com/username/ZenLytics.git

cd ZenLytics
```

## 2. Membuat Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / MacOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Jalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan berjalan pada:

```text
http://localhost:8501
```

---

# 🔐 Login Dashboard

Secara default dashboard menggunakan autentikasi sederhana.

Credential bawaan:

```text
Username : admin
Password : admin123
```

Untuk deployment disarankan menggunakan environment variable:

```env
APP_USERNAME=your_username
APP_PASSWORD=your_password
```

---

# 📈 Fitur Dashboard

## 1. Dashboard

File:

```text
app.py
```

Menampilkan:

- Total dataset review
- Jumlah sentimen positif
- Jumlah sentimen netral
- Jumlah sentimen negatif
- Distribusi sentimen
- Proporsi sentimen
- Kategori produk terbanyak
- Ringkasan dataset

---

## 2. Predict Sentiment

File:

```text
1_Predict_Sentiment.py
```

Fitur:

- Prediksi sentimen realtime
- Menampilkan confidence score
- Menampilkan hasil preprocessing
- Mendukung input review Bahasa Indonesia

Output:

```text
Positive
Neutral
Negative
```

---

## 3. Analytics

File:

```text
2_Analytics.py
```

Fitur:

### Overview

- Distribusi sentimen
- Histogram panjang review

### Frekuensi Kata

- Most Common Words
- Top Positive Words
- Top Neutral Words
- Top Negative Words

### WordCloud

- WordCloud keseluruhan
- WordCloud per sentimen

---

## 4. Model Performance

File:

```text
3_Model_Performance.py
```

Menampilkan:

- Accuracy
- Precision
- Recall
- Macro F1-Score
- Classification Report
- Confusion Matrix
- Perbandingan beberapa model

Metrik evaluasi digunakan untuk mengukur performa model pada data testing.

---

## 5. Batch Prediction

File:

```text
4_Batch_Prediction.py
```

Fitur:

- Upload CSV
- Prediksi banyak data sekaligus
- Download hasil prediksi

Kolom hasil:

```text
sentiment_predicted
processed_text
confidence
```

Contoh format CSV:

```csv
review_text
"Barang bagus dan cepat sampai"
"Produk tidak sesuai deskripsi"
"Kualitas standar"
```

---

## 6. About Project

File:

```text
5_About_Project.py
```

Menampilkan:

- Informasi project
- Pipeline machine learning
- Metadata dataset
- Informasi model

---

# 📉 Evaluasi Model

Model utama yang digunakan:

```text
TF-IDF + Support Vector Machine (SVM)
```

Evaluasi model dilakukan menggunakan:

- Accuracy
- Precision
- Recall
- Macro F1-Score
- Confusion Matrix

Macro F1-Score digunakan sebagai metrik utama karena dataset memiliki distribusi kelas yang tidak seimbang sehingga lebih representatif dibanding Accuracy.

---

# 💡 Insight Bisnis

ZenLytics dapat digunakan untuk:

- Monitoring kepuasan pelanggan
- Evaluasi kualitas produk
- Identifikasi keluhan pelanggan
- Analisis persepsi konsumen
- Pengambilan keputusan berbasis data

---

# 📜 Lisensi

Project ini dibuat untuk kebutuhan Capstone Project Pijak × IBM SkillsBuild.

Silakan gunakan dan kembangkan sesuai kebutuhan akademik maupun penelitian.

---

# 📬 Kontak

Hilman Fauzi Abdilah

AI Engineer | Information Systems Student

GitHub:
https://github.com/hilmanfaujiabdilah

LinkedIn:
[Hilman Fauzi Abdilah](https://www.linkedin.com/in/hilman-fauji-abdilah/)

Email:
hilmanfaujiabdilah@gmail.com
