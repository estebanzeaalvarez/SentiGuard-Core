import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
import subprocess
import sys
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. SETUP DE SISTEMA CRÍTICO
st.set_page_config(
    page_title="SENTIGUARD | CORE",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st_autorefresh(interval=30000, key="datarefresh")

# 2. ESTILO CYBER-RED
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=JetBrains+Mono:wght@300;700&display=swap');
    .stApp { background-color: #000000; color: #ff3131; font-family: 'JetBrains Mono', monospace; }
    .matrix-title {
        font-family: 'Orbitron', sans-serif;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 5px;
        text-shadow: 0 0 15px rgba(255, 0, 0, 0.8);
        border-left: 5px solid #ff3131;
        padding-left: 15px;
        margin-bottom: 20px;
    }
    [data-testid="stMetricValue"] { font-family: 'Orbitron', sans-serif; color: #ff3131 !important; }
    .main-header {
        background: linear-gradient(90deg, #ff3131 0%, #000000 100%);
        padding: 10px; color: white; font-family: 'Orbitron', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

def cargar_datos():
    ruta_raiz = os.path.dirname(os.path.abspath(__file__))
    ruta_db = os.path.join(ruta_raiz, "sentiguard.db")
    if not os.path.exists(ruta_db): return pd.DataFrame()
    try:
        conn = sqlite3.connect(ruta_db, check_same_thread=False)
        df = pd.read_sql_query("SELECT * FROM alertas", conn)
        conn.close()
        if df.empty: return df
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        return df.dropna(subset=['fecha'])
    except:
        return pd.DataFrame()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🛠️ COMANDOS DE SISTEMA")
    if st.button("🚀 INICIAR ESCANEO DE RED", type="primary"):
        try:
            subprocess.Popen([sys.executable, "main.py"], 
                             creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            st.success("📡 Escáner iniciado.")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("🔄 ACTUALIZAR VISTA"):
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
df = cargar_datos()

if not df.empty:
    st.markdown('<div class="main-header"> > SYSTEM.SENTIGUARD_CORE // ACCESS_GRANTED</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("ESTADO", "EN LÍNEA")
    with c2: st.metric("CRÍTICOS", len(df[df['label'] == 'NEGATIVO']))
    with c3: st.metric("NODOS", len(df))
    promedio = df['score'].mean() if not df.empty else 0
    with c4: st.metric("IA_SYNC", f"{promedio:.1%}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_main, col_side = st.columns([1.6, 1])

    with col_main:
        st.markdown('<div class="matrix-title">Frecuencia_Amenazas</div>', unsafe_allow_html=True)
# Agrupamos cada 5 segundos para que los puntos se sumen y creen picos
        df_counts = df.groupby(pd.Grouper(key='fecha', freq='5s')).size().reset_index(name='n')
        
        fig = px.area(df_counts, x='fecha', y='n', template="plotly_dark")
        fig.update_traces(line_color='#ff3131', line_width=3, fillcolor='rgba(255, 49, 49, 0.2)')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=350,
            xaxis_title="LÍNEA_DE_TIEMPO",
            yaxis_title="ALERTAS",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_side:
        st.markdown('<div class="matrix-title">Análisis_Objetivos</div>', unsafe_allow_html=True)
        marcas = ["Tesla", "Apple", "Meta", "Google", "Microsoft", "Sony", "GPS", "US", "Wired"]
        conteos = {m: df['texto'].str.contains(m, case=False).sum() for m in marcas}
        df_m = pd.DataFrame(list(conteos.items()), columns=['T', 'V']).sort_values('V', ascending=True)
        df_m = df_m[df_m['V'] > 0]
        if not df_m.empty:
            fig_b = px.bar(df_m, y='T', x='V', orientation='h', template="plotly_dark")
            fig_b.update_traces(marker_color='#ff3131')
            fig_b.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, showlegend=False)
            st.plotly_chart(fig_b, use_container_width=True)

    st.markdown('<div class="matrix-title">Data_Stream_Incident_Log</div>', unsafe_allow_html=True)
    df_pro = df.sort_values('fecha', ascending=False).copy()
    df_pro['Amenaza'] = df_pro['score'].apply(lambda x: x if x > 0 else 0)
    
# 1. Definimos el estilo visual para la columna STATUS
    def color_status(val):
        color = '#ff3131' if val == 'NEGATIVO' else '#00ff00' if val == 'POSITIVO' else '#888888'
        return f'color: {color}; font-weight: bold;'

    # 2. Configuración de columnas
    config = {
        "fecha": st.column_config.DatetimeColumn("TIMESTAMP", format="HH:mm:ss"),
        "usuario": st.column_config.TextColumn("SOURCE"),
        "texto": st.column_config.TextColumn("INTEL_REPORT", width="large"),
        "Amenaza": st.column_config.ProgressColumn("GRAVEDAD", min_value=0, max_value=1),
        "label": st.column_config.TextColumn("STATUS")
    }

    # 3. Aplicamos estilo y renderizamos
    df_styled = df_pro[['fecha', 'usuario', 'texto', 'Amenaza', 'label']].style.map(color_status, subset=['label'])

    st.dataframe(
        df_styled, 
        column_config=config, 
        use_container_width=True, 
        hide_index=True
    )
else:
    st.warning("⚠️ ESPERANDO DATOS... INICIE EL ESCANEO EN EL SIDEBAR")