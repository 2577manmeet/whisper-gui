@echo off
setlocal

REM Go to the folder where this .bat lives
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Run install.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call ".venv\Scripts\activate.bat"

echo Starting Whisper GUI...
python app.py

endlocal
