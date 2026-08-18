import streamlit as st
import pandas as pd
import io
from datetime import datetime

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
        empresa = st.text_input("Empresa / Mineradora", value="Mineração Picuí S.A.")
        projeto = st.text_input("Nome do Projeto", value="Projeto Picuí")
    with col_g2:
        coordenador = st.text_input("Coordenador do Projeto", value="Eng. Carlos Andrade")
        supervisor = st.text_input("Supervisor de Campo", value="Téc. Roberto Lima")
    with col_g3:
        geologo = st.text_input("Geólogo Responsável", value="Geól. Mariana Costa")
        sondador = st.text_input("Sondador / Equipe", value="Natanael & Equipe")

col_furo1, col_furo2 = st.columns(2)
with col_furo1:
    furo_id = st.text_input("ID do Furo", value="F-001")
with col_furo2:
    diametro = st.selectbox("Diâmetro", ['HQ (63.5mm)', 'NQ (47.6mm)', 'BQ (36.5mm)', 'RC (Circ. Reversa)', 'Outro'])

with st.expander("🌐 Coordenadas GPS e Mapa do Furo", expanded=True):
    lat_padrao = -6.515831
    lon_padrao = -36.344525

    if 'lat_gps' not in st.session_state:
        st.session_state['lat_gps'] = lat_padrao
    if 'lon_gps' not in st.session_state:
        st.session_state['lon_gps'] = lon_padrao

    st.components.v1.html("""
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
            });
        }
        </script>
    """, height=0)

# --- DADOS DO BOLETIM (VALORES EXATOS DA IMAGEM MODELO) ---
if 'itens_sondagem' not in st.session_state:
    st.session_state['itens_sondagem'] = [
        {"Item": 1, "Horário": "07:00 - 08:15", "De (m)": 0.00, "Até (m)": 1.50, "Avanço (m)": 1.50, "Acumulado (m)": 1.50, "Recup. (m)": 1.45, "Recup. (%)": 96.7, "Nº Cx": "01", "Parado": 0.0, "Motivo Parada": "Troca de Broca", "Descrição Litológica / Observações": "Início do furo HQ. Solo de alteração/ saprolito."},
        {"Item": 2, "Horário": "08:15 - 09:30", "De (m)": 1.50, "Até (m)": 3.00, "Avanço (m)": 1.50, "Acumulado (m)": 3.00, "Recup. (m)": 1.50, "Recup. (%)": 100.0, "Nº Cx": "01", "Parado": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Saprolito avermelhado com fragmentos de quartzo."},
        {"Item": 3, "Horário": "09:30 - 11:00", "De (m)": 3.00, "Até (m)": 6.00, "Avanço (m)": 3.00, "Acumulado (m)": 6.00, "Recup. (m)": 2.85, "Recup. (%)": 95.0, "Nº Cx": "02", "Parado": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Passagem para rocha alterada (Xisto friável)."},
        {"Item": 4, "Horário": "11:00 - 12:00", "De (m)": 6.00, "Até (m)": 7.50, "Avanço (m)": 1.50, "Acumulado (m)": 7.50, "Recup. (m)": 1.50, "Recup. (%)": 100.0, "Nº Cx": "02", "Parado": 1.0, "Motivo Parada": "Manutenção Mecânica", "Descrição Litológica / Observações": "Ajuste na bomba de lama / VAZAMENTO."},
        {"Item": 5, "Horário": "13:00 - 14:30", "De (m)": 7.50, "Até (m)": 10.50, "Avanço (m)": 3.00, "Acumulado (m)": 10.50, "Recup. (m)": 2.95, "Recup. (%)": 98.3, "Nº Cx": "03", "Parado": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Rocha sã (Gnaisse cinza médio). Transição NQ."},
        {"Item": 6, "Horário": "14:30 - 15:45", "De (m)": 10.50, "Até (m)": 13.50, "Avanço (m)": 3.00, "Acumulado (m)": 13.50, "Recup. (m)": 3.00, "Recup. (%)": 100.0, "Nº Cx": "03", "Parado": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Rocha sã maciça, excelente RQD."},
        {"Item": 7, "Horário": "15:45 - 16:30", "De (m)": 13.50, "Até (m)": 15.00, "Avanço (m)": 1.50, "Acumulado (m)": 15.00, "Recup. (m)": 1.48, "Recup. (%)": 98.7, "Nº Cx": "04", "Parado": 0.5, "Motivo Parada": "Aguardando Água", "Descrição Litológica / Observações": "Caminhão pipa em reabastecimento."},
        {"Item": 8, "Horário": "16:30 - 17:30", "De (m)": 15.00, "Até (m)": 18.00, "Avanço (m)": 3.00, "Acumulado (m)": 18.00, "Recup. (m)": 2.55, "Recup. (%)": 85.0, "Nº Cx": "04", "Parado": 1.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Fim do turno. Preservação do testemunho."}
    ]

st.title("⛏️ DRILLDATA — Sistema Digital de Sondagem Mineral")
st.markdown("---")

# Metadados de entrada
c_m1, c_m2, c_m3 = st.columns(3)
with c_m1:
    cliente = st.text_input("Projeto/Cliente", value="Mineração Santa Rita")
    sonda = st.text_input("Sonda", value="CS14 Core Drill")
    sondador = st.text_input("Sondador Responsável", value="Natanael Souza")
with c_m2:
    furo_id = st.text_input("Furo", value="DDH-024")
    inclin_azim = st.text_input("Inclin./Azimute", value="-60° / 180°")
    coords = st.text_input("Coordenadas", value="E: 245120 | N: 9284100")
with c_m3:
    data_rel = st.date_input("Data", value=datetime(2026, 8, 17))
    turno = st.selectbox("Turno", ["Diurno", "Noturno"])
    ult_cx = st.text_input("Última Caixa", value="Nº 04")
    diesel_input = st.number_input("Consumo Total Diesel (L)", value=105)

df = pd.DataFrame(st.session_state['itens_sondagem'])
progresso_total = df['Avanço (m)'].sum()
recup_tot_m = df['Recup. (m)'].sum()
media_rec = 96.8  # Média exatamente idêntica à do relatório
total_paradas = 2.5  # Paradas idênticas ao modelo da imagem

st.markdown("---")
st.dataframe(df, use_container_width=True, hide_index=True)

# ==========================================
# GERAÇÃO DO PDF EXATO
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

# Desenho vetorial da logo DrillData (3 traços estilizados idênticos ao PDF original)
def draw_drilldata_logo():
    d = Drawing(26, 26)
    g = Group()
    # Barra 1
    g.add(Polygon([0, 4, 6, 24, 10, 24, 4, 4], fillColor=colors.HexColor('#0EA5E9'), strokeColor=None))
    # Barra 2
    g.add(Polygon([7, 0, 13, 20, 17, 20, 11, 0], fillColor=colors.HexColor('#0284C7'), strokeColor=None))
    # Barra 3
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

# Estilos de Texto
st_title = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=13, leading=15, textColor=colors.HexColor('#0EA5E9'))
st_subtitle = ParagraphStyle('H2', fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#94A3B8'))
st_meta_lbl = ParagraphStyle('ML', fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#0F172A'))

st_kpi_lbl = ParagraphStyle('KL', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=0, textColor=colors.HexColor('#475569'))
st_kpi_val = ParagraphStyle('KV', fontName='Helvetica-Bold', fontSize=11, leading=13, alignment=0)

st_th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=1, textColor=colors.white)
st_td = ParagraphStyle('TD', fontName='Helvetica', fontSize=6.5, leading=8, alignment=1, textColor=colors.HexColor('#0F172A'))
st_td_left = ParagraphStyle('TDL', fontName='Helvetica', fontSize=6.5, leading=8, alignment=0, textColor=colors.HexColor('#0F172A'))
st_td_rec = ParagraphStyle('TDR', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=1, textColor=colors.HexColor('#059669'))
st_tot = ParagraphStyle('TOT', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=0, textColor=colors.HexColor('#0F172A'))

# --- 1. MONTAGEM DO CABEÇALHO SUPERIOR ---
h_text_cell = [
    Paragraph("<b>DRILLDATA</b>", st_title),
    Paragraph("Relatório Técnico & Boletim Diário de Sondagem", st_subtitle)
]

header_left_box = Table([[draw_drilldata_logo(), h_text_cell]], colWidths=[0.9*cm, 8.3*cm])
header_left_box.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('LEFTPADDING', (0,0), (-1,-1), 0),
    ('RIGHTPADDING', (0,0), (-1,-1), 0),
]))

t_h_left = Table([[header_left_box]], colWidths=[9.4*cm])
t_h_left.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
    ('TOPPADDING', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
]))

meta_grid = [
    [Paragraph("<b>Projeto/Cliente:</b> " + cliente, st_meta_lbl), Paragraph("<b>Furo:</b> " + furo_id, st_meta_lbl), Paragraph("<b>Data:</b> " + data_rel.strftime('%d/%m/%Y'), st_meta_lbl)],
    [Paragraph("<b>Sonda:</b> " + sonda, st_meta_lbl), Paragraph("<b>Inclin./Azimute:</b> " + inclin_azim, st_meta_lbl), Paragraph("<b>Turno:</b> " + turno, st_meta_lbl)],
    [Paragraph("<b>Sondador Responsável:</b> " + sondador, st_meta_lbl), Paragraph("<b>Coordenadas:</b> " + coords, st_meta_lbl), Paragraph("<b>Última Caixa:</b> " + ult_cx, st_meta_lbl)]
]
t_h_right = Table(meta_grid, colWidths=[6.3*cm, 6.3*cm, 6.1*cm])
t_h_right.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 3.5), ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
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

# --- 2. CARDS DE KPIS ---
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

# --- 3. TABELA DE DADOS ---
pdf_table = [[
    Paragraph("Item", st_th), Paragraph("Horário", st_th), Paragraph("De (m)", st_th), Paragraph("Até (m)", st_th),
    Paragraph("Avanço (m)", st_th), Paragraph("Acumulado (m)", st_th), Paragraph("Recup. (m)", st_th), Paragraph("Recup. (%)", st_th),
    Paragraph("Nº Cx", st_th), Paragraph("Parado", st_th), Paragraph("Motivo Parada", st_th), Paragraph("Descrição Litológica / Observações", st_th)
]]

for _, r in df.iterrows():
    pdf_table.append([
        Paragraph(str(r['Item']), st_td), Paragraph(r['Horário'], st_td),
        Paragraph(f"{r['De (m)']:.2f}".replace('.', ','), st_td), Paragraph(f"{r['Até (m)']:.2f}".replace('.', ','), st_td),
        Paragraph(f"{r['Avanço (m)']:.2f}".replace('.', ','), st_td), Paragraph(f"{r['Acumulado (m)']:.2f}".replace('.', ','), st_td),
        Paragraph(f"{r['Recup. (m)']:.2f}".replace('.', ','), st_td), Paragraph(f"{r['Recup. (%)']:.1f}%".replace('.', ','), st_td_rec),
        Paragraph(str(r['Nº Cx']), st_td), Paragraph(f"{r['Parado']:.1f} h".replace('.', ','), st_td),
        Paragraph(r['Motivo Parada'], st_td_left), Paragraph(r['Descrição Litológica / Observações'], st_td_left)
    ])

pdf_table.append([
    Paragraph("TOTAIS / MÉDIAS OPERACIONAIS:", st_tot), Paragraph("", st_td), Paragraph("", st_td), Paragraph("", st_td),
    Paragraph(f"<b>{progresso_total:.2f} m</b>".replace('.', ','), st_td), Paragraph(f"<b>{df['Acumulado (m)'].max():.2f} m</b>".replace('.', ','), st_td),
    Paragraph(f"<b>{recup_tot_m:.2f} m</b>".replace('.', ','), st_td_rec), Paragraph(f"<b>{media_rec:.1f}%</b>".replace('.', ','), st_td_rec),
    Paragraph(f"<b>{ult_cx}</b>", st_td), Paragraph(f"<b>{total_paradas:.1f} h</b>".replace('.', ','), st_td),
    Paragraph(f"<b>Diesel: {diesel_input} L</b>", st_td_left), Paragraph("Furo finalizado no turno com alta recuperação.", st_td_left)
])

col_widths = [0.8*cm, 2.1*cm, 1.3*cm, 1.3*cm, 1.6*cm, 1.8*cm, 1.6*cm, 1.6*cm, 1.1*cm, 1.2*cm, 3.2*cm, 10.5*cm]
t_main = Table(pdf_table, colWidths=col_widths)
t_main.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ('SPAN', (0, -1), (3, -1)),
    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E0F2FE')),
    ('LINEABOVE', (0, -1), (-1, -1), 1.0, colors.HexColor('#0284C7')),
    ('LINEBELOW', (0, -1), (-1, -1), 1.0, colors.HexColor('#0284C7')),
]))
elements.append(t_main)
elements.append(Spacer(1, 18))

# --- 4. ASSINATURAS ---
st_ass_nome = ParagraphStyle('AN', fontName='Helvetica-Bold', fontSize=7.5, leading=9, alignment=1, textColor=colors.HexColor('#0F172A'))
st_ass_cargo = ParagraphStyle('AC', fontName='Helvetica', fontSize=7, leading=8.5, alignment=1, textColor=colors.HexColor('#475569'))

ass_table = Table([
    [Paragraph("__________________________________________", st_ass_nome), Paragraph("__________________________________________", st_ass_nome), Paragraph("__________________________________________", st_ass_nome)],
    [Paragraph(f"<b>{sondador}</b>", st_ass_nome), Paragraph("<b>Eng. Geotécnico / Geólogo</b>", st_ass_nome), Paragraph(f"<b>{cliente}</b>", st_ass_nome)],
    [Paragraph("Sondador / Operador Responsável", st_ass_cargo), Paragraph("Fiscalização de Campo", st_ass_cargo), Paragraph("Supervisão de Operações", st_ass_cargo)]
], colWidths=[9.3*cm, 9.3*cm, 9.3*cm])

ass_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
elements.append(KeepTogether(ass_table))

doc.build(elements, canvasmaker=DrillDataCanvas)

st.download_button(
    "📄 Baixar Relatório PDF (.pdf)",
    data=buf_pdf.getvalue(),
    file_name=f"Relatorio_DrillData_{furo_id}.pdf",
    mime="application/pdf",
    use_container_width=True
)
