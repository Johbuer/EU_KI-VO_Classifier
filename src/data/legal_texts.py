"""
Liest die Gesetzestexte der EU-KI-Verordnung aus legal_texts.json ein.
Dadurch können alle rechtlichen Inhalte direkt manuell bearbeitet werden.
"""

import json
from pathlib import Path

# Pfad zur legal_texts.json ermitteln
JSON_PATH = Path(__file__).parent / "legal_texts.json"

try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        _data = json.load(f)
except Exception as exc:
    # Fallback bei Ladefehlern
    _data = {}

ART3_DEFINITIONS = _data.get("ART3_DEFINITIONS", {})
ART5_PROHIBITED = _data.get("ART5_PROHIBITED", [])
ART6_HIGH_RISK = _data.get("ART6_HIGH_RISK", {})
ANNEX_III_CATEGORIES = _data.get("ANNEX_III_CATEGORIES", [])
ART25_ROLE_SHIFT = _data.get("ART25_ROLE_SHIFT", {})
ART50_TRANSPARENCY = _data.get("ART50_TRANSPARENCY", [])
ART51_GPAI = _data.get("ART51_GPAI", {})
