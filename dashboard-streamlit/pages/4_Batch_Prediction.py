import pandas as pd
import streamlit as st

from utils.modeling import predict_many
from utils.supabase_db import SupabaseDB
from utils.ui import page_hero, setup_page


setup_page("Batch Prediction", "📂")
page_hero(
    "Batch Prediction",
    "Upload CSV berisi banyak review untuk diprediksi sekaligus dan unduh hasilnya.",
)

# Initialize session state untuk menyimpan hasil batch prediction
if "batch_results" not in st.session_state:
    st.session_state.batch_results = None
if "batch_df" not in st.session_state:
    st.session_state.batch_df = None
if "batch_filename" not in st.session_state:
    st.session_state.batch_filename = None
if "batch_text_column" not in st.session_state:
    st.session_state.batch_text_column = None

uploaded = st.file_uploader("Upload file CSV", type=["csv"])

if uploaded is None:
    st.info("CSV minimal memiliki satu kolom teks, misalnya `review_text`.")
else:
    try:
        df = pd.read_csv(uploaded)
        st.subheader("Preview Data")
        st.dataframe(df.head(10), use_container_width=True)

        text_candidates = [col for col in df.columns if "text" in col.lower() or "review" in col.lower()]
        default_index = df.columns.get_loc(text_candidates[0]) if text_candidates else 0
        text_column = st.selectbox("Kolom teks untuk prediksi", df.columns, index=default_index)

        if st.button("Jalankan Batch Prediction", type="primary"):
            with st.spinner("Memproses seluruh review..."):
                results = predict_many(df[text_column].fillna("").astype(str).tolist())
                result_df = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
                
                # Simpan ke session state agar tersedia di rerun berikutnya
                st.session_state.batch_results = results
                st.session_state.batch_df = result_df
                st.session_state.batch_filename = uploaded.name
                st.session_state.batch_text_column = text_column

            st.rerun()

        # Tampilkan hasil jika ada di session state
        if st.session_state.batch_results is not None:
            results = st.session_state.batch_results
            result_df = st.session_state.batch_df
            
            st.success(f"Selesai memprediksi {len(result_df):,} baris.")
            st.dataframe(result_df.head(30), use_container_width=True)

            csv_bytes = result_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "Download hasil CSV",
                data=csv_bytes,
                file_name="vibesight_batch_prediction.csv",
                mime="text/csv",
                use_container_width=True,
            )

            # Simpan ke Supabase
            st.divider()
            col_save, col_status = st.columns([0.3, 0.7])
            
            save_to_db = col_save.button("💾 Simpan ke Database", use_container_width=True)
            
            if save_to_db:
                with st.spinner(f"Menyimpan {len(results)} prediksi ke Supabase..."):
                    # Format data untuk batch insert
                    batch_data = []
                    for i, result in enumerate(results):
                        batch_data.append({
                            "review_text": df[st.session_state.batch_text_column].iloc[i],
                            "processed_text": result.get("processed_text", ""),
                            "sentiment_label": result.get("label", ""),
                            "confidence": result.get("confidence", 0.0),
                        })
                    
                    batch_id = SupabaseDB.save_batch_predictions(
                        batch_data,
                        batch_name=st.session_state.batch_filename
                    )
                
                if batch_id:
                    st.success(f"✅ Batch prediksi berhasil disimpan ke database! (Batch ID: {batch_id})")
                    # Clear session state setelah berhasil save
                    st.session_state.batch_results = None
                    st.session_state.batch_df = None
                else:
                    st.error("❌ Gagal menyimpan batch. Pastikan database sudah terhubung.")
                    
    except Exception as exc:
        st.error(f"Gagal memproses file: {exc}")
