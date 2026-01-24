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

# --- CSS PER ESTETICA E PULIZIA ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    table { border-collapse: collapse !important; width: 100%; }
    th { background-color: #f8f9fa !important; border: 1px solid #dee2e6 !important; text-align: left !important; }
    td { border: 1px solid #dee2e6 !important; padding: 8px !important; text-align: left !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONE PER COSTRUIRE IL LINK DI ESPORTAZIONE ---
def get_google_sheet_url(sheet_name):
    try:
        sheet_id = URL_GOOGLE_SHEET.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
    except:
        return None

# --- FUNZIONE COLORAZIONE RIGHE ---
def colora_righe(row):
    valore_girone = ""
    for cella in row:
        if "Girone" in str(cella):
            valore_girone = str(cella)
            break
            
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
@st.cache_data(ttl=60)
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

        # Pulizia decimali e conversione NaN in stringa vuota
        df = df.fillna('') # Risolve il problema dei 'nan' visibili
        df = df.map(lambda x: str(x)[:-2] if str(x).endswith('.0') else str(x).strip())
        
        return df
    except:
        return pd.DataFrame()

# --- INTERFACCIA ---
st.title("🏆 Torneo One Wall - Accademia Pallapugno")

if st.sidebar.button("🔄 Aggiorna Dati Live"):
    st.cache_data.clear()
    st.rerun()

tab_gare, tab1, tab2, tab3 = st.tabs(["🎾 Gare Gironi", "📊 Classifiche", "⚔️ Playoff", "🏁 Tabelloni Finali"])

with tab_gare:
    st.subheader("Andamento Gare e Punteggi Live")
    df_g = carica_dati(TAB_GARE_GIRONI)
    if not df_g.empty:
        st.dataframe(df_g.style.apply(colora_righe, axis=1), use_container_width=True, hide_index=True)

with tab1:
    st.subheader("Classifica Gironi")
    df_c = carica_dati(TAB_CLASSIFICA)
    if not df_c.empty:
        df_styled = df_c.style.apply(colora_righe, axis=1)
        st.dataframe(
            df_styled, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Punti Totali": st.column_config.Column(
                    "Punti Totali",
                    width="small",
                    required=True,
                )
            }
        )

with tab2:
    st.subheader("Tabellone Playoff")
    # Carichiamo i dati dei playoff assicurandoci che non ci siano nan
    df_p = carica_dati(TAB_PLAYOFF)
    st.dataframe(df_p, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Tabelloni di Posizionamento Finale")
    st.dataframe(carica_dati(TAB_FINALI), use_container_width=True, hide_index=True)

st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
