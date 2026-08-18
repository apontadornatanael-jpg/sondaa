import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime
from PIL import Image

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as OpenpyxlImage

# ReportLab para geração do PDF no padrão DrillData
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

# --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
st.set_page_config(page_title="DrillData - Boletim Diário de Sondagem", layout="wide")

# Ocultar elementos padrão do Streamlit Cloud
ocultar_elementos = """
    <style>
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stAppHeader {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    button[title="Manage app"] {display: none !important;}
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    </style>
"""
st.markdown(ocultar_elementos, unsafe_allow_html=True)

# Estilização no padrão Verde DrillData
st.markdown("""
    <style>
    h1 {
        color: #065F46 !important;
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        padding: 16px 20px;
        border-radius: 12px;
        border-left: 6px solid #059669;
        font-weight: 800 !important;
    }
    h2, h3 { color: #047857 !important; font-weight: 700 !important; }
    .stButton > button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSÃO E DADOS INICIAIS ---
if 'itens_sondagem' not in st.session_state:
    st.session_state['itens_sondagem'] = [
        {"Item": 1, "Horário": "07:00 - 08:15", "De (m)": 0.00, "Até (m)": 1.50, "Avanço (m)": 1.50, "Acumulado (m)": 1.50, "Recup. (m)": 1.45, "Recup. (%)": 96.7, "Nº Cx": "01", "Parado (h)": 0.0, "Motivo Parada": "Troca de Broca", "Descrição Litológica / Observações": "Início do furo HQ. Solo de alteração/ saprolito."},
        {"Item": 2, "Horário": "08:15 - 09:30", "De (m)": 1.50, "Até (m)": 3.00, "Avanço (m)": 1.50, "Acumulado (m)": 3.00, "Recup. (m)": 1.50, "Recup. (%)": 100.0, "Nº Cx": "01", "Parado (h)": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Saprolito avermelhado com fragmentos de quartzo."},
        {"Item": 3, "Horário": "09:30 - 11:00", "De (m)": 3.00, "Até (m)": 6.00, "Avanço (m)": 3.00, "Acumulado (m)": 6.00, "Recup. (m)": 2.85, "Recup. (%)": 95.0, "Nº Cx": "02", "Parado (h)": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Passagem para rocha alterada (Xisto friável)."},
        {"Item": 4, "Horário": "11:00 - 12:00", "De (m)": 6.00, "Até (m)": 7.50, "Avanço (m)": 1.50, "Acumulado (m)": 7.50, "Recup. (m)": 1.50, "Recup. (%)": 100.0, "Nº Cx": "02", "Parado (h)": 1.0, "Motivo Parada": "Manutenção Mecânica", "Descrição Litológica / Observações": "Ajuste na bomba de lama / VAZAMENTO."},
        {"Item": 5, "Horário": "13:00 - 14:30", "De (m)": 7.50, "Até (m)": 10.50, "Avanço (m)": 3.00, "Acumulado (m)": 10.50, "Recup. (m)": 2.95, "Recup. (%)": 98.3, "Nº Cx": "03", "Parado (h)": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Rocha sã (Gnaisse cinza médio). Transição NQ."},
        {"Item": 6, "Horário": "14:30 - 15:45", "De (m)": 10.50, "Até (m)": 13.50, "Avanço (m)": 3.00, "Acumulado (m)": 13.50, "Recup. (m)": 3.00, "Recup. (%)": 100.0, "Nº Cx": "03", "Parado (h)": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Rocha sã maciça, excelente RQD."},
        {"Item": 7, "Horário": "15:45 - 16:30", "De (m)": 13.50, "Até (m)": 15.00, "Avanço (m)": 1.50, "Acumulado (m)": 15.00, "Recup. (m)": 1.48, "Recup. (%)": 98.7, "Nº Cx": "04", "Parado (h)": 0.5, "Motivo Parada": "Aguardando Água", "Descrição Litológica / Observações": "Caminhão pipa em reabastecimento."},
        {"Item": 8, "Horário": "16:30 - 17:30", "De (m)": 15.00, "Até (m)": 18.00, "Avanço (m)": 3.00, "Acumulado (m)": 18.00, "Recup. (m)": 3.00, "Recup. (%)": 100.0, "Nº Cx": "04", "Parado (h)": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Fim do turno. Preservação do testemunho."}
    ]

st.title("⛏️ DRILLDATA — Sistema Digital de Sondagem Mineral")
st.markdown("---")

# --- 1. CABEÇALHO DO RELATÓRIO ---
st.header("1. Cabeçalho do Projeto & Equipamento")

c_l1, c_l2 = st.columns([1, 4])
with c_l1:
    logo_up = st.file_uploader("Logo da Empresa", type=['png', 'jpg', 'jpeg'])
    img_logo = Image.open(logo_up) if logo_up else None
with c_l2:
    g1, g2, g3 = st.columns(3)
    with g1:
        cliente = st.text_input("Projeto/Cliente", value="Mineração Santa Rita")
        furo_id = st.text_input("Furo", value="DDH-024")
        data_rel = st.date_input("Data", value=datetime(2026, 8, 17))
    with g2:
        sonda = st.text_input("Sonda", value="CS14 Core Drill")
        inclin_azim = st.text_input("Inclin. / Azimute", value="-60° / 180°")
        turno = st.selectbox("Turno", ["Diurno", "Noturno"])
    with g3:
        sondador = st.text_input("Sondador Responsável", value="Natanael Souza")
        coords = st.text_input("Coordenadas", value="E: 245120 | N: 9284100")
        ult_cx = st.text_input("Última Caixa", value="Nº 04")

st.markdown("---")

# --- 2. ENTRADA DE MANOBRAS ---
st.header("2. Registro Operacional do Turno")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    h_inicio = st.time_input("Hora Início", value=datetime.strptime("07:00", "%H:%M").time())
    h_fim = st.time_input("Hora Fim", value=datetime.strptime("08:15", "%H:%M").time())
with c2:
    de_m = st.number_input("De (m)", value=0.00, step=0.5, format="%.2f")
    ate_m = st.number_input("Até (m)", value=1.50, step=0.5, format="%.2f")
with c3:
    rec_m = st.number_input("Recup. (m)", value=1.45, step=0.01, format="%.2f")
    cx_num = st.text_input("Nº Caixa", value="01")
with c4:
    parado_h = st.number_input("Horas Parado (h)", value=0.0, step=0.5)
    motivo = st.text_input("Motivo Parada", value="Nenhuma")
with c5:
    diesel_input = st.number_input("Consumo Diesel Turno (L)", value=105, step=5)

obs_lito = st.text_area("Descrição Litológica / Observações", value="Início do furo HQ. Solo de alteração/ saprolito.")

if st.button("➕ Adicionar Registro ao Boletim"):
    avanco = round(ate_m - de_m, 2)
    rec_pct = round((rec_m / avanco) * 100, 1) if avanco > 0 else 0.0
    item_n = len(st.session_state['itens_sondagem']) + 1
    acum = (st.session_state['itens_sondagem'][-1]['Acumulado (m)'] if st.session_state['itens_sondagem'] else 0.0) + avanco
    
    st.session_state['itens_sondagem'].append({
        "Item": item_n,
        "Horário": f"{h_inicio.strftime('%H:%M')} - {h_fim.strftime('%H:%M')}",
        "De (m)": de_m, "Até (m)": ate_m, "Avanço (m)": avanco,
        "Acumulado (m)": acum, "Recup. (m)": rec_m, "Recup. (%)": rec_pct,
        "Nº Cx": cx_num, "Parado (h)": parado_h, "Motivo Parada": motivo,
        "Descrição Litológica / Observações": obs_lito
    })
    st.success("Item adicionado com sucesso!")
    st.rerun()

st.markdown("---")

# --- 3. EXIBIÇÃO E KPIS ---
df = pd.DataFrame(st.session_state['itens_sondagem'])

progresso_total = df['Avanço (m)'].sum()
media_rec = df['Recup. (%)'].mean()
total_paradas = df['Parado (h)'].sum()

st.header("3. Resumo Diário & Tabela do Boletim")

k1, k2, k3, k4 = st.columns(4)
k1.metric("PROGRESSO TOTAL PERFURADO", f"{progresso_total:.2f} m")
k2.metric("MÉDIA DE RECUPERAÇÃO", f"{media_rec:.1f} %")
k3.metric("TOTAL HORAS PARADAS", f"{total_paradas:.1f} h")
k4.metric("CONSUMO TOTAL DIESEL", f"{diesel_input} L")

st.dataframe(df, use_container_width=True, hide_index=True)

# --- 4. EXPORTAÇÕES (EXCEL E PDF DRILLDATA) ---
col_ex1, col_ex2 = st.columns(2)

# --- GERADOR DE EXCEL (DRILLDATA FORMAT) ---
with col_ex1:
    buffer_xls = io.BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Boletim DrillData"
    ws.views.sheetView[0].showGridLines = True

    # Estilos
    f_tit = Font(name='Arial', size=12, bold=True, color='065F46')
    f_sub = Font(name='Arial', size=9, bold=True, color='1F2937')
    f_head = Font(name='Arial', size=8, bold=True, color='FFFFFF')
    f_body = Font(name='Arial', size=8)
    f_tot = Font(name='Arial', size=8, bold=True, color='000000')

    fill_head = PatternFill('solid', fgColor='059669')
    fill_tot = PatternFill('solid', fgColor='E5E7EB')
    fill_kpi = PatternFill('solid', fgColor='ECFDF5')

    border_thin = Border(left=Side(style='thin', color='CCCCCC'), right=Side(style='thin', color='CCCCCC'),
                         top=Side(style='thin', color='CCCCCC'), bottom=Side(style='thin', color='CCCCCC'))

    al_center = Alignment(horizontal='center', vertical='center', wrap_text=True)
    al_left = Alignment(horizontal='left', vertical='center', wrap_text=True)
    al_right = Alignment(horizontal='right', vertical='center')

    # Titulo
    ws.merge_cells('A1:L1')
    ws['A1'] = "DRILLDATA - Relatório Técnico & Boletim Diário de Sondagem"
    ws['A1'].font = f_tit
    ws['A1'].alignment = al_center

    # Metadados
    meta = [
        [f"Projeto/Cliente: {cliente}", f"Furo: {furo_id}", f"Data: {data_rel.strftime('%d/%m/%Y')}"],
        [f"Sonda: {sonda}", f"Inclin./Azimute: {inclin_azim}", f"Turno: {turno}"],
        [f"Sondador Resp.: {sondador}", f"Coordenadas: {coords}", f"Última Caixa: {ult_cx}"]
    ]
    for r_idx, row in enumerate(meta, start=2):
        ws.cell(row=r_idx, column=1, value=row[0]).font = f_sub
        ws.cell(row=r_idx, column=5, value=row[1]).font = f_sub
        ws.cell(row=r_idx, column=9, value=row[2]).font = f_sub

    # KPIs
    ws.merge_cells('A6:C6'); ws['A6'] = f"PROGRESSO TOTAL: {progresso_total:.2f} m"
    ws.merge_cells('D6:F6'); ws['D6'] = f"MÉDIA RECUPERAÇÃO: {media_rec:.1f} %"
    ws.merge_cells('G6:I6'); ws['G6'] = f"TOTAL H. PARADAS: {total_paradas:.1f} h"
    ws.merge_cells('J6:L6'); ws['J6'] = f"CONSUMO DIESEL: {diesel_input} L"
    for c in range(1, 13):
        ws.cell(row=6, column=c).fill = fill_kpi
        ws.cell(row=6, column=c).font = f_sub
        ws.cell(row=6, column=c).alignment = al_center

    # Tabela Headers
    headers = ["Item", "Horário", "De (m)", "Até (m)", "Avanço (m)", "Acumulado (m)", "Recup. (m)", "Recup. (%)", "Nº Cx", "Parado", "Motivo Parada", "Descrição Litológica / Observações"]
    ws.row_dimensions[8].height = 25
    for c_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=8, column=c_idx, value=h)
        cell.font = f_head
        cell.fill = fill_head
        cell.alignment = al_center
        cell.border = border_thin

    # Linhas
    curr_r = 9
    for _, r in df.iterrows():
        ws.cell(row=curr_r, column=1, value=r['Item']).alignment = al_center
        ws.cell(row=curr_r, column=2, value=r['Horário']).alignment = al_center
        ws.cell(row=curr_r, column=3, value=r['De (m)']).alignment = al_right
        ws.cell(row=curr_r, column=4, value=r['Até (m)']).alignment = al_right
        ws.cell(row=curr_r, column=5, value=r['Avanço (m)']).alignment = al_right
        ws.cell(row=curr_r, column=6, value=r['Acumulado (m)']).alignment = al_right
        ws.cell(row=curr_r, column=7, value=r['Recup. (m)']).alignment = al_right
        ws.cell(row=curr_r, column=8, value=f"{r['Recup. (%)']:.1f}%").alignment = al_right
        ws.cell(row=curr_r, column=9, value=r['Nº Cx']).alignment = al_center
        ws.cell(row=curr_r, column=10, value=f"{r['Parado (h)']} h").alignment = al_center
        ws.cell(row=curr_r, column=11, value=r['Motivo Parada']).alignment = al_left
        ws.cell(row=curr_r, column=12, value=r['Descrição Litológica / Observações']).alignment = al_left

        for c in range(1, 13):
            ws.cell(row=curr_r, column=c).font = f_body
            ws.cell(row=curr_r, column=c).border = border_thin
        curr_r += 1

    # Totais
    ws.cell(row=curr_r, column=1, value="TOTAIS / MÉDIAS:").font = f_tot
    ws.cell(row=curr_r, column=5, value=progresso_total).font = f_tot
    ws.cell(row=curr_r, column=6, value=df['Acumulado (m)'].max()).font = f_tot
    ws.cell(row=curr_r, column=7, value=df['Recup. (m)'].sum()).font = f_tot
    ws.cell(row=curr_r, column=8, value=f"{media_rec:.1f}%").font = f_tot
    ws.cell(row=curr_r, column=10, value=f"{total_paradas:.1f} h").font = f_tot
    ws.cell(row=curr_r, column=12, value=f"Diesel: {diesel_input} L").font = f_tot

    for c in range(1, 13):
        ws.cell(row=curr_r, column=c).fill = fill_tot
        ws.cell(row=curr_r, column=c).border = border_thin

    # Largura de colunas
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = 14
    ws.column_dimensions['L'].width = 35

    wb.save(buffer_xls)
    st.download_button(
        "📊 Baixar Planilha Excel (.xlsx)",
        data=buffer_xls.getvalue(),
        file_name=f"Boletim_DrillData_{furo_id}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# --- GERADOR DE PDF EXATO DRILLDATA (REPORTLAB) ---
with col_ex2:
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
                self.setFillColor(colors.HexColor('#4B5563'))
                self.drawString(1.5*cm, 1.0*cm, "DrillData — Sistema Digital de Sondagem Mineral")
                self.drawRightString(28.2*cm, 1.0*cm, f"Página {self._pageNumber} de {num_pages}")
                super().showPage()
            super().save()

    pdf_buf = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buf, pagesize=landscape(A4),
        leftMargin=1.2*cm, rightMargin=1.2*cm,
        topMargin=1.2*cm, bottomMargin=1.5*cm
    )
    elements = []
    styles = getSampleStyleSheet()

    st_tit = ParagraphStyle('DocTit', fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=colors.HexColor('#065F46'))
    st_sub = ParagraphStyle('DocSub', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor('#1F2937'))
    st_meta_lbl = ParagraphStyle('MetaLbl', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.HexColor('#374151'))
    st_meta_val = ParagraphStyle('MetaVal', fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#111827'))
    
    st_kpi_num = ParagraphStyle('KpiNum', fontName='Helvetica-Bold', fontSize=11, leading=13, alignment=1, textColor=colors.HexColor('#065F46'))
    st_kpi_lbl = ParagraphStyle('KpiLbl', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=1, textColor=colors.HexColor('#4B5563'))

    st_th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=7, leading=8, alignment=1, textColor=colors.white)
    st_td = ParagraphStyle('TD', fontName='Helvetica', fontSize=6.5, leading=8, alignment=1)
    st_td_left = ParagraphStyle('TDL', fontName='Helvetica', fontSize=6.5, leading=8, alignment=0)

    # 1. Header DrillData
    hdr_txt = f"<b>DRILLDATA</b><br/><font size=9 color='#047857'>Relatório Técnico & Boletim Diário de Sondagem</font>"
    header_table = Table([[Paragraph(hdr_txt, st_tit)]], colWidths=[27.0*cm])
    elements.append(header_table)
    elements.append(Spacer(1, 4))

    # 2. Grid Metadados
    meta_data = [
        [Paragraph("<b>Projeto/Cliente:</b>", st_meta_lbl), Paragraph(cliente, st_meta_val), Paragraph("<b>Furo:</b>", st_meta_lbl), Paragraph(furo_id, st_meta_val), Paragraph("<b>Data:</b>", st_meta_lbl), Paragraph(data_rel.strftime('%d/%m/%Y'), st_meta_val)],
        [Paragraph("<b>Sonda:</b>", st_meta_lbl), Paragraph(sonda, st_meta_val), Paragraph("<b>Inclin./Azimute:</b>", st_meta_lbl), Paragraph(inclin_azim, st_meta_val), Paragraph("<b>Turno:</b>", st_meta_lbl), Paragraph(turno, st_meta_val)],
        [Paragraph("<b>Sondador Resp.:</b>", st_meta_lbl), Paragraph(sondador, st_meta_val), Paragraph("<b>Coordenadas:</b>", st_meta_lbl), Paragraph(coords, st_meta_val), Paragraph("<b>Última Caixa:</b>", st_meta_lbl), Paragraph(ult_cx, st_meta_val)]
    ]
    t_meta = Table(meta_data, colWidths=[2.5*cm, 6.5*cm, 2.5*cm, 6.5*cm, 2.5*cm, 6.5*cm])
    t_meta.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9FAFB')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 6))

    # 3. Cards KPIs
    kpi_table_data = [[
        Paragraph(f"PROGRESSO TOTAL PERFURADO<br/><font size=10 color='#065F46'><b>{progresso_total:.2f} m</b></font>", st_kpi_lbl),
        Paragraph(f"MÉDIA DE RECUPERAÇÃO<br/><font size=10 color='#065F46'><b>{media_rec:.1f} %</b></font>", st_kpi_lbl),
        Paragraph(f"TOTAL HORAS PARADAS<br/><font size=10 color='#065F46'><b>{total_paradas:.1f} h</b></font>", st_kpi_lbl),
        Paragraph(f"CONSUMO TOTAL DIESEL<br/><font size=10 color='#065F46'><b>{diesel_input} L</b></font>", st_kpi_lbl),
    ]]
    t_kpi = Table(kpi_table_data, colWidths=[6.75*cm]*4)
    t_kpi.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#10B981')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ECFDF5')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_kpi)
    elements.append(Spacer(1, 8))

    # 4. Tabela Operacional
    table_pdf = [[
        Paragraph("Item", st_th), Paragraph("Horário", st_th), Paragraph("De (m)", st_th), Paragraph("Até (m)", st_th),
        Paragraph("Avanço (m)", st_th), Paragraph("Acumulado (m)", st_th), Paragraph("Recup. (m)", st_th), Paragraph("Recup. (%)", st_th),
        Paragraph("Nº Cx", st_th), Paragraph("Parado", st_th), Paragraph("Motivo Parada", st_th), Paragraph("Descrição Litológica / Observações", st_th)
    ]]

    for _, r in df.iterrows():
        table_pdf.append([
            Paragraph(str(r['Item']), st_td), Paragraph(r['Horário'], st_td),
            Paragraph(f"{r['De (m)']:.2f}", st_td), Paragraph(f"{r['Até (m)']:.2f}", st_td),
            Paragraph(f"{r['Avanço (m)']:.2f}", st_td), Paragraph(f"{r['Acumulado (m)']:.2f}", st_td),
            Paragraph(f"{r['Recup. (m)']:.2f}", st_td), Paragraph(f"{r['Recup. (%)']:.1f}%", st_td),
            Paragraph(str(r['Nº Cx']), st_td), Paragraph(f"{r['Parado (h)']} h", st_td),
            Paragraph(r['Motivo Parada'], st_td_left), Paragraph(r['Descrição Litológica / Observações'], st_td_left)
        ])

    # Linha de Totais
    table_pdf.append([
        Paragraph("<b>TOTAIS / MÉDIAS:</b>", st_td_left), Paragraph("", st_td), Paragraph("", st_td), Paragraph("", st_td),
        Paragraph(f"<b>{progresso_total:.2f} m</b>", st_td), Paragraph(f"<b>{df['Acumulado (m)'].max():.2f} m</b>", st_td),
        Paragraph(f"<b>{df['Recup. (m)'].sum():.2f} m</b>", st_td), Paragraph(f"<b>{media_rec:.1f}%</b>", st_td),
        Paragraph(f"<b>{ult_cx}</b>", st_td), Paragraph(f"<b>{total_paradas:.1f} h</b>", st_td),
        Paragraph(f"<b>Diesel: {diesel_input} L</b>", st_td_left), Paragraph("Furo acompanhado com alta recuperação.", st_td_left)
    ])

    col_w = [0.9*cm, 1.8*cm, 1.2*cm, 1.2*cm, 1.4*cm, 1.6*cm, 1.4*cm, 1.4*cm, 1.0*cm, 1.1*cm, 2.8*cm, 9.2*cm]
    t_ops = Table(table_pdf, colWidths=col_w)
    t_ops.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#059669')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E5E7EB')),
    ]))
    elements.append(t_ops)
    elements.append(Spacer(1, 15))

    # 5. Bloco Triplo de Assinaturas (Padrão DrillData)
    st_ass_nome = ParagraphStyle('AssNome', fontName='Helvetica-Bold', fontSize=7.5, leading=9, alignment=1)
    st_ass_cargo = ParagraphStyle('AssCargo', fontName='Helvetica', fontSize=7, leading=8, alignment=1, textColor=colors.HexColor('#4B5563'))

    ass_data = [
        [Paragraph("___________________________________", st_ass_nome), Paragraph("___________________________________", st_ass_nome), Paragraph("___________________________________", st_ass_nome)],
        [Paragraph(f"<b>{sondador}</b>", st_ass_nome), Paragraph("<b>Eng. Geotécnico / Geólogo</b>", st_ass_nome), Paragraph(f"<b>{cliente}</b>", st_ass_nome)],
        [Paragraph("Sondador / Operador Responsável", st_ass_cargo), Paragraph("Fiscalização de Campo", st_ass_cargo), Paragraph("Supervisão de Operações", st_ass_cargo)]
    ]
    t_ass = Table(ass_data, colWidths=[9.0*cm, 9.0*cm, 9.0*cm])
    t_ass.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    
    elements.append(KeepTogether(t_ass))

    doc.build(elements, canvasmaker=DrillDataCanvas)

    st.download_button(
        "📄 Baixar Relatório PDF (.pdf)",
        data=pdf_buf.getvalue(),
        file_name=f"Relatorio_DrillData_{furo_id}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
