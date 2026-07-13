import streamlit as st
from src.components import step_header, question_header, question_details, yes_no_buttons, navigate_step
from src.state import get_value, update_data, set_current_step, get_data
from src.data.legal_texts import ART3_DEFINITIONS
from src.data.info_texts import AI_CHECK_INFO


def render_step():
    step_header(
        title="Vorprüfung: Definition KI-System",
        subtitle="Prüfung, ob das System in den Anwendungsbereich der KI-Verordnung fällt",
        step_num=2,
        total_steps=10
    )

    ki_def = ART3_DEFINITIONS["ki_system"]
    
    question_header(
        question_text="Handelt es sich bei Ihrem System um ein KI-System im Sinne des Art. 3 Nr. 1 KI-VO?",
        citation=ki_def["citation"]
    )

    def handle_click(val):
        if val is False:
            set_current_step(9)
        else:
            set_current_step(3)

    is_ai_system = yes_no_buttons("classification.is_ai_system", on_click_callback=handle_click)

    if is_ai_system is True:
        st.markdown("### Begründung")
        is_ai_system_reasoning = st.text_area(
            "Begründung / Detailangaben zur Einstufung (Freitext):",
            value=get_value("classification.is_ai_system_reasoning", ""),
            placeholder="Z.B. Das System nutzt maschinelles Lernen zur Mustererkennung und zur Generierung von Empfehlungen..."
        )
        update_data("classification.is_ai_system_reasoning", is_ai_system_reasoning)

    st.markdown("---")

    question_details(
        legal_text=ki_def["text"],
        plain_info=AI_CHECK_INFO,
        intro=ki_def.get("intro")
    )

    can_proceed = is_ai_system is not None
    show_next = is_ai_system is True

    st.markdown("---")

    next_step = 9 if is_ai_system is False else 3
    navigate_step(2, next_step, 1, can_proceed=can_proceed, show_next=show_next)
