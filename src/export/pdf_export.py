import logging
from datetime import datetime, timezone
from fpdf import FPDF
from src.state import get_data
from src.logic.classifier_engine import run_eval
from src.logic.obligations import get_obligations, get_rights

logger = logging.getLogger(__name__)


class ComplianceReportPDF(FPDF):
    def header(self):
        self.set_font("Times", "B", 10)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "KI-VO Compliance Report", border=0, ln=1, align="L")
        self.ln(2)
        self.set_draw_color(220, 220, 220)
        self.line(10, 18, 200, 18)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Seite {self.page_no()}/{{nb}}", 0, 0, "C")


def generate_pdf(data=None):
    if data is None:
        data = get_data()

    risk_cat = run_eval(data)
    
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

    pdf = ComplianceReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Times", "B", 20)
    pdf.set_text_color(0, 0, 0)
    sys_name = app.get('system_name', 'Unbenannt')
    pdf.cell(0, 12, f"{sys_name}: Klassifizierungsreport", ln=1, align="L")
    pdf.set_font("Times", "I", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, "Compliance-Klassifizierung nach der KI-Verordnung (EU) 2024/1689", ln=1, align="L")
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 4,
        "Hinweis: Dieses Dokument wurde mit einem Legal-Tech-Prototyp erstellt, der primär die technische "
        "Umsetzung der regulatorischen Klassifizierungslogik demonstriert. Dieses Tool ersetzt keine Rechtsberatung."
    )
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, f"Generiert am: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} | Sitzungs-ID: {data.get('metadata', {}).get('session_id', 'N/A')}", ln=1)
    pdf.ln(4)

    metadata_lines = []
    
    resp = app.get('responsible_person')
    if resp:
        metadata_lines.append(f"Verantwortlicher: {resp}")
        
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
    if status_val in status_label_map:
        status_text = status_label_map[status_val]
        dev_val = app.get("development_status")
        if status_val == "in_development" and dev_val in dev_status_label_map:
            status_text += f" ({dev_status_label_map[dev_val]})"
        metadata_lines.append(f"Betriebsstatus: {status_text}")
        
    metadata_lines.append(f"Regulatorische Risikoklasse: {risk_text}")
    
    active_roles = []
    role_translations = {
        "provider": "Anbieter",
        "deployer": "Betreiber",
        "importer": "Einführer",
        "distributor": "Händler",
        "downstream_provider": "Nachgelagerter Anbieter"
    }
    for r_key, r_label in role_translations.items():
        if roles.get(r_key):
            active_roles.append(r_label)
    if roles.get("provider_by_art25"):
        active_roles.append("Anbieter (Art. 25)")
    if roles.get("provider_by_self_use"):
        active_roles.append("Anbieter (Eigengebrauch)")
        
    if active_roles:
        metadata_lines.append(f"Ermittelte Rollen: {', '.join(active_roles)}")
        
    box_height = 14 + len(metadata_lines) * 6
    
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(210, 210, 210)
    rect_y = pdf.get_y()
    pdf.rect(10, rect_y, 190, box_height, style="FD")
    
    pdf.set_font("Times", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(14, rect_y + 4)
    system_name = app.get('system_name', 'Unbenannt')
    version = app.get('system_version')
    sys_title = f"KI-System: {system_name}"
    if version:
        sys_title += f" (Version {version})"
    pdf.cell(0, 6, sys_title, ln=1)
    
    for line in metadata_lines:
        pdf.set_x(14)
        if "Regulatorische Risikoklasse:" in line:
            pdf.set_font("Times", "B", 10.5)
            if risk_cat == "prohibited":
                pdf.set_text_color(200, 0, 0)
            elif risk_cat == "high_risk":
                pdf.set_text_color(210, 90, 0)
            elif risk_cat == "limited_risk":
                pdf.set_text_color(160, 120, 0)
            elif risk_cat == "minimal_risk":
                pdf.set_text_color(0, 120, 50)
            else:
                pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 6, line, ln=1)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(80, 80, 80)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 6, line, ln=1)
            
    pdf.set_y(rect_y + box_height + 4)

    def print_section_heading(title):
        pdf.ln(4)
        pdf.set_font("Times", "B", 13)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, title, ln=1)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

    print_section_heading("1. Systembeschreibung")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    
    start_y = pdf.get_y()
    
    fields = []
    if app.get('purpose'):
        fields.append(("Zweck und Einsatzbereich", app.get('purpose')))
    if app.get('working_description'):
        fields.append(("Arbeitsweise", app.get('working_description')))
    if app.get('contribution_explanation'):
        fields.append(("Beitrag zur Zweckerreichung", app.get('contribution_explanation')))
    if app.get('interfaces'):
        fields.append(("Schnittstellen", app.get('interfaces')))
        
    if app.get('personal_data_processed'):
        p_categories = app.get('personal_data_categories')
        p_text = f"Ja (Kategorien: {p_categories})" if p_categories else "Ja"
    else:
        p_text = "Nein"
    fields.append(("Personenbezogene Daten", p_text))
    
    s_system = "Eigenentwicklung" if app.get('sourcing_system') == 'inhouse' else ("Extern beschafft" if app.get('sourcing_system') == 'extern' else "N/A")
    if app.get('sourcing_system') == 'extern' and app.get('developer_system'):
        s_system += f" (Hersteller: {app.get('developer_system')})"
    fields.append(("Sourcing System", s_system))

    for label, val in fields:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, f"{label}:", ln=1)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.multi_cell(0, 5, str(val))
        pdf.ln(3)

    print_section_heading("2. Modellkomponenten")
    if components:
        pdf.set_font("Helvetica", "B", 9)
        with pdf.table(col_widths=(35, 25, 30, 30, 20, 50), text_align="LEFT", v_align="TOP") as table:
            header_row = table.row()
            header_row.cell("Name")
            header_row.cell("Typ")
            header_row.cell("Sourcing")
            header_row.cell("Anbieter")
            header_row.cell("Version")
            header_row.cell("Datenquellen")
            
            pdf.set_font("Helvetica", "", 9)
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
                
                sourcing_label = {
                    "extern_sourcing": "Extern beschafft",
                    "inhouse_sourcing": "Selbst trainiert",
                    "extern_adapted": "Extern & nachtrainiert"
                }.get(comp.get("sourcing"), "N/A")
                
                row = table.row()
                row.cell(comp.get("name", "Unbenannt"))
                row.cell(c_type)
                row.cell(sourcing_label)
                row.cell(comp.get("provider", "N/A") or "-")
                row.cell(comp.get("version", "N/A") or "-")
                row.cell(comp.get("data_sources", "N/A") or "-")
    else:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Keine spezifischen Modellkomponenten erfasst.", ln=1)

    print_section_heading("3. Infrastruktur & Enabler-Plattform")
    pdf.set_font("Helvetica", "", 10)
    if infra.get("platform_used"):
        p_type_map = {"cloud": "Public Cloud", "on_premise": "On-Premise", "hybrid": "Hybrid"}
        p_type = p_type_map.get(infra.get("platform_type"), infra.get("platform_type", "N/A"))
        
        primary = infra.get("primary_platform") or infra.get("platform_name") or ""
        secondary = infra.get("secondary_platform", "")
        
        if not secondary:
            sub_list = infra.get("connected_sub_platforms", [])
            if sub_list:
                secondary = ", ".join(sub_list)
        
        infra_fields = [
            ("Primäre Plattform / UI", primary),
            ("Integrierte Infrastruktur / API-Gateway", secondary),
            ("Betriebsmodell", p_type),
            ("Sicherheitsmaßnahmen (TOMs)", infra.get("ikt_security_notes")),
            ("IKT-Drittparteienrisiko (DORA)", infra.get("third_party_risk_notes")),
            ("Zugriffskontrollen", infra.get("access_controls"))
        ]
        
        for label, val in infra_fields:
            if val and str(val).strip() and str(val).strip() != "N/A":
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 6, f"{label}:", ln=1)
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 6, str(val))
                pdf.ln(1)
    else:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 6, "Basiert auf Enabler-Plattform:", ln=0)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Nein", ln=1)
        pdf.ln(2)

    print_section_heading("4. Rechtliche Bewertung & Risikoeinstufung")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
       
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(60, 6, "Verbotene Praktiken:", ln=0)
    pdf.set_font("Helvetica", "", 10)
    if risk_cat == "prohibited":
        pdf.set_text_color(200, 0, 0)
        prob_details = clf.get("prohibited", {}).get("details", {})
        reasons = [f"{pk}: {pv.get('notes', '')}" for pk, pv in prob_details.items() if pv.get("detected")]
        pdf.multi_cell(130, 6, f"Ja ({', '.join(reasons)})")
        pdf.ln(2)
        pdf.set_text_color(50, 50, 50)
    else:
        pdf.cell(0, 6, "Nein", ln=1)
        pdf.ln(1)
        
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(60, 6, "Hochrisiko-System:", ln=0)
    pdf.set_font("Helvetica", "", 10)
    if risk_cat == "high_risk":
        pdf.set_text_color(210, 90, 0)
        matches = [k for k, v in clf.get("high_risk", {}).get("annex_iii_matches", {}).items() if v]
        hr_desc = "Ja (Anhang III: " + ", ".join(matches) + ")" if matches else "Ja"
        if clf.get("high_risk", {}).get("annex_i_applies"):
            hr_desc += " (Annex I Produktsicherheitskomponente)"
        pdf.multi_cell(130, 6, hr_desc)
        pdf.ln(2)
        pdf.set_text_color(50, 50, 50)
    else:
        pdf.cell(0, 6, "Nein", ln=1)
        pdf.ln(1)
        
    if transp.get("any_applies"):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 6, "Begrenztes Risiko:", ln=0)
        pdf.set_font("Helvetica", "", 10)
        t_flags = []
        if transp.get("direct_interaction"): t_flags.append("Direkte Interaktion (Art. 50 Abs. 1)")
        if transp.get("synthetic_content"): t_flags.append("Synthetische Inhalte (Art. 50 Abs. 2)")
        if transp.get("emotion_recognition"): t_flags.append("Emotionserkennung (Art. 50 Abs. 3)")
        if transp.get("biometric_categorization"): t_flags.append("Biometrische Kategorisierung (Art. 50 Abs. 3)")
        if transp.get("deepfake"): t_flags.append("Deepfake (Art. 50 Abs. 4)")
        if transp.get("public_interest_text"): t_flags.append("Öffentliche Texte (Art. 50 Abs. 4)")
        pdf.multi_cell(130, 6, f"Ja, Transparenzpflichten ({', '.join(t_flags)})")
        pdf.ln(2)
        
    if gpai.get("is_gpai"):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 6, "GPAI-Modell (Art. 3 Nr. 63):", ln=0)
        pdf.set_font("Helvetica", "", 10)
        g_text = f"Ja ({gpai.get('model_name', 'N/A')})"
        if gpai.get("systemic_risk"):
            g_text += " - MIT SYSTEMISCHEM RISIKO"
        pdf.multi_cell(130, 6, g_text)
        pdf.ln(1)

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 6, "GPAI-System (Art. 3 Nr. 66 / EG 85):", ln=0)
        pdf.set_font("Helvetica", "", 10)
        if gpai.get("is_gpai_system") is True:
            sys_text = "Ja (Zweckoffenes System / Freitext)"
        elif gpai.get("is_gpai_system") is False:
            sys_text = "Nein (Narrow AI / Auf spezifischen Zweck verengt)"
        else:
            sys_text = "N/A"
        pdf.multi_cell(130, 6, sys_text)
        pdf.ln(2)
        
    aut = clf.get('autonomy_level')
    imp = clf.get('decision_impact')
    if aut and aut != "N/A":
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 6, "Betriebsautonomie / Aufsicht:", ln=0)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Autonomie: {str(aut).upper()} / Wirkung: {str(imp or 'N/A').upper()}", ln=1)
        pdf.ln(1)
        
    pdf.ln(2)

    print_section_heading("5. Gesetzlicher Pflichtenkatalog (Pflichtenmatrix)")
    obligations = get_obligations(risk_cat, roles, gpai, transp)
    
    if obligations:
        pdf.set_font("Helvetica", "B", 9)
        with pdf.table(col_widths=(45, 30, 30, 85), text_align="LEFT", v_align="TOP") as table:
            header_row = table.row()
            header_row.cell("Pflicht")
            header_row.cell("Rechtsgrundlage")
            header_row.cell("Adressat")
            header_row.cell("Beschreibung")
            
            pdf.set_font("Helvetica", "", 9)
            for obl in obligations:
                row = table.row()
                row.cell(obl["title"])
                row.cell(obl["citation"])
                row.cell(obl["addressee"])
                row.cell(obl["description"])
    else:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Keine spezifischen Pflichten für diese Einstufung identifiziert.", ln=1)

    pdf.ln(6)
    print_section_heading("6. Rechte und Ansprüche gegenüber Dritten")
    rights = get_rights(roles, gpai, risk_cat)
    
    if rights:
        pdf.set_font("Helvetica", "B", 9)
        with pdf.table(col_widths=(45, 30, 35, 80), text_align="LEFT", v_align="TOP") as table:
            header_row = table.row()
            header_row.cell("Anspruch / Recht")
            header_row.cell("Rechtsgrundlage")
            header_row.cell("Gegenüber")
            header_row.cell("Beschreibung")
            
            pdf.set_font("Helvetica", "", 9)
            for r in rights:
                row = table.row()
                row.cell(r["title"])
                row.cell(r["citation"])
                row.cell(r["against"])
                row.cell(r["description"])
    else:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Keine spezifischen Rechte gegenüber Dritten für diese Einstufung identifiziert.", ln=1)

    try:
        pdf_bytes = pdf.output(dest='S')
        return bytes(pdf_bytes) if pdf_bytes else None
    except Exception as exc:
        logger.error("Failed to generate PDF: %s", exc)
        return None
