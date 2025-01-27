@echo off
echo Installing requirements...
pip install -r requirements.txt

echo Starting Email Tracking Service...
python Script.py
pause 