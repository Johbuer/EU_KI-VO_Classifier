import logging
from src.state import get_data

logger = logging.getLogger(__name__)


def get_risk_class(data=None):
    if data is None:
        data = get_data()

    clf = data.get("classification", {})

    if clf.get("is_ai_system") is False:
        return "not_ai"

    if clf.get("prohibited", {}).get("detected"):
        return "prohibited"

    if clf.get("high_risk", {}).get("final_is_high_risk"):
        return "high_risk"

    if clf.get("transparency", {}).get("any_applies"):
        return "limited_risk"

    if clf.get("is_ai_system") is True:
        return "minimal_risk"

    return ""


def eval_high_risk(data=None):
    if data is None:
        data = get_data()

    hr = data["classification"]["high_risk"]
    annex_i = hr.get("annex_i_applies") is True
    annex_iii = hr.get("any_annex_iii_match", False)

    if not annex_i and not annex_iii:
        hr["final_is_high_risk"] = False
        return False

    exception = hr.get("exception_art6_3_applies") is True
    profiling = hr.get("profiling_override") is True

    # Art. 6 Abs. 3 UAbs. 3 KI-VO: Wenn das System Profiling betreibt,
    # erlischt die Ausnahme. Das System gilt dann zwingend als Hochrisiko.
    if profiling:
        hr["final_is_high_risk"] = True
        return True

    if exception:
        hr["final_is_high_risk"] = False
        return False

    hr["final_is_high_risk"] = True
    return True


def eval_transparency(data=None):
    if data is None:
        data = get_data()

    transp = data["classification"]["transparency"]
    applies = any([
        transp.get("direct_interaction") is True,
        transp.get("synthetic_content") is True,
        transp.get("emotion_recognition") is True,
        transp.get("biometric_categorization") is True,
        transp.get("deepfake") is True,
        transp.get("public_interest_text") is True,
    ])
    transp["any_applies"] = applies
    return applies


def eval_role_shift(data=None):
    if data is None:
        data = get_data()

    app = data["layer3_application"]
    clf = data["classification"]
    role = clf["role"]
    hr = clf["high_risk"]

    # Art. 25 Abs. 1 lit. c KI-VO: Wer ein bestehendes System maßgeblich modifiziert
    # oder die Zweckbestimmung in einen Hochrisikobereich ändert, gilt rechtlich als Anbieter.
    if app.get("sourcing_system") == "extern" and hr.get("final_is_high_risk"):
        role["provider_by_art25"] = True
        role["provider_by_art25_reason"] = (
            "Pflichtenuebergang nach Art. 25 Abs. 1 lit. c KI-VO: "
            "Aenderung der Zweckbestimmung in einen Hochrisiko-Bereich."
        )

    # Art. 3 Nr. 3 i.V.m. Nr. 11 KI-VO: Wer ein System für den Eigengebrauch entwickelt,
    # gilt als Anbieter und übernimmt die vollen Anbieterpflichten.
    if app.get("sourcing_system") == "inhouse":
        role["provider_by_self_use"] = True
        role["provider"] = True

    # Art. 53 Abs. 1 lit. b KI-VO: Bei der Integration externer GPAI-Modelle
    # entstehen für nachgelagerte Anbieter Auskunftsansprüche gegenüber dem GPAI-Anbieter.
    gpai = clf.get("gpai", {})
    components = data.get("layer2_components", [])
    has_external_llm = any(c.get("type") == "llm" and c.get("sourcing") in ["extern_sourcing", "extern_adapted"] for c in components)
    if gpai.get("is_gpai") is True and has_external_llm:
        role["downstream_provider"] = True


def run_eval(data=None):
    if data is None:
        data = get_data()

    components = data.get("layer2_components", [])
    llm_comps = [c for c in components if c.get("type") == "llm"]
    gpai = data["classification"].setdefault("gpai", {})
    
    if llm_comps:
        gpai["is_gpai"] = True
        names = [c.get("name") or "Unbenanntes LLM" for c in llm_comps]
        gpai["model_name"] = ", ".join(names)
        gpai["is_provider"] = any(c.get("sourcing") == "inhouse_sourcing" for c in llm_comps)
    else:
        gpai["is_gpai"] = False
        gpai["is_provider"] = False

    eval_high_risk(data)
    eval_transparency(data)
    eval_role_shift(data)

    risk_cat = get_risk_class(data)
    data["classification"]["risk_category"] = risk_cat

    return risk_cat
