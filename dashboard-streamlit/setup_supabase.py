"""
Setup script untuk inisialisasi Supabase database.
Run script ini sekali untuk membuat tabel dan mengetes koneksi.

Usage:
    python setup_supabase.py
"""

import sys
from pathlib import Path

# Tambahkan dashboard directory ke path
DASHBOARD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DASHBOARD_DIR))

from utils.supabase_config import get_supabase_connection, load_supabase_config
from utils.supabase_db import SupabaseDB


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_config():
    """Display Supabase configuration."""
    print_header("Supabase Configuration")
    
    config = load_supabase_config()
    print(f"Host:      {config.host}")
    print(f"Port:      {config.port}")
    print(f"Database:  {config.database}")
    print(f"User:      {config.user}")
    print(f"Password:  {'*' * len(config.password) if config.password else '(empty)'}")


def test_connection():
    """Test koneksi ke Supabase."""
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
        print("\n   Troubleshooting tips:")
        print("   1. Verify your Supabase credentials in environment variables")
        print("   2. Check if password contains special characters (try URL encoding)")
        print("   3. Ensure port 6543 is accessible (might be blocked by firewall)")
        print("   4. Test connection from command line:")
        print("      psql -h aws-1-ap-southeast-1.pooler.supabase.com -p 6543 -U postgres.rjyqzsroukgttltrpgtc -d postgres")
        return False


def initialize_database():
    """Inisialisasi database tables."""
    print_header("Initializing Database Tables")
    
    try:
        conn = get_supabase_connection()
        cursor = conn.cursor()

        # Tabel predictions
        print("Creating 'predictions' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                review_text TEXT NOT NULL,
                processed_text TEXT NOT NULL,
                sentiment_label VARCHAR(50) NOT NULL,
                confidence FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Tabel batch_predictions
        print("Creating 'batch_predictions' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_predictions (
                id SERIAL PRIMARY KEY,
                batch_name VARCHAR(255),
                total_records INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Tabel batch_prediction_details
        print("Creating 'batch_prediction_details' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_prediction_details (
                id SERIAL PRIMARY KEY,
                batch_id INT REFERENCES batch_predictions(id) ON DELETE CASCADE,
                review_text TEXT NOT NULL,
                processed_text TEXT NOT NULL,
                sentiment_label VARCHAR(50) NOT NULL,
                confidence FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Create indexes
        print("Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_created_at 
            ON predictions(created_at DESC);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_sentiment 
            ON predictions(sentiment_label);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_batch_predictions_created_at 
            ON batch_predictions(created_at DESC);
        """)

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Database tables initialized successfully!")
        return True

    except Exception as e:
        print(f"❌ Failed to initialize tables: {str(e)}")
        return False


def verify_tables():
    """Verifikasi tabel yang telah dibuat."""
    print_header("Verifying Tables")
    
    try:
        conn = get_supabase_connection()
        cursor = conn.cursor()

        # Check existing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
            AND table_type='BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        if tables:
            print("✅ Found the following tables:")
            for table in tables:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table[0]};
                """)
                count = cursor.fetchone()[0]
                print(f"   - {table[0]} ({count} records)")
        else:
            print("❌ No tables found!")
            return False

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error verifying tables: {str(e)}")
        return False


def insert_sample_data():
    """Insert sample data untuk testing."""
    print_header("Inserting Sample Data")
    
    try:
        conn = get_supabase_connection()
        cursor = conn.cursor()

        # Insert sample prediction
        cursor.execute("""
            INSERT INTO predictions 
            (review_text, processed_text, sentiment_label, confidence)
            VALUES 
            (%s, %s, %s, %s),
            (%s, %s, %s, %s),
            (%s, %s, %s, %s)
        """, (
            "Barang bagus, pengiriman cepat!",
            "barang bagus pengiriman cepat",
            "positive",
            0.95,
            
            "Produk jelek, tidak sesuai foto.",
            "produk jelek tidak sesuai foto",
            "negative",
            0.88,
            
            "Produk standar, biasa saja.",
            "produk standar biasa",
            "neutral",
            0.72,
        ))

        conn.commit()
        
        # Verify inserted data
        cursor.execute("SELECT COUNT(*) FROM predictions;")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Sample data inserted! (Total: {count} records)")
        return True

    except Exception as e:
        print(f"❌ Failed to insert sample data: {str(e)}")
        return False


def show_sample_data():
    """Display sample data."""
    print_header("Sample Data")
    
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
        
        if rows:
            print(f"{'ID':<5} {'Review':<30} {'Sentiment':<10} {'Confidence':<12} {'Created At':<20}")
            print("-" * 80)
            for row in rows:
                review = row[1][:27] + "..." if len(row[1]) > 30 else row[1]
                print(f"{row[0]:<5} {review:<30} {row[2]:<10} {row[3]:<12.2%} {str(row[4]):<20}")
        else:
            print("No data found.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error reading sample data: {str(e)}")


def generate_env_template():
    """Generate template untuk environment variables."""
    print_header("Environment Variables Template")
    
    template = """
# Supabase Database Configuration
# Copy into your .env file or set as environment variables

SUPABASE_HOST=aws-1-ap-southeast-1.pooler.supabase.com
SUPABASE_PORT=6543
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres.rjyqzsroukgttltrpgtc
SUPABASE_PASSWORD=your_password_here
"""
    
    print(template)
    print("\nFor Streamlit secrets, create .streamlit/secrets.toml:")
    secrets_template = """
[supabase]
host = "aws-1-ap-southeast-1.pooler.supabase.com"
port = "6543"
database = "postgres"
user = "postgres.rjyqzsroukgttltrpgtc"
password = "your_password_here"
"""
    print(secrets_template)


def main():
    """Run setup wizard."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         SUPABASE DATABASE SETUP WIZARD                     ║")
    print("║                  for Sentiment Dashboard                   ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # 1. Show configuration
    print_config()
    
    # 2. Test connection
    if not test_connection():
        print("\n❌ Cannot proceed without a valid connection.")
        print("   Please verify your Supabase credentials and try again.")
        return False
    
    # 3. Initialize database
    if not initialize_database():
        print("\n❌ Failed to initialize database tables.")
        return False
    
    # 4. Verify tables
    if not verify_tables():
        print("\n❌ Failed to verify tables.")
        return False
    
    # 5. Insert sample data
    user_input = input("\nWould you like to insert sample data for testing? (y/n): ").strip().lower()
    if user_input == 'y':
        insert_sample_data()
        show_sample_data()
    
    # 6. Show environment template
    user_input = input("\nShow environment variables template? (y/n): ").strip().lower()
    if user_input == 'y':
        generate_env_template()
    
    print_header("Setup Complete!")
    print("✅ Your Supabase database is ready to use!")
    print("\nNext steps:")
    print("1. Run the Streamlit app: streamlit run app.py")
    print("2. Go to 'Prediksi Sentimen Realtime' page and make predictions")
    print("3. Click 'Simpan ke Database' to save predictions to Supabase")
    print("4. View analytics in 'Analytics' page (pulling from database)")
    print("\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
