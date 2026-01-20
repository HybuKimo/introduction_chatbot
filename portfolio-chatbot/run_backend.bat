@echo off
echo Starting Portfolio Chatbot Backend...
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
