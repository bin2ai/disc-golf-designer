@echo off
echo 🥏 Disc Golf Designer Pro
echo ======================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Streamlit application...
echo The application will open in your browser at http://localhost:8501
echo.
streamlit run app.py
pause