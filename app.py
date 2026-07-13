import streamlit as st

st.set_page_config(
    page_title="KI-VO Compliance Classifier",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import logging
from src.state import init_session_state, get_current_step, import_from_json, set_current_step
from src.components import apply_custom_css, show_progress

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

init_session_state()
apply_custom_css()

from src.steps import (
    step0_welcome,
    step1_general,
    step2_ai_check,
    step3_prohibited,
    step4_high_risk,
    step5_transparency,
    step6_gpai,
    step7_role,
    step8_autonomy,
    step9_result
)

with st.sidebar:
    st.image("src/scale-of-justice.png", width=64)
    st.title("KI-VO Classifier")
    st.markdown("---")
    
    st.subheader("Bestehende Analyse laden")
    uploaded_file = st.file_uploader(
        "JSON-Klassifizierungsdatei hochladen:",
        type=["json"],
        help="Laden Sie eine zuvor exportierte .json Klassifizierungsdatei hoch."
    )
    
    if uploaded_file is not None:
        try:
            json_string = uploaded_file.read().decode("utf-8")
            if import_from_json(json_string):
                st.success("Klassifizierung erfolgreich importiert!")
                st.rerun()
            else:
                st.error("Ungültiges Dateiformat oder veraltete Schema-Version.")
        except Exception as exc:
            st.error(f"Fehler beim Lesen der Datei: {exc}")
            
    st.markdown("---")
    st.markdown("""
    **KI-Verordnung (KI-VO)**  
    Verordnung (EU) 2024/1689  
    *Quelle:*  
    - Gesetzestext (Amtsblatt der EU)
    """)
    st.markdown("---")
    st.caption(
        "⚠️ Dieses Tool ist ein Legal-Tech-Prototyp, der primär die technische "
        "Umsetzung der regulatorischen Klassifizierungslogik demonstriert. "
        "Es wird Wert auf rechtliche Korrektheit gelegt, jedoch steht die "
        "technische Funktionalität im Vordergrund. Dieses Tool ersetzt keine Rechtsberatung."
    )
    
    if st.button("Analyse zurücksetzen", type="secondary", use_container_width=True):
        if "classifier_data" in st.session_state:
            del st.session_state.classifier_data
        set_current_step(0)
        st.rerun()

current_step = get_current_step()

if 0 < current_step < 9:
    show_progress(current_step, 10)
    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

if current_step == 0:
    step0_welcome.render_step()
elif current_step == 1:
    step1_general.render_step()
elif current_step == 2:
    step2_ai_check.render_step()
elif current_step == 3:
    step3_prohibited.render_step()
elif current_step == 4:
    step4_high_risk.render_step()
elif current_step == 5:
    step5_transparency.render_step()
elif current_step == 6:
    step6_gpai.render_step()
elif current_step == 7:
    step7_role.render_step()
elif current_step == 8:
    step8_autonomy.render_step()
elif current_step == 9:
    step9_result.render_step()
else:
    st.error(f"Ungültiger Wizard-Schritt: {current_step}")
    if st.button("Zum Startbildschirm"):
        set_current_step(0)
        st.rerun()
