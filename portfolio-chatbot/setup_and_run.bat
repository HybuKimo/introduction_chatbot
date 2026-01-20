@echo off
echo Installing dependencies...
cd backend
pip install -r requirements.txt
echo.
echo Installing Playwright browsers...
playwright install chromium
echo.
echo Starting AI Portfolio Agent v2.0...
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
