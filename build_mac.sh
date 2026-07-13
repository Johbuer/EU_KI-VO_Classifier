#!/bin/bash

# EU AI Act Compliance Classifier - Mac-Compiler
echo "========================================================"
echo "  Kompiliere eigenstaendige macOS-Anwendung..."
echo "  (Bitte auf dem Ziel-Mac ausfuehren)"
echo "========================================================"
echo

# Pruefe virtuelle Umgebung
if [ ! -d ".venv" ]; then
    echo "[INFO] Virtuelle Umgebung (.venv) fehlt. Erstelle venv..."
    python3 -m venv .venv
fi

echo "Aktiviere virtuelle Umgebung..."
source .venv/bin/activate

echo "Installiere Voraussetzungen..."
pip install -r requirements.txt
pip install pyinstaller

echo
echo "Starte PyInstaller Kompilierung..."
echo "(Dies kann 1-2 Minuten dauern, bitte warten...)"
echo

# macOS nutzt : statt ; fuer --add-data
pyinstaller --clean --noconfirm --onefile --name="EU_AI_Act_Classifier" --collect-all streamlit --collect-all fpdf2 --add-data "app.py:." --add-data "src:src" --add-data ".streamlit:.streamlit" run_app.py

if [ $? -eq 0 ]; then
    echo
    echo "========================================================"
    echo "  Kompilierung ERFOLGREICH!"
    echo "  Die fertige Anwendung befindet sich im Ordner:"
    echo "  $(pwd)/dist/EU_AI_Act_Classifier"
    echo "========================================================"
else
    echo
    echo "[FEHLER] Kompilierung fehlgeschlagen!"
fi

echo
read -p "Druecke Enter zum Beenden..."
