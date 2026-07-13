import streamlit as st
from src.components import step_header, warning_box, nav_buttons, yes_no_buttons, question_header, question_details
from src.state import get_value, update_data, set_current_step, get_current_substep, set_current_substep, get_data
from src.data.legal_texts import ART5_PROHIBITED


def render_step():
    substep = get_current_substep()
    total_substeps = len(ART5_PROHIBITED)
    
    if substep < 0 or substep >= total_substeps:
        substep = 0
        set_current_substep(0)

    practice = ART5_PROHIBITED[substep]
    key = practice["key"]

    step_header(
        title=f"Art. 5 KI-VO: {practice['short_title']}",
        subtitle=f"Verbotene Praktik {substep + 1} von {total_substeps}",
        step_num=3,
        total_steps=10
    )

    details = get_value("classification.prohibited.details", {})
    if key not in details:
        details[key] = {"detected": None, "notes": ""}
        update_data("classification.prohibited.details", details)

    question_header(
        question_text=f"Wird das KI-System für den Zweck '{practice['short_title']}' eingesetzt?",
        citation=practice["citation"]
    )

    def handle_click(val):
        if val is False:
            if substep < total_substeps - 1:
                set_current_substep(substep + 1)
            else:
                update_data("classification.prohibited.detected", False)
                set_current_step(4)

    detected_path = f"classification.prohibited.details.{key}.detected"
    detected_val = yes_no_buttons(detected_path, key_suffix=key, on_click_callback=handle_click)

    if detected_val is True:
        warning_box(
            "**Hinweis:** Die Auswahl von 'JA' stuft dieses System als verbotene Praktik ein. "
            "Das Inverkehrbringen oder Betreiben dieses Systems ist in der EU nicht zulässig."
        )
        
        notes_val = st.text_area(
            "Bitte geben Sie nähere Angaben dazu an *:",
            value=get_value(f"classification.prohibited.details.{key}.notes", ""),
            key=f"prohibited_notes_{key}",
            placeholder="Beschreiben Sie den Anwendungsfall und warum er zutrifft..."
        )
        update_data(f"classification.prohibited.details.{key}.notes", notes_val)

    st.markdown("---")

    question_details(
        legal_text=practice["legal_text"],
        plain_info=practice["plain_info"],
        intro=practice.get("intro")
    )

    can_proceed = detected_val is not None
    if detected_val is True:
        notes = get_value(f"classification.prohibited.details.{key}.notes", "")
        if not notes.strip():
            can_proceed = False
            st.warning("Bitte füllen Sie das Freitextfeld mit weiteren Details aus, um fortzufahren.")
        st.caption("* Kennzeichnet Pflichtfelder")

    if detected_val is None:
        st.warning("Bitte wählen Sie JA oder NEIN aus, um fortzufahren.")

    st.markdown("---")

    show_next = (detected_val is True)

    action = nav_buttons(3, 10, can_proceed=can_proceed, show_next=show_next)
    if action == "next":
        if detected_val is True:
            update_data("classification.prohibited.detected", True)
            set_current_step(9)
        else:
            if substep < total_substeps - 1:
                set_current_substep(substep + 1)
            else:
                update_data("classification.prohibited.detected", False)
                set_current_step(4)
        st.rerun()
        
    elif action == "back":
        if substep > 0:
            set_current_substep(substep - 1)
        else:
            set_current_step(2)
        st.rerun()
