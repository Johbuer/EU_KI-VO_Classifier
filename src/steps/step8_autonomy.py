import streamlit as st
from src.components import step_header, info_box, nav_buttons
from src.state import get_value, update_data, set_current_step, get_current_substep, set_current_substep, get_data
from src.data.info_texts import AUTONOMY_INFO, DECISION_IMPACT_INFO


def render_step():
    substep = get_current_substep()
    
    if substep < 0 or substep > 1:
        substep = 0
        set_current_substep(0)

    step_header(
        title="Betriebsmerkmale & Aufsicht",
        subtitle=f"Betriebsparameter - Schritt {substep + 1} von 2",
        step_num=8,
        total_steps=10
    )

    can_proceed = True

    if substep == 0:
        st.markdown("### 1. Autonomiegrad")
        st.markdown("""
        Wie selbstständig agiert das System? Der Autonomiegrad bestimmt, wie intensiv die menschliche 
        Aufsicht (**Human-in-the-Loop** nach Art. 14 KI-VO) ausgelegt sein muss.
        """)

        auto_options = ["agentisch", "vollautomatisiert", "teilautomatisiert", "assistierend"]
        auto_val = get_value("classification.autonomy_level", "")
        auto_index = None if auto_val == "" else auto_options.index(auto_val)

        autonomy_level = st.selectbox(
            "Autonomiegrad auswählen:",
            options=auto_options,
            format_func=lambda x: {
                "agentisch": "Agentisch (Handelt vollständig eigenständig, initiiert eigene Aktionen)",
                "vollautomatisiert": "Vollautomatisiert (Trifft Entscheidungen ohne menschlichen Zwischenschritt)",
                "teilautomatisiert": "Teilautomatisiert (Menschliche Freigabe vor Ausführung)",
                "assistierend": "Assistierend (Macht nur Vorschläge, Mensch entscheidet)"
            }[x],
            index=auto_index,
            placeholder="Bitte wählen..."
        )
        update_data("classification.autonomy_level", autonomy_level if autonomy_level else "")

        if autonomy_level:
            st.markdown("**Erklärung:**")
            info_box(AUTONOMY_INFO[autonomy_level])

        can_proceed = autonomy_level is not None
        if not can_proceed:
            st.warning("Bitte wählen Sie einen Autonomiegrad aus, um fortzufahren.")

    elif substep == 1:
        st.markdown("### 2. Entscheidungswirkung")
        st.markdown("""
        Welchen Einfluss haben die Ausgaben des KI-Systems auf die endgültige Entscheidung?
        """)

        decision_options = ["bindend", "suggerierend"]
        decision_val = get_value("classification.decision_impact")
        decision_index = None if decision_val in [None, ""] else decision_options.index(decision_val)

        decision_impact = st.radio(
            "Entscheidungswirkung auswählen:",
            options=decision_options,
            format_func=lambda x: {
                "bindend": "Bindend (Ausgaben werden direkt und autark umgesetzt)",
                "suggerierend": "Suggerierend / Human-in-the-Loop (KI macht Vorschläge, Mensch entscheidet)"
            }[x],
            index=decision_index,
            key="autonomy_decision_impact_radio"
        )
        update_data("classification.decision_impact", decision_impact)

        if decision_impact:
            st.markdown("**Erklärung:**")
            info_box(DECISION_IMPACT_INFO[decision_impact])

        can_proceed = decision_impact is not None
        if not can_proceed:
            st.warning("Bitte wählen Sie eine Entscheidungswirkung aus, um fortzufahren.")

    st.markdown("---")

    action = nav_buttons(8, 10, can_proceed=can_proceed, show_next=True)
    if action == "next":
        if substep == 0:
            set_current_substep(1)
        else:
            set_current_step(9)
        st.rerun()
        
    elif action == "back":
        if substep == 1:
            set_current_substep(0)
        else:
            set_current_step(7)
            set_current_substep(5)
        st.rerun()
