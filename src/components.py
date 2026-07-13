import streamlit as st
from src.state import update_data, get_value

COLOR_PRIMARY = "#000000"
COLOR_TEXT = "#111111"
COLOR_MUTED = "#555555"
COLOR_SURFACE = "#FFFFFF"
COLOR_BORDER = "#111111"


def apply_custom_css():
    st.markdown("""
    <style>
    .stApp {
        font-family: -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background-color: #FAF9F6 !important;
        color: #111111 !important;
    }

    header[data-testid="stHeader"] {
        background-color: #FAF9F6 !important;
        border-bottom: 1px solid #111111 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #FAF9F6 !important;
        border-right: 1px solid #111111 !important;
    }

    section[data-testid="stSidebar"] *, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #111111 !important;
    }

    div[data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 1px solid #111111 !important;
        padding: 12px !important;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background-color: #FAF9F6 !important;
        border: 1px dashed #111111 !important;
    }

    div[data-testid="stFileUploaderDropzone"] p,
    div[data-testid="stFileUploaderDropzone"] span,
    div[data-testid="stFileUploaderDropzone"] div {
        color: #111111 !important;
    }

    div[data-testid="stFileUploaderDropzone"] button {
        background-color: #FFFFFF !important;
        border: 1px solid #111111 !important;
        color: #111111 !important;
        border-radius: 0px !important;
    }

    div[data-testid="stFileUploaderDropzone"] button * {
        color: inherit !important;
    }

    div[data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #111111 !important;
        color: #FFFFFF !important;
    }

    div[data-testid="stTooltipIcon"] svg,
    svg[data-testid="stWidgetLabelHelpIcon"],
    .stTooltipIcon svg {
        color: #555555 !important;
        opacity: 1.0 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', Georgia, 'Times New Roman', serif !important;
        font-weight: 700 !important;
        color: #111111 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.8rem !important;
        border-bottom: none !important;
    }

    .stMarkdown p {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #222222;
    }

    label, .stWidgetLabel, div[data-testid="stWidgetLabel"] p {
        color: #111111 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    div[data-testid="stTextInput"] input, 
    div[data-testid="stTextArea"] textarea,
    input, textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        border: 1px solid #888888 !important;
        border-radius: 0px !important;
        -webkit-text-fill-color: #111111 !important;
    }

    input::placeholder,
    textarea::placeholder,
    [data-baseweb="input"] input::placeholder,
    [data-baseweb="textarea"] textarea::placeholder,
    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder,
    ::-webkit-input-placeholder,
    :-ms-input-placeholder,
    ::-ms-input-placeholder {
        color: #444444 !important;
        -webkit-text-fill-color: #444444 !important;
        opacity: 1 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        border: 1px solid #888888 !important;
        border-radius: 0px !important;
    }
    
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
    }
    
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"],
    div[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid #888888 !important;
        color: #111111 !important;
    }

    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"] *,
    ul[role="listbox"] *,
    div[role="listbox"] * {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
    }

    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="menu"] li:hover,
    ul[role="listbox"] li:hover {
        background-color: #EEEEEE !important;
        color: #000000 !important;
    }

    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] div,
    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] span {
        color: #111111 !important;
    }

    div[data-testid="stCheckbox"] label p,
    div[data-testid="stCheckbox"] label,
    div[data-testid="stCheckbox"] span {
        color: #111111 !important;
    }

    div[data-testid="stAlert"], 
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] li,
    div[data-testid="stAlert"] div,
    div[data-testid="stAlert"] span {
        color: #222222 !important;
    }

    hr {
        border: 0 !important;
        border-top: 2px double #111111 !important;
        margin: 2rem 0 !important;
    }

    .step-header {
        border-bottom: 1px solid #111111;
        padding-bottom: 16px;
        margin-bottom: 24px;
        text-align: center;
    }

    .step-header h2 {
        font-size: 2.2rem;
        margin: 0;
    }

    .step-header p {
        font-family: 'Playfair Display', Georgia, 'Times New Roman', serif;
        font-style: italic;
        color: #555555;
        font-size: 1.1rem;
        margin-top: 6px;
    }

    .legal-badge {
        display: inline-block;
        border: 1px solid #111111;
        background: #FFFFFF;
        color: #111111;
        padding: 3px 10px;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'Playfair Display', Georgia, 'Times New Roman', serif;
        font-style: italic;
        letter-spacing: 0.02em;
        margin: 4px 2px;
    }

    .risk-badge {
        display: inline-block;
        padding: 12px 32px;
        border: 3px double #111111;
        background: #FFFFFF;
        color: #111111;
        font-family: 'Playfair Display', Georgia, 'Times New Roman', serif;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        text-align: center;
        margin: 20px 0;
    }

    .info-box {
        border: 1px solid #333333;
        background-color: #FFFFFF;
        padding: 16px;
        margin: 12px 0;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #222222;
    }

    .legal-text-box {
        border: 1px solid #333333;
        background-color: #FDFDFD;
        padding: 16px;
        margin: 12px 0;
        font-size: 0.95rem;
        line-height: 1.6;
        font-style: italic;
        color: #333333;
        border-left: 4px solid #111111;
    }

    .warning-box {
        border: 2px solid #E53E3E;
        background-color: #FFF5F5;
        color: #C53030;
        padding: 16px;
        margin: 12px 0;
    }

    .warning-box h3, .warning-box p {
        color: #C53030 !important;
    }

    .obligation-card {
        border: 1px solid #111111;
        background: #FFFFFF;
        padding: 18px;
        margin: 12px 0;
    }

    .obligation-card h4 {
        margin-top: 0 !important;
        font-family: 'Playfair Display', Georgia, 'Times New Roman', serif !important;
        font-size: 1.25rem !important;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 6px;
    }

    .stButton>button {
        border-radius: 0px !important;
        border: 1px solid #111111 !important;
        background-color: #FFFFFF !important;
        color: #111111 !important;
        font-family: 'Playfair Display', Georgia, 'Times New Roman', serif !important;
        font-weight: bold !important;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background-color: #111111 !important;
        color: #FFFFFF !important;
    }

    .stButton>button[kind="primary"] {
        background-color: #111111 !important;
        color: #FFFFFF !important;
    }

    .stButton>button[kind="primary"]:hover {
        background-color: #333333 !important;
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)


def legal_badge(citation):
    st.markdown(f'<span class="legal-badge">{citation}</span>', unsafe_allow_html=True)


def legal_badges(citations):
    badges_html = " ".join(f'<span class="legal-badge">{c}</span>' for c in citations)
    st.markdown(badges_html, unsafe_allow_html=True)


def risk_badge(category):
    label_map = {
        "prohibited": "VERBOTEN - Art. 5 KI-VO",
        "high_risk": "HOCHRISIKO - Art. 6 KI-VO",
        "limited_risk": "BEGRENZTES RISIKO - Art. 50 KI-VO",
        "minimal_risk": "MINIMALES RISIKO",
        "not_ai": "KEIN KI-SYSTEM i.S.d. KI-VO",
    }
    label = label_map.get(category, category)
    st.markdown(
        f'<div style="text-align:center;margin:20px 0;">'
        f'<span class="risk-badge">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def info_box(text):
    st.markdown(f'<div class="info-box">{text}</div>', unsafe_allow_html=True)


def legal_text_box(text):
    st.markdown(f'<div class="legal-text-box">{text}</div>', unsafe_allow_html=True)


def warning_box(text):
    st.markdown(f'<div class="warning-box">{text}</div>', unsafe_allow_html=True)


def step_header(title, subtitle="", step_num=None, total_steps=None):
    step_indicator = ""
    if step_num is not None and total_steps is not None:
        step_indicator = f"<p style='font-family: \"Playfair Display\", serif; font-size:0.9rem; margin:0; text-transform: uppercase; letter-spacing: 0.1em;'>Schritt {step_num} von {total_steps}</p>"

    st.markdown(
        f'<div class="step-header">'
        f'{step_indicator}'
        f'<h2>{title}</h2>'
        f'{"<p>" + subtitle + "</p>" if subtitle else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )


def question_header(question_text, citation):
    legal_badge(citation)
    st.markdown(
        f"""
        <div style="min-height: 105px; display: flex; align-items: flex-start; margin-top: 10px; margin-bottom: 10px;">
            <h3 style="margin: 0; padding: 0; font-family: 'Playfair Display', Georgia, 'Times New Roman', serif; font-size: 1.6rem; font-weight: normal; line-height: 1.35; color: #000000;">
                {question_text}
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )


def question_details(legal_text, plain_info, intro=None):
    st.markdown("**Gesetzestext:**")
    if intro:
        st.markdown(f"*{intro}*")
    legal_text_box(legal_text)
    
    st.markdown("**Erklärung:**")
    info_box(plain_info)


def question_with_info(question_text, citation, legal_text, plain_info, intro=None):
    question_header(question_text, citation)
    question_details(legal_text, plain_info, intro)


def show_progress(current_step, total_steps):
    progress = current_step / max(total_steps - 1, 1)
    st.progress(progress)

    step_labels = [
        "Start", "Stammdaten", "KI-Prüfung", "Verboten",
        "Hochrisiko", "Transparenz", "GPAI", "Rolle",
        "Autonomie", "Ergebnis"
    ]

    cols = st.columns(len(step_labels))
    for i, (col, label) in enumerate(zip(cols, step_labels)):
        with col:
            if i == current_step:
                st.markdown(
                    f"<div style='text-align:center;font-size:0.7rem;font-family: \"Playfair Display\", serif;"
                    f"color:#000000;font-weight:700;text-decoration:underline;'>{label}</div>",
                    unsafe_allow_html=True,
                )
            elif i < current_step:
                st.markdown(
                    f"<div style='text-align:center;font-size:0.7rem;"
                    f"color:#555555;'>{label} &bull;</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='text-align:center;font-size:0.7rem;"
                    f"color:#aaaaaa;'>{label}</div>",
                    unsafe_allow_html=True,
                )


def nav_buttons(current_step, total_steps, can_proceed=True, next_label="Weiter", back_label="Zurück", show_next=True):
    cols = st.columns([1, 1, 1])
    action = None

    with cols[0]:
        if current_step > 0:
            if st.button(back_label, key=f"nav_back_{current_step}", use_container_width=True):
                action = "back"

    with cols[2]:
        if show_next and current_step < total_steps - 1:
            if st.button(
                next_label,
                key=f"nav_next_{current_step}",
                use_container_width=True,
                disabled=not can_proceed,
                type="primary",
            ):
                action = "next"

    return action


def yes_no_buttons(state_path, key_suffix="", on_click_callback=None):
    val = get_value(state_path)
    
    def handle_click(new_val):
        update_data(state_path, new_val)
        if on_click_callback:
            on_click_callback(new_val)
            
    col1, col2 = st.columns(2)
    with col1:
        btn_type = "primary" if val is True else "secondary"
        st.button(
            "JA",
            key=f"btn_yes_{state_path}_{key_suffix}",
            use_container_width=True,
            type=btn_type,
            on_click=handle_click,
            args=(True,)
        )
            
    with col2:
        btn_type = "primary" if val is False else "secondary"
        st.button(
            "NEIN",
            key=f"btn_no_{state_path}_{key_suffix}",
            use_container_width=True,
            type=btn_type,
            on_click=handle_click,
            args=(False,)
        )
            
    return val


def navigate_step(current_step, next_step, prev_step, can_proceed=True, show_next=True):
    from src.state import set_current_step
    
    action = nav_buttons(current_step, 10, can_proceed=can_proceed, show_next=show_next)
    if action == "next" and next_step is not None:
        set_current_step(next_step)
        st.rerun()
    elif action == "back" and prev_step is not None:
        set_current_step(prev_step)
        st.rerun()
