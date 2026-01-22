import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. UI DESIGN
st.set_page_config(page_title="MP Intel Agent", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        border-radius: 10px; background-color: #d32f2f; color: white; 
        height: 3.5em; width: 100%; font-weight: bold; border: none;
    }
    .report-container { 
        background-color: white; padding: 30px; border-radius: 15px; 
        border: 1px solid #e0e0e0; color: #1e1e1e;
    }
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
    st.info("Lade die CSV hoch, um das Referenz-Matching zu starten.")

# 4. MAIN INTERFACE
st.title("🏢 Swiss Company Intelligence")

col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Firmenname", placeholder="z.B. LOXY International AG")
with col2:
    contact = st.text_input("Ansprechperson", placeholder="z.B. Daniel Schnyder")

if st.button("🚀 Analyse starten"):
    if not company or not ref_file:
        st.warning("⚠️ Bitte Firmennamen eingeben und CSV hochladen.")
    else:
        with st.spinner('Analysiere Firma und Referenzen...'):
            try:
                # CSV einlesen
                try:
                    ref_content = ref_file.getvalue().decode("utf-8")
                except:
                    ref_content = ref_file.getvalue().decode("latin-1")

                # PROMPT
                prompt = f"""
                Analysiere die Firma '{company}' für Account Manager '{contact}'.
                Nutze dein Wissen über den Schweizer Markt.
                
                Marketingpoint Referenzen:
                {ref_content}

                AUFGABE (Dashboard-Stil):
                1. Struktur: Mutterhaus/Holding?
                2. Tabelle: Mitarbeiter & Umsatz für CH, DACH, Global.
                3. Business: Kern-Fokus & Top 3 Technologie-Partner.
                4. Matching: Nenne 3 passende Referenzen aus der Liste oben und begründe warum.
                5. Sales Intel: Marktgrösse DACH, Deal-Size, Cycle.
                6. 3 Fragen: Analytische Fragen für das Meeting.

                Antworte kurz, auf Deutsch, tabellarisch. Keine Einleitung.
                """

                # Wir probieren erst Flash, dann Pro (Fallback)
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                except:
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(prompt)
                
                if response.text:
                    st.markdown("---")
                    st.markdown(f"### Ergebnisse für {company}")
                    st.markdown('<div class="report-container">', unsafe_allow_html=True)
                    st.markdown(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("Keine Antwort von der KI.")

            except Exception as e:
                st.error(f"Fehler: {str(e)}")

st.caption("Powered by Marketingpoint AI")
