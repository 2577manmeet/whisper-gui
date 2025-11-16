@echo off
setlocal

REM Go to the folder where this .bat lives
cd /d "%~dp0"

echo.
echo === Whisper GUI Installer ===
echo.

REM Check for Python
where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found on PATH.
    echo Please install Python 3.10+ from https://www.python.org/ and try again.
    pause
    exit /b 1
)

echo Creating virtual environment (.venv)...
python -m venv .venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call ".venv\Scripts\activate.bat"

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install Python dependencies.
    pause
    exit /b 1
)

echo.
echo All done! You can now run app.bat to start the GUI.
echo.
pause
endlocal
