#!/bin/bash

# EU AI Act Compliance Classifier - Startskript fuer macOS
echo "========================================================"
echo "  Starte EU AI Act Compliance Classifier..."
echo "========================================================"
echo

# Pruefe, ob python3 installiert ist
if ! command -v python3 &> /dev/null; then
    echo "[FEHLER] Python 3 wurde auf diesem System nicht gefunden!"
    echo "Bitte installiere Python 3.10 oder neuer (z. B. via Homebrew oder python.org)."
    echo
    read -p "Druecke Enter zum Beenden..."
    exit 1
fi

# Erstelle venv, falls nicht vorhanden
if [ ! -d ".venv" ]; then
    echo "Erstelle virtuelle Umgebung (.venv)..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[FEHLER] Erstellung der virtuellen Umgebung fehlgeschlagen!"
        read -p "Druecke Enter zum Beenden..."
        exit 1
    fi
fi

# Aktiviere venv und installiere requirements
echo "Aktiviere virtuelle Umgebung und pruefe Pakete..."
source .venv/bin/activate
python3 -m pip install --upgrade pip >/dev/null 2>&1
echo "Installiere/Aktualisiere requirements.txt..."
pip3 install -r requirements.txt

# Starte App
echo
echo "========================================================"
echo "  Die Anwendung wird im Browser geoeffnet."
echo "  Schliesse dieses Terminal nicht, solange du arbeitest."
echo "========================================================"
echo
streamlit run app.py
