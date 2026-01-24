import streamlit as st
import pandas as pd
import datetime

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Dashboard Torneo One Wall", layout="wide")

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

def colora_gironi(row):
    valore = str(row.iloc[0])
    colori = {
        'Girone 1': 'background-color: #fce4ec', 'Girone 2': 'background-color: #e8f5e9',
        'Girone 3': 'background-color: #e3f2fd', 'Girone 4': 'background-color: #fffde7',
        'Girone 5': 'background-color: #f3e5f5', 'Girone 6': 'background-color: #e0f7fa',
        'Girone 7': 'background-color: #fff3e0', 'Girone 8': 'background-color: #efebe9'
    }
    return [colori.get(valore, '')] * len(row)

def stile_tabellone_finale(df):
    styles = pd.DataFrame('', index=df.index, columns=df.columns)
    blocco = "upper"
    for i in range(len(df)):
        testo_riga = " ".join(df.iloc[i].astype(str)).upper()
        
        # Cambio blocco
        if "9-16" in testo_riga: blocco = "lower"
        elif "1-8" in testo_riga: blocco = "upper"
        
        # Colore base
        sfondo = "background-color: #e3f2fd" if blocco == "upper" else "background-color: #ffebee"
        
        # Se è un'intestazione o riga vuota importante, grigio
        if any(x in testo_riga for x in ["POSIZIONI", "QUARTI", "SEMI", "FINALE", "MATCH", "FASE"]):
            sfondo = "background-color: #cfd8dc; font-weight: bold; color: black;"
            
        styles.iloc[i, :] = sfondo
    return styles

@st.cache_data(ttl=60)
def carica_dati(nome_foglio):
    try:
        url = get_google_sheet_url(nome_foglio)
        df = pd.read_csv(url)
        
        if nome_foglio == TAB_GARE_GIRONI: df = df.iloc[:, :11]
        elif nome_foglio == TAB_CLASSIFICA: df = df.iloc[:, :3]
        elif nome_foglio == TAB_PLAYOFF:
            df = df.fillna('')
            if "PERDENTE" in df.columns:
                idx = df.columns.get_loc("PERDENTE")
                df = df.iloc[:, :idx + 1]
        elif nome_foglio == TAB_FINALI:
            df = df.iloc[:, :13] # Aumentato per includere TB_G2, Vincitore, Perdente
            if not df.empty and 'Fase' not in str(df.columns):
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)

        # Pulizia anti-crash NaN
        df = df.fillna('').astype(str)
        df = df.map(lambda x: x[:-2] if x.endswith('.0') else ("" if x.lower() == "nan" else x.strip()))
        return df
    except: return pd.DataFrame()

# --- INTERFACCIA ---
st.title("🏆 Torneo One Wall - Accademia Pallapugno")

if st.sidebar.button("🔄 Aggiorna Dati Live"):
    st.cache_data.clear()
    st.rerun()

t_gare, t_class, t_play, t_fin = st.tabs(["🎾 Gare Gironi", "📊 Classifiche", "⚔️ Playoff", "🏁 Tabelloni Finali"])

with t_gare:
    df = carica_dati(TAB_GARE_GIRONI)
    if not df.empty: st.dataframe(df.style.apply(colora_gironi, axis=1), use_container_width=True, hide_index=True)

with t_class:
    df = carica_dati(TAB_CLASSIFICA)
    if not df.empty: st.dataframe(df.style.apply(colora_gironi, axis=1), use_container_width=True, hide_index=True)

with t_play:
    st.dataframe(carica_dati(TAB_PLAYOFF), use_container_width=True, hide_index=True)

with t_fin:
    df = carica_dati(TAB_FINALI)
    if not df.empty:
        st.dataframe(df.style.apply(stile_tabellone_finale, axis=None), use_container_width=True, hide_index=True)

st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
