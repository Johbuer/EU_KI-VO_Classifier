import streamlit as st
from src.components import step_header, nav_buttons, yes_no_buttons, question_header, question_details
from src.state import get_value, update_data, set_current_step, get_current_substep, set_current_substep, get_data
from src.data.legal_texts import ART51_GPAI, ART3_DEFINITIONS
from src.data.info_texts import GPAI_INFO


def render_step():
    data = get_data()
    components = data.get("layer2_components", [])
    has_llm = any(c.get("type") == "llm" for c in components)
    
    substep = get_current_substep()
    
    if has_llm and substep == 0:
        substep = 1
        set_current_substep(1)
        
    if substep < 0 or substep > 2:
        substep = 0
        set_current_substep(0)

    step_header(
        title="Art. 51 ff. KI-VO: GPAI-Modelle",
        subtitle=f"GPAI-Prüfung - Schritt {substep + 1} von 3",
        step_num=6,
        total_steps=10
    )

    can_proceed = True

    if substep == 0:
        def handle_click_0(val):
            if val is False:
                update_data("classification.gpai.systemic_risk", False)
                update_data("classification.gpai.flops_above_threshold", False)
                set_current_step(7)
            else:
                set_current_substep(1)

        gpai_def = ART3_DEFINITIONS["gpai_modell"]
        question_header(
            question_text="Basiert das KI-System auf einem KI-Modell mit allgemeinem Verwendungszweck (General Purpose AI / GPAI)?",
            citation=gpai_def["citation"]
        )
        val = yes_no_buttons("classification.gpai.is_gpai", key_suffix="is_gpai", on_click_callback=handle_click_0)
        can_proceed = val is not None
        if not can_proceed:
            st.warning("Bitte wählen Sie JA oder NEIN aus, um fortzufahren.")

        st.markdown("---")
        question_details(
            legal_text=gpai_def["text"],
            plain_info=GPAI_INFO,
            intro=gpai_def.get("intro")
        )

    elif substep == 1:
        def handle_click_1(val):
            set_current_substep(2)

        sys_def = ART51_GPAI["classification"]
        question_header(
            question_text="Birgt das genutzte GPAI-Modell ein systemisches Risiko?",
            citation=sys_def["citation"]
        )
        val = yes_no_buttons("classification.gpai.systemic_risk", key_suffix="systemic_risk", on_click_callback=handle_click_1)
        can_proceed = val is not None
        if not can_proceed:
            st.warning("Bitte wählen Sie JA oder NEIN aus, um fortzufahren.")

        st.markdown("---")
        question_details(
            legal_text=sys_def["legal_text"],
            plain_info="Ein systemisches Risiko liegt vor, wenn das Modell über sehr hohe Leistungsfähigkeiten verfügt, die weitreichende negative Auswirkungen auf den EU-Markt haben können.",
            intro=sys_def.get("intro")
        )

    elif substep == 2:
        def handle_click_2(val):
            if val is True:
                update_data("classification.gpai.systemic_risk", True)
            set_current_step(7)

        flops_def = ART51_GPAI["flops_threshold"]
        question_header(
            question_text="Wurde das GPAI-Modell mit einer kumulierten Rechenleistung von mehr als 10^25 FLOPs trainiert?",
            citation=flops_def["citation"]
        )
        val = yes_no_buttons("classification.gpai.flops_above_threshold", key_suffix="flops", on_click_callback=handle_click_2)
        can_proceed = val is not None
        if not can_proceed:
            st.warning("Bitte wählen Sie JA oder NEIN aus, um fortzufahren.")

        st.markdown("---")
        question_details(
            legal_text=flops_def["legal_text"],
            plain_info=flops_def["plain_info"],
            intro=flops_def.get("intro")
        )

    st.markdown("---")

    action = nav_buttons(6, 10, can_proceed=can_proceed, show_next=False)
    if action == "next":
        is_gpai = get_value("classification.gpai.is_gpai")
        
        if substep == 0:
            if is_gpai is False:
                update_data("classification.gpai.systemic_risk", False)
                update_data("classification.gpai.flops_above_threshold", False)
                set_current_step(7)
            else:
                set_current_substep(1)
        elif substep == 1:
            set_current_substep(2)
        elif substep == 2:
            flops = get_value("classification.gpai.flops_above_threshold")
            if flops is True:
                update_data("classification.gpai.systemic_risk", True)
            set_current_step(7)
        st.rerun()
        
    elif action == "back":
        if substep == 2:
            set_current_substep(1)
        elif substep == 1:
            if has_llm:
                set_current_step(5)
                set_current_substep(5)
            else:
                set_current_substep(0)
        else:
            set_current_step(5)
            set_current_substep(5)
        st.rerun()
