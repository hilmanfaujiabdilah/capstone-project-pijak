"""
Test Streamlit connection secara direct tanpa cache
Pastikan environment variable dan secrets sudah bekerja
"""

import streamlit as st
import os
from pathlib import Path
import sys

# Add dashboard dir to path
DASHBOARD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DASHBOARD_DIR))

st.set_page_config(page_title="DB Connection Test", layout="wide")

st.title("🔧 Supabase Connection Test")
st.markdown("---")

# Show configuration
st.subheader("1️⃣ Configuration Status")

col1, col2 = st.columns(2)

with col1:
    st.write("**Environment Variables:**")
    password_env = os.getenv("SUPABASE_PASSWORD", "(not set)")
    host_env = os.getenv("SUPABASE_HOST", "(not set)")
    user_env = os.getenv("SUPABASE_USER", "(not set)")
    
    st.text(f"SUPABASE_PASSWORD: {password_env if password_env == '(not set)' else '*** (set)'}")
    st.text(f"SUPABASE_HOST: {host_env}")
    st.text(f"SUPABASE_USER: {user_env}")

with col2:
    st.write("**Streamlit Secrets:**")
    try:
        password_secret = st.secrets.get("supabase", {}).get("password", "(not set)")
        host_secret = st.secrets.get("supabase", {}).get("host", "(not set)")
        user_secret = st.secrets.get("supabase", {}).get("user", "(not set)")
        
        st.text(f"supabase.password: {password_secret if password_secret == '(not set)' else '*** (set)'}")
        st.text(f"supabase.host: {host_secret}")
        st.text(f"supabase.user: {user_secret}")
    except Exception as e:
        st.error(f"Error reading secrets: {str(e)}")

st.markdown("---")

# Test connection
st.subheader("2️⃣ Test Database Connection")

from utils.supabase_config import load_supabase_config, get_supabase_connection

config = load_supabase_config()

col1, col2 = st.columns(2)

with col1:
    st.write("**Loaded Config:**")
    st.text(f"Host: {config.host}")
    st.text(f"Port: {config.port}")
    st.text(f"Database: {config.database}")
    st.text(f"User: {config.user}")
    st.text(f"Password: {('*' * len(config.password) if config.password else '❌ KOSONG')}")

with col2:
    st.write("**Connection Test:**")
    try:
        conn = get_supabase_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        st.success(f"✅ Connection successful!")
        st.text(f"Server time: {result}")
    except Exception as e:
        st.error(f"❌ Connection failed: {str(e)}")

st.markdown("---")

# Test save
st.subheader("3️⃣ Test Save to Database")

test_review = st.text_input("Test review text:", value="Test streamlit connection - ini harus masuk database")
test_sentiment = st.selectbox("Select sentiment:", ["positive", "negative", "neutral"])

if st.button("Test Save to Database"):
    with st.spinner("Saving..."):
        try:
            from utils.supabase_db import SupabaseDB
            
            result = SupabaseDB.save_prediction(
                review_text=test_review,
                processed_text=test_review.lower(),
                sentiment_label=test_sentiment,
                confidence=0.95,
            )
            
            if result:
                st.success("✅ Save successful!")
                
                # Verify
                conn = get_supabase_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM predictions;")
                count = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                
                st.info(f"Total rows in predictions table: {count}")
            else:
                st.error("❌ Save returned False")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            st.error(traceback.format_exc())

st.markdown("---")

# Check data
st.subheader("4️⃣ Check Latest Data")

try:
    from utils.supabase_config import get_supabase_connection
    
    conn = get_supabase_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM predictions;")
    total = cursor.fetchone()[0]
    st.write(f"**Total predictions: {total}**")
    
    cursor.execute("""
        SELECT id, review_text, sentiment_label, confidence, created_at
        FROM predictions
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    rows = cursor.fetchall()
    for row in rows:
        st.write(f"ID: {row[0]} | {row[1][:50]}... | {row[2]} ({row[3]:.0%}) | {row[4]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    st.error(f"Error: {str(e)}")
