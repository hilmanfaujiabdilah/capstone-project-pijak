# VibeSight 🔍
**AI-Powered Business Intelligence untuk Analisis Penjualan 
dan Customer Sentiment pada E-Commerce**

Capstone Project — Pijak in collaboration with IBM SkillsBuild

----------------------------------------------------------------

👥 Tim
| Peran | GitHub |
|---|---|
| Ketua Tim | hilmanfaujiabdilah |
| Data Engineer | kusumaeditz |


----------------------------------------------------------------

📦 Dataset & Akses Data

Download Dataset Olist (Raw)
[Brazilian E-Commerce Public Dataset — Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

Data yang Sudah Diproses (Internal Tim)
📁 Google Drive: https://drive.google.com/drive/folders/1Kyfi_hOg0sUEng3zwnq7KSwBwW_59tPO?usp=sharing

Struktur folder:
- raw/       → 9 CSV Olist original
- processed/ → Data setelah cleaning  
- final/     → master_dataset, rfm_table, sentiment_dataset

----------------------------------------------------------------

📊 Output Data Engineering
| File | Rows | Untuk |
|---|---|---|
| master_dataset.csv | 96,470 | Dashboard BI |
| rfm_table.csv | 93,350 | AI Customer Segmentation |
| sentiment_dataset.csv | 40,783 | AI Sentiment Analysis |

---------------------------------------------------------------

🗂️ Struktur Project
capstone-project-pijak/
├── data/
│   ├── 01_data_loading.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_feature_engineering.ipynb
│   └── README.md
├── modeling/
├── website/
└── README.md

----------------------------------------------------------------

⚙️ Setup Lokal

1. Clone repo
git clone https://github.com/hilmanfaujiabdilah/capstone-project-pijak.git

2. Install dependencies
pip install pandas numpy matplotlib seaborn scikit-learn jupyter ipykernel

3. Download data dari Google Drive
Link: https://drive.google.com/drive/folders/1Kyfi_hOg0sUEng3zwnq7KSwBwW_59tPO?usp=sharing

Letakkan file sesuai struktur:
- data/raw/
- data/processed/
- data/final/

4. Jalankan notebook berurutan
1. 01_data_loading.ipynb
2. 02_data_cleaning.ipynb
3. 03_feature_engineering.ipynb