import streamlit as st
from src.components import step_header, question_header, question_details, yes_no_buttons, warning_box, nav_buttons
from src.state import get_value, update_data, set_current_step, get_current_substep, set_current_substep, get_data
from src.data.legal_texts import ART6_HIGH_RISK, ANNEX_III_CATEGORIES


def get_questions_config():
    categories = ANNEX_III_CATEGORIES
    
    config = {
        0: {
            "type": "annex_i",
            "title": "Produktsicherheit (Art. 6 Abs. 1)",
            "question": "Ist das KI-System als Sicherheitsbauteil eines Produkts vorgesehen, das unter Anhang I fällt, ODER ist es selbst ein solches Produkt UND muss es einer Konformitätsbewertung durch Dritte unterzogen werden?",
            "citation": ART6_HIGH_RISK["abs1"]["citation"],
            "legal_text": ART6_HIGH_RISK["abs1"]["legal_text"],
            "plain_info": ART6_HIGH_RISK["abs1"]["plain_info"],
            "intro": ART6_HIGH_RISK["abs1"].get("intro"),
            "state_path": "classification.high_risk.annex_i_applies"
        }
    }
    
    idx = 1
    for cat in categories:
        config[idx] = {
            "type": "parent_category",
            "cat_nr": cat["nr"],
            "title": f"Anhang III Bereich {cat['nr']}: {cat['title']}",
            "question": f"Fällt Ihr System thematisch in den Bereich '{cat['title']}'?",
            "citation": cat["citation_base"],
            "legal_text": f"Betrifft Anwendungen im Bereich {cat['title']}.",
            "plain_info": cat["condition"] if cat["condition"] else "Prüfung der spezifischen Anwendungsfälle dieses Bereichs.",
            "state_path": f"classification.high_risk.parent_cat_{cat['nr']}"
        }
        idx += 1
        
        for sub in cat["subcategories"]:
            config[idx] = {
                "type": "sub_category",
                "cat_nr": cat["nr"],
                "title": f"Anhang III Bereich {cat['nr']}: {sub['title']}",
                "question": f"Trifft der Anwendungsfall '{sub['title']}' auf Ihr KI-System zu?",
                "citation": sub["citation"],
                "legal_text": sub["text"],
                "plain_info": sub["plain_info"],
                "intro": sub.get("intro"),
                "state_path": f"classification.high_risk.annex_iii_matches.{sub['citation']}"
            }
            idx += 1
            
    config[34] = {
        "type": "exception_ask",
        "title": "Ausnahmefilter (Art. 6 Abs. 3)",
        "question": "Erfüllt das KI-System ausschließlich eine oder mehrere Bedingungen des Art. 6 Abs. 3, sodass es KEIN erhebliches Risiko für Gesundheit, Sicherheit oder Grundrechte birgt?",
        "citation": ART6_HIGH_RISK["abs3_exception"]["citation"],
        "legal_text": ART6_HIGH_RISK["abs3_exception"]["legal_text"],
        "plain_info": ART6_HIGH_RISK["abs3_exception"]["plain_info"],
        "intro": ART6_HIGH_RISK["abs3_exception"].get("intro"),
        "state_path": "classification.high_risk.exception_art6_3_applies"
    }
    config[35] = {
        "type": "exception_condition",
        "title": "Ausnahme-Bedingung",
        "state_path": "classification.high_risk.exception_art6_3_condition"
    }
    config[36] = {
        "type": "exception_reasoning",
        "title": "Ausnahme-Begründung",
        "state_path": "classification.high_risk.exception_art6_3_reasoning"
    }
    config[37] = {
        "type": "profiling_override",
        "title": "Profiling-Ausschlusskriterium (Art. 6 Abs. 3 UAbs. 3)",
        "question": "Nimmt das KI-System ein Profiling natürlicher Personen vor?",
        "citation": "Art. 6 Abs. 3 UAbs. 3 KI-VO",
        "legal_text": ART6_HIGH_RISK["abs3_exception"]["profiling_override"],
        "plain_info": "Falls das System Profiling betreibt, erlischt die Ausnahme. Das System gilt dann ausnahmslos als Hochrisiko.",
        "intro": ART6_HIGH_RISK["abs3_exception"].get("intro_profiling"),
        "state_path": "classification.high_risk.profiling_override"
    }
    
    return config


def any_hr_match(data):
    if get_value("classification.high_risk.annex_i_applies") is True:
        return True
    matches = get_value("classification.high_risk.annex_iii_matches", {})
    return any(matches.values())


def next_idx(current, data, config):
    q = config[current]
    
    if q["type"] == "parent_category":
        val = get_value(q["state_path"])
        if val is False:
            cat_nr = q["cat_nr"]
            n_idx = current + 1
            while n_idx in config and config[n_idx]["type"] == "sub_category" and config[n_idx]["cat_nr"] == cat_nr:
                n_idx += 1
            return n_idx

    if current == 33:
        if any_hr_match(data):
            return 34
        else:
            return 99

    if current == 34:
        val = get_value(q["state_path"])
        if val is False or val is None:
            return 99

    return current + 1


def prev_idx(current, data, config):
    p_idx = current - 1
    
    if current == 34:
        idx = 33
        while idx > 0:
            p_cat = config[idx]
            if p_cat["type"] == "sub_category":
                p_nr = p_cat["cat_nr"]
                parent_idx = idx
                while parent_idx > 0 and config[parent_idx]["type"] != "parent_category":
                    parent_idx -= 1
                
                if get_value(config[parent_idx]["state_path"]) is True:
                    return idx
                else:
                    idx = parent_idx - 1
            else:
                idx -= 1
        return 0

    if p_idx in config:
        p_q = config[p_idx]
        if p_q["type"] == "sub_category":
            cat_nr = p_q["cat_nr"]
            parent_idx = p_idx
            while parent_idx > 0 and config[parent_idx]["type"] != "parent_category":
                parent_idx -= 1
            
            if get_value(config[parent_idx]["state_path"]) is False:
                return parent_idx
                
    return p_idx


def render_step():
    config = get_questions_config()
    substep = get_current_substep()
    
    if substep < 0 or substep > 37:
        substep = 0
        set_current_substep(0)

    data = get_data()
    q = config[substep]

    step_header(
        title=f"Art. 6 KI-VO: {q['title']}",
        subtitle=f"Hochrisiko-Prüfung - Schritt {substep + 1} von 38",
        step_num=4,
        total_steps=10
    )

    can_proceed = True

    def handle_click(val):
        if q["type"] == "exception_ask" and val is True:
            return
            
        n_idx = next_idx(substep, data, config)
        if n_idx == 99:
            hr = data["classification"]["high_risk"]
            annex_i = hr.get("annex_i_applies") is True
            annex_iii = any_hr_match(data)
            profiling = hr.get("profiling_override") is True
            exception = hr.get("exception_art6_3_applies") is True
            
            final_hr = False
            if annex_i or annex_iii:
                # Art. 6 Abs. 3 UAbs. 3 KI-VO: Profiling hebelt Ausnahme aus.
                if profiling:
                    final_hr = True
                elif exception:
                    final_hr = False
                else:
                    final_hr = True
            
            update_data("classification.high_risk.final_is_high_risk", final_hr)
            set_current_step(5)
        else:
            set_current_substep(n_idx)

    if q["type"] in ["annex_i", "parent_category", "sub_category", "exception_ask", "profiling_override"]:
        question_header(
            question_text=q["question"],
            citation=q["citation"]
        )
        
        val = yes_no_buttons(q["state_path"], key_suffix=str(substep), on_click_callback=handle_click)
        can_proceed = val is not None
        if not can_proceed:
            st.warning("Bitte wählen Sie JA oder NEIN aus, um fortzufahren.")

        st.markdown("---")
        
        question_details(
            legal_text=q["legal_text"],
            plain_info=q["plain_info"],
            intro=q.get("intro")
        )

    elif q["type"] == "exception_condition":
        st.markdown("### Welche Bedingung des Art. 6 Abs. 3 trifft auf Ihr System zu?")
        st.caption("Bitte wählen Sie die zutreffende Bedingung aus:")
        
        cond_options = [
            "a) eng gefasste Verfahrensaufgabe (Art. 6 Abs. 3 UAbs. 2 lit. a)",
            "b) Verbesserung einer zuvor abgeschlossenen menschlichen Tätigkeit (Art. 6 Abs. 3 UAbs. 2 lit. b)",
            "c) Erkennung von Entscheidungsmustern ohne Ersetzung menschlicher Bewertung (Art. 6 Abs. 3 UAbs. 2 lit. c)",
            "d) Vorbereitende Aufgabe für eine Bewertung (Art. 6 Abs. 3 UAbs. 2 lit. d)"
        ]
        cond_val = get_value(q["state_path"], "")
        cond_index = None if cond_val == "" else cond_options.index(cond_val)
        
        condition = st.selectbox(
            "Bedingung auswählen *:",
            options=cond_options,
            index=cond_index,
            placeholder="Bitte wählen..."
        )
        update_data(q["state_path"], condition if condition else "")
        
        can_proceed = condition is not None
        if not can_proceed:
            st.warning("Bitte wählen Sie eine Bedingung aus, um fortzufahren.")
        st.caption("* Kennzeichnet Pflichtfelder")

    elif q["type"] == "exception_reasoning":
        st.markdown("### Begründung für die Ausnahme")
        st.caption("Bitte begründen Sie detailliert, warum die gewählte Bedingung erfüllt ist (Freitext):")
        
        reasoning = st.text_area(
            "Begründung *:",
            value=get_value(q["state_path"], ""),
            placeholder="Z.B. Das System korrigiert lediglich Tippfehler im Freitextfeld des HR-Portals und nimmt keinerlei Bewertung der Bewerber vor..."
        )
        update_data(q["state_path"], reasoning)
        
        can_proceed = len(reasoning.strip()) > 0
        if not can_proceed:
            st.warning("Bitte geben Sie eine Begründung an, um fortzufahren.")
        st.caption("* Kennzeichnet Pflichtfelder")

    st.markdown("---")

    show_next = (q["type"] in ["exception_condition", "exception_reasoning"]) or (q["type"] == "exception_ask" and get_value(q["state_path"]) is True)

    action = nav_buttons(4, 10, can_proceed=can_proceed, show_next=show_next)
    if action == "next":
        n_idx = next_idx(substep, data, config)
        if n_idx == 99:
            hr = data["classification"]["high_risk"]
            annex_i = hr.get("annex_i_applies") is True
            annex_iii = any_hr_match(data)
            profiling = hr.get("profiling_override") is True
            exception = hr.get("exception_art6_3_applies") is True
            
            final_hr = False
            if annex_i or annex_iii:
                if profiling:
                    final_hr = True
                elif exception:
                    final_hr = False
                else:
                    final_hr = True
            
            update_data("classification.high_risk.final_is_high_risk", final_hr)
            set_current_step(5)
        else:
            set_current_substep(n_idx)
        st.rerun()
        
    elif action == "back":
        if substep > 0:
            p_idx = prev_idx(substep, data, config)
            set_current_substep(p_idx)
        else:
            set_current_step(3)
            set_current_substep(7)
        st.rerun()
