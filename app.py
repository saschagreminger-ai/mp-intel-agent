import streamlit as st
import pandas as pd
import google.generativeai as genai

# UI DESIGN
st.set_page_config(page_title="MP Intel Agent", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { border-radius: 10px; background-color: #d32f2f; color: white; height: 3em; width: 100%; font-weight: bold; }
    .report-container { background-color: white; padding: 25px; border-radius: 15px; border: 1px solid #e0e0e0; color: black; }
    </style>
    """, unsafe_allow_html=True)

# API SETUP
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key fehlt in den Streamlit Secrets!")

# SIDEBAR
with st.sidebar:
    st.title("🛡️ Marketingpoint")
    ref_file = st.file_uploader("Referenzliste (CSV) hochladen", type="csv")
    st.info("Lade deine CSV hoch, um das Matching zu aktivieren.")

# MAIN
st.title("🏢 Swiss Company Intelligence")

col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Firmenname", placeholder="z.B. LOXY International AG")
with col2:
    contact = st.text_input("Ansprechperson")

if st.button("Analyse starten"):
    if not company or not ref_file:
        st.warning("Bitte Firma eingeben und CSV hochladen.")
    else:
        with st.spinner('Analysiere...'):
            try:
                # CSV laden
                try:
                    ref_text = ref_file.getvalue().decode("utf-8")
                except:
                    ref_text = ref_file.getvalue().decode("latin-1")

                # STABILES MODELL OHNE SEARCH-TOOL (Verhindert 404)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Du bist ein Sales-Experte für Marketingpoint AG. 
                Analysiere die Firma: {company}
                Ansprechpartner: {contact}

                REFERENZLISTE MARKETINGPOINT:
                {ref_text}

                DEINE AUFGABE:
                1. Beschreibe kurz das Business & Mutterhaus der Zielfirma.
                2. Erstelle eine Tabelle: Mitarbeiter & Umsatz (CH, DACH, Global).
                3. Suche die 3 besten Referenzen aus der Liste oben, die zu dieser Firma passen (Branche/Partner).
                4. Schätze: Marktgröße DACH, Deal-Size, Sales Cycle.
                5. Erstelle 3 analytische Fragen für das Meeting.

                Antworte kurz, tabellarisch und auf Deutsch.
                """

                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown(f"### Ergebnisse für {company}")
                st.markdown('<div class="report-container">', unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Ein Fehler ist aufgetreten: {str(e)}")

st.caption("Powered by Marketingpoint AI")
