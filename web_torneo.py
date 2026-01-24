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

# --- CSS PER PULIZIA INTERFACCIA ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- FUNZIONI DI SUPPORTO ---
def get_google_sheet_url(sheet_name):
    try:
        sheet_id = URL_GOOGLE_SHEET.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
    except: return None

@st.cache_data(ttl=30)
def carica_e_pulisci(nome_foglio):
    try:
        url = get_google_sheet_url(nome_foglio)
        df = pd.read_csv(url)
        
        # Selezione colonne per tipo di foglio
        if nome_foglio == TAB_GARE_GIRONI:
            df = df.iloc[:, :11]
        elif nome_foglio == TAB_CLASSIFICA:
            df = df.iloc[:, :3]
        elif nome_foglio == TAB_PLAYOFF:
            df = df.iloc[:, :12]
        elif nome_foglio == TAB_FINALI:
            df = df.iloc[:, :15] # Prende tutte le colonne fino a Vincente/Perdente
            if not df.empty and 'Fase' not in str(df.columns):
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)

        # 🛑 PULIZIA TOTALE ANTI-CRASH
        # Trasformiamo tutto in stringa PRIMA di ogni operazione
        df = df.astype(str).replace('nan', '', regex=True).replace('NaN', '', regex=True)
        
        # Rimuoviamo i decimali .0 e puliamo gli spazi
        df = df.apply(lambda x: x.str.replace(r'\.0$', '', regex=True).str.strip())
        
        return df.fillna('')
    except: return pd.DataFrame()

# --- INTERFACCIA ---
st.title("🏆 Torneo One Wall - Accademia Pallapugno")

if st.sidebar.button("🔄 Aggiorna Dati Live"):
    st.cache_data.clear()
    st.rerun()

t_gare, t_class, t_play, t_fin = st.tabs(["🎾 Gare Gironi", "📊 Classifiche", "⚔️ Playoff", "🏁 Tabelloni Finali"])

# Funzione per applicare i colori in modo sicuro (senza crash JSON)
def applica_stile_sicuro(df, tipo="gironi"):
    if df.empty: return df
    
    if tipo == "gironi":
        return df.style.map(lambda x: 'font-weight: bold' if 'Girone' in str(x) else '')
    
    if tipo == "finali":
        # Evidenziamo solo le righe dei titoli per evitare sfasamenti JSON
        return df.style.map(lambda x: 'background-color: #cfd8dc; font-weight: bold' if any(tit in str(x).upper() for tit in ["POSIZIONI", "QUARTI", "SEMI", "FINALE"]) else '')

with t_gare:
    df = carica_e_pulisci(TAB_GARE_GIRONI)
    st.dataframe(applica_stile_sicuro(df, "gironi"), use_container_width=True, hide_index=True)

with t_class:
    df = carica_e_pulisci(TAB_CLASSIFICA)
    st.dataframe(applica_stile_sicuro(df, "gironi"), use_container_width=True, hide_index=True)

with t_play:
    st.dataframe(carica_e_pulisci(TAB_PLAYOFF), use_container_width=True, hide_index=True)

with t_fin:
    df = carica_e_pulisci(TAB_FINALI)
    if not df.empty:
        # Mostriamo il tabellone completo con tutte le colonne
        st.dataframe(applica_stile_sicuro(df, "finali"), use_container_width=True, hide_index=True)

st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
