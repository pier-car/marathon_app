import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# Configurazione Pagina (Deve essere la prima istruzione Streamlit)
st.set_page_config(page_title="Mission 4:35 - Pier", page_icon="🏃‍♂️", layout="wide")

def check_password():
    if st.session_state.get("password_correct", False):
        return True
    st.title("🔐 Accesso Riservato")
    password = st.text_input("Password", type="password")
    if st.button("Entra"):
        if password == "pier2026":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Password errata")
    return False

if check_password():
    # --- HEADER ---
    st.title("🏃‍♂️ Road to 18 Aprile: Target 4:35")
    
    # Calcolo Giorni Mancanti
    giorni_mancanti = (date(2026, 4, 18) - date.today()).days
    st.metric("Conto alla rovescia", f"{giorni_mancanti} Giorni alla Gara")

    # --- LAYOUT A COLONNE ---
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📝 Registra Allenamento")
        with st.form("workout_form", clear_on_submit=True):
            d = st.date_input("Data", date.today())
            k = st.number_input("Distanza (Km)", min_value=0.1, step=0.1)
            p = st.number_input("Passo Medio (min/km)", min_value=3.0, value=4.40, step=0.01)
            tipo = st.selectbox("Tipo", ["Lento", "Medio", "Ripetute", "Lungo"])
            
            if st.form_submit_button("Salva Sessione"):
                conn = sqlite3.connect('maratona.db')
                c = conn.cursor()
                c.execute("INSERT INTO allenamenti (data, km, passo_min_km, tipo) VALUES (?, ?, ?, ?)", (d, k, p, tipo))
                conn.commit()
                conn.close()
                st.success("Allenamento salvato con successo!")

    with col2:
        st.subheader("📊 Analisi Progressi")
        conn = sqlite3.connect('maratona.db')
        df = pd.read_sql_query("SELECT * FROM allenamenti ORDER BY data DESC", conn)
        conn.close()

        if not df.empty:
            # Mostriamo una tabella stilizzata
            st.dataframe(df, use_container_width=True)
            
            # Un piccolo grafico del passo nel tempo
            st.line_chart(df.set_index('data')['passo_min_km'])
            st.caption("Grafico del passo: l'obiettivo è restare sotto la linea dei 4:40!")
        else:
            st.info("Ancora nessun dato registrato. Inizia oggi!")

    # --- SIDEBAR PER INTEGRAZIONE ---
    with st.sidebar:
        st.header("💊 Integrazione")
        creatina = st.checkbox("Creatina Presa")
        proteine = st.slider("Proteine (g)", 0, 200, 150)
        if st.button("Salva Salute"):
             st.toast("Dati integrazione salvati!") # Una notifica a scomparsa