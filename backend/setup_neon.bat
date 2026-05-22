@echo off
echo ============================================================
echo ServiceLink AI - Neon DB Migration Setup
echo ============================================================
echo.

echo Step 1: Installing dependencies...
pip install psycopg2-binary
echo.

echo Step 2: Running database migration...
cd database
python migrate_to_neon.py
cd ..
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Start backend: python main.py
echo 2. Start frontend: cd ../frontend ^&^& npm run dev
echo 3. Open dashboard: http://localhost:3000/dashboard
echo.
pause
