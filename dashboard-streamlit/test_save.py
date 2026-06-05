"""
Script untuk test save_prediction function langsung
"""

import os
import sys
from pathlib import Path

# Tambahkan dashboard directory ke path
DASHBOARD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DASHBOARD_DIR))

# Set password SEBELUM import, agar tidak menggunakan cache yang lama
os.environ["SUPABASE_PASSWORD"] = "Z6nLytics123$"

from utils.supabase_config import get_supabase_connection


def test_save_directly():
    """Test save langsung ke database (tidak pakai cache)."""
    
    print("\n" + "=" * 60)
    print("  Testing Direct Save to Database")
    print("=" * 60)
    
    try:
        # Gunakan get_supabase_connection() tanpa cache
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        # Data untuk di-insert
        review_text = "Test dari script - ini harus masuk ke database!"
        processed_text = "test dari script ini harus masuk database"
        sentiment_label = "positive"
        confidence = 0.95
        
        print(f"\nMenyimpan data:")
        print(f"  Review: {review_text}")
        print(f"  Sentiment: {sentiment_label} ({confidence:.0%})")
        
        # Insert ke database
        cursor.execute(
            """
            INSERT INTO predictions 
            (review_text, processed_text, sentiment_label, confidence)
            VALUES (%s, %s, %s, %s)
            """,
            (review_text, processed_text, sentiment_label, confidence),
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ DATA BERHASIL DISIMPAN!")
        
        # Verifikasi dengan query
        conn = get_supabase_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM predictions;")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"✅ Total rows di table predictions: {count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_save_directly()
    sys.exit(0 if success else 1)
