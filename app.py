import streamlit as st
import pandas as pd
import google.generativeai as genai
from duckduckgo_search import DDGS

# 1. UI DESIGN
st.set_page_config(page_title="MP Intel Agent PRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        border-radius: 10px; background-color: #d32f2f; color: white; 
        height: 3.5em; width: 100%; font-weight: bold; border: none;
    }
    .report-container { 
        background-color: white; padding: 30px; border-radius: 15px; 
        border: 1px solid #e0e0e0; color: #1e1e1e; line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. API SETUP
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# 3. SIDEBAR
with st.sidebar:
    st.title("🛡️ Marketingpoint")
    ref_file = st.file_uploader("Referenzliste (CSV) hochladen", type="csv")
    st.info("Das Tool sucht jetzt LIVE im Web nach echten Firmendaten.")

# 4. MAIN
st.title("🏢 Swiss Company Intelligence")

col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Firmenname", placeholder="z.B. LOXY International AG")
with col2:
    contact = st.text_input("Ansprechperson")

if st.button("🚀 Deep Dive Analyse starten"):
    if not company or not ref_file or not api_key:
        st.warning("Bitte Daten eingeben und CSV hochladen.")
    else:
        with st.spinner(f'Suche im Web nach echten Daten zu {company}...'):
            try:
                # ECHTE WEBSUCHE STARTEN
                search_results = ""
                with DDGS() as ddgs:
                    # Wir suchen gezielt nach der Schweizer Firma und ihren harten Fakten
                    query = f"{company} Schweiz Mitarbeiter Umsatz Partner Telematik LSVA"
                    results = ddgs.text(query, max_results=5)
                    for r in results:
                        search_results += f"\nQuelle: {r['href']}\nInhalt: {r['body']}\n"

                # CSV Referenzen laden
                try:
                    ref_text = ref_file.getvalue().decode("utf-8")
                except:
                    ref_text = ref_file.getvalue().decode("latin-1")

                # PROMPT MIT ECHTEN DATEN FÜTTERN
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Du bist ein Sales-Experte für Marketingpoint AG. 
                Hier sind ECHTE Suchergebnisse aus dem Internet zu der Firma '{company}':
                ---
                {search_results}
                ---

                HIER SIND DIE REFERENZEN VON MARKETINGPOINT:
                {ref_text}

                DEINE AUFGABE:
                1. Analysiere die Suchergebnisse oben genau. Was macht die Firma wirklich? (Falls es Telematik/IT ist, ignoriere Textil-Firmen).
                2. Erstelle ein Dashboard:
                   - Struktur: Mutterhaus/Holding?
                   - Tabelle: MA & Umsatz (CH, DACH, Global) - nimm die Daten aus den Suchergebnissen oder schätze basierend auf diesen.
                   - Business: Kern-Fokus & Partner.
                3. Matching: Suche in den Marketingpoint-Referenzen nach Firmen aus dem Bereich Logistik, Telematik, IT oder Flottenmanagement.
                4. Argumentation: Warum verstehen wir deren Business?
                5. 3 analytische Fragen für das Meeting.

                Antworte auf Deutsch und sei extrem präzise.
                """

                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown(f"### Echte Analyse für {company}")
                st.markdown('<div class="report-container">', unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Fehler: {str(e)}")

st.caption("Powered by Marketingpoint AI | Live Web Search Enabled")
