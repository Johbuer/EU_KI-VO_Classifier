"""
Schritt 0: Willkommensbildschirm des KI-VO Classifier Wizards.
"""

import streamlit as st
from src.components import step_header, info_box, warning_box
from src.state import set_current_step, get_data


def render_step():
    step_header(
        title="KI-VO Classifier",
        subtitle="Strukturierte Klassifizierung und Compliance-Analyse Ihres KI-Systems",
        step_num=0,
        total_steps=10
    )

    st.markdown("""
    Willkommen beim **KI-VO Classifier**. Dieses Tool unterstützt Sie bei der regulatorischen Einordnung 
    Ihres Softwaresystems gemäß der **Verordnung (EU) 2024/1689 (KI-Verordnung / KI-VO)**.

    ### Was macht dieses Tool?
    1. **Stammdatenerfassung:** Erfassung des Einsatzkontexts, der Infrastruktur und der Komponenten (3-Layer-Modell).
    2. **KI-Vorprüfung:** Systematische Prüfung, ob Ihr System überhaupt als KI-System i.S.d. Verordnung gilt.
    3. **Risikoklassifizierung:** Einzelfragen-basierte Einstufung in eine der vier Risikoklassen (Verboten, Hochrisiko, Begrenztes Risiko, Minimales Risiko).
    4. **Rollenbestimmung:** Ermittlung Ihrer rechtlichen Rolle (Anbieter, Betreiber, nachgelagerter Anbieter etc.) inkl. automatischer Rollenverschiebung (Art. 25).
    5. **Compliance-Katalog:** Dynamische Generierung Ihres konkreten Pflichtenkatalogs und Ihrer Rechte gegenüber Drittparteien.
    6. **Export:** Export des fertigen Berichts als PDF, Markdown oder strukturiertes JSON für Ihre Dokumentation.
    """)

    warning_box(
        "**Hinweis:** Dieses Tool ist ein Legal-Tech-Prototyp, der primär die technische "
        "Umsetzung der regulatorischen Klassifizierungslogik demonstriert. Es wird Wert auf "
        "rechtliche Korrektheit gelegt, jedoch steht die technische Funktionalität im Vordergrund. "
        "Die rechtliche Validierung wird fortlaufend erweitert. Dieses Tool ersetzt keine Rechtsberatung."
    )

    st.markdown("**Datenschutz-Hinweis:**")
    info_box(
        "Alle erfassten Daten verbleiben in dieser lokalen Streamlit-Instanz "
        "und werden nicht an externe Server übertragen. Sie können Ihre Daten jederzeit exportieren "
        "oder über einen JSON-Import wieder laden."
    )

    st.markdown("---")

    if st.button("Klassifizierung starten", type="primary", use_container_width=True):
        set_current_step(1)
        st.rerun()
