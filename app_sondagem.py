import io
import os
from datetime import datetime
from PIL import Image

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Imports do Plotly e Folium
import folium
import plotly.express as px
from streamlit_folium import st_folium

# Imports do ReportLab para geração de PDF
from reportlab.graphics.shapes import Drawing, Group, Polygon
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image as RLImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
st.set_page_config(page_title="Relatório de Sondagem - Boa Fortuna", layout="wide")

# --- PALETA DE CORES BASEADA NA LOGO BOA FORTUNA ---
st.markdown("""
<style>
:root {
    --bf-bg: #0b1511;           /* Fundo escuro levemente esverdeado */
    --bf-panel: #12221b;        /* Painéis e cards internos */
    --bf-border: #224234;       /* Bordas de divisores e inputs */
    --bf-text: #e8f5e9;         /* Texto principal */
    --bf-muted: #81c784;        /* Texto secundário */
    --bf-green: #2e7d32;        /* Verde institucional */
    --bf-green-light: #4caf50;  /* Verde destaque */
    --bf-gold: #d4af37;         /* Dourado / Amarelo da logo */
    --bf-blue: #0288d1;         /* Azul complementar da logo */
    --bf-red: #e53935;          /* Alertas / Erros */
}

/* Fundo Principal da Aplicação */
.stApp {
    background: radial-gradient(circle at 80% 0%, rgba(76, 175, 80, 0.12), transparent 35%),
                linear-gradient(135deg, #0b1511 0%, #10211a 50%, #08100d 100%);
    color: var(--bf-text);
}

.block-container {
    max-width: 1500px !important;
    padding: 1.15rem 1.45rem 2rem !important;
}

#MainMenu, header, footer, [data-testid="stStatusWidget"], button[title="Manage app"] {
    visibility: hidden !important;
    display: none !important;
}

/* Sidebar / Menu Lateral */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1e18 0%, #08120e 100%) !important;
    border-right: 1px solid var(--bf-border);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

section[data-testid="stSidebar"] .stButton button {
    background: #142a20;
    border: 1px solid #2e5944;
    color: #e8f5e9;
    border-radius: 8px;
    font-weight: 600;
}

section[data-testid="stSidebar"] .stButton button:hover {
    border-color: var(--bf-gold);
    background: #1e3d2f;
}

.dd-side-nav {
    display: flex;
    flex-direction: column;
    gap: 7px;
    margin: 8px 0 14px;
}

.dd-side-nav a {
    display: block;
    text-decoration: none !important;
    color: #e8f5e9 !important;
    background: #12221b;
    border: 1px solid #224234;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 13px;
    font-weight: 700;
    transition: .15s;
}

.dd-side-nav a:hover {
    background: #1b382c;
    border-color: var(--bf-gold);
    color: #ffffff !important;
    transform: translateX(2px);
}

.dd-anchor {
    scroll-margin-top: 20px;
}

/* Tipografia e Entradas de Texto */
h1, h2, h3, h4, p, label, .stMarkdown {
    color: var(--bf-text) !important;
}

h1 {
    font-size: 2rem !important;
    font-weight: 800 !important;
    letter-spacing: -.03em;
}

h2, h3 {
    font-weight: 750 !important;
}

.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input {
    background: var(--bf-panel) !important;
    color: #ffffff !important;
    border: 1px solid var(--bf-border) !important;
    border-radius: 8px !important;
}

.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus, .stDateInput input:focus {
    border-color: var(--bf-gold) !important;
    box-shadow: 0 0 0 1px var(--bf-gold) !important;
}

/* Botões */
.stButton > button, .stDownloadButton > button {
    border-radius: 8px !important;
    border: 1px solid #2b5240 !important;
    background: #152b21 !important;
    color: #e8f5e9 !important;
    font-weight: 700 !important;
    min-height: 40px;
}

.stButton > button[kind="primary"], .stButton > button:hover, .stDownloadButton > button:hover {
    background: linear-gradient(90deg, #1b5e20, #2e7d32) !important;
    border-color: var(--bf-gold) !important;
    color: #ffffff !important;
}

[data-testid="stExpander"] {
    background: var(--bf-panel) !important;
    border: 1px solid var(--bf-border) !important;
    border-radius: 12px !important;
}

button[data-baseweb="tab"] {
    color: #a5d6a7 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--bf-gold) !important;
    border-bottom-color: var(--bf-gold) !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--bf-border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* Cards KPI */
.dd-kpi {
    background: linear-gradient(145deg, #14281f, #0d1a14);
    border: 1px solid #204032;
    border-radius: 11px;
    padding: 15px 17px;
    min-height: 112px;
    box-shadow: 0 7px 24px rgba(0, 0, 0, .30);
}

.dd-kpi-label {
    color: #a5d6a7;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .04em;
    text-transform: uppercase;
}

.dd-kpi-value {
    margin-top: 7px;
    font-size: 28px;
    line-height: 1;
    font-weight: 850;
}

.dd-kpi-sub {
    margin-top: 8px;
    color: #81c784;
    font-size: 11px;
}

/* Classes de Cores para KPIs */
.dd-blue { color: var(--bf-blue) !important; }
.dd-green { color: var(--bf-green-light) !important; }
.dd-cyan { color: #80deea !important; }
.dd-orange { color: var(--bf-gold) !important; }
.dd-red { color: var(--bf-red) !important; }
.dd-purple { color: #ce93d8 !important; }

.dd-section {
    background: linear-gradient(145deg, rgba(18, 34, 27, .96), rgba(10, 20, 16, .96));
    border: 1px solid #224234;
    border-radius: 12px;
    padding: 16px 18px;
    margin: 10px 0;
}

.dd-section-title {
    font-size: 15px;
    font-weight: 800;
    color: var(--bf-gold);
    margin-bottom: 12px;
    letter-spacing: .02em;
}

.dd-topline {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 16px;
}

.dd-title {
    font-size: 30px;
    font-weight: 850;
    color: #ffffff;
    letter-spacing: -.035em;
}

.dd-subtitle {
    color: #a5d6a7;
    font-size: 13px;
    margin-top: 3px;
}

.dd-status {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: rgba(76, 175, 80, 0.15);
    border: 1px solid rgba(76, 175, 80, 0.4);
    color: #66bb6a;
    font-size: 11px;
    font-weight: 800;
}

div[data-testid="stMetric"] {
    background: var(--bf-panel);
    border: 1px solid var(--bf-border);
    border-radius: 10px;
    padding: 12px;
}

div[data-testid="stMetricLabel"] {
    color: #a5d6a7 !important;
}

div[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

.stAlert {
    background: var(--bf-panel) !important;
    border: 1px solid var(--bf-border) !important;
}

hr {
    border-color: var(--bf-border) !important;
}
</style>
""", unsafe_allow_html=True)

# --- DEFINIÇÃO DA LOGOMARCA FIXA ---
CAMINHO_LOGO_FIXO = "boa fortuna.jpg"

# --- CONTROLE DE AUTENTICAÇÃO / LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

USUARIOS = {
    "admin": "admin123",
    "sondador": "drill2026",
    "geologo": "geo2026"
}

def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## **BOA FORTUNA** — Acesso ao Sistema")
        st.markdown("Por favor, insira suas credenciais para continuar.")
        
        with st.form("login_form"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            btn_login = st.form_submit_button("Entrar", use_container_width=True, type="primary")
            
            if btn_login:
                if usuario in USUARIOS and USUARIOS[usuario] == senha:
                    st.session_state['autenticado'] = True
                    st.success("Acesso liberado!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

if not st.session_state['autenticado']:
    login_screen()
else:
    # --- MENU LATERAL / NAVEGAÇÃO ---
    with st.sidebar:
        if os.path.exists(CAMINHO_LOGO_FIXO):
            st.image(CAMINHO_LOGO_FIXO, use_container_width=True)
        else:
            st.markdown("## ⛏️ BOA FORTUNA")

        st.markdown("### MENU")
        st.markdown("""
        <div class="dd-side-nav">
            <a href="#dashboard">▣ &nbsp; Dashboard</a>
            <a href="#boletim">▤ &nbsp; Boletim de Sondagem</a>
            <a href="#manobras">⚒ &nbsp; Manobras / Testemunho</a>
            <a href="#analise">◉ &nbsp; Análise Digital</a>
            <a href="#relatorio">▥ &nbsp; Relatórios / PDF</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption("SESSÃO ATIVA")
        if st.button("Sair / Logout", use_container_width=True):
            st.session_state['autenticado'] = False
            st.rerun()

    # --- INICIALIZAÇÃO DA SESSÃO ---
    if 'itens_sondagem' not in st.session_state:
        st.session_state['itens_sondagem'] = []

    if 'auto_lat' not in st.session_state:
        st.session_state['auto_lat'] = -6.515831
    if 'auto_long' not in st.session_state:
        st.session_state['auto_long'] = -36.344525

    # --- SCRIPT DE GEOLOCALIZAÇÃO AUTOMÁTICA EM TEMPO REAL ---
    loc_html = """
    <script>
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const urlParams = new URLSearchParams(window.parent.location.search);
            
            if (urlParams.get('lat') !== lat.toString() || urlParams.get('lon') !== lon.toString()) {
                urlParams.set('lat', lat);
                urlParams.set('lon', lon);
                window.parent.location.search = urlParams.toString();
            }
        }, function(error) {
            console.log("Erro na geolocalização: " + error.message);
        }, {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0
        });
    }
    </script>
    """
    components.html(loc_html, height=0, width=0)

    query_params = st.query_params
    if 'lat' in query_params and 'lon' in query_params:
        try:
            st.session_state['auto_lat'] = float(query_params['lat'])
            st.session_state['auto_long'] = float(query_params['lon'])
        except ValueError:
            pass

    st.markdown('<div id="dashboard" class="dd-anchor"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="dd-topline">
      <div><div class="dd-title">BOA FORTUNA — Sistema Digital de Sondagem Mineral</div>
      <div class="dd-subtitle">Acompanhe o desempenho da perfuração, recuperação, horas operacionais e localização do furo.</div></div>
      <div><span class="dd-status">● SISTEMA OPERACIONAL</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div id="boletim" class="dd-anchor"></div>', unsafe_allow_html=True)

    # --- 1. CABEÇALHO DO PROJETO & EQUIPE TÉCNICA ---
    st.header("1. Cabeçalho do Projeto & Equipe Técnica")

    img_logo_pil = None
    if os.path.exists(CAMINHO_LOGO_FIXO):
        img_logo_pil = Image.open(CAMINHO_LOGO_FIXO)

    col_logo, col_gest = st.columns([1, 3])
    with col_logo:
        st.subheader("Logomarca da Empresa")
        
        if img_logo_pil:
            st.image(img_logo_pil, caption="Boa Fortuna (Logo Padrão)", width=180)
            st.info("Logomarca padrão ativa automaticamente.")
        else:
            st.warning("Logomarca padrão não localizada. Faça o upload manual abaixo.")
        
        logo_file = st.file_uploader("Substituir Logo (Opcional)", type=['png', 'jpg', 'jpeg'])
        if logo_file:
            img_logo_pil = Image.open(logo_file)
            st.image(img_logo_pil, caption="Nova logo selecionada", width=180)

    with col_gest:
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            empresa = st.text_input("Empresa / Mineradora", value="Boa Fortuna")
            nome_projeto = st.text_input("Nome do Projeto", value="")
        with col_g2:
            coordenador = st.text_input("Coordenador do Projeto", value="")
            supervisor = st.text_input("Supervisor de Campo", value="")
        with col_g3:
            geologo = st.text_input("Geólogo Responsável", value="")
            sondador_equipe = st.text_input("Sondador / Equipe", value="")

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        furo_id = st.text_input("ID do Furo", value="F-001")
    with col_p2:
        diametro = st.selectbox("Diâmetro", ["HQ (63.5mm)", "NQ (47.6mm)", "PQ (85.0mm)", "BQ (36.5mm)"])
    with col_p3:
        diesel_input = st.number_input("Consumo Total Diesel (L)", value=0, step=5)

    with st.expander("Coordenadas GPS Automáticas e Detalhes do Furo", expanded=True):
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            latitude = st.number_input("Latitude (Capturada do GPS)", value=st.session_state['auto_lat'], format="%.6f")
            longitude = st.number_input("Longitude (Capturada do GPS)", value=st.session_state['auto_long'], format="%.6f")
        with col_c2:
            datum = st.text_input("Datum", value="SIRGAS 2000")
            inclinacao = st.number_input("Inclinação (°)", value=-90.0, step=1.0, format="%.1f")
        with col_c3:
            azimute = st.number_input("Azimute (°)", value=0.0, step=1.0, format="%.1f")
        with col_c4:
            dt_inicio = st.date_input("Data de Início", value=datetime.now())
            dt_termino = st.date_input("Data de Término", value=datetime.now())

    st.markdown("---")

    st.markdown('<div id="manobras" class="dd-anchor"></div>', unsafe_allow_html=True)

    # --- 2. REGISTRO DE MANOBRAS E REGISTRO FOTOGRÁFICO ---
    st.header("2. Registro de Manobra e Testemunho")

    itens = st.session_state['itens_sondagem']
    prox_de = itens[-1]['Até (m)'] if itens else 0.0
    prox_ate = round(prox_de + 1.5, 2)

    col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
    with col_m1:
        de = st.number_input("De (m)", value=float(prox_de), step=0.5, format="%.2f")
    with col_m2:
        ate = st.number_input("Até (m)", value=float(prox_ate), step=0.5, format="%.2f")
    with col_m3:
        rec = st.number_input("Recup. (m)", value=round(max(0.0, ate - de), 2), step=0.1, format="%.2f")
    with col_m4:
        num_caixa_str = st.text_input("Nº da Caixa", value=itens[-1]['Nº Cx'] if itens else "01")
    with col_m5:
        horas_trabalhadas = st.number_input("Horas Trab. (h)", value=1.0, step=0.5, format="%.1f")
    with col_m6:
        horas_parado = st.number_input("Horas Parado (h)", value=0.0, step=0.5, format="%.1f")

    col_h1, col_h2, col_l1 = st.columns([1, 2, 3])
    with col_h1:
        horario_str = st.text_input("Horário (Ex: 07:00 - 08:15)", value="")
    with col_h2:
        motivo_parada = st.text_input("Motivo Parada", value="Nenhuma")
    with col_l1:
        litologia_obs = st.text_input("Descrição Litológica / Observações da Manobra", value="")

    st.subheader("Registro Fotográfico da Manobra (Até 3 fotos)")
    aba_up, aba_cam = st.tabs(["Selecionar da Galeria (Até 3)", "Tirar Foto Agora"])

    fotos_manobra_pil = []

    with aba_up:
        fotos_files = st.file_uploader(
            "Selecione até 3 imagens da manobra/testemunho",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            key="uploader_manobra_multi"
        )
        if fotos_files:
            if len(fotos_files) > 3:
                st.warning("Foram selecionadas mais de 3 fotos. Apenas as 3 primeiras serão mantidas.")
                fotos_files = fotos_files[:3]
            for f in fotos_files:
                fotos_manobra_pil.append(Image.open(f))

    with aba_cam:
        foto_cam = st.camera_input("Tirar foto individual")
        if foto_cam and len(fotos_manobra_pil) < 3:
            fotos_manobra_pil.append(Image.open(foto_cam))

    if fotos_manobra_pil:
        st.write(f"**{len(fotos_manobra_pil)} foto(s) anexada(s) nesta manobra:**")
        cols_preview = st.columns(len(fotos_manobra_pil))
        for i, img in enumerate(fotos_manobra_pil):
            with cols_preview[i]:
                st.image(img, caption=f"Foto {i+1}", use_container_width=True)

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        btn_adicionar = st.button("Adicionar Manobra", type="primary")
    with col_btn2:
        btn_remover = st.button("Remover Última")

    if btn_adicionar:
        avanco = round(ate - de, 2)
        if avanco <= 0:
            st.error("O valor 'Até' deve ser maior que 'De'!")
        else:
            acumulado = round((itens[-1]['Acumulado (m)'] if itens else 0.0) + avanco, 2)
            pct_rec = min(100.0, round((rec / avanco) * 100, 1)) if avanco > 0 else 0.0
            
            st.session_state['itens_sondagem'].append({
                "Item": len(itens) + 1,
                "Horário": horario_str,
                "De (m)": de,
                "Até (m)": ate,
                "Avanço (m)": avanco,
                "Acumulado (m)": acumulado,
                "Recup. (m)": rec,
                "Recup. (%)": pct_rec,
                "Nº Cx": num_caixa_str,
                "Trabalhado": horas_trabalhadas,
                "Parado": horas_parado,
                "Motivo Parada": motivo_parada,
                "Descrição Litológica / Observações": litologia_obs,
                "Fotos": fotos_manobra_pil.copy()
            })
            st.success("Manobra registrada!")
            st.rerun()

    if btn_remover and st.session_state['itens_sondagem']:
        st.session_state['itens_sondagem'].pop()
        st.warning("Última manobra removida.")
        st.rerun()

    st.markdown("---")
    st.subheader("Observações Gerais do Furo / Relatório")
    obs_gerais_furo = st.text_area(
        "Observações Gerais do Relatório (serão exibidas na caixa abaixo da tabela no PDF)",
        value="Furo executado conforme o planejamento geotécnico e normas de segurança. Nível d'água não detectado durante a perfuração. Amostras preservadas e catalogadas.",
        height=100
    )

    # --- DATAFRAME & CÁLCULOS DINÂMICOS ---
    df = pd.DataFrame(st.session_state['itens_sondagem'])

    if not df.empty:
        if 'Trabalhado' not in df.columns:
            df['Trabalhado'] = 0.0
        if 'Parado' not in df.columns:
            df['Parado'] = 0.0

        progresso_total = df['Avanço (m)'].sum()
        recup_tot_m = df['Recup. (m)'].sum()
        media_rec = round(df['Recup. (%)'].mean(), 1)
        total_trabalhado = df['Trabalhado'].sum()
        total_paradas = df['Parado'].sum()
        ult_cx = df['Nº Cx'].iloc[-1]
    else:
        progresso_total = 0.0
        recup_tot_m = 0.0
        media_rec = 0.0
        total_trabalhado = 0.0
        total_paradas = 0.0
        ult_cx = "-"

    eficiencia_operacional = (total_trabalhado / (total_trabalhado + total_paradas) * 100) if (total_trabalhado + total_paradas) > 0 else 0.0
    media_avanco = (progresso_total / len(df)) if not df.empty else 0.0

    st.markdown("<div class=\"dd-section-title\">VISÃO GERAL DA OPERAÇÃO</div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    cards = [
      (k1, "PROGRESSO TOTAL PERFURADO", f"{progresso_total:.2f} m", "Avanço acumulado", "dd-blue"),
      (k2, "MÉDIA DE RECUPERAÇÃO", f"{media_rec:.1f}%", "Recuperação média", "dd-green"),
      (k3, "HORAS TRABALHADAS", f"{total_trabalhado:.1f} h", "Tempo produtivo", "dd-cyan"),
      (k4, "HORAS PARADAS", f"{total_paradas:.1f} h", "Tempo improdutivo", "dd-orange"),
      (k5, "CONSUMO TOTAL DIESEL", f"{diesel_input} L", "Consumo registrado", "dd-red"),
      (k6, "EFICIÊNCIA OPERACIONAL", f"{eficiencia_operacional:.1f}%", "Produtividade horária", "dd-purple")]
    for col, title, value, sub, color in cards:
        with col:
            st.markdown(f"<div class=\"dd-kpi\"><div class=\"dd-kpi-label\">{title}</div><div class=\"dd-kpi-value {color}\">{value}</div><div class=\"dd-kpi-sub\">{sub}</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Tabela do Boletim Diário")
    if not df.empty:
        df_exibicao = df.copy()
        df_exibicao['Qtd Fotos'] = df_exibicao['Fotos'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        df_exibicao = df_exibicao.drop(columns=['Fotos'], errors='ignore')
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma manobra cadastrada até o momento. Preencha os campos acima para iniciar.")

    st.markdown('<div id="analise" class="dd-anchor"></div>', unsafe_allow_html=True)

    # ==========================================
    # 3. VISUALIZAÇÃO & ANÁLISE DIGITAL
    # ==========================================
    st.markdown("---")
    st.header("3. Visualização & Análise Digital")

    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("FUROS / MANOBRAS", len(df), "registros")
    with s2: st.metric("AVANÇO MÉDIO", f"{media_avanco:.2f} m", "por manobra")
    with s3: st.metric("RECUPERAÇÃO TOTAL", f"{recup_tot_m:.2f} m", "testemunho")
    with s4: st.metric("ÚLTIMA CAIXA", str(ult_cx), "registro atual")

    col_mapa, col_grafico = st.columns([1, 1])

    fig_rec = None
    fig_horas = None

    with col_mapa:
        st.subheader("Localização GPS do Furo")
        m = folium.Map(location=[latitude, longitude], zoom_start=15, tiles="OpenStreetMap")
        folium.Marker(
            [latitude, longitude],
            popup=f"Furo: {furo_id}<br>Projeto: {nome_projeto}",
            tooltip=f"Furo {furo_id}",
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(m)
        st_folium(m, width="100%", height=350)

    with col_grafico:
        st.subheader("Desempenho da Perfuração (Plotly)")
        if not df.empty:
            fig_rec = px.bar(
                df, 
                x="Item", 
                y=["Avanço (m)", "Recup. (m)"], 
                barmode="group",
                title="Avanço vs. Recuperação por Manobra",
                labels={"value": "Metros (m)", "Item": "Nº da Manobra", "variable": "Métrica"},
                color_discrete_sequence=["#0288d1", "#2e7d32"]
            )
            fig_rec.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_rec, use_container_width=True)
        else:
            st.info("Adicione manobras para gerar o gráfico de recuperação.")

    if not df.empty:
        st.subheader("Análise de Horas Operacionais")
        fig_horas = px.pie(
            names=["Trabalhadas", "Paradas"],
            values=[total_trabalhado, total_paradas],
            title="Distribuição das Horas de Trabalho",
            color_discrete_sequence=["#2e7d32", "#d4af37"],
            hole=0.4
        )
        fig_horas.update_layout(height=300)
        st.plotly_chart(fig_horas, use_container_width=True)

    st.markdown("---")
    st.markdown('<div id="relatorio" class="dd-anchor"></div>', unsafe_allow_html=True)

    # ==========================================
    # 4. GERAÇÃO E DOWNLOAD DO RELATÓRIO PDF
    # ==========================================
    st.header("4. Exportação do Relatório em PDF")

    def gerar_pdf_boa_fortuna():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1.2 * cm,
            leftMargin=1.2 * cm,
            topMargin=1.2 * cm,
            bottomMargin=1.2 * cm,
        )

        elements = []
        styles = getSampleStyleSheet()

        # --- ESTILOS ---
        title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor("#12221b"), alignment=0)
        sub_title_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#2e7d32"), alignment=0)
        
        header_cell = ParagraphStyle('HCell', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.white, alignment=1)
        cell_center = ParagraphStyle('CCell', fontName='Helvetica', fontSize=7.5, alignment=1)
        cell_left = ParagraphStyle('LCell', fontName='Helvetica', fontSize=7.5, alignment=0)
        cell_left_bold = ParagraphStyle('LCellB', fontName='Helvetica-Bold', fontSize=7.5, alignment=0)

        kpi_title_style = ParagraphStyle('KPITitle', fontName='Helvetica-Bold', fontSize=6.5, textColor=colors.HexColor("#2e7d32"), alignment=1)
        kpi_val_style = ParagraphStyle('KPIVal', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#12221b"), alignment=1)

        # --- 1. CABEÇALHO DO DOCUMENTO ---
        logo_element = Paragraph('<b>BOA FORTUNA</b><br/><font size="6">INVESTIMENTOS</font>', title_style)
        if img_logo_pil:
            img_byte_arr = io.BytesIO()
            img_logo_pil.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            logo_element = RLImage(img_byte_arr, width=3.2*cm, height=1.2*cm)

        header_data = [
            [logo_element, 
             Paragraph(f"<b>Empresa:</b> {empresa}<br/><b>Projeto:</b> {nome_projeto}<br/><b>Coordenador:</b> {coordenador}<br/><b>Geólogo:</b> {geologo}", cell_left),
             Paragraph(f"<b>Furo:</b> {furo_id}<br/><b>Diâmetro:</b> {diametro}<br/><b>Supervisor:</b> {supervisor}<br/><b>Sondador/Equipe:</b> {sondador_equipe}", cell_left),
             Paragraph(f"<b>Início/Fim:</b> {dt_inicio.strftime('%d/%m/%Y')} a {dt_termino.strftime('%d/%m/%Y')}<br/><b>Coordenadas:</b> Lat: {latitude:.6f} | Long: {longitude:.6f}<br/><b>Datum:</b> {datum}<br/><b>Inclin. / Azim.:</b> {inclinacao}°/{azimute}°", cell_left)]
        ]
        t_header = Table(header_data, colWidths=[4.0*cm, 7.5*cm, 7.5*cm, 8.2*cm])
        t_header.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#224234")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#d0dcd5")),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fafafa")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        elements.append(t_header)
        elements.append(Spacer(1, 0.2*cm))

        # --- 2. CARDS KPI ---
        kpi_data = [
            [Paragraph("PROGRESSO TOTAL PERFURADO", kpi_title_style), Paragraph("MÉDIA DE RECUPERAÇÃO", kpi_title_style), Paragraph("TOTAL HORAS TRABALHADAS", kpi_title_style), Paragraph("TOTAL HORAS PARADAS", kpi_title_style), Paragraph("CONSUMO TOTAL DIESEL", kpi_title_style)],
            [Paragraph(f"{progresso_total:.2f} m", kpi_val_style), Paragraph(f"{media_rec:.1f}%", kpi_val_style), Paragraph(f"{total_trabalhado:.1f} h", kpi_val_style), Paragraph(f"{total_paradas:.1f} h", kpi_val_style), Paragraph(f"{diesel_input} L", kpi_val_style)]
        ]
        t_kpi = Table(kpi_data, colWidths=[5.44*cm]*5)
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f4f7f5")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#2e7d32")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        elements.append(t_kpi)
        elements.append(Spacer(1, 0.25*cm))

        # --- 3. TABELA DE MANOBRAS / BOLETIM ---
        headers = ["Item", "Horário", "De (m)", "Até (m)", "Avanço (m)", "Acumulado (m)", "Recup. (m)", "Recup. (%)", "N° Cx", "Trab.", "Parado", "Motivo Parada", "Descrição Litológica / Observações"]
        t_boletim_data = [[Paragraph(h, header_cell) for h in headers]]

        if not df.empty:
            for _, r in df.iterrows():
                t_boletim_data.append([
                    Paragraph(str(r["Item"]), cell_center),
                    Paragraph(str(r["Horário"]), cell_center),
                    Paragraph(f"{r['De (m)']:.2f}", cell_center),
                    Paragraph(f"{r['Até (m)']:.2f}", cell_center),
                    Paragraph(f"{r['Avanço (m)']:.2f}", cell_center),
                    Paragraph(f"{r['Acumulado (m)']:.2f}", cell_center),
                    Paragraph(f"{r['Recup. (m)']:.2f}", cell_center),
                    Paragraph(f"{r['Recup. (%)']:.1f}%", cell_center),
                    Paragraph(str(r["Nº Cx"]), cell_center),
                    Paragraph(f"{r['Trabalhado']:.1f} h", cell_center),
                    Paragraph(f"{r['Parado']:.1f} h", cell_center),
                    Paragraph(str(r["Motivo Parada"]), cell_left),
                    Paragraph(str(r["Descrição Litológica / Observações"]), cell_left)
                ])

            # Linha de Totais
            t_boletim_data.append([
                Paragraph("TOTAIS/MÉDIAS OPERACIONAIS:", cell_left_bold),
                Paragraph("", cell_center), Paragraph("", cell_center),
                Paragraph(f"<b>{progresso_total:.2f} m</b>", cell_center),
                Paragraph(f"<b>{progresso_total:.2f} m</b>", cell_center),
                Paragraph(f"<b>{progresso_total:.2f} m</b>", cell_center),
                Paragraph(f"<b>{recup_tot_m:.2f} m</b>", cell_center),
                Paragraph(f"<b>{media_rec:.1f}%</b>", cell_center),
                Paragraph(str(ult_cx), cell_center),
                Paragraph(f"<b>{total_trabalhado:.1f} h</b>", cell_center),
                Paragraph(f"<b>{total_paradas:.1f} h</b>", cell_center),
                Paragraph(f"Diesel: {diesel_input} L", cell_left_bold),
                Paragraph("Furo em andamento/finalizado.", cell_left)
            ])

        widths = [0.9*cm, 1.8*cm, 1.3*cm, 1.3*cm, 1.5*cm, 1.7*cm, 1.4*cm, 1.4*cm, 1.0*cm, 1.1*cm, 1.1*cm, 2.5*cm, 8.2*cm]
        t_boletim = Table(t_boletim_data, colWidths=widths, repeatRows=1)
        t_boletim.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#12221b")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#224234")),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#e8f5e9")),
            ('SPAN', (0,-1), (2,-1)),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        elements.append(t_boletim)
        elements.append(Spacer(1, 0.2*cm))

        # --- 4. OBSERVAÇÕES E NOTAS DE CAMPO ---
        p_obs_title = Paragraph("<b>OBSERVAÇÕES/NOTAS DE CAMPO</b>", cell_left_bold)
        p_obs_text = Paragraph(obs_gerais_furo, cell_left)
        t_obs = Table([[p_obs_title], [p_obs_text]], colWidths=[27.2*cm])
        t_obs.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fafafa")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        elements.append(t_obs)
        elements.append(Spacer(1, 0.3*cm))

        # --- 5. EXPORTAÇÃO DO GRÁFICO PLOTLY PARA O PDF (USANDO KALEIDO) ---
        if fig_rec is not None and not df.empty:
            try:
                img_bytes_chart = fig_rec.to_image(format="png", width=1000, height=350, engine="kaleido")
                chart_stream = io.BytesIO(img_bytes_chart)
                rl_chart = RLImage(chart_stream, width=27.2*cm, height=7.0*cm)
                elements.append(KeepTogether([
                    Paragraph("<b>GRÁFICO DE AVANÇO VS. RECUPERAÇÃO</b>", sub_title_style),
                    Spacer(1, 0.1*cm),
                    rl_chart
                ]))
                elements.append(Spacer(1, 0.3*cm))
            except Exception as e:
                elements.append(Paragraph(f"<i>Não foi possível renderizar o gráfico no PDF: {e}</i>", cell_left))

        # --- 6. ANEXO FOTOGRÁFICO DE MANOBRAS ---
        todas_fotos = []
        if not df.empty:
            for _, r in df.iterrows():
                fotos_lista = r.get("Fotos", [])
                if isinstance(fotos_lista, list):
                    for idx, img_pil in enumerate(fotos_lista):
                        todas_fotos.append((r["Item"], r["De (m)"], r["Até (m)"], idx + 1, img_pil))

        if todas_fotos:
            elements.append(PageBreak())
            elements.append(Paragraph("<b>ANEXO FOTOGRÁFICO DAS MANOBRAS DE SONDAGEM</b>", title_style))
            elements.append(Spacer(1, 0.3*cm))

            foto_rows = []
            row_temp = []
            for item_num, de_m, ate_m, f_idx, img_p in todas_fotos:
                img_buf = io.BytesIO()
                img_p.save(img_buf, format='JPEG', quality=85)
                img_buf.seek(0)
                
                rl_img = RLImage(img_buf, width=8.2*cm, height=5.5*cm)
                caption = Paragraph(f"<b>Manobra {item_num}</b> ({de_m:.2f}m - {ate_m:.2f}m) - Foto {f_idx}", cell_center)
                cell_box = Table([[rl_img], [caption]], colWidths=[8.5*cm])
                cell_box.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#224234")),
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fafafa")),
                    ('TOPPADDING', (0,0), (-1,-1), 3),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ]))

                row_temp.append(cell_box)
                if len(row_temp) == 3:
                    foto_rows.append(row_temp)
                    row_temp = []

            if row_temp:
                while len(row_temp) < 3:
                    row_temp.append(Paragraph("", cell_center))
                foto_rows.append(row_temp)

            t_fotos = Table(foto_rows, colWidths=[8.8*cm, 8.8*cm, 8.8*cm])
            t_fotos.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ]))
            elements.append(t_fotos)

        doc.build(elements)
        buffer.seek(0)
        return buffer

    # --- BOTÃO DE DOWNLOAD NA INTERFACE ---
    col_dl1, col_dl2 = st.columns([1, 2])
    with col_dl1:
        if st.button("Gerar Relatório PDF", type="primary", use_container_width=True):
            pdf_out = gerar_pdf_boa_fortuna()
            st.download_button(
                label=" Baixar Relatório PDF Completo",
                data=pdf_out,
                file_name=f"Relatorio_Sondagem_{furo_id}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
