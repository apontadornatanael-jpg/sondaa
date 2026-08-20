import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Configuração da página
st.set_page_config(
    page_title="DRILLDATA — Sistema Digital de Sondagem Mineral",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (LAYOUT IGUAL AO MOCKUP)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Ocultar elementos padrão */
    #MainMenu, header, footer, .stAppHeader {visibility: hidden !important; display: none !important;}
    
    /* Fundo da área principal */
    .stApp {
        background-color: #F3F4F6;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Ajuste de espaçamento topo e margens */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1350px;
    }

    /* Estilização da Sidebar Escura */
    [data-testid="stSidebar"] {
        background-color: #030F26 !important;
        border-right: none;
    }
    
    [data-testid="stSidebar"] * {
        color: #94A3B8 !important;
    }

    /* Títulos da Sidebar */
    .sidebar-category {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: #475569 !important;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
    }

    /* Botões do Menu Lateral */
    .stSidebar button {
        background-color: transparent !important;
        border: none !important;
        color: #94A3B8 !important;
        text-align: left !important;
        width: 100%;
        border-radius: 8px !important;
        padding: 0.5rem 0.75rem !important;
        font-weight: 500 !important;
    }

    .stSidebar button:hover {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }

    /* Cartões de Métricas Superiores */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    /* Containers de Seções */
    .section-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        height: 100%;
    }

    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 1rem;
    }

    /* Status Badges */
    .badge-andamento {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-planejamento {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-concluido {
        background-color: #F1F5F9;
        color: #475569;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Timeline de Atividades */
    .timeline-item {
        border-left: 2px solid #E2E8F0;
        padding-left: 1rem;
        position: relative;
        padding-bottom: 1.2rem;
    }
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -5px;
        top: 2px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #2563EB;
    }
    .timeline-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #1E293B;
    }
    .timeline-sub {
        font-size: 0.75rem;
        color: #64748B;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR (NAVEGAÇÃO LATERAL)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⛏️ **DRILLDATA**")
    st.caption("Sistema Digital de Sondagem Mineral")
    st.markdown("---")
    
    st.button("📊 Dashboard", type="primary")
    
    st.markdown('<p class="sidebar-category">PROJETOS</p>', unsafe_allow_html=True)
    st.button("📁 Projetos")
    st.button("🎯 Sondagens")
    st.button("📄 Relatórios")
    st.button("🗺️ Mapas")
    st.button("📑 Documentos")

    st.markdown('<p class="sidebar-category">CONFIGURAÇÕES</p>', unsafe_allow_html=True)
    st.button("🏢 Empresas")
    st.button("👥 Equipes")
    st.button("👤 Usuários")
    st.button("⚙️ Configurações")

    st.markdown("---")
    st.button("🚪 Sair / Logout")

# ---------------------------------------------------------
# CABAÇALHO PRINCIPAL
# ---------------------------------------------------------
col_title, col_user = st.columns([4, 1])
with col_title:
    st.caption("Bem-vindo ao DrillData")
    st.markdown("<h2 style='margin-top:-15px;'>Dashboard</h2>", unsafe_allow_html=True)

with col_user:
    st.markdown("""
        <div style="text-align: right; font-size: 0.85rem;">
            <b>Maria Oliveira</b><br>
            <span style="color: #64748B;">Geóloga Responsável</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. LINHA DE CARDS DE MÉTRICAS (KPIS)
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
        <div class="metric-card">
            <div style="background:#EFF6FF; padding:12px; border-radius:10px; font-size:1.5rem;">📁</div>
            <div>
                <div style="color:#64748B; font-size:0.8rem;">Projetos Ativos</div>
                <div style="font-size:1.5rem; font-weight:700; color:#0F172A;">12</div>
                <div style="color:#16A34A; font-size:0.75rem;">+2 este mês</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
        <div class="metric-card">
            <div style="background:#F0FDF4; padding:12px; border-radius:10px; font-size:1.5rem;">🎯</div>
            <div>
                <div style="color:#64748B; font-size:0.8rem;">Sondagens Totais</div>
                <div style="font-size:1.5rem; font-weight:700; color:#0F172A;">86</div>
                <div style="color:#16A34A; font-size:0.75rem;">+8 este mês</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
        <div class="metric-card">
            <div style="background:#FEF2F2; padding:12px; border-radius:10px; font-size:1.5rem;">📏</div>
            <div>
                <div style="color:#64748B; font-size:0.8rem;">Metros Perfurados</div>
                <div style="font-size:1.5rem; font-weight:700; color:#0F172A;">24.560 m</div>
                <div style="color:#16A34A; font-size:0.75rem;">+1.250 m este mês</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
        <div class="metric-card">
            <div style="background:#F3E8FF; padding:12px; border-radius:10px; font-size:1.5rem;">👥</div>
            <div>
                <div style="color:#64748B; font-size:0.8rem;">Equipe</div>
                <div style="font-size:1.5rem; font-weight:700; color:#0F172A;">18</div>
                <div style="color:#64748B; font-size:0.75rem;">Membros ativos</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SEÇÃO INTERMEDIÁRIA: TABELA DE PROJETOS E ATIVIDADES
# ---------------------------------------------------------
col_proj, col_ativ = st.columns([2, 1])

with col_proj:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Projetos Recentes</div>', unsafe_allow_html=True)
    
    # Tabela estilizada via HTML/Dataframe
    df_projetos = pd.DataFrame({
        "Projeto": ["Projeto Aurora", "Projeto Jaguar", "Projeto Horizonte", "Projeto Vale Verde"],
        "Empresa": ["Mineração Boa Fortuna", "Mineração Boa Fortuna", "Aurora Minerals", "Vale Verde Mineração"],
        "Localização": ["Pará, Brasil", "Goiás, Brasil", "Bahia, Brasil", "Minas Gerais, Brasil"],
        "Sondagens": [15, 12, 8, 20],
        "Status": ["Em andamento", "Em andamento", "Planejamento", "Concluído"]
    })
    
    st.dataframe(
        df_projetos, 
        use_container_width=True, 
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_ativ:
    st.markdown("""
        <div class="section-card">
            <div class="section-title">Atividades Recentes</div>
            <div class="timeline-item">
                <div class="timeline-title">Sondagem SDR-001 finalizada</div>
                <div class="timeline-sub">Projeto Aurora • 2h atrás</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-title">Novo relatório gerado</div>
                <div class="timeline-sub">Relatório Semanal - Projeto Jaguar • 5h atrás</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-title">Amostra registrada</div>
                <div class="timeline-sub">Amostra AM-045 - Projeto Aurora • 1d atrás</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-title">Novo projeto criado</div>
                <div class="timeline-sub">Projeto Horizonte • 2d atrás</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. SEÇÃO INFERIOR: GRÁFICO DE PROGRESSO E MAPA
# ---------------------------------------------------------
col_graf, col_mapa = st.columns([1, 1])

with col_graf:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Progresso dos Projetos</div>', unsafe_allow_html=True)
    
    # Dados do gráfico
    data_progresso = pd.DataFrame({
        "Projeto": ["Projeto Aurora", "Projeto Jaguar", "Projeto Horizonte", "Projeto Vale Verde"],
        "Progresso (%)": [75, 60, 25, 100]
    })
    
    # Gráfico com Plotly Express
    fig = px.bar(
        data_progresso,
        x="Progresso (%)",
        y="Projeto",
        orientation="h",
        text="Progresso (%)",
        color_discrete_sequence=["#2563EB"]
    )
    
    fig.update_layout(
        xaxis_range=[0, 100],
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=20, t=10, b=0),
        height=280,
        xaxis=dict(showgrid=True, gridcolor="#E2E8F0")
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_mapa:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Mapa de Sondagens</div>', unsafe_allow_html=True)
    
    # Criar Mapa interativo com Folium
    m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4, tiles="CartoDB positron")
    
    # Pontos de Sondagem
    coords = [
        [-5.5, -48.5],   # Pará
        [-15.8, -47.9],  # Goiás
        [-12.9, -38.5],  # Bahia
        [-19.9, -43.9]   # Minas Gerais
    ]
    
    for lat, lon in coords:
        folium.CircleMarker(
            location=[lat, lon],
            radius=7,
            color="#2563EB",
            fill=True,
            fill_color="#2563EB",
            fill_opacity=0.8
        ).add_to(m)
        
    st_folium(m, height=260, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
