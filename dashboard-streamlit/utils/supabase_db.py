"""
Database operations untuk Supabase.
Menyediakan fungsi untuk menyimpan dan mengambil data prediksi dari database.
"""

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from utils.supabase_config import get_cached_supabase_connection


class SupabaseDB:
    """Helper class untuk operasi database Supabase."""

    @staticmethod
    def initialize_tables():
        """
        Buat tabel yang diperlukan jika belum ada.
        Dipanggil sekali saat setup aplikasi.
        
        Tables:
        - predictions: Menyimpan semua hasil prediksi
        - batch_predictions: Menyimpan batch predictions
        """
        try:
            conn = get_cached_supabase_connection()
            cursor = conn.cursor()

            # Tabel untuk single predictions
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

            # Tabel untuk batch predictions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS batch_predictions (
                    id SERIAL PRIMARY KEY,
                    batch_name VARCHAR(255),
                    total_records INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Tabel untuk detail batch predictions
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

            # Create indexes untuk performa query
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_created_at 
                ON predictions(created_at DESC);
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_sentiment 
                ON predictions(sentiment_label);
            """)

            conn.commit()
            cursor.close()
            conn.close()
            
            st.success("✅ Database tables initialized successfully!")
            return True
            
        except Exception as e:
            st.error(f"❌ Error initializing database: {str(e)}")
            return False

    @staticmethod
    def save_prediction(
        review_text: str,
        processed_text: str,
        sentiment_label: str,
        confidence: float,
    ) -> bool:
        """
        Simpan hasil single prediction ke database.
        
        Args:
            review_text: Teks review asli
            processed_text: Teks setelah preprocessing
            sentiment_label: Label sentimen (positive, neutral, negative)
            confidence: Score confidence (0-1)
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            from utils.supabase_config import get_supabase_connection
            
            # Gunakan get_supabase_connection() TANPA cache untuk fresh connection
            conn = get_supabase_connection()
            cursor = conn.cursor()

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
            
            print(f"[DEBUG] ✅ Data saved successfully for review: {review_text[:50]}")
            return True
            
        except Exception as e:
            error_msg = f"❌ Error saving prediction: {str(e)}"
            print(f"[DEBUG] {error_msg}")
            import traceback
            traceback.print_exc()
            st.error(error_msg)
            return False

    @staticmethod
    def save_batch_predictions(
        predictions_data: list[dict],
        batch_name: str | None = None,
    ) -> int | None:
        """
        Simpan batch predictions ke database.
        
        Args:
            predictions_data: List of dicts dengan keys:
                - review_text
                - processed_text
                - sentiment_label
                - confidence
            batch_name: Nama batch (optional)
            
        Returns:
            int: Batch ID jika berhasil, None jika gagal
        """
        if not predictions_data:
            st.warning("No predictions to save.")
            return None

        try:
            from utils.supabase_config import get_supabase_connection
            
            # Gunakan get_supabase_connection() TANPA cache untuk fresh connection
            conn = get_supabase_connection()
            cursor = conn.cursor()

            # Create batch record
            cursor.execute(
                """
                INSERT INTO batch_predictions (batch_name, total_records)
                VALUES (%s, %s)
                RETURNING id;
                """,
                (batch_name, len(predictions_data)),
            )
            batch_id = cursor.fetchone()[0]

            # Insert batch details
            for pred in predictions_data:
                cursor.execute(
                    """
                    INSERT INTO batch_prediction_details
                    (batch_id, review_text, processed_text, sentiment_label, confidence)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        batch_id,
                        pred.get("review_text", ""),
                        pred.get("processed_text", ""),
                        pred.get("sentiment_label", ""),
                        pred.get("confidence", 0.0),
                    ),
                )

            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"[DEBUG] ✅ Batch {batch_id} saved with {len(predictions_data)} predictions")
            return batch_id
            
        except Exception as e:
            error_msg = f"❌ Error saving batch predictions: {str(e)}"
            print(f"[DEBUG] {error_msg}")
            import traceback
            traceback.print_exc()
            st.error(error_msg)
            return None

    @staticmethod
    def get_predictions(limit: int = 100) -> pd.DataFrame | None:
        """
        Ambil data predictions dari database.
        
        Args:
            limit: Jumlah records terbaru yang diambil
            
        Returns:
            pd.DataFrame: DataFrame dengan predictions atau None jika gagal
        """
        try:
            conn = get_cached_supabase_connection()
            
            query = f"""
                SELECT id, review_text, processed_text, sentiment_label, confidence, created_at
                FROM predictions
                ORDER BY created_at DESC
                LIMIT {limit};
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df if not df.empty else None
            
        except Exception as e:
            st.error(f"❌ Error fetching predictions: {str(e)}")
            return None

    @staticmethod
    def get_sentiment_summary(days: int = 30) -> pd.DataFrame | None:
        """
        Ambil summary sentimen dari predictions dalam N hari terakhir.
        
        Args:
            days: Jumlah hari terakhir
            
        Returns:
            pd.DataFrame: Summary dengan columns (sentiment_label, count, percentage)
        """
        try:
            conn = get_cached_supabase_connection()
            
            query = f"""
                SELECT 
                    sentiment_label,
                    COUNT(*) as count,
                    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM predictions 
                           WHERE created_at >= NOW() - INTERVAL '{days} days'), 2) as percentage
                FROM predictions
                WHERE created_at >= NOW() - INTERVAL '{days} days'
                GROUP BY sentiment_label
                ORDER BY count DESC;
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df if not df.empty else None
            
        except Exception as e:
            st.error(f"❌ Error fetching sentiment summary: {str(e)}")
            return None

    @staticmethod
    def get_recent_predictions_with_stats(limit: int = 50) -> dict:
        """
        Ambil recent predictions dengan statistik.
        
        Args:
            limit: Jumlah recent predictions
            
        Returns:
            dict: Berisi 'data' (DataFrame) dan 'stats' (dict)
        """
        try:
            conn = get_cached_supabase_connection()
            cursor = conn.cursor()

            # Get recent predictions
            cursor.execute(f"""
                SELECT id, review_text, processed_text, sentiment_label, confidence, created_at
                FROM predictions
                ORDER BY created_at DESC
                LIMIT {limit};
            """)
            
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)

            # Get stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_predictions,
                    COUNT(DISTINCT DATE(created_at)) as days_with_predictions,
                    MIN(created_at) as first_prediction,
                    MAX(created_at) as last_prediction
                FROM predictions;
            """)
            
            stats_data = cursor.fetchone()
            stats = {
                "total_predictions": stats_data[0] if stats_data else 0,
                "days_with_predictions": stats_data[1] if stats_data else 0,
                "first_prediction": stats_data[2],
                "last_prediction": stats_data[3],
            }

            cursor.close()
            conn.close()
            
            return {
                "data": df if not df.empty else None,
                "stats": stats,
            }
            
        except Exception as e:
            st.error(f"❌ Error fetching recent predictions with stats: {str(e)}")
            return {"data": None, "stats": {}}

    @staticmethod
    def clear_old_predictions(days: int = 90) -> bool:
        """
        Hapus predictions yang lebih lama dari N hari.
        
        Args:
            days: Umur predictions yang akan dihapus
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            conn = get_cached_supabase_connection()
            cursor = conn.cursor()

            cursor.execute(
                f"""
                DELETE FROM predictions
                WHERE created_at < NOW() - INTERVAL '{days} days';
                """
            )

            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            st.info(f"✅ Deleted {deleted_count} old predictions.")
            return True
            
        except Exception as e:
            st.error(f"❌ Error clearing old predictions: {str(e)}")
            return False

    @staticmethod
    def test_connection() -> bool:
        """
        Test koneksi ke Supabase database.
        
        Returns:
            bool: True jika berhasil terhubung, False jika gagal
        """
        try:
            conn = get_cached_supabase_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT NOW();")
            cursor.fetchone()
            cursor.close()
            conn.close()
            return True
        except Exception:
            return False
