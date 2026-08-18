import streamlit as st
import pandas as pd
import io
from datetime import datetime
from PIL import Image

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, Image as RLImage
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

# --- INICIALIZAÇÃO DINÂMICA DA SESSÃO ---
if 'itens_sondagem' not in st.session_state:
    st.session_state['itens_sondagem'] = []

st.title("⛏️ DRILLDATA — Sistema Digital de Sondagem Mineral")
st.markdown("---")

# --- 1. CABEÇALHO DO PROJETO & EQUIPE TÉCNICA ---
st.header("1. Cabeçalho do Projeto & Equipe Técnica")

col_logo, col_gest = st.columns([1, 3])
with col_logo:
    st.subheader("🖼️ Logomarca")
    logo_file = st.file_uploader("Carregar Logo (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    img_logo_pil = Image.open(logo_file) if logo_file else None
    if img_logo_pil:
        st.image(img_logo_pil, width=180)

with col_gest:
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        cliente = st.text_input("Projeto/Cliente", value="Mineração Santa Rita")
        sonda = st.text_input("Sonda", value="CS14 Core Drill")
    with col_g2:
        furo_id = st.text_input("Furo", value="DDH-024")
        inclin_azim = st.text_input("Inclin./Azimute", value="-60° / 180°")
    with col_g3:
        sondador = st.text_input("Sondador Responsável", value="Natanael Souza")
        coords = st.text_input("Coordenadas", value="E: 245120 | N: 9284100")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    data_rel = st.date_input("Data", value=datetime.now())
with col_f2:
    turno = st.selectbox("Turno", ["Diurno", "Noturno"])
with col_f3:
    diesel_input = st.number_input("Consumo Total Diesel (L)", value=105, step=5)

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
    horario_str = st.text_input("Horário (Ex: 07:00 - 08:15)", value="07:00 - 08:15")
with col_h2:
    motivo_parada = st.text_input("Motivo Parada", value="Nenhuma")
with col_l1:
    litologia_obs = st.text_input("Descrição Litológica / Observações", value="Solo de alteração / saprolito.")

# Registro Fotográfico da Manobra / Caixa
st.subheader("📷 Registro Fotográfico da Manobra")
aba_cam, aba_up = st.tabs(["📸 Tirar Foto Agora", "📁 Carregar da Galeria"])

img_capturada = None
with aba_cam:
    foto_cam = st.camera_input("Tirar foto da caixa/testemunho")
    if foto_cam:
        img_capturada = Image.open(foto_cam)

with aba_up:
    foto_file = st.file_uploader("Selecione uma imagem", type=['jpg', 'jpeg', 'png'], key="uploader_manobra")
    if foto_file and not img_capturada:
        img_capturada = Image.open(foto_file)

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
            "Foto": img_capturada
        })
        st.success("✅ Manobra registrada com sucesso!")
        st.rerun()

if btn_remover and st.session_state['itens_sondagem']:
    st.session_state['itens_sondagem'].pop()
    st.warning("🗑️ Última manobra removida.")
    st.rerun()

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
    ult_cx = "N/A"

st.markdown("---")
st.subheader("📋 Tabela do Boletim Diário")
if not df.empty:
    df_exibicao = df.drop(columns=['Foto'], errors='ignore')
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
else:
    st.info("Nenhuma manobra cadastrada até o momento. Preencha os campos acima para iniciar.")

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

# 1. CABEÇALHO SUPERIOR
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
    [Paragraph("<b>Sondador Responsável:</b> " + sondador, st_meta_lbl), Paragraph("<b>Coordenadas:</b> " + coords, st_meta_lbl), Paragraph("<b>Última Caixa:</b> " + str(ult_cx), st_meta_lbl)]
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

# 2. CARDS DE KPIS
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

# 3. TABELA DE DADOS
pdf_table = [[
    Paragraph("Item", st_th), Paragraph("Horário", st_th), Paragraph("De (m)", st_th), Paragraph("Até (m)", st_th),
    Paragraph("Avanço (m)", st_th), Paragraph("Acumulado (m)", st_th), Paragraph("Recup. (m)", st_th), Paragraph("Recup. (%)", st_th),
    Paragraph("Nº Cx", st_th), Paragraph("Parado", st_th), Paragraph("Motivo Parada", st_th), Paragraph("Descrição Litológica / Observações", st_th)
]]

if not df.empty:
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
    Paragraph(f"<b>{progresso_total:.2f} m</b>".replace('.', ','), st_td), Paragraph(f"<b>{(df['Acumulado (m)'].max() if not df.empty else 0.0):.2f} m</b>".replace('.', ','), st_td),
    Paragraph(f"<b>{recup_tot_m:.2f} m</b>".replace('.', ','), st_td_rec), Paragraph(f"<b>{media_rec:.1f}%</b>".replace('.', ','), st_td_rec),
    Paragraph(f"<b>{ult_cx}</b>", st_td), Paragraph(f"<b>{total_paradas:.1f} h</b>".replace('.', ','), st_td),
    Paragraph(f"<b>Diesel: {diesel_input} L</b>", st_td_left), Paragraph("Furo em andamento/finalizado.", st_td_left)
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
elements.append(Spacer(1, 12))

# 4. REGISTRO FOTOGRÁFICO NO PDF
fotos_para_pdf = [item for item in st.session_state['itens_sondagem'] if item.get('Foto') is not None]

if fotos_para_pdf:
    elements.append(Paragraph("<b>REGISTRO FOTOGRÁFICO DOS TESTEMUNHOS</b>", ParagraphStyle('H_Foto', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#0F172A'))))
    elements.append(Spacer(1, 4))
    
    foto_rows = []
    current_row = []
    
    for idx, item in enumerate(fotos_para_pdf):
        img_buffer = io.BytesIO()
        item['Foto'].convert('RGB').save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        rl_img = RLImage(img_buffer, width=8.5*cm, height=4.5*cm)
        caption = Paragraph(f"<b>Manobra {item['Item']}</b>: {item['De (m)']}m - {item['Até (m)']}m | Caixa {item['Nº Cx']}", st_td)
        
        cell_table = Table([[rl_img], [caption]], colWidths=[8.5*cm])
        cell_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2)
        ]))
        
        current_row.append(cell_table)
        
        if len(current_row) == 3 or idx == len(fotos_para_pdf) - 1:
            while len(current_row) < 3:
                current_row.append("")
            foto_rows.append(current_row)
            current_row = []
            
    grid_fotos = Table(foto_rows, colWidths=[9.2*cm, 9.2*cm, 9.2*cm])
    grid_fotos.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6)
    ]))
    elements.append(KeepTogether([grid_fotos]))
    elements.append(Spacer(1, 12))

# 5. ASSINATURAS
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
    "📄 Baixar Relatório PDF Atualizado (.pdf)",
    data=buf_pdf.getvalue(),
    file_name=f"Relatorio_DrillData_{furo_id}.pdf",
    mime="application/pdf",
    use_container_width=True
)
