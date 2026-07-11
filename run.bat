@echo off
setlocal
cd /d "%~dp0"

echo == AI Product Image Intelligence Platform ==

cd backend
if not exist ".venv" (
  echo [backend] creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
echo [backend] installing dependencies (first run downloads ~3-5GB of ML libraries)...
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo [backend] starting API on http://localhost:8000 ...
start "backend" cmd /k uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
cd ..

cd frontend
if not exist "node_modules" (
  echo [frontend] installing dependencies...
  call npm install
)
echo [frontend] starting dev server on http://localhost:5173 ...
start "frontend" cmd /k npm run dev
cd ..

echo.
echo Backend:  http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo Two new windows were opened for backend and frontend. Close them to stop.
