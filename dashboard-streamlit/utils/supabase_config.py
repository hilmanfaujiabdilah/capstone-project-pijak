"""
Konfigurasi koneksi ke Supabase PostgreSQL database.
Mendukung environment variables dan Streamlit secrets.
"""

import os
from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class SupabaseConfig:
    """Dataclass untuk menyimpan konfigurasi Supabase PostgreSQL."""
    host: str
    port: int
    database: str
    user: str
    password: str


def _secret_value(section: str, key: str, default: str | None = None) -> str | None:
    """Ambil nilai dari Streamlit secrets dengan fallback ke default."""
    try:
        return st.secrets.get(section, {}).get(key, default)
    except Exception:
        return default


def load_supabase_config() -> SupabaseConfig:
    """
    Load konfigurasi Supabase dari environment variables atau Streamlit secrets.
    
    Priority:
    1. Environment variables (SUPABASE_HOST, SUPABASE_PORT, dll)
    2. Streamlit secrets (secrets.toml)
    3. Default values
    
    Returns:
        SupabaseConfig: Konfigurasi Supabase yang siap digunakan
    """
    return SupabaseConfig(
        host=os.getenv("SUPABASE_HOST") or _secret_value("supabase", "host", "aws-1-ap-southeast-1.pooler.supabase.com"),
        port=int(os.getenv("SUPABASE_PORT") or _secret_value("supabase", "port", "6543")),
        database=os.getenv("SUPABASE_DATABASE") or _secret_value("supabase", "database", "postgres"),
        user=os.getenv("SUPABASE_USER") or _secret_value("supabase", "user", "postgres.rjyqzsroukgttltrpgtc"),
        password=os.getenv("SUPABASE_PASSWORD") or _secret_value("supabase", "password", ""),
    )


def supabase_connection_kwargs() -> dict[str, str | int]:
    """
    Generate connection kwargs untuk psycopg2.
    
    Returns:
        dict: Dictionary dengan host, port, database, user, password
    """
    config = load_supabase_config()
    return {
        "host": config.host,
        "port": config.port,
        "database": config.database,
        "user": config.user,
        "password": config.password,
    }


def get_supabase_connection():
    """
    Buat koneksi baru ke Supabase PostgreSQL.
    Memerlukan psycopg2 terinstall.
    
    Returns:
        psycopg2.connection: Koneksi database yang aktif
        
    Raises:
        ImportError: Jika psycopg2 belum terinstall
        psycopg2.Error: Jika koneksi gagal
    """
    try:
        import psycopg2
    except ImportError:
        raise ImportError(
            "psycopg2 diperlukan untuk koneksi Supabase. "
            "Install dengan: pip install psycopg2-binary"
        )

    return psycopg2.connect(**supabase_connection_kwargs())


@st.cache_resource(show_spinner=False)
def get_cached_supabase_connection():
    """
    Dapatkan cached connection ke Supabase.
    Menggunakan Streamlit caching untuk menghindari koneksi berulang.
    
    Returns:
        psycopg2.connection: Cached connection database
    """
    return get_supabase_connection()
