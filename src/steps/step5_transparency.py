import streamlit as st
from src.components import step_header, nav_buttons, yes_no_buttons, question_header, question_details
from src.state import get_value, update_data, set_current_step, get_current_substep, set_current_substep, get_data
from src.data.legal_texts import ART50_TRANSPARENCY


def get_trans_questions():
    t_map = {p["key"]: p for p in ART50_TRANSPARENCY}
    
    return [
        {
            "key": "direct_interaction",
            "question": "Interagiert das KI-System direkt mit natürlichen Personen (z.B. Chatbot, Voice-Agent)?",
            "info": t_map["direct_interaction"]
        },
        {
            "key": "synthetic_content",
            "question": "Erzeugt das system synthetische Audio-, Bild-, Video- oder Textinhalte (Generative AI)?",
            "info": t_map["synthetic_content"]
        },
        {
            "key": "emotion_recognition",
            "question": "Handelt es sich bei dem System um ein Emotionserkennungssystem?",
            "info": t_map["emotion_recognition"]
        },
        {
            "key": "biometric_categorization",
            "question": "Handelt es sich bei dem System um ein System zur biometrischen Kategorisierung?",
            "info": t_map["emotion_recognition"]
        },
        {
            "key": "deepfake",
            "question": "Erzeugt oder manipuliert das System Deepfakes (Bild/Ton/Video)?",
            "info": t_map["deepfake"]
        },
        {
            "key": "public_interest_text",
            "question": "Erzeugt oder manipuliert das System Text, der zur Information der Öffentlichkeit über Angelegenheiten von öffentlichem Interesse bestimmt ist?",
            "info": t_map["public_interest_text"]
        }
    ]


def render_step():
    questions = get_trans_questions()
    substep = get_current_substep()
    total_substeps = len(questions)

    if substep < 0 or substep >= total_substeps:
        substep = 0
        set_current_substep(0)

    q = questions[substep]
    key = q["key"]

    step_header(
        title="Art. 50 KI-VO: Transparenzpflichten",
        subtitle=f"Transparenzprüfung - Schritt {substep + 1} von {total_substeps}",
        step_num=5,
        total_steps=10
    )

    question_header(
        question_text=q["question"],
        citation=q["info"]["citation"]
    )

    def handle_click(val):
        if substep < total_substeps - 1:
            set_current_substep(substep + 1)
        else:
            data = get_data()
            transp = data["classification"]["transparency"]
            any_applies = any([
                transp.get("direct_interaction") is True,
                transp.get("synthetic_content") is True,
                transp.get("emotion_recognition") is True,
                transp.get("biometric_categorization") is True,
                transp.get("deepfake") is True,
                transp.get("public_interest_text") is True
            ])
            update_data("classification.transparency.any_applies", any_applies)
            set_current_step(6)

    state_path = f"classification.transparency.{key}"
    detected_val = yes_no_buttons(state_path, key_suffix=key, on_click_callback=handle_click)

    can_proceed = detected_val is not None
    if not can_proceed:
        st.warning("Bitte wählen Sie JA oder NEIN aus, um fortzufahren.")

    st.markdown("---")

    question_details(
        legal_text=q["info"]["legal_text"],
        plain_info=q["info"]["plain_info"],
        intro=q["info"].get("intro")
    )

    st.markdown("---")

    action = nav_buttons(5, 10, can_proceed=can_proceed, show_next=False)
    if action == "next":
        if substep < total_substeps - 1:
            set_current_substep(substep + 1)
        else:
            data = get_data()
            transp = data["classification"]["transparency"]
            any_applies = any([
                transp.get("direct_interaction") is True,
                transp.get("synthetic_content") is True,
                transp.get("emotion_recognition") is True,
                transp.get("biometric_categorization") is True,
                transp.get("deepfake") is True,
                transp.get("public_interest_text") is True
            ])
            update_data("classification.transparency.any_applies", any_applies)
            set_current_step(6)
        st.rerun()
        
    elif action == "back":
        if substep > 0:
            set_current_substep(substep - 1)
        else:
            set_current_step(4)
            data = get_data()
            annex_i = data["classification"]["high_risk"].get("annex_i_applies") is True
            annex_iii_matches = data["classification"]["high_risk"].get("annex_iii_matches", {})
            any_annex_iii = any(annex_iii_matches.values())
            
            if annex_i or any_annex_iii:
                set_current_substep(37)
            else:
                set_current_substep(33)
        st.rerun()
