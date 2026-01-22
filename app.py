import streamlit as st
import pandas as pd
import requests
import json

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
api_key = st.secrets.get("GEMINI_API_KEY")

# 3. SIDEBAR
with st.sidebar:
    st.title("🛡️ Marketingpoint")
    st.subheader("Wissensbasis")
    ref_file = st.file_uploader("Referenzliste (CSV) hochladen", type="csv")

# 4. MAIN INTERFACE
st.title("🏢 Swiss Company Intelligence")

col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Firmenname", placeholder="z.B. LOXY International AG")
with col2:
    contact = st.text_input("Ansprechperson", placeholder="z.B. Daniel Schnyder")

if st.button("🚀 Analyse starten"):
    if not company or not ref_file or not api_key:
        st.warning("⚠️ Bitte Daten eingeben, CSV hochladen und API-Key prüfen.")
    else:
        with st.spinner('Analysiere Firma und Referenzen über stabile Leitung...'):
            try:
                # CSV einlesen
                try:
                    ref_content = ref_file.getvalue().decode("utf-8")
                except:
                    ref_content = ref_file.getvalue().decode("latin-1")

                # STABILER API AUFRUF (v1 statt v1beta)
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": f"Analysiere die Firma '{company}' für Account Manager '{contact}'. Referenzen: {ref_content}. Erstelle ein kurzes B2B Dashboard auf Deutsch mit Konzernstruktur, MA/Umsatz Tabelle (CH/DACH/Global), 3 Referenz-Matches aus der Liste, Sales Metrics und 3 Fragen."
                        }]
                    }]
                }

                response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
                data = response.json()

                if response.status_code == 200:
                    answer = data['candidates'][0]['content']['parts'][0]['text']
                    st.markdown("---")
                    st.markdown(f"### Ergebnisse für {company}")
                    st.markdown('<div class="report-container">', unsafe_allow_html=True)
                    st.markdown(answer)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error(f"API Fehler {response.status_code}: {data.get('error', {}).get('message', 'Unbekannter Fehler')}")
                    st.info("Versuche es mit Modell 'gemini-pro'...")
                    # Fallback auf gemini-pro
                    url_pro = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
                    response = requests.post(url_pro, json=payload)
                    st.markdown(response.json()['candidates'][0]['content']['parts'][0]['text'])

            except Exception as e:
                st.error(f"Technischer Fehler: {str(e)}")

st.caption("Powered by Marketingpoint AI | Direct API Access")
