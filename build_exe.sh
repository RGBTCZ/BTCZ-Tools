#!/bin/bash
cd "$(dirname "$0")"
echo "🏗️  Build BTCZ Tools .exe (PyInstaller)"

if [ ! -d "venv" ]; then
    python -m venv venv
fi
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q

pyinstaller btcz_tools.spec --noconfirm --clean

echo "✅ Terminé : dist/BTCZ Tools.exe"
read -p "Entrée pour fermer..."
