import streamlit as st
import pandas as pd
import os
import datetime

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Dashboard Torneo One Wall", layout="wide")

# --- 🟢 CONFIGURAZIONE GOOGLE SHEETS 🟢 ---
# Incolla qui il link del tuo foglio Google Sheets (assicurati che sia condiviso come "Chiunque abbia il link")
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1Cy0Splr65TWOD-F7PpLb1K_1fw7du_x1HvctafKkXv0/edit?usp=sharing"

# Nomi esatti dei fogli (devono corrispondere a quelli su Google Sheets)
TAB_GIRONI = 'Classifica Automatica'
TAB_PLAYOFF = 'PLAYOFF_INIZIO'
TAB_FINALI = 'TABELLONI_FINALI'

# --- CSS PER ESTETICA ---
st.markdown("""
<style>
    table { border-collapse: collapse !important; width: 100%; }
    th { background-color: #f8f9fa !important; border: 1px solid #dee2e6 !important; text-align: left !important; }
    td { border: 1px solid #dee2e6 !important; padding: 8px !important; text-align: left !important; }
    thead tr th:first-child { display:none; }
    tbody tr td:first-child { display:none; }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONE PER COSTRUIRE IL LINK DI ESPORTAZIONE ---
def get_google_sheet_url(sheet_name):
    try:
        # Estraiamo l'ID del foglio dal link fornito
        sheet_id = URL_GOOGLE_SHEET.split("/d/")[1].split("/")[0]
        # Creiamo il link per scaricare direttamente in formato CSV la scheda specifica
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
    except:
        return None

# --- FUNZIONE VINCITORI DINAMICI ---
def ottieni_vincitori_gironi():
    try:
        url = get_google_sheet_url(TAB_GIRONI)
        df_c = pd.read_csv(url)
        if not df_c.empty:
            col_nome = 'Nome Giocatore'
            col_girone = 'Girone'
            col_punti = 'Punti Totali'
            df_c[col_punti] = pd.to_numeric(df_c[col_punti], errors='coerce').fillna(0)
            idx = df_c.groupby(col_girone)[col_punti].idxmax()
            return df_c.loc[idx, col_nome].astype(str).str.strip().tolist()
    except:
        pass
    return []

# --- FUNZIONE CARICAMENTO DATI ---
def carica_dati(nome_foglio):
    try:
        url = get_google_sheet_url(nome_foglio)
        if not url:
            st.error("Link Google Sheets non valido.")
            return pd.DataFrame()

        # Leggiamo il CSV dal web
        df = pd.read_csv(url)
        
        # Pulizia intestazioni per i tabelloni finali
        if nome_foglio == TAB_FINALI:
            # Riconosciamo la riga con "Fase" per promuoverla a header
            if not df.empty and 'Fase' in str(df.iloc[0,0]):
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)
            # Rimuoviamo colonne vuote (Unnamed)
            df = df.loc[:, ~df.columns.astype(str).str.contains('Unnamed|nan|^$')]

        # Funzione pulizia decimali .0
        def pulisci_decimali(valore):
            if pd.isna(valore) or valore == '': return ''
            s = str(valore)
            return s[:-2] if s.endswith('.0') else s
        
        df = df.applymap(pulisci_decimali)
        
        # Medaglia Dinamica (solo nella TAB Classifica)
        if nome_foglio == TAB_GIRONI:
            lista_vincitori = ottieni_vincitori_gironi()
            if lista_vincitori and 'Nome Giocatore' in df.columns:
                df['Nome Giocatore'] = df['Nome Giocatore'].apply(
                    lambda x: f"{str(x).strip()} 🥇" if str(x).strip() in lista_vincitori else x
                )
        
        return df.fillna('')
    except Exception as e:
        st.error(f"Errore nel caricamento del foglio '{nome_foglio}': {e}")
        return pd.DataFrame()

# --- INTERFACCIA ---
st.title("🏆 Torneo One Wall - Accademia Pallapugno")

# Pulsante aggiornamento nella barra laterale
if st.sidebar.button("🔄 Aggiorna Dati Live"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.info("Modifica i dati su Google Sheets e clicca 'Aggiorna' per vedere i risultati sul sito.")

tab1, tab2, tab3 = st.tabs(["📊 Classifiche Gironi", "⚔️ Playoff", "🏁 Tabelloni Finali"])

with tab1:
    st.subheader("Classifica Gironi (🥇 calcolata in tempo reale)")
    st.dataframe(carica_dati(TAB_GIRONI), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Tabellone Playoff")
    st.dataframe(carica_dati(TAB_PLAYOFF), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Tabelloni di Posizionamento Finale")
    df_f = carica_dati(TAB_FINALI)
    if not df_f.empty:
        st.table(df_f)

st.markdown("---")
st.caption(f"Ultimo controllo: {datetime.datetime.now().strftime('%H:%M:%S')} | Dati sincronizzati con Google Sheets")