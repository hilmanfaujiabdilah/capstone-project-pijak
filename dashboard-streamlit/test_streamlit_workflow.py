"""
Script untuk simulate dan debug apa yang Streamlit lakukan saat simpan
"""

import os
import sys
from pathlib import Path

# Tambahkan dashboard directory ke path
DASHBOARD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DASHBOARD_DIR))

# Set password SEBELUM import
os.environ["SUPABASE_PASSWORD"] = "Z6nLytics123$"

# Import persis seperti di Streamlit page
from utils.modeling import predict_sentiment
from utils.supabase_db import SupabaseDB


def test_full_workflow():
    """Test full workflow: predict -> save to database"""
    
    print("\n" + "=" * 60)
    print("  Testing Full Workflow (Predict + Save)")
    print("=" * 60)
    
    # Test text
    text = "barang buruk dan saya ingin refund"
    
    print(f"\n1️⃣  Input text: '{text}'")
    
    try:
        # Step 1: Predict
        print("\n2️⃣  Running prediction...")
        result = predict_sentiment(text)
        
        print(f"   ✅ Prediction result:")
        print(f"      - Label: {result['label']}")
        print(f"      - Confidence: {result['confidence']:.1%}")
        print(f"      - Processed text: {result['processed_text'][:50]}...")
        
        # Step 2: Save to database
        print("\n3️⃣  Saving to Supabase...")
        success = SupabaseDB.save_prediction(
            review_text=text,
            processed_text=result["processed_text"],
            sentiment_label=result["label"],
            confidence=result["confidence"],
        )
        
        if success:
            print("   ✅ Save returned True")
        else:
            print("   ❌ Save returned False")
            
        # Step 3: Verify
        print("\n4️⃣  Verifying in database...")
        from utils.supabase_config import get_supabase_connection
        
        conn = get_supabase_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE review_text = %s;", (text,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        if count > 0:
            print(f"   ✅ Data ditemukan! ({count} rows)")
        else:
            print("   ❌ Data TIDAK ditemukan di database!")
        
        return count > 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_workflow()
    if success:
        print("\n" + "=" * 60)
        print("✅ Full workflow berhasil!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Ada masalah dengan workflow")
        print("=" * 60)
