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

# --- CSS PER PULIZIA TOTALE (Rimosso ogni grigio) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Forza sfondo bianco su tutto */
    .stDataFrame, div[data-testid="stTable"] { background-color: white !important; }
    table { border-collapse: collapse !important; width: 100%; }
    th { background-color: #f0f2f6 !important; border: 1px solid #dee2e6 !important; text-align: center !important; color: black !important; }
    td { border: 1px solid #dee2e6 !important; padding: 8px !important; background-color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONE LINK GOOGLE ---
def get_google_sheet_url(sheet_name):
    try:
        sheet_id = URL_GOOGLE_SHEET.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
    except:
        return None

# --- FUNZIONE COLORAZIONE GIRONI (Rimane come la volevi) ---
def colora_righe(row):
    valore_girone = ""
    for cella in row:
        if "Girone" in str(cella):
            valore_girone = str(cella)
            break
    colori = {
        'Girone 1': 'background-color: #fce4ec', 'Girone 2': 'background-color: #e8f5e9',
        'Girone 3': 'background-color: #e3f2fd', 'Girone 4': 'background-color: #fffde7',
        'Girone 5': 'background-color: #f3e5f5', 'Girone 6': 'background-color: #e0f7fa',
        'Girone 7': 'background-color: #fff3e0', 'Girone 8': 'background-color: #efebe9'
    }
    return [colori.get(valore_girone, '')] * len(row)

# --- FUNZIONE CARICAMENTO DATI (Corretta per Tabelloni Finali) ---
@st.cache_data(ttl=30)
def carica_dati(nome_foglio):
    try:
        url = get_google_sheet_url(nome_foglio)
        # Leggiamo il CSV senza intestazioni predefinite per gestire le righe vuote di Google
        df = pd.read_csv(url, header=None)

        if nome_foglio == TAB_FINALI:
            # 1. Prendiamo le colonne dalla A alla M (indice 0 a 12)
            df = df.iloc[:, 0:13]
            
            # 2. La riga 2 del foglio (indice 1) contiene le vere intestazioni: Fase, ID Match, ecc.
            # La riga 1 (indice 0) contiene Column1, Column2... la saltiamo.
            nuove_colonne = df.iloc[1].tolist()
            df.columns = nuove_colonne
            
            # 3. Teniamo i dati dalla riga 3 in poi (indice 2)
            df = df.iloc[2:].reset_index(drop=True)
            
        elif nome_foglio == TAB_GARE_GIRONI:
            df = pd.read_csv(url).iloc[:, :11]
        elif nome_foglio == TAB_CLASSIFICA:
            df = pd.read_csv(url).iloc[:, :3]
        else:
            df = pd.read_csv(url)

        # Pulizia NaN e decimali .0
        df = df.fillna('')
        df = df.astype(str).map(lambda x: x[:-2] if x.endswith('.0') else x.strip())
        return df
    except Exception as e:
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
        st.dataframe(df_g.style.apply(colora_righe, axis=1), use_container_width=True, hide_index=True)

with tab1:
    df_c = carica_dati(TAB_CLASSIFICA)
    if not df_c.empty:
        st.dataframe(df_c.style.apply(colora_righe, axis=1), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Tabellone Playoff")
    st.dataframe(carica_dati(TAB_PLAYOFF), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Tabelloni di Posizionamento Finale")
    df_f = carica_dati(TAB_FINALI)
    if not df_f.empty:
        # Visualizzazione pulita Bianco/Nero, con tutte le colonne fino a PERDENTE
        st.dataframe(df_f, use_container_width=True, hide_index=True)

st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
