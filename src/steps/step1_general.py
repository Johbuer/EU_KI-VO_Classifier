import streamlit as st
from src.components import step_header, info_box, nav_buttons
from src.state import get_value, update_data, add_component, remove_component, get_data, set_current_step
from src.data.info_texts import GENERAL_INFO


def add_comp_cb():
    name = st.session_state.get("new_comp_name", "").strip()
    comp_type = st.session_state.get("new_comp_type")
    sourcing = st.session_state.get("new_comp_sourcing")
    license_type = st.session_state.get("new_comp_license")
    provider = st.session_state.get("new_comp_provider", "")
    version = st.session_state.get("new_comp_version", "")
    data_sources = st.session_state.get("new_comp_datasources", "")

    if not name or not comp_type or not sourcing:
        st.session_state["add_comp_error"] = "Name, Typ und Sourcing der Komponente sind Pflichtfelder."
        return

    add_component(
        name=name,
        comp_type=comp_type,
        license_type=license_type,
        provider=provider,
        version=version,
        data_sources=data_sources,
        sourcing=sourcing
    )
    if comp_type == "llm":
        update_data("classification.gpai.is_gpai", True)

    st.session_state["new_comp_name"] = ""
    st.session_state["new_comp_type"] = None
    st.session_state["new_comp_sourcing"] = None
    st.session_state["new_comp_license"] = None
    st.session_state["new_comp_provider"] = ""
    st.session_state["new_comp_version"] = ""
    st.session_state["new_comp_datasources"] = ""
    if "add_comp_error" in st.session_state:
        del st.session_state["add_comp_error"]


def render_step():
    step_header(
        title="Stammdaten & Relationales Deployment",
        subtitle="Erfassung der Systemarchitektur und allgemeinen Angaben (3-Layer-Modell)",
        step_num=1,
        total_steps=10
    )

    data = get_data()

    st.subheader("Layer 3: Anwendung & Stammdaten")
    
    col1, col2 = st.columns(2)
    with col1:
        system_name = st.text_input(
            "Name des KI-Systems *",
            value=get_value("layer3_application.system_name", ""),
            help="Eindeutiger Name des KI-Systems."
        )
        update_data("layer3_application.system_name", system_name)

        responsible_person = st.text_input(
            "Name des Verantwortlichen *",
            value=get_value("layer3_application.responsible_person", ""),
            help="Zuständige Person für das System."
        )
        update_data("layer3_application.responsible_person", responsible_person)

        sys_val = get_value("layer3_application.sourcing_system", "")
        sys_index = None if sys_val == "" else ["inhouse", "extern"].index(sys_val)
        sourcing_system = st.selectbox(
            "Sourcing KI-System *",
            options=["inhouse", "extern"],
            format_func=lambda x: "Eigenentwicklung" if x == "inhouse" else "Extern beschafft",
            index=sys_index,
            placeholder="Bitte wählen..."
        )
        update_data("layer3_application.sourcing_system", sourcing_system if sourcing_system else "")

        if sourcing_system == "extern":
            developer_system = st.text_input(
                "Hersteller/Entwickler des Systems",
                value=get_value("layer3_application.developer_system", ""),
                help="Welches externe Unternehmen hat das System entwickelt?"
            )
            update_data("layer3_application.developer_system", developer_system)
        else:
            update_data("layer3_application.developer_system", "")

    with col2:
        system_version = st.text_input(
            "Version des KI-Systems",
            value=get_value("layer3_application.system_version", ""),
            help="Aktuelle Versionsnummer oder Entwicklungsstufe."
        )
        update_data("layer3_application.system_version", system_version)

        status_val = get_value("layer3_application.status", "")
        status_options = ["in_operation", "out_of_operation", "testing", "in_development"]
        status_index = None if status_val == "" else status_options.index(status_val)
        status = st.selectbox(
            "Betriebsstatus *",
            options=status_options,
            format_func=lambda x: {
                "in_operation": "In Betrieb",
                "out_of_operation": "Außer Betrieb",
                "testing": "Testphase",
                "in_development": "In Entwicklung"
            }[x],
            index=status_index,
            placeholder="Bitte wählen..."
        )
        update_data("layer3_application.status", status if status else "")

        if status == "in_development":
            dev_status_val = get_value("layer3_application.development_status", "")
            dev_status_options = ["conception", "active_dev", "mvp"]
            dev_status_index = None if dev_status_val == "" else dev_status_options.index(dev_status_val)
            development_status = st.selectbox(
                "Entwicklungsstatus *",
                options=dev_status_options,
                format_func=lambda x: {
                    "conception": "Konzeption",
                    "active_dev": "Aktive Entwicklung",
                    "mvp": "Minimum Viable Product (MVP)"
                }[x],
                index=dev_status_index,
                placeholder="Bitte wählen..."
            )
            update_data("layer3_application.development_status", development_status if development_status else "")
        else:
            update_data("layer3_application.development_status", "")

    st.markdown("**Erklärung zum Sourcing:**")
    info_box(f"**Sourcing System:** {GENERAL_INFO['sourcing_system']}")

    st.markdown("#### Systembeschreibung & Datenfluss")
    purpose = st.text_area(
        "Zweck und Einsatzbereich des KI-Systems",
        value=get_value("layer3_application.purpose", ""),
        placeholder="Z.B. Automatisierte Vorauswahl von Bewerbungen für die HR-Abteilung..."
    )
    update_data("layer3_application.purpose", purpose)
    
    st.markdown("**Erklärung zum Einsatzzweck:**")
    info_box(GENERAL_INFO["purpose"])

    working_description = st.text_area(
        "Arbeitsweise des KI-Systems",
        value=get_value("layer3_application.working_description", ""),
        placeholder="Z.B. Das System analysiert Lebensläufe as PDF, extrahiert Qualifikationen..."
    )
    update_data("layer3_application.working_description", working_description)

    contribution_explanation = st.text_area(
        "Beitrag zur Zweckerreichung",
        value=get_value("layer3_application.contribution_explanation", ""),
        placeholder="Wie trägt das System zur Zweckerreichung bei und was passiert ohne das System?"
    )
    update_data("layer3_application.contribution_explanation", contribution_explanation)

    interfaces = st.text_area(
        "Schnittstellen (APIs, Datenbanken, Vorsysteme)",
        value=get_value("layer3_application.interfaces", ""),
        placeholder="Z.B. REST API zu SAP HR, Datenbankverbindung zu MS SQL Server..."
    )
    update_data("layer3_application.interfaces", interfaces)

    st.markdown("#### Personenbezogene Daten")
    pd_val = get_value("layer3_application.personal_data_processed")
    pd_index = None if pd_val is None else [True, False].index(pd_val)
    personal_data_processed = st.radio(
        "Werden personenbezogene Daten verarbeitet?",
        options=[True, False],
        format_func=lambda x: "Ja" if x is True else "Nein",
        index=pd_index
    )
    update_data("layer3_application.personal_data_processed", personal_data_processed)

    if personal_data_processed is True:
        personal_data_categories = st.text_area(
            "Welche Kategorien personenbezogener Daten werden verarbeitet?",
            value=get_value("layer3_application.personal_data_categories", ""),
            placeholder="Z.B. Name, E-Mail-Adresse, Qualifikationsdaten, Bewerbungsfotos..."
        )
        update_data("layer3_application.personal_data_categories", personal_data_categories)
    else:
        update_data("layer3_application.personal_data_categories", "")

    st.markdown("**Erklärung zu personenbezogenen Daten:**")
    info_box(GENERAL_INFO["personal_data"])

    st.markdown("---")

    st.subheader("Layer 1: Enabler-Plattform / Infrastruktur")
    plat_val = get_value("layer1_infrastructure.platform_used")
    plat_index = None if plat_val is None else [True, False].index(plat_val)
    platform_used = st.radio(
        "Basiert das System auf einer Enabler-Plattform?",
        options=[True, False],
        format_func=lambda x: "Ja" if x is True else "Nein",
        index=plat_index
    )
    update_data("layer1_infrastructure.platform_used", platform_used)

    if platform_used is True:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            platform_name = st.text_input(
                "Primäre Plattform / UI *",
                value=get_value("layer1_infrastructure.primary_platform", get_value("layer1_infrastructure.platform_name", "")),
                placeholder="Z.B. Dataiku, Databricks, Azure AI Studio...",
                help="Die Hauptplattform, über die Anwender direkt arbeiten."
            )
            update_data("layer1_infrastructure.platform_name", platform_name)
            update_data("layer1_infrastructure.primary_platform", platform_name)

            secondary_platform = st.text_input(
                "Integrierte Infrastruktur / API-Gateway (optional)",
                value=get_value("layer1_infrastructure.secondary_platform", ""),
                placeholder="Z.B. AWS Bedrock, Azure OpenAI Service, GCP Vertex AI...",
                help="Falls die primäre Plattform LLMs oder andere Modelle über ein nachgelagertes API-Gateway bezieht."
            )
            update_data("layer1_infrastructure.secondary_platform", secondary_platform)

            p_type_val = get_value("layer1_infrastructure.platform_type", "")
            p_type_index = None if p_type_val == "" else ["cloud", "on_premise", "hybrid"].index(p_type_val)
            platform_type = st.selectbox(
                "Betriebsmodell der Hauptplattform",
                options=["cloud", "on_premise", "hybrid"],
                format_func=lambda x: {
                    "cloud": "Public Cloud",
                    "on_premise": "On-Premise (eigenes RZ)",
                    "hybrid": "Hybrid"
                }[x],
                index=p_type_index,
                placeholder="Bitte wählen..."
            )
            update_data("layer1_infrastructure.platform_type", platform_type if platform_type else "")

        with col_p2:
            ikt_security_notes = st.text_area(
                "Zentrale TOMs & IT-Sicherheitsmaßnahmen der Plattform",
                value=get_value("layer1_infrastructure.ikt_security_notes", ""),
                placeholder="Z.B. Verschlüsselung, IAM-Rollen, Netzwerktrennung..."
            )
            update_data("layer1_infrastructure.ikt_security_notes", ikt_security_notes)

        col_p3, col_p4 = st.columns(2)
        with col_p3:
            third_party_risk_notes = st.text_area(
                "IKT-Drittparteienrisiko (DORA)",
                value=get_value("layer1_infrastructure.third_party_risk_notes", ""),
                placeholder="Details zur Absicherung bei Cloud-Anbietern..."
            )
            update_data("layer1_infrastructure.third_party_risk_notes", third_party_risk_notes)
        with col_p4:
            access_controls = st.text_area(
                "Zugriffskontrollen und Berechtigungen",
                value=get_value("layer1_infrastructure.access_controls", ""),
                placeholder="Wer hat Zugriff auf die Plattform und die Daten?"
            )
            update_data("layer1_infrastructure.access_controls", access_controls)
    else:
        update_data("layer1_infrastructure.platform_name", "")
        update_data("layer1_infrastructure.primary_platform", "")
        update_data("layer1_infrastructure.secondary_platform", "")
        update_data("layer1_infrastructure.platform_type", "")
        update_data("layer1_infrastructure.sub_platform_used", None)
        update_data("layer1_infrastructure.connected_sub_platforms", [])
        update_data("layer1_infrastructure.ikt_security_notes", "")
        update_data("layer1_infrastructure.third_party_risk_notes", "")
        update_data("layer1_infrastructure.access_controls", "")

    st.markdown("**Erklärung zu Enabler-Plattformen:**")
    info_box(GENERAL_INFO["platform"])

    st.markdown("---")

    st.subheader("Layer 2: Modellkomponenten")
    st.markdown("Geben Sie hier die einzelnen Modelle/Komponenten an, die im System verbaut sind.")

    components = get_value("layer2_components", [])

    if components:
        for idx, comp in enumerate(components):
            with st.container():
                st.markdown(f"**Komponente {idx+1}: {comp['name'] or 'Unbenannt'}** ({comp['type'].upper()})")
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    sourcing_label = {
                        "extern_sourcing": "Extern beschafft",
                        "inhouse_sourcing": "Selbst trainiert",
                        "extern_adapted": "Extern beschafft & nachtrainiert"
                    }.get(comp.get("sourcing"), "-")
                    st.write(f"**Sourcing:** {sourcing_label}")
                    st.write(f"**Hersteller:** {comp['provider'] or '-'}")
                with col_c2:
                    st.write(f"**Version:** {comp['version'] or '-'}")
                    st.write(f"**Lizenz:** {comp['license'] or '-'}")
                with col_c3:
                    st.write(f"**Datenquellen:** {comp['data_sources'] or '-'}")
                
                if st.button("Komponente löschen", key=f"del_comp_{comp['id']}"):
                    remove_component(comp['id'])
                    st.rerun()
                st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
    else:
        st.info("Bisher keine Komponenten hinzugefügt. Mindestens eine Komponente wird benötigt.")

    st.markdown("##### Neue Komponente hinzufügen")
    col_nc1, col_nc2 = st.columns(2)
    with col_nc1:
        nc_name = st.text_input("Name der Komponente *", key="new_comp_name", placeholder="Z.B. Qwen-2.5, Llama-3, Eigenes Audiomodell...")
        nc_type = st.selectbox(
            "Typ der Komponente *",
            options=["llm", "gan_diffusion", "random_forest", "rpa", "deterministic", "rag_pipeline", "other"],
            format_func=lambda x: {
                "llm": "Large Language Model (LLM) / Allzweck-KI (GPAI)",
                "gan_diffusion": "Spezialisierte Generative KI (z.B. GAN, Diffusion, Bildgenerierung ohne GPAI-Charakter)",
                "random_forest": "Klassisches ML-Modell (z.B. Random Forest, XGBoost)",
                "rpa": "Robotic Process Automation (RPA)",
                "deterministic": "Deterministisches Regelwerk",
                "rag_pipeline": "RAG-Pipeline",
                "other": "Sonstiges"
            }[x],
            index=None,
            placeholder="Bitte wählen...",
            key="new_comp_type"
        )
        nc_sourcing = st.selectbox(
            "Modell-Sourcing *",
            options=["extern_sourcing", "inhouse_sourcing", "extern_adapted"],
            format_func=lambda x: {
                "extern_sourcing": "Extern beschafft",
                "inhouse_sourcing": "Selbst trainiert",
                "extern_adapted": "Extern beschafft und maßgeblich nachtrainiert"
            }[x],
            index=None,
            placeholder="Bitte wählen...",
            key="new_comp_sourcing"
        )
        
    with col_nc2:
        nc_license = st.selectbox(
            "Lizenztyp",
            options=["open_source", "proprietary"],
            format_func=lambda x: "Open Source" if x == "open_source" else "Proprietär / Kommerziell",
            index=None,
            placeholder="Bitte wählen...",
            key="new_comp_license"
        )
        
        if nc_sourcing in ["extern_sourcing", "extern_adapted"]:
            nc_provider = st.text_input("Modellanbieter / Entwickler (optional)", key="new_comp_provider", placeholder="Z.B. Alibaba, OpenAI, Meta...")
        else:
            nc_provider = ""
            
        nc_version = st.text_input("Version", key="new_comp_version", placeholder="Z.B. v1.2, 2024-05-13...")
        nc_datasources = st.text_input("Datenquellen", key="new_comp_datasources", placeholder="Z.B. Trainingsdaten, externe APIs...")

    if "add_comp_error" in st.session_state:
        st.error(st.session_state["add_comp_error"])

    st.button("Komponente hinzufügen", type="secondary", on_click=add_comp_cb)

    st.markdown("**Erklärung zu Modellkomponenten:**")
    info_box(GENERAL_INFO["components"])

    st.markdown("---")
    st.caption("* Kennzeichnet Pflichtfelder")

    can_proceed = True
    errors = []
    if not system_name:
        errors.append("Name des KI-Systems fehlt.")
        can_proceed = False
    if not responsible_person:
        errors.append("Name des Verantwortlichen fehlt.")
        can_proceed = False
    if not sourcing_system:
        errors.append("Sourcing-Typ des KI-Systems fehlt.")
        can_proceed = False
    if not status:
        errors.append("Betriebsstatus fehlt.")
        can_proceed = False
    if status == "in_development" and not get_value("layer3_application.development_status"):
        errors.append("Entwicklungsstatus fehlt.")
        can_proceed = False
    if not components:
        errors.append("Mindestens eine Modellkomponente muss hinzugefügt werden.")
        can_proceed = False
    if personal_data_processed is None:
        errors.append("Angabe zur Verarbeitung personenbezogener Daten fehlt.")
        can_proceed = False
    if platform_used is None:
        errors.append("Angabe zur Enabler-Plattform fehlt.")
        can_proceed = False

    if errors:
        st.warning("Bitte füllen Sie alle Pflichtfelder aus, um fortzufahren:\n- " + "\n- ".join(errors))

    from src.components import navigate_step
    navigate_step(1, 2, 0, can_proceed=can_proceed)
