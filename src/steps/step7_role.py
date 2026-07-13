import streamlit as st
from src.components import step_header, question_header, question_details, info_box, warning_box, nav_buttons, yes_no_buttons
from src.state import get_value, update_data, set_current_step, get_current_substep, set_current_substep, get_data
from src.data.legal_texts import ART3_DEFINITIONS, ART25_ROLE_SHIFT
from src.data.info_texts import ROLE_INFO
from src.logic.classifier_engine import eval_role_shift


def get_role_questions():
    return [
        {
            "key": "provider",
            "title": "Rolle: Anbieter",
            "question": "Sind Sie der Anbieter des KI-Systems?",
            "citation": ART3_DEFINITIONS["anbieter"]["citation"],
            "legal_text": ART3_DEFINITIONS["anbieter"]["text"],
            "info": ROLE_INFO["anbieter"],
            "intro": ART3_DEFINITIONS["anbieter"].get("intro")
        },
        {
            "key": "deployer",
            "title": "Rolle: Betreiber",
            "question": "Sind Sie der Betreiber des KI-Systems?",
            "citation": ART3_DEFINITIONS["betreiber"]["citation"],
            "legal_text": ART3_DEFINITIONS["betreiber"]["text"],
            "info": ROLE_INFO["betreiber"],
            "intro": ART3_DEFINITIONS["betreiber"].get("intro")
        },
        {
            "key": "importer",
            "title": "Rolle: Einführer",
            "question": "Sind Sie der Einführer des KI-Systems?",
            "citation": ART3_DEFINITIONS["einfuehrer"]["citation"],
            "legal_text": ART3_DEFINITIONS["einfuehrer"]["text"],
            "info": ROLE_INFO["einfuehrer"],
            "intro": ART3_DEFINITIONS["einfuehrer"].get("intro")
        },
        {
            "key": "distributor",
            "title": "Rolle: Händler",
            "question": "Sind Sie der Händler des KI-Systems?",
            "citation": ART3_DEFINITIONS["haendler"]["citation"],
            "legal_text": ART3_DEFINITIONS["haendler"]["text"],
            "info": ROLE_INFO["haendler"],
            "intro": ART3_DEFINITIONS["haendler"].get("intro")
        },
        {
            "key": "downstream_provider",
            "title": "Rolle: Nachgelagerter Anbieter",
            "question": "Sind Sie ein nachgelagerter Anbieter, weil Sie ein externes GPAI-Modell in Ihr System integrieren?",
            "citation": ART3_DEFINITIONS["nachgelagerter_anbieter"]["citation"],
            "legal_text": ART3_DEFINITIONS["nachgelagerter_anbieter"]["text"],
            "info": ROLE_INFO["nachgelagerter_anbieter"],
            "intro": ART3_DEFINITIONS["nachgelagerter_anbieter"].get("intro")
        }
    ]


def render_step():
    questions = get_role_questions()
    substep = get_current_substep()
    total_substeps = len(questions) + 1

    if substep < 0 or substep >= total_substeps:
        substep = 0
        set_current_substep(0)

    data = get_data()

    if substep < len(questions):
        q = questions[substep]
        key = q["key"]
        
        step_header(
            title=q["title"],
            subtitle=f"Manuelle Rollenbestimmung - Schritt {substep + 1} von {total_substeps}",
            step_num=7,
            total_steps=10
        )
        
        question_header(
            question_text=q["question"],
            citation=q["citation"]
        )
        
        def handle_click(val):
            set_current_substep(substep + 1)

        val = yes_no_buttons(f"classification.role.{key}", key_suffix=key, on_click_callback=handle_click)
        can_proceed = val is not None
        if not can_proceed:
            st.warning("Bitte wählen Sie JA oder NEIN aus, um fortzufahren.")

        st.markdown("---")

        question_details(
            legal_text=q["legal_text"],
            plain_info=q["info"],
            intro=q.get("intro")
        )

        st.markdown("---")
            
        action = nav_buttons(7, 10, can_proceed=can_proceed, show_next=False)
        if action == "next":
            set_current_substep(substep + 1)
            st.rerun()
        elif action == "back":
            if substep > 0:
                prev_substep = substep - 1
                set_current_substep(prev_substep)
            else:
                set_current_step(6)
                is_gpai = get_value("classification.gpai.is_gpai")
                if is_gpai is True:
                    set_current_substep(2)
                else:
                    set_current_substep(0)
            st.rerun()

            
    else:
        step_header(
            title="System-Rollenbewertung",
            subtitle=f"Rechtliche Bewertung des Pflichtenübergangs - Schritt {total_substeps} von {total_substeps}",
            step_num=7,
            total_steps=10
        )
        
        eval_role_shift(data)

        shift_provider = get_value("classification.role.provider_by_art25", False)
        shift_reason = get_value("classification.role.provider_by_art25_reason", "")
        self_use_provider = get_value("classification.role.provider_by_self_use", False)
        auto_downstream = get_value("classification.role.downstream_provider", False)

        any_shift = False

        if self_use_provider:
            st.info(
                "**Automatische Anbieter-Einstufung durch Inbetriebnahme zum Eigengebrauch:**\n\n"
                "Da es sich bei dem System um eine **Eigenentwicklung** handelt, gelten Sie rechtlich als **Anbieter** "
                "(Art. 3 Nr. 3 i.V.m. Nr. 11 KI-VO). Das System hat dieses Flag automatisch auf JA gesetzt."
            )
            update_data("classification.role.provider", True)
            any_shift = True

        if shift_provider:
            warning_box(
                f"**WARNUNG: Automatische Rollenverschiebung nach Art. 25 Abs. 1 KI-VO erkannt!**\n\n"
                f"**Grund:** {shift_reason}\n\n"
                f"**Konsequenz:** Sie gelten rechtlich als **Anbieter** des Hochrisiko-KI-Systems. "
                f"Sie übernehmen damit alle gesetzlichen Pflichten des Original-Anbieters (z.B. Risiko- und Qualitätsmanagement, CE-Kennzeichnung)."
            )
            update_data("classification.role.provider", True)
            any_shift = True
            
            st.markdown("**Auszug aus Art. 25 Abs. 1 lit. c KI-VO:**")
            st.markdown(f"*{ART25_ROLE_SHIFT['abs1_conditions'][2]['text']}*")
            info_box(ART25_ROLE_SHIFT["abs1_conditions"][2]["plain_info"])

        if auto_downstream:
            st.info(
                "**Automatische Einstufung als nachgelagerter Anbieter:**\n\n"
                "Da das System auf einem externen GPAI-Modell basiert, gelten Sie als **nachgelagerter Anbieter**. "
                "Sie erhalten dadurch gesetzliche Auskunftsansprüche gegenüber dem GPAI-Anbieter (Art. 53 Abs. 1 lit. b)."
            )
            update_data("classification.role.downstream_provider", True)
            any_shift = True

        if not any_shift:
            st.success("Keine automatischen Rollenverschiebungen oder Sonderrollen erkannt.")

        st.markdown("### Ihre finalen Rollen:")
        roles = get_value("classification.role", {})
        role_list = []
        if roles.get("provider"): role_list.append("Anbieter")
        if roles.get("deployer"): role_list.append("Betreiber")
        if roles.get("importer"): role_list.append("Einführer")
        if roles.get("distributor"): role_list.append("Händler")
        if roles.get("downstream_provider"): role_list.append("Nachgelagerter Anbieter")
        
        st.markdown("\n".join(f"- **{r}**" for r in role_list) if role_list else "Keine Rollen festgelegt.")

        st.markdown("---")

        can_proceed = len(role_list) > 0
        if not can_proceed:
            st.warning("Bitte wählen Sie in den vorherigen Schritten mindestens eine Rolle aus.")

        action = nav_buttons(7, 10, can_proceed=can_proceed, show_next=True)
        if action == "next":
            set_current_step(8)
            st.rerun()
        elif action == "back":
            set_current_substep(len(questions) - 1)
            st.rerun()
