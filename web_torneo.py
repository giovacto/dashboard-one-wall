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

# --- CSS PER PULIZIA ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    table { border-collapse: collapse !important; width: 100%; }
    th { background-color: #f0f2f6 !important; border: 1px solid #dee2e6 !important; text-align: center !important; color: black !important; font-weight: bold; }
    td { border: 1px solid #dee2e6 !important; padding: 6px !important; }
</style>
""", unsafe_allow_html=True)

def get_google_sheet_url(sheet_name):
    try:
        sheet_id = URL_GOOGLE_SHEET.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
    except:
        return None

# --- FUNZIONE COLORAZIONE GIRONI ---
def colora_righe_gironi(row):
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

# --- FUNZIONE COLORAZIONE TABELLONE FINALE (SICURA) ---
def colora_tabellone_finale(df):
    # Creiamo una maschera di stili vuota
    style_df = pd.DataFrame('', index=df.index, columns=df.columns)
    
    current_section = "top" # Default per 1-8
    
    for i in range(len(df)):
        fase_text = str(df.iloc[i, 0]).upper() # Legge la colonna "Fase"
        
        # Cambio sezione in base al testo trovato
        if "9-16" in fase_text:
            current_section = "bottom"
        elif "1-8" in fase_text:
            current_section = "top"
            
        # Determina il colore di base
        if any(keyword in fase_text for keyword in ["POSIZIONI", "QUARTI DI", "SEMIFINALI", "FINALI POSIZ"]):
            color = 'background-color: #eeeeee; font-weight: bold;' # Grigio intestazione
        elif current_section == "top":
            color = 'background-color: #f0f7ff;' # Azzurro molto tenue
        else:
            color = 'background-color: #fff5f0;' # Arancio/Rosa molto tenue
            
        style_df.iloc[i, :] = color
        
    return style_df

# --- CARICAMENTO DATI ---
@st.cache_data(ttl=30)
def carica_dati(nome_foglio):
    try:
        url = get_google_sheet_url(nome_foglio)
        if nome_foglio == TAB_FINALI:
            df = pd.read_csv(url, header=None).iloc[:, 0:13]
            df.columns = df.iloc[1].fillna('').astype(str).tolist()
            df = df.iloc[2:].reset_index(drop=True)
        elif nome_foglio == TAB_GARE_GIRONI:
            df = pd.read_csv(url).iloc[:, :11]
        elif nome_foglio == TAB_CLASSIFICA:
            df = pd.read_csv(url).iloc[:, :3]
        else:
            df = pd.read_csv(url)

        df = df.fillna('').astype(str)
        df = df.map(lambda x: x[:-2] if x.endswith('.0') else x)
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
    df_g = carica_dati(TAB_GARE_GIRONI)
    if not df_g.empty:
        st.dataframe(df_g.style.apply(colora_righe_gironi, axis=1), use_container_width=True, hide_index=True)

with tab1:
    df_c = carica_dati(TAB_CLASSIFICA)
    if not df_c.empty:
        st.dataframe(df_c.style.apply(colora_righe_gironi, axis=1), use_container_width=True, hide_index=True)

with tab2:
    st.dataframe(carica_dati(TAB_PLAYOFF), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Tabelloni di Posizionamento Finale")
    df_f = carica_dati(TAB_FINALI)
    if not df_f.empty:
        # Applichiamo la colorazione differenziata
        st.dataframe(df_f.style.apply(colora_tabellone_finale, axis=None), use_container_width=True, hide_index=True)

st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
