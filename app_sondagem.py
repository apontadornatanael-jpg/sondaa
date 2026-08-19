import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
from datetime import datetime
from PIL import Image

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, Image as RLImage
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Polygon, Group

# --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
st.set_page_config(page_title="DrillData - Relatório de Sondagem", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    button[title="Manage app"] {display: none !important;}
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- CONTROLE DE AUTENTICAÇÃO / LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Dicionário de usuários padrão (usuário: senha)
USUARIOS = {
    "admin": "admin123",
    "sondador": "drill2026",
    "geologo": "geo2026"
}

def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## ⛏️ **DRILLDATA** — Acesso ao Sistema")
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
    # Botão para encerrar a sessão
    with st.sidebar:
        st.write("👤 **Sessão Ativa**")
        if st.button("🚪 Sair / Logout", use_container_width=True):
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

    st.title("⛏️ DRILLDATA — Sistema Digital de Sondagem Mineral")
    st.markdown("---")

    # --- 1. CABEÇALHO DO PROJETO & EQUIPE TÉCNICA ---
    st.header("1. Cabeçalho do Projeto & Equipe Técnica")

    col_logo, col_gest = st.columns([1, 3])
    with col_logo:
        st.subheader("🖼️ Logomarca da Empresa")
        logo_file = st.file_uploader("Carregar Logo (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
        img_logo_pil = Image.open(logo_file) if logo_file else None
        if img_logo_pil:
            st.image(img_logo_pil, width=180)

    with col_gest:
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            empresa = st.text_input("Empresa / Mineradora", value="")
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

    with st.expander("🌐 Coordenadas GPS Automáticas e Detalhes do Furo", expanded=True):
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

    # --- 2. REGISTRO DE MANOBRAS E REGISTRO FOTOGRÁFICO ---
    st.header("2. Registro de Manobra e Testemunho")

    itens = st.session_state['itens_sondagem']
    prox_de = itens[-1]['Até (m)'] if itens else 0.0
    prox_ate = round(prox_de + 1.5, 2)

    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    with col_m1:
        de = st.number_input("De (m)", value=float(prox_de), step=0.5, format="%.2f")
    with col_m2:
        ate = st.number_input("Até (m)", value=float(prox_ate), step=0.5, format="%.2f")
    with col_m3:
        rec = st.number_input("Recup. (m)", value=round(max(0.0, ate - de), 2), step=0.1, format="%.2f")
    with col_m4:
        num_caixa_str = st.text_input("Nº da Caixa", value=itens[-1]['Nº Cx'] if itens else "01")
    with col_m5:
        horas_parado = st.number_input("Horas Parado (h)", value=0.0, step=0.5, format="%.1f")

    col_h1, col_h2, col_l1 = st.columns([1, 2, 3])
    with col_h1:
        horario_str = st.text_input("Horário (Ex: 07:00 - 08:15)", value="")
    with col_h2:
        motivo_parada = st.text_input("Motivo Parada", value="Nenhuma")
    with col_l1:
        litologia_obs = st.text_input("Descrição Litológica / Observações da Manobra", value="")

    # Registro Fotográfico (Até 3 Fotos por Manobra)
    st.subheader("📷 Registro Fotográfico da Manobra (Até 3 fotos)")
    aba_up, aba_cam = st.tabs(["📁 Selecionar da Galeria (Até 3)", "📸 Tirar Foto Agora"])

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
                st.warning("⚠️ Foram selecionadas mais de 3 fotos. Apenas as 3 primeiras serão mantidas.")
                fotos_files = fotos_files[:3]
            for f in fotos_files:
                fotos_manobra_pil.append(Image.open(f))

    with aba_cam:
        foto_cam = st.camera_input("Tirar foto individual")
        if foto_cam and len(fotos_manobra_pil) < 3:
            fotos_manobra_pil.append(Image.open(foto_cam))

    if fotos_manobra_pil:
        st.write(f"📸 **{len(fotos_manobra_pil)} foto(s) anexada(s) nesta manobra:**")
        cols_preview = st.columns(len(fotos_manobra_pil))
        for i, img in enumerate(fotos_manobra_pil):
            with cols_preview[i]:
                st.image(img, caption=f"Foto {i+1}", use_container_width=True)

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        btn_adicionar = st.button("➕ Adicionar Manobra", type="primary")
    with col_btn2:
        btn_remover = st.button("🗑️ Remover Última")

    if btn_adicionar:
        avanco = round(ate - de, 2)
        if avanco <= 0:
            st.error("⚠️ O valor 'Até' deve ser maior que 'De'!")
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
                "Parado": horas_parado,
                "Motivo Parada": motivo_parada,
                "Descrição Litológica / Observações": litologia_obs,
                "Fotos": fotos_manobra_pil.copy()
            })
            st.success("✅ Manobra registrada!")
            st.rerun()

    if btn_remover and st.session_state['itens_sondagem']:
        st.session_state['itens_sondagem'].pop()
        st.warning("🗑️ Última manobra removida.")
        st.rerun()

    # Campo de Observações Gerais do Furo
    st.markdown("---")
    st.subheader("📝 Observações Gerais do Furo / Relatório")
    obs_gerais_furo = st.text_area(
        "Observações Gerais do Relatório (serão exibidas na caixa abaixo da tabela no PDF)",
        value="Furo executado conforme o planejamento geotécnico e normas de segurança. Nível d'água não detectado durante a perfuração. Amostras preservadas e catalogadas.",
        height=100
    )

    # --- DATAFRAME & CÁLCULOS DINÂMICOS ---
    df = pd.DataFrame(st.session_state['itens_sondagem'])

    if not df.empty:
        progresso_total = df['Avanço (m)'].sum()
        recup_tot_m = df['Recup. (m)'].sum()
        media_rec = round(df['Recup. (%)'].mean(), 1)
        total_paradas = df['Parado'].sum()
        ult_cx = df['Nº Cx'].iloc[-1]
    else:
        progresso_total = 0.0
        recup_tot_m = 0.0
        media_rec = 0.0
        total_paradas = 0.0
        ult_cx = "-"

    st.markdown("---")
    st.subheader("📋 Tabela do Boletim Diário")
    if not df.empty:
        df_exibicao = df.copy()
        df_exibicao['Qtd Fotos'] = df_exibicao['Fotos'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        df_exibicao = df_exibicao.drop(columns=['Fotos'], errors='ignore')
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma manobra cadastrada até o momento. Preencha os campos acima para iniciar.")

    # ==========================================
    # GERAÇÃO DO PDF DINÂMICO MULTIPÁGINAS
    # ==========================================
    class DrillDataCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.setFont("Helvetica", 8)
                self.setFillColor(colors.HexColor('#64748B'))
                self.drawString(1.0*cm, 0.7*cm, "DrillData — Sistema Digital de Sondagem Mineral")
                self.drawRightString(28.7*cm, 0.7*cm, f"Página {self._pageNumber} de {num_pages}")
                super().showPage()
            super().save()

    def draw_drilldata_logo():
        d = Drawing(26, 26)
        g = Group()
        g.add(Polygon([0, 4, 6, 24, 10, 24, 4, 4], fillColor=colors.HexColor('#0EA5E9'), strokeColor=None))
        g.add(Polygon([7, 0, 13, 20, 17, 20, 11, 0], fillColor=colors.HexColor('#0284C7'), strokeColor=None))
        g.add(Polygon([14, 0, 20, 16, 24, 16, 18, 0], fillColor=colors.HexColor('#0369A1'), strokeColor=None))
        d.add(g)
        return d

    buf_pdf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf_pdf, pagesize=landscape(A4),
        leftMargin=0.8*cm, rightMargin=0.8*cm,
        topMargin=0.8*cm, bottomMargin=1.0*cm
    )
    elements = []

    # Estilos de Texto PDF
    st_title = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=13, leading=15, textColor=colors.HexColor('#0EA5E9'))
    st_subtitle = ParagraphStyle('H2', fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#94A3B8'))
    st_meta_lbl = ParagraphStyle('ML', fontName='Helvetica', fontSize=6.5, leading=8.5, textColor=colors.HexColor('#0F172A'))

    st_kpi_lbl = ParagraphStyle('KL', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=0, textColor=colors.HexColor('#475569'))
    st_kpi_val = ParagraphStyle('KV', fontName='Helvetica-Bold', fontSize=11, leading=13, alignment=0)

    st_th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=1, textColor=colors.white)
    st_td = ParagraphStyle('TD', fontName='Helvetica', fontSize=6.5, leading=8, alignment=1, textColor=colors.HexColor('#0F172A'))
    st_td_left = ParagraphStyle('TDL', fontName='Helvetica', fontSize=6.5, leading=8, alignment=0, textColor=colors.HexColor('#0F172A'))
    st_td_rec = ParagraphStyle('TDR', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=1, textColor=colors.HexColor('#059669'))
    st_tot = ParagraphStyle('TOT', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=0, textColor=colors.HexColor('#0F172A'))

    st_obs_title = ParagraphStyle('OBST', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.HexColor('#0F172A'))
    st_obs_body = ParagraphStyle('OBSB', fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#334155'))

    st_page2_title = ParagraphStyle('P2T', fontName='Helvetica-Bold', fontSize=11, leading=13, textColor=colors.HexColor('#0F172A'))

    # ==========================================
    # 1. CABEÇALHO DA PRIMEIRA PÁGINA
    # ==========================================
    if img_logo_pil:
        logo_buf = io.BytesIO()
        img_logo_pil.convert("RGB").save(logo_buf, format="JPEG")
        logo_buf.seek(0)
        logo_element = RLImage(logo_buf, width=1.5*cm, height=1.1*cm)
    else:
        logo_element = draw_drilldata_logo()

    h_text_cell = [
        Paragraph("<b>DRILLDATA</b>", st_title),
        Paragraph("Relatório Técnico & Boletim Diário de Sondagem", st_subtitle)
    ]

    header_left_box = Table([[logo_element, h_text_cell]], colWidths=[1.7*cm, 7.5*cm])
    header_left_box.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))

    t_h_left = Table([[header_left_box]], colWidths=[9.4*cm])
    t_h_left.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
        ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))

    meta_grid = [
        [Paragraph(f"<b>Empresa:</b> {empresa}", st_meta_lbl), Paragraph(f"<b>Furo:</b> {furo_id}", st_meta_lbl), Paragraph(f"<b>Início/Fim:</b> {dt_inicio.strftime('%d/%m')} a {dt_termino.strftime('%d/%m/%Y')}", st_meta_lbl)],
        [Paragraph(f"<b>Projeto:</b> {nome_projeto}", st_meta_lbl), Paragraph(f"<b>Diâmetro:</b> {diametro}", st_meta_lbl), Paragraph(f"<b>Coordenadas:</b> Lat: {latitude:.6f} | Long: {longitude:.6f}", st_meta_lbl)],
        [Paragraph(f"<b>Coord./Geól.:</b> {coordenador} / {geologo}", st_meta_lbl), Paragraph(f"<b>Inclin./Azim.:</b> {inclinacao}° / {azimute}°", st_meta_lbl), Paragraph(f"<b>Sondador:</b> {sondador_equipe}", st_meta_lbl)]
    ]
    t_h_right = Table(meta_grid, colWidths=[6.3*cm, 6.3*cm, 6.1*cm])
    t_h_right.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))

    header_full = Table([[t_h_left, t_h_right]], colWidths=[9.4*cm, 18.7*cm])
    header_full.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    elements.append(header_full)
    elements.append(Spacer(1, 6))

    # CARDS DE KPIS
    def create_kpi_card(title, value, color_hex):
        v_style = ParagraphStyle('KVc', parent=st_kpi_val, textColor=colors.HexColor(color_hex))
        p_t = Paragraph(title, st_kpi_lbl)
        p_v = Paragraph(value, v_style)
        t = Table([[p_t], [p_v]], colWidths=[6.7*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('LINELEFT', (0,0), (0,-1), 3.5, colors.HexColor(color_hex)),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    k1 = create_kpi_card("PROGRESSO TOTAL PERFURADO", f"{progresso_total:.2f} m", "#0284C7")
    k2 = create_kpi_card("MÉDIA DE RECUPERAÇÃO", f"{media_rec:.1f} %", "#059669")
    k3 = create_kpi_card("TOTAL HORAS PARADAS", f"{total_paradas:.1f} h".replace('.', ','), "#DC2626")
    k4 = create_kpi_card("CONSUMO TOTAL DIESEL", f"{diesel_input} L", "#D97706")

    kpi_bar = Table([[k1, k2, k3, k4]], colWidths=[7.0*cm]*4)
    kpi_bar.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(kpi_bar)
    elements.append(Spacer(1, 6))

    # ==========================================
    # 2. TABELA PRINCIPAL DE MANOBRAS (DINÂMICA)
    # ==========================================
    pdf_table_rows = [[
        Paragraph("Item", st_th), Paragraph("Horário", st_th), Paragraph("De (m)", st_th), Paragraph("Até (m)", st_th),
        Paragraph("Avanço (m)", st_th), Paragraph("Acumulado (m)", st_th), Paragraph("Recup. (m)", st_th), Paragraph("Recup. (%)", st_th),
        Paragraph("Nº Cx", st_th), Paragraph("Parado", st_th), Paragraph("Motivo Parada", st_th), Paragraph("Descrição Litológica / Observações", st_th)
    ]]

    if not df.empty:
        for _, r in df.iterrows():
            pdf_table_rows.append([
                Paragraph(str(r['Item']), st_td), Paragraph(r['Horário'], st_td),
                Paragraph(f"{r['De (m)']:.2f}".replace('.', ','), st_td), Paragraph(f"{r['Até (m)']:.2f}".replace('.', ','), st_td),
                Paragraph(f"{r['Avanço (m)']:.2f}".replace('.', ','), st_td), Paragraph(f"{r['Acumulado (m)']:.2f}".replace('.', ','), st_td),
                Paragraph(f"{r['Recup. (m)']:.2f}".replace('.', ','), st_td), Paragraph(f"{r['Recup. (%)']:.1f}%".replace('.', ','), st_td_rec),
                Paragraph(str(r['Nº Cx']), st_td), Paragraph(f"{r['Parado']:.1f} h".replace('.', ','), st_td),
                Paragraph(r['Motivo Parada'], st_td_left), Paragraph(r['Descrição Litológica / Observações'], st_td_left)
            ])

    col_widths = [0.8*cm, 2.1*cm, 1.3*cm, 1.3*cm, 1.6*cm, 1.8*cm, 1.6*cm, 1.6*cm, 1.1*cm, 1.2*cm, 3.2*cm, 10.5*cm]

    t_main = Table(pdf_table_rows, colWidths=col_widths, repeatRows=1)
    t_main.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    elements.append(t_main)

    # ==========================================
    # 3. RODA PÉ DE TOTAIS, OBSERVAÇÕES E ASSINATURAS (FICA SEMPRE JUNTO)
    # ==========================================
    totals_row = [[
        Paragraph("TOTAIS / MÉDIAS OPERACIONAIS:", st_tot), Paragraph("", st_td), Paragraph("", st_td), Paragraph("", st_td),
        Paragraph(f"<b>{progresso_total:.2f} m</b>".replace('.', ','), st_td), Paragraph(f"<b>{(df['Acumulado (m)'].max() if not df.empty else 0.0):.2f} m</b>".replace('.', ','), st_td),
        Paragraph(f"<b>{recup_tot_m:.2f} m</b>".replace('.', ','), st_td_rec), Paragraph(f"<b>{media_rec:.1f}%</b>".replace('.', ','), st_td_rec),
        Paragraph(f"<b>{ult_cx}</b>", st_td), Paragraph(f"<b>{total_paradas:.1f} h</b>".replace('.', ','), st_td),
        Paragraph(f"<b>Diesel: {diesel_input} L</b>", st_td_left), Paragraph("Furo em andamento/finalizado.", st_td_left)
    ]]
    t_tot = Table(totals_row, colWidths=col_widths)
    t_tot.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E0F2FE')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('SPAN', (0, 0), (3, 0)),
        ('LINEABOVE', (0, 0), (-1, -1), 1.0, colors.HexColor('#0284C7')),
        ('LINEBELOW', (0, 0), (-1, -1), 1.0, colors.HexColor('#0284C7')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))

    obs_content = [
        [Paragraph("<b>📌 OBSERVAÇÕES / NOTAS DE CAMPO</b>", st_obs_title)],
        [Paragraph(obs_gerais_furo if obs_gerais_furo.strip() else "Nenhuma observação adicional registrada para este boletim.", st_obs_body)]
    ]
    t_obs = Table(obs_content, colWidths=[28.1*cm])
    t_obs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('LINELEFT', (0,0), (0,-1), 3.0, colors.HexColor('#0EA5E9')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))

    st_ass_nome = ParagraphStyle('AN', fontName='Helvetica-Bold', fontSize=7.5, leading=9, alignment=1, textColor=colors.HexColor('#0F172A'))
    st_ass_cargo = ParagraphStyle('AC', fontName='Helvetica', fontSize=7, leading=8.5, alignment=1, textColor=colors.HexColor('#475569'))

    ass_table = Table([
        [Paragraph("__________________________________________", st_ass_nome), Paragraph("__________________________________________", st_ass_nome), Paragraph("__________________________________________", st_ass_nome)],
        [Paragraph(f"<b>{sondador_equipe if sondador_equipe else 'Sondador / Equipe'}</b>", st_ass_nome), Paragraph(f"<b>{geologo if geologo else 'Geólogo Responsável'}</b>", st_ass_nome), Paragraph(f"<b>{empresa if empresa else 'Empresa / Cliente'}</b>", st_ass_nome)],
        [Paragraph("Sondador / Operador Responsável", st_ass_cargo), Paragraph("Fiscalização de Campo / Geologia", st_ass_cargo), Paragraph("Supervisão de Operações", st_ass_cargo)]
    ], colWidths=[9.3*cm, 9.3*cm, 9.3*cm])
    ass_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))

    # Agrupa Totais, Obs e Assinaturas para que nunca fiquem órfãos em páginas separadas
    elements.append(KeepTogether([
        t_tot,
        Spacer(1, 6),
        t_obs,
        Spacer(1, 10),
        ass_table
    ]))

    # ==========================================
    # 4. ANEXO: REGISTRO FOTOGRÁFICO DE CAMPO
    # ==========================================
    elements.append(PageBreak())

    p2_header = Table([[
        Paragraph(f"<b>ANEXO: REGISTRO FOTOGRÁFICO DOS TESTEMUNHOS — FURO {furo_id}</b>", st_page2_title),
        Paragraph(f"<b>Projeto:</b> {nome_projeto} | <b>Data:</b> {dt_inicio.strftime('%d/%m/%Y')}", st_meta_lbl)
    ]], colWidths=[18.0*cm, 10.1*cm])
    p2_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(p2_header)
    elements.append(Spacer(1, 10))

    cards_de_fotos = []

    for item in st.session_state['itens_sondagem']:
        lista_fotos = item.get('Fotos', [])
        total_fotos_manobra = len(lista_fotos)
        
        for idx_foto, img_pil in enumerate(lista_fotos):
            img_buffer = io.BytesIO()
            img_pil.convert('RGB').save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            
            rl_img = RLImage(img_buffer, width=8.5*cm, height=4.3*cm)
            lbl_foto = f" ({idx_foto + 1}/{total_fotos_manobra})" if total_fotos_manobra > 1 else ""
            caption = Paragraph(f"<b>Manobra {item['Item']}{lbl_foto}</b>: {item['De (m)']}m - {item['Até (m)']}m | Cx: {item['Nº Cx']}", st_td)
            
            cell_table = Table([[rl_img], [caption]], colWidths=[8.5*cm])
            cell_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3)
            ]))
            cards_de_fotos.append(cell_table)

    if cards_de_fotos:
        foto_rows = []
        current_row = []
        
        for idx, card in enumerate(cards_de_fotos):
            current_row.append(card)
            if len(current_row) == 3 or idx == len(cards_de_fotos) - 1:
                while len(current_row) < 3:
                    current_row.append("")
                foto_rows.append(current_row)
                current_row = []
                
        grid_fotos = Table(foto_rows, colWidths=[9.2*cm, 9.2*cm, 9.2*cm])
        grid_fotos.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8)
        ]))
        elements.append(grid_fotos)
    else:
        no_photo_box = Table([[Paragraph("Nenhum registro fotográfico foi anexado para este boletim de sondagem.", st_obs_body)]], colWidths=[28.1*cm])
        no_photo_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ]))
        elements.append(no_photo_box)

    doc.build(elements, canvasmaker=DrillDataCanvas)

    st.download_button(
        "📄 Baixar Relatório PDF Atualizado (.pdf)",
        data=buf_pdf.getvalue(),
        file_name=f"Relatorio_DrillData_{furo_id if furo_id else 'Sondagem'}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
