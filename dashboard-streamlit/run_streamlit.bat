@echo off
REM Script untuk run Streamlit dengan environment variable Supabase

set SUPABASE_PASSWORD=Z6nLytics123$
set SUPABASE_HOST=aws-1-ap-southeast-1.pooler.supabase.com
set SUPABASE_PORT=6543
set SUPABASE_DATABASE=postgres
set SUPABASE_USER=postgres.rjyqzsroukgttltrpgtc

echo ============================================================
echo  Starting Sentiment Dashboard with Supabase Connection
echo ============================================================
echo.
echo Environment Variables Set:
echo   - SUPABASE_PASSWORD: *** (protected)
echo   - SUPABASE_HOST: %SUPABASE_HOST%
echo.

cd /d "%~dp0"
streamlit run app.py

pause
