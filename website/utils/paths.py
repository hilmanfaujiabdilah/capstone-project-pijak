from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent

MODEL_PATH = PROJECT_ROOT / "modeling" / "model_save" / "model_lstm.h5"
VECTORIZER_PATH = PROJECT_ROOT / "modeling" / "lstm_tokenizer.pkl"
DATA_PATH = PROJECT_ROOT / "data" / "fix_tokopedia_reviews.csv"
TRAIN_PATH = PROJECT_ROOT / "data" / "fix_tokopedia_reviews.csv"
TEST_PATH = PROJECT_ROOT / "data" / "fix_tokopedia_reviews.csv"
METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "metadata_v1.0_20260502_2121.json"
