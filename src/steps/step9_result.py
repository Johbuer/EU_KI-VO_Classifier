import streamlit as st
from src.components import step_header, risk_badge, info_box, warning_box, nav_buttons
from src.state import get_value, update_data, set_current_step, get_current_substep, set_current_substep, get_data
from src.logic.classifier_engine import run_eval
from src.logic.obligations import get_obligations, get_rights
from src.export.json_export import generate_json
from src.export.markdown_export import generate_markdown
from src.export.pdf_export import generate_pdf
from src.data.legal_texts import ART5_PROHIBITED


def render_step():
    step_header(
        title="Ergebnis-Dashboard & Compliance-Bericht",
        subtitle="Übersicht über die Risikoeinstufung, rechtliche Pflichten und Rechte nach KI-VO",
        step_num=9,
        total_steps=10
    )

    data = get_data()
    risk_cat = run_eval(data)
    
    app = data.get("layer3_application", {})
    clf = data.get("classification", {})
    roles = clf.get("role", {})
    gpai = clf.get("gpai", {})
    transp = clf.get("transparency", {})

    risk_badge(risk_cat)

    st.subheader("1. Zusammenfassung")
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
        "mvp": "Minimum Viable Product (MVP)"
    }
    status_text = "N/A"
    if status_val in status_label_map:
        status_text = status_label_map[status_val]
        dev_val = app.get("development_status")
        if status_val == "in_development" and dev_val in dev_status_label_map:
            status_text += f" ({dev_status_label_map[dev_val]})"

    st.markdown(f"""
    **KI-System:** {app.get('system_name', 'Unbenannt')} (Version {app.get('system_version', 'N/A')})  
    **Verantwortlicher:** {app.get('responsible_person', 'N/A')}  
    **Betriebsstatus:** {status_text}  
    """)

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
        active_roles.append("Anbieter durch Pflichtenübertrag (Art. 25)")
    if roles.get("provider_by_self_use"):
        active_roles.append("Anbieter durch Inbetriebnahme zum Eigengebrauch")
        
    st.markdown(f"**Ermittelte Rollen:** {', '.join(active_roles) if active_roles else 'Keine Rolle ermittelt'}")

    if gpai.get("is_gpai"):
        gpai_type = "systemischem Risiko" if gpai.get("systemic_risk") else "Standard"
        st.markdown(f"**GPAI-Status:** Basiert auf GPAI-Modell ({gpai_type})")

    st.markdown("---")

    st.subheader("2. Gesetzlicher Pflichtenkatalog (Pflichtenmatrix)")
    
    if risk_cat == "not_ai":
        st.success(
            "Das System wurde als **kein KI-System i.S.d. KI-VO** klassifiziert. "
            "Es fallen keine Pflichten nach der EU-KI-Verordnung an. Die allgemeinen Bestimmungen "
            "(z.B. DSGVO bei personenbezogenen Daten, Produkthaftungsrecht) gelten unberührt."
        )
    elif risk_cat == "prohibited":
        warning_box(
            "### SYSTEM IN DER EU VERBOTEN\n\n"
            "Es liegt ein verstoß gegen Art. 5 KI-VO vor. Das System darf in der EU NICHT in Verkehr gebracht, "
            "in Betrieb genommen oder betrieben werden. Bereits aktive Systeme müssen unverzüglich "
            "außer Betrieb genommen werden!"
        )
    else:
        obligations = get_obligations(risk_cat, roles, gpai, transp)
        if obligations:
            st.markdown(
                "Nachfolgend finden Sie die gesetzlichen Pflichten, die Sie als **" + 
                ", ".join(active_roles) + "** für ein **" + risk_cat.upper().replace("_", " ") + "**-System erfüllen müssen:"
            )
            for obl in obligations:
                obl_html = f"""
                <div class="obligation-card">
                    <h4 style="font-family: 'Playfair Display', Georgia, 'Times New Roman', serif; font-size:1.2rem; font-weight:bold; margin-bottom: 6px;">
                        {obl['title']} <span class="legal-badge">{obl['citation']}</span>
                    </h4>
                    <p style="font-size:0.85rem;color:#555555;margin-bottom:8px;"><b>Adressat:</b> {obl['addressee']}</p>
                    <p style="font-size:0.95rem;line-height:1.5;color:#222222;">{obl['description']}</p>
                </div>
                """
                st.markdown(obl_html, unsafe_allow_html=True)
        else:
            st.info("Für diese Konstellation wurden keine spezifischen Pflichten nach KI-VO ermittelt.")

    st.markdown("---")

    st.subheader("3. Rechte und Ansprüche gegenüber Dritten")
    rights = get_rights(roles, gpai, risk_cat)
    
    if rights and risk_cat != "not_ai" and risk_cat != "prohibited":
        st.markdown(
            "Als **" + ", ".join(active_roles) + "** haben Sie folgende gesetzliche Rechte "
            "und Ansprüche gegenüber Ihren Zulieferern und Drittanbietern:"
        )
        for r in rights:
            r_html = f"""
            <div class="obligation-card" style="border-left: 3px solid #111111;">
                <h4 style="font-family: 'Playfair Display', Georgia, 'Times New Roman', serif; font-size:1.2rem; font-weight:bold; margin-bottom: 6px;">
                    {r['title']} <span class="legal-badge">{r['citation']}</span>
                </h4>
                <p style="font-size:0.85rem;color:#555555;margin-bottom:8px;"><b>Gerichtet gegen:</b> {r['against']}</p>
                <p style="font-size:0.95rem;line-height:1.5;color:#222222;">{r['description']}</p>
            </div>
            """
            st.markdown(r_html, unsafe_allow_html=True)
    else:
        st.info("Keine spezifischen Rechte oder Ansprüche gegenüber Dritten identifiziert.")

    st.markdown("---")

    st.subheader("4. Compliance-Bericht exportieren")
    st.markdown("Laden Sie den vollständigen Bericht als PDF, Markdown oder im JSON-Format für Ihre Akten herunter.")

    col_ex1, col_ex2, col_ex3 = st.columns(3)
    
    with col_ex1:
        import re
        pdf_data = generate_pdf(data)
        if pdf_data:
            sys_name = data.get("layer3_application", {}).get("system_name", "").strip()
            if sys_name:
                clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', sys_name)
                clean_name = clean_name[:64]
            else:
                clean_name = "klassifizierungsreport"
            
            st.download_button(
                label="PDF herunterladen",
                data=pdf_data,
                file_name=f"{clean_name}_klassifizierungsreport.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        else:
            st.error("Fehler bei PDF-Generierung")

    with col_ex2:
        md_data = generate_markdown(data)
        st.download_button(
            label="Markdown herunterladen",
            data=md_data,
            file_name="klassifizierungsreport.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col_ex3:
        json_data = generate_json()
        st.download_button(
            label="JSON exportieren (API/Import)",
            data=json_data,
            file_name="kivo_classifier_daten.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("---")

    back_step = 8
    back_substep = 1
    
    if clf.get("is_ai_system") is False:
        back_step = 2
        back_substep = 0
    elif clf.get("prohibited", {}).get("detected") is True:
        back_step = 3
        details = clf.get("prohibited", {}).get("details", {})
        for idx, practice in enumerate(ART5_PROHIBITED):
            if details.get(practice["key"], {}).get("detected") is True:
                back_substep = idx
                break

    cols = st.columns([1, 1, 1])
    with cols[0]:
        if st.button("Zurück", key="nav_back_9", use_container_width=True):
            if back_step == 2:
                update_data("classification.is_ai_system", None)
            elif back_step == 3:
                key = ART5_PROHIBITED[back_substep]["key"]
                update_data(f"classification.prohibited.details.{key}.detected", None)
                update_data(f"classification.prohibited.details.{key}.notes", "")
            elif back_step == 8:
                update_data("classification.decision_impact", None)
                
            set_current_step(back_step)
            set_current_substep(back_substep)
            st.rerun()

    with cols[2]:
        if st.button("Neue Klassifizierung", key="nav_reset_9", use_container_width=True, type="secondary"):
            if "classifier_data" in st.session_state:
                del st.session_state.classifier_data
            set_current_step(0)
            st.rerun()
