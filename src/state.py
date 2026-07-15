"""
Zentrales Session-State Management für den KI-VO Classifier Wizard.
Nutzt Streamlit session_state für die In-Session-Persistenz und JSON für den Datei-Export.
"""

import json
import logging
from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "1.0.0"
APP_VERSION = "1.0.0"
TOTAL_STEPS = 10  # 0-9

DEFAULT_STATE = {
    "metadata": {
        "schema_version": SCHEMA_VERSION,
        "app_version": APP_VERSION,
        "created_at": "",
        "updated_at": "",
        "session_id": "",
    },
    "current_step": 0,
    "current_substep": 0,
    "max_visited_step": 0,
    "layer1_infrastructure": {
        "platform_used": None,
        "platform_name": "",
        "primary_platform": "",
        "platform_type": "",
        "sub_platform_used": None,
        "connected_sub_platforms": [],
        "secondary_platform": "",
        "ikt_security_notes": "",
        "third_party_risk_notes": "",
        "access_controls": "",
    },
    "layer2_components": [],
    "layer3_application": {
        "system_name": "",
        "system_version": "",
        "responsible_person": "",
        "status": "",
        "development_status": "",
        "sourcing_system": "",
        "developer_system": "",
        "purpose": "",
        "working_description": "",
        "contribution_explanation": "",
        "interfaces": "",
        "personal_data_processed": None,
        "personal_data_categories": "",
    },
    "classification": {
        "is_ai_system": None,
        "is_ai_system_reasoning": "",
        "prohibited": {
            "detected": False,
            "details": {},
        },
        "high_risk": {
            "annex_i_applies": None,
            "annex_iii_matches": {},
            "any_annex_iii_match": False,
            "exception_art6_3_applies": None,
            "exception_art6_3_condition": "",
            "exception_art6_3_reasoning": "",
            "profiling_override": None,
            "final_is_high_risk": False,
        },
        "transparency": {
            "direct_interaction": None,
            "synthetic_content": None,
            "content_generation_mode": None,
            "emotion_recognition": None,
            "biometric_categorization": None,
            "deepfake": None,
            "public_interest_text": None,
            "any_applies": False,
        },
        "gpai": {
            "is_gpai": None,
            "systemic_risk": None,
            "flops_above_threshold": None,
        },
        "role": {
            "provider": False,
            "deployer": False,
            "importer": False,
            "distributor": False,
            "downstream_provider": False,
            "provider_by_art25": False,
            "provider_by_art25_reason": "",
            "provider_by_self_use": False,
        },
        "autonomy_level": "",
        "decision_impact": "",
        "risk_category": "",
    },
}


def init_session_state():
    if "classifier_data" not in st.session_state:
        data = json.loads(json.dumps(DEFAULT_STATE))
        data["metadata"]["created_at"] = datetime.now(timezone.utc).isoformat()
        data["metadata"]["session_id"] = str(uuid4())[:8]
        st.session_state.classifier_data = data
        logger.info("Session state initialisiert mit frischen Daten")


def get_data():
    init_session_state()
    return st.session_state.classifier_data


def update_data(path, value):
    """Aktualisiert einen geschachtelten Wert in den Classifier-Daten per Dot-Notation."""
    data = get_data()
    keys = path.split(".")
    current = data
    for key in keys[:-1]:
        current = current[key]
    current[keys[-1]] = value
    data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()


def get_value(path, default=None):
    """Liest einen geschachtelten Wert aus den Classifier-Daten per Dot-Notation."""
    data = get_data()
    keys = path.split(".")
    current = data
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def set_current_step(step):
    data = get_data()
    data["current_step"] = step
    data["current_substep"] = 0
    if step > data["max_visited_step"]:
        data["max_visited_step"] = step


def get_current_step():
    return get_data()["current_step"]


def set_current_substep(substep):
    data = get_data()
    data["current_substep"] = substep


def get_current_substep():
    return get_data().get("current_substep", 0)


def add_component(name="", comp_type="", license_type="", provider="", version="", data_sources="", sourcing=""):
    data = get_data()
    component = {
        "id": str(uuid4())[:8],
        "name": name,
        "type": comp_type,
        "license": license_type,
        "provider": provider,
        "version": version,
        "data_sources": data_sources,
        "sourcing": sourcing,
    }
    data["layer2_components"].append(component)
    return component["id"]


def remove_component(comp_id):
    data = get_data()
    data["layer2_components"] = [
        c for c in data["layer2_components"] if c["id"] != comp_id
    ]


def export_to_json():
    data = get_data()
    data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    return json.dumps(data, indent=2, ensure_ascii=False)


def import_from_json(json_string):
    try:
        data = json.loads(json_string)
        if data.get("metadata", {}).get("schema_version") != SCHEMA_VERSION:
            logger.warning("Schema-Versionskonflikt beim Import")
        st.session_state.classifier_data = data
        return True
    except (json.JSONDecodeError, KeyError) as exc:
        logger.error("Fehler beim JSON-Import: %s", exc)
        return False
