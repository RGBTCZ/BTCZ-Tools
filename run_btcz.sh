#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 BTCZ Tools"

PY=""
for candidate in py python python3; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" --version >/dev/null 2>&1; then
        PY="$candidate"
        break
    fi
done

if [ -z "$PY" ]; then
    echo "❌ Python introuvable."
    echo "   Installe Python 3.10+ depuis https://www.python.org/downloads/"
    echo "   Puis décoche 'python' et 'python3' dans :"
    echo "   Paramètres > Applications > Alias d'exécution d'application"
    read -p "Entrée pour quitter..."
    exit 1
fi

echo "🐍 Python détecté : $($PY --version)"

FRESH=0
if [ ! -d "venv" ]; then
    echo "📦 Création du venv..."
    "$PY" -m venv venv || { echo "❌ Échec de la création du venv"; read -p "Entrée pour quitter..."; exit 1; }
    FRESH=1
fi

if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ venv introuvable après création"
    read -p "Entrée pour quitter..."
    exit 1
fi

if [ "$FRESH" = "1" ]; then
    echo "🔧 Installation des dépendances..."
    python -m pip install --upgrade pip -q
    python -m pip install -r requirements.txt -q
fi

echo "🚀 Lancement de BTCZ Tools..."
python run.py

read -p "✅ Fin - Appuie sur Entrée pour fermer..."
