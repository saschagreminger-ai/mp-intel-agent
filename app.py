import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. UI DESIGN (Marketingpoint Style)
st.set_page_config(page_title="MP Intel Agent", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        border-radius: 10px; 
        background-color: #d32f2f; 
        color: white; 
        height: 3.5em; 
        width: 100%; 
        font-weight: bold;
        border: none;
    }
    .report-container { 
        background-color: white; 
        padding: 30px; 
        border-radius: 15px; 
        border: 1px solid #e0e0e0; 
        color: #1e1e1e;
        line-height: 1.6;
    }
    h3 { color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

# 2. API SETUP
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key fehlt! Bitte in den Streamlit Secrets hinterlegen.")

# 3. SIDEBAR
with st.sidebar:
    st.title("🛡️ Marketingpoint")
    st.subheader("Wissensbasis")
    ref_file = st.file_uploader("Referenzliste (CSV) hochladen", type="csv")
    st.divider()
    st.info("Tipp: Nutze eine CSV mit Firmenname und Branche für bestes Matching.")

# 4. MAIN INTERFACE
st.title("🏢 Swiss Company Intelligence")
st.markdown("Dein strategisches Briefing für Neukundentermine.")

col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Name der Zielfirma", placeholder="z.B. LOXY International AG")
with col2:
    contact = st.text_input("Ansprechperson", placeholder="z.B. Daniel Schnyder")

if st.button("🚀 Analyse & Matching starten"):
    if not company or not ref_file:
        st.warning("⚠️ Bitte gib einen Firmennamen ein und lade deine Referenz-CSV hoch.")
    else:
        with st.spinner('KI generiert Analyse...'):
            try:
                # CSV einlesen
                try:
                    ref_content = ref_file.getvalue().decode("utf-8")
                except:
                    ref_context = ref_file.getvalue().decode("latin-1")

                # DAS MODELL (Wir nutzen den stabilen Standard-Aufruf ohne 404-anfällige Tools)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Du bist ein Senior Sales Analyst für die Marketingpoint AG.
                Ziel: Bereite Account Manager auf einen Termin mit '{company}' vor.
                Ansprechpartner: {contact}

                HIER IST UNSERE REFERENZLISTE (Gleiche sie mit der Zielfirma ab):
                {ref_content}

                DEIN AUFTRAG (Erstelle ein kompaktes Dashboard):
                1. KONZERN: Wer ist das Mutterhaus? (Falls Tochtergesellschaft).
                2. KPI TABELLE: Mitarbeiter & Umsatz für CH, DACH, Global separat auflisten.
                3. BUSINESS: Kern-Business in 3 Stichworten & Top 3 Technologie-Partner.
                4. MATCHING: Wähle die 3 besten Referenzen aus unserer Liste oben. Begründe kurz, warum sie perfekt zu '{company}' passen (z.B. gleiches Partne
