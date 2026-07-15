import streamlit as st
from src.components import step_header, nav_buttons, yes_no_buttons, question_header, question_details, legal_badge, info_box
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
            "question": "Erzeugt das System synthetische Audio-, Bild-, Video- oder Textinhalte (Generative AI)?",
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


def has_llm_component():
    data = get_data()
    comps = data.get("layer2_components", [])
    return any(c.get("type") == "llm" for c in comps)


def finalize_transparency():
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


def render_followup_synthetic():
    """Nachfrage, wenn bei synthetischen Inhalten 'Nein' gewählt wurde.
    Art. 50 Abs. 2 KI-VO: Ausnahme greift nur, wenn die Semantik der
    Eingabedaten nicht wesentlich verändert wird (reine RAG-Extraktion)."""

    step_header(
        title="Art. 50 KI-VO: Transparenzpflichten",
        subtitle="Nachfrage: Erzeugung synthetischer Inhalte",
        step_num=5,
        total_steps=10
    )

    legal_badge("Art. 50 Abs. 2 KI-VO")

    llm_hint = ""
    if has_llm_component():
        llm_hint = (
            "\n\n⚠️ **Hinweis:** Ihr System enthält ein Large Language Model (LLM). "
            "LLMs erzeugen in der Regel synthetische Inhalte, es sei denn, sie werden "
            "ausschließlich zur Datenextraktion ohne Umformulierung eingesetzt."
        )

    st.markdown(
        f"Sie haben angegeben, dass Ihr System **keine synthetischen Inhalte** erzeugt. "
        f"Da die Abgrenzung in der Praxis schwierig sein kann, möchten wir das genauer prüfen."
        f"{llm_hint}"
    )
    st.markdown("")
    st.markdown("**Wie verarbeitet das System Inhalte?**")

    mode = get_value("classification.transparency.content_generation_mode")

    option_generativ = (
        "Das System formuliert eigene Antworten, Texte oder fasst Inhalte in eigenen Worten zusammen. "
        "Dabei könnten semantische Änderungen gegenüber den Quelldaten auftreten."
    )
    option_extraktion = (
        "Das System extrahiert Inhalte per RAG oder vergleichbaren Methoden und gibt diese unverändert wieder. "
        "Allenfalls erfolgt eine Unterstützung durch z.B. Rechtschreibkorrektur oder Formatierung, "
        "ohne die Inhalte inhaltlich zu verändern. Semantische Veränderung ist ausgeschlossen."
    )

    options = [option_generativ, option_extraktion]
    labels = ["generates", "extracts_only"]
    
    idx = None
    if mode == "generates":
        idx = 0
    elif mode == "extracts_only":
        idx = 1

    selected = st.radio(
        "Bitte wählen Sie die zutreffende Aussage:",
        options=options,
        index=idx,
        key="synth_followup_radio"
    )

    st.markdown("---")

    if selected == option_generativ:
        info_box(
            "→ Das System erzeugt <b>synthetische Inhalte</b> im Sinne des Art. 50 Abs. 2 KI-VO. "
            "Die Transparenz- und Kennzeichnungspflichten sind anwendbar."
        )
    elif selected == option_extraktion:
        info_box(
            "→ Reine Datenextraktion ohne wesentliche semantische Veränderung fällt unter die "
            "<b>Ausnahme</b> des Art. 50 Abs. 2 KI-VO. Keine Kennzeichnungspflicht für synthetische Inhalte, "
            "sofern die Semantik der Eingabedaten nicht wesentlich verändert wird."
        )

    st.markdown("---")

    cols = st.columns([1, 1, 1])
    with cols[0]:
        if st.button("Zurück", key="synth_followup_back", use_container_width=True):
            update_data("classification.transparency.content_generation_mode", None)
            set_current_substep(1)
            st.rerun()

    with cols[2]:
        can_confirm = selected is not None
        if st.button("Bestätigen", key="synth_followup_confirm", use_container_width=True,
                      disabled=not can_confirm, type="primary"):
            if selected == option_generativ:
                update_data("classification.transparency.content_generation_mode", "generates")
                # Art. 50 Abs. 2: Eigenständige Formulierung = synthetische Inhalte
                update_data("classification.transparency.synthetic_content", True)
            else:
                update_data("classification.transparency.content_generation_mode", "extracts_only")

            set_current_substep(2)
            st.rerun()


def render_step():
    questions = get_trans_questions()
    substep = get_current_substep()
    total_substeps = len(questions)

    # Substep 100 = Nachfrage bei synth. Inhalten
    if substep == 100:
        render_followup_synthetic()
        return

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
        # Bei "Nein" auf synthetische Inhalte: Nachfrage einblenden
        if key == "synthetic_content" and val is False:
            set_current_substep(100)
            return

        if substep < total_substeps - 1:
            set_current_substep(substep + 1)
        else:
            finalize_transparency()

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
            finalize_transparency()
        st.rerun()
        
    elif action == "back":
        if substep > 0:
            # Wenn wir von Substep 2 zurückgehen und zuvor die Nachfrage
            # bei synth. Inhalten besucht haben, dorthin zurück
            prev = substep - 1
            set_current_substep(prev)
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
