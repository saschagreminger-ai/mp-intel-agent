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
    .report-container { background-color: white; padding: 25px; border-radius: 15px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_stdio=True)

# API SETUP
# Wir holen den Key sicher aus den Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Bitte API Key in den Secrets hinterlegen!")

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
    company = st.text_input("Name der Zielfirma")
with col2:
    contact = st.text_input("Ansprechperson (optional)")

if st.button("🔥 Deep Dive Recherche & Matching starten"):
    if not company or not ref_file:
        st.warning("⚠️ Bitte Firmennamen eingeben und Referenz-CSV in der Sidebar hochladen.")
    else:
        with st.spinner('Deep Research aktiv... Scanne Konzernstrukturen und Partner (CH/DACH/Global)...'):
            try:
                # Referenzen laden
                df = pd.read_csv(ref_file)
                ref_context = df.to_string()

                # Gemini Pro 1.5 mit SEARCH GROUNDING (verhindert Halluzinationen)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-pro",
                    tools=[{"google_search_retrieval": {}}] 
                )

                prompt = f"""
                Analysiere die Firma '{company}' extrem präzise für Account Manager '{contact}'.
                Nutze die Google Suche für exakte, aktuelle Daten.
                Marketingpoint Referenzen: {ref_context}

                AUFTRAG: Erstelle ein High-Density Dashboard (maximal 1 Seite).
                
                STRUKTUR:
                1. KONZERN: Wer ist das Mutterhaus? (Falls Tochtergesellschaft).
                2. KPI TABELLE: MA & Umsatz einzeln für CH, DACH, Global.
                3. BUSINESS & PARTNER: Kern-Fokus & Top 3 Technologie-Partner.
                4. MP PROOF: Wähle die 3 besten Referenzen aus der Liste. Begründe das Matching (Partner-Identität oder Branchen-Similarity).
                5. SALES INTEL: Schätze Marktgrösse DACH, Deal-Size, Cycle.
                6. 3 FRAGEN: Analytische Fragen für das Meeting.

                WICHTIG: Keine Füllwörter. Keine Einleitung. Nutze Tabellen. Markiere Schätzungen als (est.).
                """

                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown(f"### Analysebericht: {company}")
                st.markdown('<div class="report-container">', unsafe_allow_stdio=True)
                st.markdown(response.text)
                st.markdown('</div>', unsafe_allow_stdio=True)
                
                st.download_button("📥 Bericht exportieren", response.text, file_name=f"MP_Report_{company}.md")

            except Exception as e:
                st.error(f"Fehler: {str(e)}")

st.markdown("---")
st.caption("Powered by Marketingpoint AI | Gemini 1.5 Pro Search Engine")
