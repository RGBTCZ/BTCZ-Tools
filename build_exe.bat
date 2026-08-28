@echo off
cd /d "%~dp0"
echo ========================================
echo   Build BTCZ Tools .exe (PyInstaller)
echo ========================================

if not exist "venv" (
    echo Creation du venv...
    python -m venv venv
)
call venv\Scripts\activate

echo Installation des dependances...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q

echo Build en cours...
pyinstaller btcz_tools.spec --noconfirm --clean

echo.
echo ========================================
echo   Termine : dist\BTCZ Tools.exe
echo ========================================
pause
