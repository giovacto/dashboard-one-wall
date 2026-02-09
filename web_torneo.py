import streamlit as st
import pandas as pd
import datetime

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Dashboard Torneo One Wall", layout="wide")

# --- 🟢 CONFIGURAZIONE GOOGLE SHEETS 🟢 ---
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1Cy0Splr65TWOD-F7PpLb1K_1fw7du_x1HvctafKkXv0/edit?usp=sharing"

TAB_GIRONI = 'Classifica Automatica'
TAB_PLAYOFF = 'PLAYOFF_INIZIO'
TAB_FINALI = 'TABELLONI_FINALI'

# --- CSS PER ESTETICA ---
st.markdown("""
<style>
    table { border-collapse: collapse !important; width: 100%; }
    th { background-color: #f8f9fa !important; border: 1px solid #dee2e6 !important; text-align: left !important; }
    td { border: 1px solid #dee2e6 !important; padding: 8px !important; text-align: left !important; }
</style>
""", unsafe_allow_html=True)

def get_google_sheet_url(sheet_name):
    try:
        sheet_id = URL_GOOGLE_SHEET.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
    except:
        return None

@st.cache_data(ttl=60)
def ottieni_vincitori_gironi():
    try:
        url = get_google_sheet_url(TAB_GIRONI)
        df_c = pd.read_csv(url)
        if not df_c.empty:
            df_c.columns = [str(c).strip() for c in df_c.columns]
            col_nome, col_girone, col_punti = 'Nome Giocatore', 'Girone', 'Punti Totali'
            if all(c in df_c.columns for c in [col_nome, col_girone, col_punti]):
                df_c[col_punti] = pd.to_numeric(df_c[col_punti], errors='coerce').fillna(0)
                idx = df_c.groupby(col_girone)[col_punti].idxmax()
                return df_c.loc[idx, col_nome].astype(str).str.strip().tolist()
    except: pass
    return []

@st.cache_data(ttl=60)
def carica_dati(nome_foglio):
    try:
        url = get_google_sheet_url(nome_foglio)
        if not url: return pd.DataFrame()
        df = pd.read_csv(url)
        
        # --- LOGICA ROBUSTA PER TABELLONI FINALI ---
        if nome_foglio == TAB_FINALI:
            # Cerchiamo la riga che contiene la parola 'Fase' o 'VINCENTE'
            header_idx = None
            for i in range(min(10, len(df))):
                row_values = [str(x).strip().upper() for x in df.iloc[i].values]
                if 'FASE' in row_values or 'VINCENTE' in row_values:
                    header_idx = i
                    break
            
            if header_idx is not None:
                # Impostiamo i nomi delle colonne puliti
                new_cols = []
                for j, val in enumerate(df.iloc[header_idx]):
                    val_str = str(val).strip()
                    if val_str == 'nan' or not val_str:
                        new_cols.append(f"col_{j}")
                    else:
                        new_cols.append(val_str)
                df.columns = new_cols
                df = df.iloc[header_idx+1:].reset_index(drop=True)

        # Pulizia colonne Unnamed o senza nome
        df = df.loc[:, ~df.columns.astype(str).str.contains('Unnamed|nan|^col_')]
        
        # Pulizia valori decimali e NaN
        def clean_val(val):
            if pd.isna(val) or str(val).lower() == 'nan': return ''
            s = str(val).strip()
            return s[:-2] if s.endswith('.0') else s

        df = df.map(clean_val) if hasattr(df, 'map') else df.applymap(clean_val)
        
        # Medaglia dinamica per i gironi
        if nome_foglio == TAB_GIRONI and 'Nome Giocatore' in df.columns:
            vincitori = ottieni_vincitori_gironi()
            df['Nome Giocatore'] = df['Nome Giocatore'].apply(
                lambda x: f"{x} 🥇" if x in vincitori else x
            )
        
        return df.fillna('')
    except Exception as e:
        st.error(f"Errore caricamento {nome_foglio}: {e}")
        return pd.DataFrame()

# --- FUNZIONE DI COLORAZIONE SICURA ---
def colora_tabellone(df):
    # Crea un dataframe di stili vuoti (stessa forma dell'originale)
    style_df = pd.DataFrame('', index=df.index, columns=df.columns)
    
    # Verifichiamo se esistono le colonne necessarie
    cols = df.columns.tolist()
    if 'VINCENTE' not in cols: return style_df
    
    for idx, row in df.iterrows():
        vincitore = str(row['VINCENTE']).strip()
        if vincitore:
            # Colora di verde lo Sfidante 1 se ha vinto
            if 'Sfidante 1' in cols and vincitore == str(row['Sfidante 1']).strip():
                style_df.at[idx, 'Sfidante 1'] = 'background-color: #d4edda; font-weight: bold; color: #155724'
            # Colora di verde lo Sfidante 2 se ha vinto
            if 'Sfidante 2' in cols and vincitore == str(row['Sfidante 2']).strip():
                style_df.at[idx, 'Sfidante 2'] = 'background-color: #d4edda; font-weight: bold; color: #155724'
    return style_df

# --- INTERFACCIA ---
st.title("🏆 Torneo One Wall - Accademia Pallapugno")

if st.sidebar.button("🔄 Aggiorna Dati Live"):
    st.cache_data.clear()
    st.rerun()

tab1, tab2, tab3 = st.tabs(["📊 Classifiche Gironi", "⚔️ Playoff", "🏁 Tabelloni Finali"])

with tab1:
    st.subheader("Classifica Gironi (🥇 calcolata in tempo reale)")
    df1 = carica_dati(TAB_GIRONI)
    st.dataframe(df1, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Tabellone Playoff")
    df2 = carica_dati(TAB_PLAYOFF)
    st.dataframe(df2, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Tabelloni di Posizionamento Finale")
    df_f = carica_dati(TAB_FINALI)
    if not df_f.empty:
        # Applichiamo la colorazione in modo sicuro
        try:
            st.dataframe(df_f.style.apply(colora_tabellone, axis=None), use_container_width=True, hide_index=True)
        except:
            # Se lo stile fallisce ancora, mostra i dati semplici per non bloccare l'app
            st.dataframe(df_f, use_container_width=True, hide_index=True)
    else:
        st.info("Dati dei tabelloni finali non ancora disponibili.")

st.markdown("---")
st.caption(f"Ultimo aggiornamento: {datetime.datetime.now().strftime('%H:%M:%S')}")
