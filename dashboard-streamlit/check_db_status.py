"""
Script untuk cek status database dan data yang ada di Supabase
"""

import os
import sys
from pathlib import Path

# Tambahkan dashboard directory ke path
DASHBOARD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DASHBOARD_DIR))

from utils.supabase_config import load_supabase_config, get_supabase_connection


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_config():
    """Cek konfigurasi Supabase."""
    print_header("Supabase Configuration")
    
    config = load_supabase_config()
    print(f"Host:      {config.host}")
    print(f"Port:      {config.port}")
    print(f"Database:  {config.database}")
    print(f"User:      {config.user}")
    print(f"Password:  {'*' * len(config.password) if config.password else '❌ KOSONG (tidak di-set)'}")
    
    if not config.password:
        print("\n⚠️  PASSWORD KOSONG! Set environment variable SUPABASE_PASSWORD:")
        print("   $env:SUPABASE_PASSWORD = 'Z6nLytics123$'")
        return False
    
    print("✅ Password sudah di-set")
    return True


def test_connection():
    """Test koneksi ke database."""
    print_header("Testing Connection")
    
    try:
        conn = get_supabase_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")
        timestamp = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"✅ Connection successful!")
        print(f"   Server time: {timestamp}")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


def check_tables_exist():
    """Cek apakah tabel sudah ada di database."""
    print_header("Checking Tables")
    
    try:
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        # Cek tabel
        tables = ['predictions', 'batch_predictions', 'batch_prediction_details']
        for table in tables:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            """)
            exists = cursor.fetchone()[0]
            status = "✅ Ada" if exists else "❌ Tidak ada"
            print(f"  {table}: {status}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking tables: {str(e)}")
        return False


def check_data_count():
    """Cek jumlah data di setiap tabel."""
    print_header("Data Count in Tables")
    
    try:
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        tables = ['predictions', 'batch_predictions', 'batch_prediction_details']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} rows")
            except:
                print(f"  {table}: ❌ Error reading (mungkin tabel tidak ada)")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def show_recent_predictions():
    """Tampilkan 5 prediksi terakhir."""
    print_header("Recent Predictions (Latest 5)")
    
    try:
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, review_text, sentiment_label, confidence, created_at
            FROM predictions
            ORDER BY created_at DESC
            LIMIT 5;
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("  ❌ Tidak ada data predictions")
        else:
            for row in rows:
                print(f"\n  ID: {row[0]}")
                print(f"  Review: {row[1][:100]}...")
                print(f"  Sentiment: {row[2]} ({row[3]:.2%})")
                print(f"  Created: {row[4]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║         SUPABASE DATABASE STATUS CHECK                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # 1. Cek config
    if not check_config():
        sys.exit(1)
    
    # 2. Test connection
    if not test_connection():
        print("\n❌ Tidak bisa connect ke database. Setup gagal.")
        sys.exit(1)
    
    # 3. Cek tabel
    check_tables_exist()
    
    # 4. Cek jumlah data
    check_data_count()
    
    # 5. Tampilkan recent predictions
    show_recent_predictions()
    
    print("\n" + "=" * 60)
    print("✅ Status check complete!")
    print("=" * 60 + "\n")
