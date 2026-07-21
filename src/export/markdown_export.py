from datetime import datetime, timezone
from src.state import get_data
from src.logic.classifier_engine import run_eval
from src.logic.obligations import get_obligations, get_rights


def generate_markdown(data=None):
    if data is None:
        data = get_data()

    risk_cat = run_eval(data)
    
    metadata = data.get("metadata", {})
    app = data.get("layer3_application", {})
    infra = data.get("layer1_infrastructure", {})
    components = data.get("layer2_components", [])
    clf = data.get("classification", {})
    
    roles = clf.get("role", {})
    gpai = clf.get("gpai", {})
    transp = clf.get("transparency", {})
    
    risk_label_map = {
        "prohibited": "VERBOTEN (Art. 5 KI-VO)",
        "high_risk": "HOCHRISIKO (Art. 6 KI-VO)",
        "limited_risk": "BEGRENZTES RISIKO (Art. 50 KI-VO)",
        "minimal_risk": "MINIMALES RISIKO",
        "not_ai": "KEIN KI-SYSTEM i.S.d. KI-VO"
    }
    
    risk_text = risk_label_map.get(risk_cat, "Unbekannt")
    
    md = []
    sys_name = app.get('system_name', 'Unbenannt')
    md.append(f"# {sys_name}: Klassifizierungsreport")
    md.append(f"**Generiert am:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    md.append(f"**Sitzungs-ID:** {metadata.get('session_id', 'N/A')}")
    md.append(f"**Tool-Version:** {metadata.get('app_version', '1.0.0')}")
    md.append("")
    md.append("> **Hinweis:** Dieses Dokument wurde mit einem Legal-Tech-Prototyp erstellt, der primär die technische ")
    md.append("> Umsetzung der regulatorischen Klassifizierungslogik demonstriert. Dieses Tool ersetzt keine Rechtsberatung.")
    md.append("")
    
    md.append("## 1. Zusammenfassung")
    md.append(f"**KI-System:** {app.get('system_name', 'Unbenannt')} (Version {app.get('system_version', 'N/A')})")
    md.append(f"**Verantwortlicher:** {app.get('responsible_person', 'N/A')}")
    
    status_val = app.get("status")
    status_label_map = {
        "in_operation": "In Betrieb",
        "out_of_operation": "Außer Betrieb",
        "testing": "Testphase",
        "in_development": "In Entwicklung"
    }
    dev_status_label_map = {
        "conception": "Konzeption",
        "active_dev": "Aktive Entwicklung",
        "mvp": "Minimum Viable Product"
    }
    status_text = "N/A"
    if status_val in status_label_map:
        status_text = status_label_map[status_val]
        dev_val = app.get("development_status")
        if status_val == "in_development" and dev_val in dev_status_label_map:
            status_text += f" ({dev_status_label_map[dev_val]})"
            
    md.append(f"**Betriebsstatus:** {status_text}")
    md.append(f"**Finale Risikoklasse:** **{risk_text}**")
    md.append("")
    
    active_roles_list = []
    role_translations = {
        "provider": "Anbieter",
        "deployer": "Betreiber",
        "importer": "Einführer",
        "distributor": "Händler",
        "downstream_provider": "Nachgelagerter Anbieter"
    }
    for r_key, r_label in role_translations.items():
        if roles.get(r_key):
            active_roles_list.append(r_label)
            
    if roles.get("provider_by_art25"):
        active_roles_list.append("Anbieter durch Pflichtenübertrag (Art. 25)")
    if roles.get("provider_by_self_use"):
        active_roles_list.append("Anbieter durch Inbetriebnahme zum Eigengebrauch")
        
    md.append(f"**Ermittelte Rollen:** {', '.join(active_roles_list) if active_roles_list else 'Keine Rolle ermittelt'}")
    md.append("")
    
    md.append("## 2. Systembeschreibung (Layer 3)")
    md.append(f"- **Einsatzzweck:** {app.get('purpose', 'N/A')}")
    md.append(f"- **Arbeitsweise:** {app.get('working_description', 'N/A')}")
    md.append(f"- **Beitrag zur Zweckerreichung:** {app.get('contribution_explanation', 'N/A')}")
    md.append(f"- **Schnittstellen:** {app.get('interfaces', 'N/A')}")
    md.append(f"- **Verarbeitung personenbezogener Daten:** {'Ja' if app.get('personal_data_processed') else 'Nein'}")
    if app.get("personal_data_processed"):
        md.append(f"  - *Kategorien:* {app.get('personal_data_categories', 'N/A')}")
    md.append(f"- **Sourcing System:** {'Eigenentwicklung' if app.get('sourcing_system') == 'inhouse' else ('Extern beschafft' if app.get('sourcing_system') == 'extern' else 'N/A')}")
    if app.get('sourcing_system') == 'extern' and app.get('developer_system'):
        md.append(f"  - *System-Entwickler:* {app.get('developer_system')}")
    md.append(f"- **Sourcing Modell:** {'Selbst trainiert' if app.get('sourcing_model') == 'inhouse' else ('Extern lizenziert / Vortrainiert' if app.get('sourcing_model') == 'extern' else 'N/A')}")
    if app.get('sourcing_model') == 'extern' and app.get('developer_model'):
        md.append(f"  - *Modell-Entwickler:* {app.get('developer_model')}")
    md.append("")
    
    md.append("## 3. Modellkomponenten (Layer 2)")
    if components:
        md.append("| Name | Typ | Lizenz | Anbieter | Version | Datenquellen |")
        md.append("| --- | --- | --- | --- | --- | --- |")
        for comp in components:
            comp_type_map = {
                "llm": "LLM",
                "gan_diffusion": "Spezialisierte GenKI",
                "random_forest": "Klassisches ML",
                "rpa": "RPA",
                "deterministic": "Regelwerk (det.)",
                "rag_pipeline": "RAG-Pipeline",
                "other": "Sonstiges"
            }
            c_type = comp_type_map.get(comp.get("type"), comp.get("type", "N/A"))
            c_license = "Open Source" if comp.get("license") == "open_source" else ("Proprietär" if comp.get("license") == "proprietary" else "N/A")
            md.append(f"| {comp.get('name', 'Unbenannt')} | {c_type} | {c_license} | {comp.get('provider', 'N/A')} | {comp.get('version', 'N/A')} | {comp.get('data_sources', 'N/A')} |")
    else:
        md.append("Keine spezifischen Modellkomponenten auf Layer 2 erfasst.")
    md.append("")

    md.append("## 4. Infrastruktur & Enabler-Plattform (Layer 1)")
    if infra.get("platform_used"):
        p_type_map = {"cloud": "Public Cloud", "on_premise": "On-Premise", "hybrid": "Hybrid"}
        p_type = p_type_map.get(infra.get("platform_type"), infra.get("platform_type", "N/A"))
        
        primary = infra.get('primary_platform') or infra.get('platform_name', 'N/A')
        md.append(f"- **Primäre Plattform / UI:** {primary}")
        
        secondary = infra.get("secondary_platform", "")
        if not secondary:
            sub_list = infra.get("connected_sub_platforms", [])
            if sub_list:
                secondary = ", ".join(sub_list)
        if secondary:
            md.append(f"- **Integrierte Infrastruktur / API-Gateway:** {secondary}")
            
        md.append(f"- **Betriebsmodell:** {p_type}")
        md.append(f"- **Sicherheitsmaßnahmen (TOMs):** {infra.get('ikt_security_notes', 'N/A')}")
        md.append(f"- **IKT-Drittparteienrisiko (DORA):** {infra.get('third_party_risk_notes', 'N/A')}")
        md.append(f"- **Zugriffskontrollen:** {infra.get('access_controls', 'N/A')}")
    else:
        md.append("Keine übergeordneten Enabler-Plattformen erfasst.")
    md.append("")

    md.append("## 5. Rechtliche Klassifizierung nach KI-VO")
    
    md.append(f"### Vorprüfung (Art. 3 Nr. 1 KI-VO)")
    md.append(f"- **Als KI-System eingestuft:** {'Ja' if clf.get('is_ai_system') else 'Nein'}")
    if clf.get("is_ai_system_reasoning"):
        md.append(f"- **Begründung:** {clf.get('is_ai_system_reasoning')}")
    md.append("")
    
    if risk_cat == "prohibited":
        md.append("### Verbotene Praktik nach Art. 5 KI-VO erkannt")
        prob_details = clf.get("prohibited", {}).get("details", {})
        for pk, pv in prob_details.items():
            if pv.get("detected"):
                md.append(f"- **Verbotsgrund (Key):** {pk}")
                md.append(f"- **Details:** {pv.get('notes', 'Keine weiteren Details angegeben')}")
        md.append("")
    
    if clf.get("high_risk", {}).get("annex_i_applies") or clf.get("high_risk", {}).get("any_annex_iii_match"):
        md.append("### Hochrisiko-Prüfung (Art. 6)")
        md.append(f"- **Sicherheitsbauteil / Anhang I (Art. 6 Abs. 1):** {'Ja' if clf.get('high_risk', {}).get('annex_i_applies') else 'Nein'}")
        
        matches = [k for k, v in clf.get("high_risk", {}).get("annex_iii_matches", {}).items() if v]
        md.append(f"- **Anhang III Anwendungsbereiche (Art. 6 Abs. 2):** {', '.join(matches) if matches else 'Keine'}")
        
        if clf.get("high_risk", {}).get("exception_art6_3_applies"):
            md.append(f"- **Ausnahme nach Art. 6 Abs. 3 beantragt:** Ja")
            md.append(f"  - **Bedingung:** {clf.get('high_risk', {}).get('exception_art6_3_condition')}")
            md.append(f"  - **Begründung:** {clf.get('high_risk', {}).get('exception_art6_3_reasoning')}")
        else:
            md.append(f"- **Ausnahme nach Art. 6 Abs. 3:** Nein")
            
        md.append(f"- **Profiling durch das System (Art. 6 Abs. 3 UAbs. 3):** {'Ja (Hebt Ausnahme auf)' if clf.get('high_risk', {}).get('profiling_override') else 'Nein'}")
        md.append(f"- **Finale Einstufung als Hochrisiko:** {'Ja' if clf.get('high_risk', {}).get('final_is_high_risk') else 'Nein'}")
        md.append("")

    md.append("### Transparenzanforderungen (Art. 50)")
    md.append(f"- **Direkte Interaktion mit Personen:** {'Ja' if transp.get('direct_interaction') else 'Nein'}")
    md.append(f"- **Erzeugung synthetischer Inhalte:** {'Ja' if transp.get('synthetic_content') else 'Nein'}")
    gen_mode = transp.get("content_generation_mode")
    if gen_mode == "extracts_only":
        md.append("  - *Hinweis: Reine Datenextraktion ohne semantische Veränderung (Ausnahme Art. 50 Abs. 2 KI-VO)*")
    elif gen_mode == "generates":
        md.append("  - *System erzeugt eigenständig formulierte Inhalte (Kennzeichnungspflicht Art. 50 Abs. 2)*")
    md.append(f"- **Emotionserkennung:** {'Ja' if transp.get('emotion_recognition') else 'Nein'}")
    md.append(f"- **Biometrische Kategorisierung:** {'Ja' if transp.get('biometric_categorization') else 'Nein'}")
    md.append(f"- **Erzeugung von Deepfakes:** {'Ja' if transp.get('deepfake') else 'Nein'}")
    md.append(f"- **KI-generierte Texte oeffentliches Interesse:** {'Ja' if transp.get('public_interest_text') else 'Nein'}")
    md.append(f"- **Transparenzpflichten anwendbar:** {'Ja' if transp.get('any_applies') else 'Nein'}")
    md.append("")

    md.append("### General Purpose AI (GPAI)")
    md.append(f"- **Basiert auf GPAI-Modell (Art. 3 Nr. 63):** {'Ja' if gpai.get('is_gpai') else 'Nein'}")
    if gpai.get("is_gpai"):
        is_sys = gpai.get("is_gpai_system")
        sys_status = "Ja (Zweckoffenes System / Freitext)" if is_sys is True else ("Nein (Auf spezifischen Zweck verengt)" if is_sys is False else "N/A")
        md.append(f"- **Einstufung als GPAI-System (Art. 3 Nr. 66):** {sys_status}")
        md.append(f"- **Systemisches Risiko:** {'Ja' if gpai.get('systemic_risk') else 'Nein'}")
        md.append(f"- **Trainingsrechenleistung > 10^25 FLOPs:** {'Ja' if gpai.get('flops_above_threshold') else 'Nein/Unbekannt'}")
    md.append("")

    md.append("### Betriebsmerkmale & Human-in-the-Loop")
    md.append(f"- **Autonomiegrad:** {clf.get('autonomy_level', 'N/A').upper()}")
    md.append(f"- **Entscheidungswirkung:** {clf.get('decision_impact', 'N/A').upper()}")
    md.append("")

    md.append("## 6. Pflichtenkatalog (Pflichtenmatrix)")
    obligations = get_obligations(risk_cat, roles, gpai, transp)
    
    if obligations:
        md.append("| Pflicht | Rechtsgrundlage | Adressat | Beschreibung |")
        md.append("| --- | --- | --- | --- |")
        for obl in obligations:
            md.append(f"| **{obl['title']}** | {obl['citation']} | {obl['addressee']} | {obl['description']} |")
    else:
        md.append("Keine spezifischen Pflichten für diese Einstufung identifiziert.")
    md.append("")

    md.append("## 7. Rechte und Ansprüche gegenüber Dritten")
    rights = get_rights(roles, gpai, risk_cat)
    
    if rights:
        md.append("| Anspruch / Recht | Rechtsgrundlage | Gerichtet gegen | Beschreibung |")
        md.append("| --- | --- | --- | --- |")
        for r in rights:
            md.append(f"| **{r['title']}** | {r['citation']} | {r['against']} | {r['description']} |")
    else:
        md.append("Keine spezifischen Rechte gegenüber Dritten für diese Einstufung identifiziert.")
    md.append("")

    md.append("---")
    md.append("*Erstellt mit dem KI-VO Compliance Classifier.*")
    
    return "\n".join(md)
