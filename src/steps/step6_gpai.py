import streamlit as st
from src.components import step_header, nav_buttons, yes_no_buttons, question_header, question_details, info_box
from src.state import get_value, update_data, set_current_step, get_current_substep, set_current_substep, get_data
from src.data.legal_texts import ART51_GPAI, ART3_DEFINITIONS
from src.data.info_texts import GPAI_INFO


def render_step():
    data = get_data()
    components = data.get("layer2_components", [])
    has_llm = any(c.get("type") == "llm" for c in components)
    
    substep = get_current_substep()
    
    if substep < 0 or substep > 3:
        substep = 0
        set_current_substep(0)

    step_header(
        title="Art. 51 ff. KI-VO: GPAI-Modelle & GPAI-Systeme",
        subtitle=f"GPAI-Prüfung - Schritt {substep + 1} von 4",
        step_num=6,
        total_steps=10
    )

    can_proceed = True

    if substep == 0:
        def handle_click_0(val):
            if val is False:
                update_data("classification.gpai.is_gpai", False)
                update_data("classification.gpai.is_gpai_system", False)
                update_data("classification.gpai.systemic_risk", False)
                update_data("classification.gpai.flops_above_threshold", False)
                set_current_step(7)
            else:
                update_data("classification.gpai.is_gpai", True)
                set_current_substep(1)

        gpai_def = ART3_DEFINITIONS["gpai_modell"]
        
        if has_llm:
            st.info("ℹ️ **LLM erkannt**: Auf Layer 2 wurde mindestens ein Large Language Model (LLM) erfasst. LLMs gelten in der Regel als GPAI-Modelle.")
            if get_value("classification.gpai.is_gpai") is None:
                update_data("classification.gpai.is_gpai", True)

        question_header(
            question_text="Basiert das KI-System auf einem KI-Modell mit allgemeinem Verwendungszweck (GPAI-Modell nach Art. 3 Nr. 63 KI-VO)?",
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
        gpai_sys_def = ART3_DEFINITIONS.get("gpai_system", {
            "citation": "Art. 3 Nr. 66 i.V.m. EG 85 KI-VO",
            "text": "„KI-System mit allgemeinem Verwendungszweck“: ein KI-System, das auf einem KI-Modell mit allgemeinem Verwendungszweck beruht und in der Lage ist, einer Vielzahl von Zwecken sowohl für die direkte Verwendung als auch für die Integration in andere KI-Systeme zu dienen. (Erwägungsgrund 85 KI-VO stellt klar, dass ein solches KI-System ein GPAI-System bleibt, solange es nicht durch technische Maßnahmen auf einen spezifischen Zweck verengt wurde.)",
            "plain_info": "Gemäß Erwägungsgrund 85 KI-VO bleibt ein KI-System, das auf einem GPAI-Modell beruht, ein GPAI-System, solange es nicht auf einen spezifischen Zweck verengt wurde. An den Begriff 'GPAI-System' knüpft die KI-VO keine eigenständigen Sonderpflichten an; bezüglich Risikoklassen gilt das allgemeine Regelregime (Art. 5, Art. 6, Art. 50 KI-VO).",
            "intro": "Ein KI-System gilt als GPAI-System, wenn:"
        })

        question_header(
            question_text="Gilt das Gesamtsystem als KI-System mit allgemeinem Verwendungszweck (GPAI-System nach Art. 3 Nr. 66 i.V.m. EG 85 KI-VO)?",
            citation=gpai_sys_def["citation"]
        )

        st.markdown(
            "Ein KI-System bleibt ein **GPAI-System**, solange es faktisch *in der Lage ist, einer Vielzahl von Zwecken zu dienen* "
            "(z.B. durch Freitextfelder, Chat-Interface oder flexible Prompt-Parameter). "
            "Wenn das System durch **harte technische Maßnahmen** (z.B. reine Dropdown-Auswahl ohne Freitextfeld, nicht umgehbare Input-Validierung) "
            "so verengt ist, dass eine Nutzung für andere Zwecke (auch durch Jailbreaking/Prompt Injection) technisch unmöglich ist, "
            "gilt es als **Narrow AI (Spezifisches KI-System auf Basis eines GPAI-Modells)**."
        )

        current_mode = get_value("classification.gpai.system_restriction")
        
        opt_open = "Nein / Freitextfeld vorhanden: Das System kann faktisch weiterhin einer Vielzahl von Zwecken dienen (GPAI-System nach Art. 3 Nr. 66 i.V.m. EG 85 KI-VO)."
        opt_restricted = "Ja, technisch eingeschränkt: Das System ist durch harte technische Schranken (z.B. ohne Freitextfeld) auf einen spezifischen Zweck verengt (Narrow AI / Spezifisches KI-System)."

        opts = [opt_open, opt_restricted]
        default_idx = None
        if current_mode == "open_purpose":
            default_idx = 0
        elif current_mode == "technically_restricted":
            default_idx = 1

        selected_opt = st.radio(
            "Wie ist die Zweckbindung des Gesamtsystems ausgestaltet?",
            options=opts,
            index=default_idx,
            key="gpai_system_restriction_radio"
        )

        if selected_opt == opt_open:
            update_data("classification.gpai.is_gpai_system", True)
            update_data("classification.gpai.system_restriction", "open_purpose")
            info_box(
                "→ **Einstufung als GPAI-System (Art. 3 Nr. 66 KI-VO)**: Das System bleibt zweckoffen. "
                "Hinsichtlich der Risikoklassifizierung gelten die allgemeinen Regeln (Art. 5, Art. 6, Art. 50 KI-VO). "
                "Modellspezifische Pflichten (Kapitel V) verbleiben beim GPAI-Modellanbieter."
            )
        elif selected_opt == opt_restricted:
            update_data("classification.gpai.is_gpai_system", False)
            update_data("classification.gpai.system_restriction", "technically_restricted")
            info_box(
                "→ **Einstufung als Narrow AI (Spezifisches KI-System auf GPAI-Basis)**: Das System ist durch technische Schranken verengt. "
                "Es gilt im Sinne der Risikoklassifizierung als spezifisches KI-System."
            )

        can_proceed = selected_opt is not None
        if not can_proceed:
            st.warning("Bitte wählen Sie eine der beiden Optionen aus, um fortzufahren.")

        st.markdown("---")
        question_details(
            legal_text=gpai_sys_def["text"],
            plain_info=gpai_sys_def["plain_info"],
            intro=gpai_sys_def.get("intro")
        )

    elif substep == 2:
        def handle_click_1(val):
            set_current_substep(3)

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

    elif substep == 3:
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

    action = nav_buttons(6, 10, can_proceed=can_proceed, show_next=True)
    if action == "next":
        is_gpai = get_value("classification.gpai.is_gpai")
        
        if substep == 0:
            if is_gpai is False:
                update_data("classification.gpai.is_gpai_system", False)
                update_data("classification.gpai.systemic_risk", False)
                update_data("classification.gpai.flops_above_threshold", False)
                set_current_step(7)
            else:
                set_current_substep(1)
        elif substep == 1:
            set_current_substep(2)
        elif substep == 2:
            set_current_substep(3)
        elif substep == 3:
            flops = get_value("classification.gpai.flops_above_threshold")
            if flops is True:
                update_data("classification.gpai.systemic_risk", True)
            set_current_step(7)
        st.rerun()
        
    elif action == "back":
        if substep == 3:
            set_current_substep(2)
        elif substep == 2:
            set_current_substep(1)
        elif substep == 1:
            set_current_substep(0)
        else:
            set_current_step(5)
            set_current_substep(5)
        st.rerun()
