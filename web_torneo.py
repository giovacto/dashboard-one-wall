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

# --- FUNZIONI DI SUPPORTO ---
def get_google_sheet_url(sheet_name):
    try:
        sheet_id = URL_GOOGLE_SHEET.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
    except: return None

# --- NUOVA FUNZIONE COLORE SICURA (Anti-Crash JSON) ---
def applica_stile_sicuro(row, tipo="gironi"):
    # Cerchiamo il valore del girone o della fase nella riga
    testo_riga = " ".join(row.astype(str)).upper()
    
    # Stile per Gare e Classifiche
    if tipo == "gironi":
        colori = {
            'GIRONE 1': 'background-color: #fce4ec', 'GIRONE 2': 'background-color: #e8f5e9',
            'GIRONE 3': 'background-color: #e3f2fd', 'GIRONE 4': 'background-color: #fffde7',
            'GIRONE 5': 'background-color: #f3e5f5', 'GIRONE 6': 'background-color: #e0f7fa',
            'GIRONE 7': 'background-color: #fff3e0', 'GIRONE 8': 'background-color: #efebe9'
        }
        for g, col in colori.items():
            if g in testo_riga: return [col] * len(row)
            
    # Stile per Tabellone Finale (Azzurro per 1-8, Rosso per 9-16)
    if tipo == "finali":
        if any(x in testo_riga for x in ["POSIZIONI", "QUARTI", "SEMI", "FINALE", "MATCH"]):
            return ['background-color: #cfd8dc; font-weight: bold; color: black'] * len(row)
        if "9-16" in testo_riga or row.name > 15: # Fallback sulla riga se il testo manca
            return ['background-color: #ffebee'] * len(row)
        return ['background-color: #e3f2fd'] * len(row)
        
    return [''] * len(row)

@st.cache_data(ttl=20)
def carica_e_bonifica(nome_foglio):
    try:
        url = get_google_sheet_url(nome_foglio)
        # Leggiamo tutto come stringa per evitare i NaN matematici
        df = pd.read_csv(url, dtype=str).fillna('')
        
        # Pulizia colonne Unnamed
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
            df = df.iloc[:, :15] # Include Vincente e Perdente
            if not df.empty and 'Fase' not in str(df.columns):
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)

        # Pulizia finale testi e decimali
        df = df.map(lambda x: x[:-2] if str(x).endswith('.0') else str(x).strip())
        return df
    except: return pd.DataFrame()

# --- INTERFACCIA ---
st.title("🏆 Torneo One Wall - Accademia Pallapugno")

if st.sidebar.button("🔄 Aggiorna Dati Live"):
    st.cache_data.clear()
    st.rerun()

t_gare, t_class, t_play, t_fin = st.tabs(["🎾 Gare Gironi", "📊 Classifiche", "⚔️ Playoff", "🏁 Tabelloni Finali"])

with t_gare:
    df = carica_e_bonifica(TAB_GARE_GIRONI)
    if not df.empty:
        st.dataframe(df.style.apply(applica_stile_sicuro, tipo="gironi", axis=1), use_container_width=True, hide_index=True)

with t_class:
    df = carica_e_bonifica(TAB_CLASSIFICA)
    if not df.empty:
        st.dataframe(df.style.apply(applica_stile_sicuro, tipo="gironi", axis=1), use_container_width=True, hide_index=True)

with t_play:
    st.dataframe(carica_e_bonifica(TAB_PLAYOFF), use_container_width=True, hide_index=True)

with t_fin:
    df = carica_e_bonifica(TAB_FINALI)
    if not df.empty:
        st.dataframe(df.style.apply(applica_stile_sicuro, tipo="finali", axis=1), use_container_width=True, hide_index=True)

st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
