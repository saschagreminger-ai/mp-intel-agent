import streamlit as st
import pandas as pd
import requests
import json

# 1. UI DESIGN
st.set_page_config(page_title="MP Intel Agent", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 10px; background-color: #d32f2f; color: white; height: 3.5em; width: 100%; font-weight: bold; border: none; }
    .report-container { background-color: white; padding: 30px; border-radius: 15px; border: 1px solid #e0e0e0; color: #1e1e1e; }
    </style>
    """, unsafe_allow_html=True)

# 2. API SETUP
api_key = st.secrets.get("GEMINI_API_KEY")

# 3. SIDEBAR
with st.sidebar:
    st.title("🛡️ Marketingpoint")
    ref_file = st.file_uploader("Referenzliste (CSV) hochladen", type="csv")
    if st.button("Verfügbare Modelle prüfen"):
        if api_key:
            res = requests.get(f"https://generativelanguage.googleapis.com/v1/models?key={api_key}")
            st.write(res.json())

# 4. MAIN INTERFACE
st.title("🏢 Swiss Company Intelligence")

col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Name der Zielfirma")
with col2:
    contact = st.text_input("Ansprechperson")

if st.button("🚀 Deep Dive starten"):
    if not company or not ref_file or not api_key:
        st.warning("⚠️ Daten fehlen.")
    else:
        with st.spinner('Suche passendes Modell und analysiere...'):
            try:
                # 1. Schritt: Verfügbare Modelle finden
                models_url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
                m_res = requests.get(models_url).json()
                
                # Wir suchen nach 1.5-flash, 1.5-pro oder gemini-pro
                available_models = [m['name'] for m in m_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                
                selected_model = ""
                for preferred in ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]:
                    if preferred in available_models:
                        selected_model = preferred
                        break
                
                if not selected_model and available_models:
                    selected_model = available_models[0]
                
                if not selected_model:
                    st.error("Kein passendes KI-Modell in deinem Account gefunden.")
                else:
                    # 2. Schritt: Analyse mit dem gefundenen Modell
                    try:
                        ref_content = ref_file.getvalue().decode("utf-8")
                    except:
                        ref_content = ref_file.getvalue().decode("latin-1")

                    url = f"https://generativelanguage.googleapis.com/v1/{selected_model}:generateContent?key={api_key}"
                    
                    prompt = f"Analysiere {company} (Ansprechpartner: {contact}). Referenzen: {ref_content}. Erstelle ein B2B Dashboard auf Deutsch (Struktur, MA/Umsatz CH/DACH/Global, 3 passende Referenzen, Sales Metrics, 3 Fragen)."
                    
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    response = requests.post(url, json=payload)
                    data = response.json()

                    if response.status_code == 200:
                        answer = data['candidates'][0]['content']['parts'][0]['text']
                        st.markdown("---")
                        st.markdown(f"### Ergebnisse via {selected_model}")
                        st.markdown('<div class="report-container">', unsafe_allow_html=True)
                        st.markdown(answer)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"Fehler {response.status_code}: {data}")

            except Exception as e:
                st.error(f"Technischer Fehler: {str(e)}")

st.caption("Powered by Marketingpoint AI")
