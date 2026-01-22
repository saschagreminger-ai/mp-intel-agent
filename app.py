import streamlit as st
import pandas as pd
import google.generativeai as genai

# UI DESIGN
st.set_page_config(page_title="MP Intel Agent", layout="wide", initial_sidebar_state="expanded")

# CSS für den Profi-Look
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stTextInput>div>div>input { border-radius: 10px; }
    .stButton>button { border-radius: 10px; background-color: #d32f2f; color: white; height: 3em; font-weight: bold; }
    .report-container { background-color: white; padding: 25px; border-radius: 15px; border: 1px solid #e0e0e0; color: black; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# API SETUP
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Bitte API Key in den Streamlit Cloud Secrets hinterlegen!")

# SIDEBAR
with st.sidebar:
    st.title("🛡️ Marketingpoint")
    st.subheader("Wissensbasis")
    ref_file = st.file_uploader("Referenzliste (CSV) hochladen", type="csv")
    st.divider()
    st.markdown("🔍 **Anleitung:**\n1. CSV hochladen\n2. Firma eingeben\n3. Deep Dive starten")

# MAIN INTERFACE
st.title("🏢 Swiss Company Intelligence")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Name der Zielfirma", placeholder="z.B. LOXY International AG")
with col2:
    contact = st.text_input("Ansprechperson (optional)")

if st.button("🔥 Deep Dive Recherche & Matching starten"):
    if not company or not ref_file:
        st.warning("⚠️ Bitte Firmennamen eingeben und Referenz-CSV in der Sidebar hochladen.")
    else:
        with st.spinner('Recherche & Referenz-Abgleich aktiv...'):
            try:
                # Referenzen laden
                try:
                    ref_context = ref_file.getvalue().decode("utf-8")
                except:
                    ref_context = ref_file.getvalue().decode("latin-1")

                # PROMPT: Wir weisen die KI an, ihr Wissen über den Schweizer Markt zu nutzen
                prompt = f"""
                Analysiere die Firma '{company}' für Account Manager '{contact}'.
                
                AUFGABE:
                1. Identifiziere die Konzernstruktur (Mutterhaus?).
                2. Erstelle eine Tabelle mit Mitarbeiterzahlen & Umsatz für CH, DACH, Global.
                3. Analysiere das Kern-Business & identifiziere die Top 3 Technologie-Partner.
                
                MATCHING MIT DIESEN REFERENZEN:
                ---
                {ref_context}
                ---

                BERICHTS-STRUKTUR:
                - Nutze Tabellen für KPIs.
                - Wähle die 3 passendsten Referenzen und begründe das Matching präzise.
                - Schätze Marktgrösse DACH, Deal-Size und Sales Cycle.
                - Erstelle 3 analytische Fragen für das Meeting.
                
                Antworte kurz, faktenorientiert und auf Deutsch.
                """

                # Wir nutzen hier den stabilsten Aufruf ohne das "Search Tool", 
                # da dies den 404 Fehler in der Schweiz oft auslöst.
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)

                # AUSGABE
                st.markdown("---")
                st.markdown(f"### Analysebericht: {company}")
                st.markdown('<div class="report-container">', unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.download_button("📥 Bericht exportieren", response.text, file_name=f"MP_Report_{company}.md")

            except Exception as e:
                st.error(f"Fehler: {str(e)}")

st.markdown("---")
st.caption("Powered by Marketingpoint AI | Gemini Engine")
