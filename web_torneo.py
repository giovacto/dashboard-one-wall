import streamlit as st
import pandas as pd
import datetime

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Dashboard Torneo One Wall", layout="wide")

# --- 🟢 CONFIGURAZIONE GOOGLE SHEETS 🟢 ---
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1Cy0Splr65TWOD-F7PpLb1K_1fw7du_x1HvctafKkXv0/edit?usp=sharing"

TAB_GARE_GIRONI = 'Gironi'
TAB_CLASSIFICA = 'Classifica Automatica'
TAB_PLAYOFF = 'PLAYOFF_INIZIO'
TAB_FINALI = 'TABELLONI_FINALI'

# --- FUNZIONE PER COSTRUIRE IL LINK DI ESPORTAZIONE ---
def get_google_sheet_url(sheet_name):
    try:
        sheet_id = URL_GOOGLE_SHEET.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
    except:
        return None

# --- FUNZIONE COLORAZIONE GIRONI ---
def colora_righe_gironi(row):
    valore_girone = str(row.iloc[0])
    colori = {
        'Girone 1': 'background-color: #fce4ec',
        'Girone 2': 'background-color: #e8f5e9',
        'Girone 3': 'background-color: #e3f2fd',
        'Girone 4': 'background-color: #fffde7',
        'Girone 5': 'background-color: #f3e5f5',
        'Girone 6': 'background-color: #e0f7fa',
        'Girone 7': 'background-color: #fff3e0',
        'Girone 8': 'background-color: #efebe9'
    }
    return [colori.get(valore_girone, '')] * len(row)

# --- FUNZIONE CARICAMENTO DATI ---
@st.cache_data(ttl=60) # Aggiorna ogni minuto
def carica_dati(nome_foglio):
    try:
        url = get_google_sheet_url(nome_foglio)
        df = pd.read_csv(url)
        
        # Pulizia universale colonne Unnamed
        df = df.loc[:, ~df.columns.astype(str).str.contains('Unnamed|nan|^$')]

        if nome_foglio == TAB_GARE_GIRONI:
            df = df.iloc[:, :11] 
        elif nome_foglio == TAB_CLASSIFICA:
            df = df.iloc[:, :3]
        elif nome_foglio == TAB_PLAYOFF:
            if "PERDENTE" in df.columns:
                idx = df.columns.get_loc("PERDENTE")
                df = df.iloc[:, :idx + 1]
        elif nome_foglio == TAB_FINALI:
            if not df.empty and 'Fase' not in df.columns:
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)
            df = df.loc[:, ~df.columns.astype(str).str.contains('Unnamed|nan|^$')]

        # Pulizia decimali (usa map invece di applymap per evitare avvisi)
        df = df.map(lambda x: str(x)[:-2] if str(x).endswith('.0') else x)
        return df.fillna('')
    except:
        return pd.DataFrame()

# --- INTERFACCIA ---
st.title("🏆 Torneo One Wall - Accademia Pallapugno")

if st.sidebar.button("🔄 Aggiorna Dati Live"):
    st.cache_data.clear()
    st.rerun()

tab_gare, tab1, tab2, tab3 = st.tabs(["🎾 Gare Gironi", "📊 Classifiche", "⚔️ Playoff", "🏁 Tabelloni Finali"])

with tab_gare:
    df_g = carica_dati(TAB_GARE_GIRONI)
    if not df_g.empty:
        st.dataframe(df_g.style.apply(colora_righe_gironi, axis=1), use_container_width=True, hide_index=True)

with tab1:
    st.dataframe(carica_dati(TAB_CLASSIFICA), use_container_width=True, hide_index=True)

with tab2:
    st.dataframe(carica_dati(TAB_PLAYOFF), use_container_width=True, hide_index=True)

with tab3:
    st.dataframe(carica_dati(TAB_FINALI), use_container_width=True, hide_index=True)

st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
