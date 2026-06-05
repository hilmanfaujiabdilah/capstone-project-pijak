# Supabase Integration Guide

Panduan lengkap untuk mengintegrasikan Supabase database dengan Sentiment Dashboard Streamlit.

## 📋 Daftar Isi

- [Quick Start](#quick-start)
- [Setup Database](#setup-database)
- [Konfigurasi Kredensial](#konfigurasi-kredensial)
- [Penggunaan](#penggunaan)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Install Dependencies

```bash
cd dashboard-streamlit
pip install -r requirements.txt
```

Pastikan `psycopg2-binary` sudah terinstall di `requirements.txt`.

### 2. Konfigurasi Supabase Credentials

**Option A: Menggunakan Streamlit Secrets (Recommended)**

1. Buat file `.streamlit/secrets.toml` di folder dashboard-streamlit:

```toml
[supabase]
host = "aws-1-ap-southeast-1.pooler.supabase.com"
port = "6543"
database = "postgres"
user = "postgres.rjyqzsroukgttltrpgtc"
password = "your_password_here"
```

2. Ganti `your_password_here` dengan password asli dari file `Databse Credential Zenlytics.txt`

**Option B: Menggunakan Environment Variables**

```bash
# Windows (PowerShell)
$env:SUPABASE_HOST = "aws-1-ap-southeast-1.pooler.supabase.com"
$env:SUPABASE_PORT = "6543"
$env:SUPABASE_DATABASE = "postgres"
$env:SUPABASE_USER = "postgres.rjyqzsroukgttltrpgtc"
$env:SUPABASE_PASSWORD = "your_password_here"

# Linux/Mac (Bash)
export SUPABASE_HOST="aws-1-ap-southeast-1.pooler.supabase.com"
export SUPABASE_PORT="6543"
export SUPABASE_DATABASE="postgres"
export SUPABASE_USER="postgres.rjyqzsroukgttltrpgtc"
export SUPABASE_PASSWORD="your_password_here"
```

### 3. Setup Database Tables

Run setup script untuk membuat tabel dan mengetes koneksi:

```bash
python setup_supabase.py
```

Script ini akan:
- ✅ Tampilkan konfigurasi Supabase
- ✅ Test koneksi ke database
- ✅ Buat tabel yang diperlukan
- ✅ Verifikasi tabel yang dibuat
- ✅ Insert sample data (optional)

### 4. Run Dashboard

```bash
streamlit run app.py
```

---

## Setup Database

### Database Schema

Aplikasi membuat 3 tabel otomatis:

#### Table: `predictions`
Menyimpan single predictions dari halaman "Prediksi Sentimen Realtime"

```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    review_text TEXT NOT NULL,
    processed_text TEXT NOT NULL,
    sentiment_label VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `batch_predictions`
Metadata untuk batch prediction uploads

```sql
CREATE TABLE batch_predictions (
    id SERIAL PRIMARY KEY,
    batch_name VARCHAR(255),
    total_records INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `batch_prediction_details`
Detail records dari setiap batch prediction

```sql
CREATE TABLE batch_prediction_details (
    id SERIAL PRIMARY KEY,
    batch_id INT REFERENCES batch_predictions(id) ON DELETE CASCADE,
    review_text TEXT NOT NULL,
    processed_text TEXT NOT NULL,
    sentiment_label VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

Aplikasi juga membuat beberapa index untuk performa optimal:

```sql
CREATE INDEX idx_predictions_created_at ON predictions(created_at DESC);
CREATE INDEX idx_predictions_sentiment ON predictions(sentiment_label);
CREATE INDEX idx_batch_predictions_created_at ON batch_predictions(created_at DESC);
```

---

## Konfigurasi Kredensial

### Dari File Credential

File `database-connection/Databse Credential Zenlytics.txt` berisi:

```
Host      : aws-1-ap-southeast-1.pooler.supabase.com
Port      : 6543
Database  : postgres
User      : postgres.rjyqzsroukgttltrpgtc
Password  : [check the file]
```

### Priority Loading

Aplikasi mencari kredensial dengan urutan priority:

1. **Environment Variables** (tertinggi)
   - `SUPABASE_HOST`
   - `SUPABASE_PORT`
   - `SUPABASE_DATABASE`
   - `SUPABASE_USER`
   - `SUPABASE_PASSWORD`

2. **Streamlit Secrets** (`.streamlit/secrets.toml`)
   - `[supabase]` section

3. **Default Values** (terendah)
   - Host: `aws-1-ap-southeast-1.pooler.supabase.com`
   - Port: `6543`
   - Database: `postgres`
   - User: `postgres.rjyqzsroukgttltrpgtc`
   - Password: (empty)

---

## Penggunaan

### 1. Single Prediction dengan Save ke Database

**Halaman:** "Prediksi Sentimen Realtime" (1_Predict_Sentiment.py)

1. Masukkan teks review di text area
2. Klik button "Prediksi"
3. Tunggu model memproses
4. Lihat hasil prediksi
5. **Klik "💾 Simpan ke Database"** untuk menyimpan ke Supabase

### 2. Batch Prediction dengan Save ke Database

**Halaman:** "Batch Prediction" (4_Batch_Prediction.py)

1. Upload file CSV dengan kolom teks
2. Pilih kolom yang ingin diprediksi
3. Klik "Jalankan Batch Prediction"
4. Tunggu selesai
5. **Klik "💾 Simpan ke Database"** untuk menyimpan semua hasil ke Supabase

### 3. View Data dari Database

Gunakan module `SupabaseDB` untuk query data:

```python
from utils.supabase_db import SupabaseDB

# Get recent predictions
df = SupabaseDB.get_predictions(limit=100)

# Get sentiment summary
summary = SupabaseDB.get_sentiment_summary(days=30)

# Get recent predictions dengan stats
result = SupabaseDB.get_recent_predictions_with_stats(limit=50)
```

### 4. Buat Chart dari Database

Contoh membuat chart dari Supabase data:

```python
import streamlit as st
from utils.supabase_db import SupabaseDB
from utils.charts import sentiment_distribution_chart

# Get data dari database
df = SupabaseDB.get_predictions(limit=1000)

if df is not None:
    st.plotly_chart(sentiment_distribution_chart(df), use_container_width=True)
else:
    st.warning("Belum ada data predictions di database")
```

---

## Troubleshooting

### Connection Failed

**Error:** `connection refused` atau `could not connect to server`

**Solusi:**

1. Pastikan password sudah benar
2. Cek koneksi internet
3. Test manual dengan psql:
   ```bash
   psql -h aws-1-ap-southeast-1.pooler.supabase.com -p 6543 -U postgres.rjyqzsroukgttltrpgtc -d postgres
   ```

### Password Contains Special Characters

**Error:** Login failed atau authentication error

**Solusi:**

URL encode password special characters. Contoh:
- `@` → `%40`
- `#` → `%23`
- `$` → `%24`
- `:` → `%3A`

Atau gunakan single quotes dalam environment variable:
```bash
export SUPABASE_PASSWORD='your$password@with#special:chars'
```

### psycopg2 Import Error

**Error:** `ModuleNotFoundError: No module named 'psycopg2'`

**Solusi:**

```bash
pip install psycopg2-binary
```

### No Tables Found

**Error:** Tabel tidak ada saat insert prediction

**Solusi:**

Run setup script:
```bash
python setup_supabase.py
```

### Query Timeout

**Error:** Database query timeout atau slow

**Solusi:**

1. Check index sudah dibuat
2. Limit data yang di-fetch
3. Add caching dengan `@st.cache_data`

### Connection Pooler vs Direct Connection

Anda menggunakan pooler (port 6543). Jika masalah connection, coba:

```python
# Di supabase_config.py, ubah port
host=os.getenv("SUPABASE_HOST") or "aws-1-ap-southeast-1.postgres.supabase.com"  # Direct
port=int(os.getenv("SUPABASE_PORT") or "5432")  # Direct port
```

---

## API Reference

### SupabaseDB Class

#### `initialize_tables()`
```python
SupabaseDB.initialize_tables()  # Returns bool
```
Buat tabel yang diperlukan jika belum ada.

#### `save_prediction(review_text, processed_text, sentiment_label, confidence)`
```python
success = SupabaseDB.save_prediction(
    review_text="Produk bagus!",
    processed_text="produk bagus",
    sentiment_label="positive",
    confidence=0.95
)
```

#### `save_batch_predictions(predictions_data, batch_name)`
```python
batch_id = SupabaseDB.save_batch_predictions(
    predictions_data=[
        {"review_text": "...", "processed_text": "...", "sentiment_label": "positive", "confidence": 0.95},
        # ... more predictions
    ],
    batch_name="my_batch_upload"
)
```

#### `get_predictions(limit)`
```python
df = SupabaseDB.get_predictions(limit=100)
```

#### `get_sentiment_summary(days)`
```python
summary = SupabaseDB.get_sentiment_summary(days=30)
```

#### `get_recent_predictions_with_stats(limit)`
```python
result = SupabaseDB.get_recent_predictions_with_stats(limit=50)
df = result["data"]
stats = result["stats"]
```

#### `clear_old_predictions(days)`
```python
SupabaseDB.clear_old_predictions(days=90)
```

#### `test_connection()`
```python
is_connected = SupabaseDB.test_connection()  # Returns bool
```

---

## Next Steps

1. ✅ Sudah install dependencies
2. ✅ Configure credentials
3. ✅ Run setup script
4. ✅ Test dengan single prediction & batch prediction
5. 🔄 Update Analytics page untuk pull dari database
6. 🔄 Create dashboard charts dari live database data

---

## Kontribusi & Support

Jika ada pertanyaan atau masalah:
1. Check troubleshooting section
2. Review credentials file
3. Run setup script untuk diagnostik
4. Check database logs di Supabase console

---

**Last Updated:** 2026-06-04
