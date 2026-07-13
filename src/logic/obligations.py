"""
Dynamischer Pflichtenkatalog und Rechte-Zuweisung.
Liest alle rechtlichen Inhalte aus obligations.json und rights.json.
Dadurch können Inhalte vom Anwender direkt manuell bearbeitet werden.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Pfade zu den JSON-Dateien ermitteln
DATA_DIR = Path(__file__).parent.parent / "data"
OBLIGATIONS_JSON_PATH = DATA_DIR / "obligations.json"
RIGHTS_JSON_PATH = DATA_DIR / "rights.json"


def load_json_data(file_path):
    """Hilfsfunktion zum Laden einer JSON-Datei mit UTF-8-Encoding."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error("Fehler beim Laden von %s: %s", file_path, exc)
        return {}


def get_obligations(risk_category, roles, gpai_status, transparency_flags):
    """
    Gibt eine Liste der anwendbaren Pflichten basierend auf Risikoklasse,
    Rolle, GPAI-Status und Transparenz-Flags zurück.
    """
    ob_data = load_json_data(OBLIGATIONS_JSON_PATH)
    obligations = []

    # 1. Universelle Pflichten (Art. 4)
    if "universal" in ob_data:
        obligations.extend(ob_data["universal"])

    # 2. Verbotene Systeme (Art. 5)
    if risk_category == "prohibited":
        if "prohibited" in ob_data:
            obligations.extend(ob_data["prohibited"])
        return obligations  # Keine weiteren Pflichten für verbotene Systeme

    # 3. Hochrisiko - Anbieter-Pflichten
    is_provider = (
        roles.get("provider") or 
        roles.get("provider_by_art25") or 
        roles.get("provider_by_self_use")
    )
    if risk_category == "high_risk" and is_provider:
        if "high_risk_provider" in ob_data:
            obligations.extend(ob_data["high_risk_provider"])

    # 4. Hochrisiko - Betreiber-Pflichten
    if risk_category == "high_risk" and roles.get("deployer"):
        if "high_risk_deployer" in ob_data:
            obligations.extend(ob_data["high_risk_deployer"])

    # 5. Transparenz-Pflichten (Art. 50)
    if transparency_flags.get("direct_interaction"):
        if "transparency_direct_interaction" in ob_data:
            obligations.extend(ob_data["transparency_direct_interaction"])

    if transparency_flags.get("synthetic_content"):
        if "transparency_synthetic_content" in ob_data:
            obligations.extend(ob_data["transparency_synthetic_content"])

    if transparency_flags.get("emotion_recognition") or transparency_flags.get("biometric_categorization"):
        if "transparency_emotion_recognition" in ob_data:
            obligations.extend(ob_data["transparency_emotion_recognition"])

    if transparency_flags.get("deepfake"):
        if "transparency_deepfake" in ob_data:
            obligations.extend(ob_data["transparency_deepfake"])

    if transparency_flags.get("public_interest_text"):
        if "transparency_public_interest_text" in ob_data:
            obligations.extend(ob_data["transparency_public_interest_text"])

    # 6. GPAI-Pflichten
    if gpai_status.get("is_gpai") and gpai_status.get("is_provider"):
        if "gpai" in ob_data:
            obligations.extend(ob_data["gpai"])

    # 7. GPAI mit systemischem Risiko
    if gpai_status.get("systemic_risk") and gpai_status.get("is_provider"):
        if "gpai_systemic" in ob_data:
            obligations.extend(ob_data["gpai_systemic"])

    return obligations


def get_rights(roles, gpai_status, risk_category):
    """
    Gibt die Ansprüche und Rechte gegenüber Dritten zurück.
    """
    rights_data = load_json_data(RIGHTS_JSON_PATH)
    rights = []

    # 1. Nachgelagerter Anbieter gegenüber GPAI-Hersteller
    if roles.get("downstream_provider") and gpai_status.get("is_gpai"):
        if "downstream_provider" in rights_data:
            rights.extend(rights_data["downstream_provider"])

    # 2. Betreiber gegenüber Anbieter bei Hochrisiko
    if roles.get("deployer") and risk_category == "high_risk":
        if "deployer_high_risk" in rights_data:
            rights.extend(rights_data["deployer_high_risk"])

    # 3. Hochrisiko-Anbieter gegenüber Komponenten-Zulieferern (Art. 25 Abs. 4)
    if risk_category == "high_risk":
        if "component_provider_high_risk" in rights_data:
            rights.extend(rights_data["component_provider_high_risk"])

    return rights
