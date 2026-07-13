"""
Liest die umgangssprachlichen Erklärungen aus der info_texts.json Datei ein.
Dadurch können Inhalte vom Anwender direkt manuell bearbeitet werden.
"""

import json
from pathlib import Path

# Pfad zur info_texts.json ermitteln
JSON_PATH = Path(__file__).parent / "info_texts.json"

try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        _data = json.load(f)
except Exception as exc:
        # Fallback bei Ladefehlern
        _data = {}

GENERAL_INFO = _data.get("GENERAL_INFO", {})
AI_CHECK_INFO = _data.get("AI_CHECK_INFO", "")
AUTONOMY_INFO = _data.get("AUTONOMY_INFO", {})
DECISION_IMPACT_INFO = _data.get("DECISION_IMPACT_INFO", {})
ROLE_INFO = _data.get("ROLE_INFO", {})
GPAI_INFO = _data.get("GPAI_INFO", "")
