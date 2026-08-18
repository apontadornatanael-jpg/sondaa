import streamlit as st
import pandas as pd
import io
from datetime import datetime

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ReportLab para geração do PDF exato DrillData
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, Polygon, Group

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

# --- DADOS DO BOLETIM (IDÊNTICOS AO MODELO DRILLDATA ORIGINAL) ---
if 'itens_sondagem' not in st.session_state:
    st.session_state['itens_sondagem'] = [
        {"Item": 1, "Horário": "07:00 - 08:15", "De (m)": 0.00, "Até (m)": 1.50, "Avanço (m)": 1.50, "Acumulado (m)": 1.50, "Recup. (m)": 1.45, "Recup. (%)": 96.7, "Nº Cx": "01", "Parado": 0.0, "Motivo Parada": "Troca de Broca", "Descrição Litológica / Observações": "Início do furo HQ. Solo de alteração/ saprolito."},
        {"Item": 2, "Horário": "08:15 - 09:30", "De (m)": 1.50, "Até (m)": 3.00, "Avanço (m)": 1.50, "Acumulado (m)": 3.00, "Recup. (m)": 1.50, "Recup. (%)": 100.0, "Nº Cx": "01", "Parado": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Saprolito avermelhado com fragmentos de quartzo."},
        {"Item": 3, "Horário": "09:30 - 11:00", "De (m)": 3.00, "Até (m)": 6.00, "Avanço (m)": 3.00, "Acumulado (m)": 6.00, "Recup. (m)": 2.85, "Recup. (%)": 95.0, "Nº Cx": "02", "Parado": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Passagem para rocha alterada (Xisto friável)."},
        {"Item": 4, "Horário": "11:00 - 12:00", "De (m)": 6.00, "Até (m)": 7.50, "Avanço (m)": 1.50, "Acumulado (m)": 7.50, "Recup. (m)": 1.50, "Recup. (%)": 100.0, "Nº Cx": "02", "Parado": 1.0, "Motivo Parada": "Manutenção Mecânica", "Descrição Litológica / Observações": "Ajuste na bomba de lama / VAZAMENTO."},
        {"Item": 5, "Horário": "13:00 - 14:30", "De (m)": 7.50, "Até (m)": 10.50, "Avanço (m)": 3.00, "Acumulado (m)": 10.50, "Recup. (m)": 2.95, "Recup. (%)": 98.3, "Nº Cx": "03", "Parado": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Rocha sã (Gnaisse cinza médio). Transição NQ."},
        {"Item": 6, "Horário": "14:30 - 15:45", "De (m)": 10.50, "Até (m)": 13.50, "Avanço (m)": 3.00, "Acumulado (m)": 13.50, "Recup. (m)": 3.00, "Recup. (%)": 100.0, "Nº Cx": "03", "Parado": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Rocha sã maciça, excelente RQD."},
        {"Item": 7, "Horário": "15:45 - 16:30", "De (m)": 13.50, "Até (m)": 15.00, "Avanço (m)": 1.50, "Acumulado (m)": 15.00, "Recup. (m)": 1.48, "Recup. (%)": 98.7, "Nº Cx": "04", "Parado": 0.5, "Motivo Parada": "Aguardando Água", "Descrição Litológica / Observações": "Caminhão pipa em reabastecimento."},
        {"Item": 8, "Horário": "16:30 - 17:30", "De (m)": 15.00, "Até (m)": 18.00, "Avanço (m)": 3.00, "Acumulado (m)": 18.00, "Recup. (m)": 3.00, "Recup. (%)": 100.0, "Nº Cx": "04", "Parado": 0.0, "Motivo Parada": "Nenhuma", "Descrição Litológica / Observações": "Fim do turno. Preservação do testemunho."}
    ]

st.title("⛏️ DRILLDATA — Sistema Digital de Sondagem Mineral")
st.markdown("---")

# Metadados
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
media_rec = (recup_tot_m / progresso_total * 100) if progresso_total > 0 else 0.0
total_paradas = df['Parado'].sum()

st.markdown("---")
st.dataframe(df, use_container_width=True, hide_index=True)

col_dl1, col_dl2 = st.columns(2)

# ==========================================
# 1. PLANILHA EXCEL DRILLDATA IDÊNTICA
# ==========================================
with col_dl1:
    buf_excel = io.BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Boletim Diário"
    ws.views.sheetView[0].showGridLines = True

    C_HEADER_BG = "0F172A"
    C_HEADER_FG = "FFFFFF"
    C_GREEN_TEXT = "059669"
    C_TOT_BG = "E0F2FE"
    C_BORDER = "CBD5E1"

    font_hdr_title = Font(name="Arial", size=13, bold=True, color="10B981")
    font_hdr_sub = Font(name="Arial", size=8, color="94A3B8")
    font_meta_lbl = Font(name="Arial", size=8, bold=True, color="0F172A")
    font_th = Font(name="Arial", size=8, bold=True, color=C_HEADER_FG)
    font_td = Font(name="Arial", size=8)
    font_td_rec = Font(name="Arial", size=8, bold=True, color=C_GREEN_TEXT)
    font_tot = Font(name="Arial", size=8, bold=True, color="0F172A")

    fill_hdr = PatternFill("solid", fgColor=C_HEADER_BG)
    fill_th = PatternFill("solid", fgColor=C_HEADER_BG)
    fill_tot = PatternFill("solid", fgColor=C_TOT_BG)
    fill_kpi = PatternFill("solid", fgColor="F8FAFC")

    border_thin = Border(left=Side(style='thin', color=C_BORDER), right=Side(style='thin', color=C_BORDER),
                         top=Side(style='thin', color=C_BORDER), bottom=Side(style='thin', color=C_BORDER))

    al_center = Alignment(horizontal="center", vertical="center")
    al_left = Alignment(horizontal="left", vertical="center")
    al_right = Alignment(horizontal="right", vertical="center")

    ws.merge_cells("A1:D3")
    ws["A1"] = "DRILLDATA\nRelatório Técnico & Boletim Diário de Sondagem"
    ws["A1"].font = font_hdr_title
    ws["A1"].fill = fill_hdr
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    meta_structure = [
        [("E1", "F1", f"Projeto/Cliente: {cliente}"), ("G1", "H1", f"Furo: {furo_id}"), ("I1", "L1", f"Data: {data_rel.strftime('%d/%m/%Y')}")],
        [("E2", "F2", f"Sonda: {sonda}"), ("G2", "H2", f"Inclin./Azimute: {inclin_azim}"), ("I2", "L2", f"Turno: {turno}")],
        [("E3", "F3", f"Sondador Responsável: {sondador}"), ("G3", "H3", f"Coordenadas: {coords}"), ("I3", "L3", f"Última Caixa: {ult_cx}")]
    ]
    for row in meta_structure:
        for m_start, m_end, val in row:
            ws.merge_cells(f"{m_start}:{m_end}")
            cell = ws[m_start]
            cell.value = val
            cell.font = font_meta_lbl
            cell.alignment = al_left
            cell.border = border_thin

    kpis = [
        ("A5:C5", "A6:C6", "PROGRESSO TOTAL PERFURADO", f"{progresso_total:.2f} m", "0284C7"),
        ("D5:F5", "D6:F6", "MÉDIA DE RECUPERAÇÃO", f"{media_rec:.1f} %", "059669"),
        ("G5:I5", "G6:I6", "TOTAL HORAS PARADAS", f"{total_paradas:.1f} h".replace('.', ','), "DC2626"),
        ("J5:L5", "J6:L6", "CONSUMO TOTAL DIESEL", f"{diesel_input} L", "D97706")
    ]
    for top_m, bot_m, lbl, val, color_hex in kpis:
        ws.merge_cells(top_m)
        ws.merge_cells(bot_m)
        top_cell = ws[top_m.split(":")[0]]
        bot_cell = ws[bot_m.split(":")[0]]
        
        top_cell.value = lbl
        top_cell.font = Font(name="Arial", size=7, bold=True, color="64748B")
        top_cell.fill = fill_kpi
        top_cell.alignment = al_center

        bot_cell.value = val
        bot_cell.font = Font(name="Arial", size=11, bold=True, color=color_hex)
        bot_cell.fill = fill_kpi
        bot_cell.alignment = al_center

    headers = ["Item", "Horário", "De (m)", "Até (m)", "Avanço (m)", "Acumulado (m)", "Recup. (m)", "Recup. (%)", "Nº Cx", "Parado", "Motivo Parada", "Descrição Litológica / Observações"]
    ws.row_dimensions[8].height = 22
    for c_idx, h_text in enumerate(headers, 1):
        cell = ws.cell(row=8, column=c_idx, value=h_text)
        cell.font = font_th
        cell.fill = fill_th
        cell.alignment = al_center
        cell.border = border_thin

    curr_row = 9
    for _, r in df.iterrows():
        ws.cell(row=curr_row, column=1, value=r["Item"]).alignment = al_center
        ws.cell(row=curr_row, column=2, value=r["Horário"]).alignment = al_center
        ws.cell(row=curr_row, column=3, value=f"{r['De (m)']:.2f}".replace('.', ',')).alignment = al_right
        ws.cell(row=curr_row, column=4, value=f"{r['Até (m)']:.2f}".replace('.', ',')).alignment = al_right
        ws.cell(row=curr_row, column=5, value=f"{r['Avanço (m)']:.2f}".replace('.', ',')).alignment = al_right
        ws.cell(row=curr_row, column=6, value=f"{r['Acumulado (m)']:.2f}".replace('.', ',')).alignment = al_right
        ws.cell(row=curr_row, column=7, value=f"{r['Recup. (m)']:.2f}".replace('.', ',')).alignment = al_right
        
        cell_rec = ws.cell(row=curr_row, column=8, value=f"{r['Recup. (%)']:.1f}%".replace('.', ','))
        cell_rec.alignment = al_right
        cell_rec.font = font_td_rec

        ws.cell(row=curr_row, column=9, value=r["Nº Cx"]).alignment = al_center
        ws.cell(row=curr_row, column=10, value=f"{r['Parado']:.1f} h".replace('.', ',')).alignment = al_center
        ws.cell(row=curr_row, column=11, value=r["Motivo Parada"]).alignment = al_left
        ws.cell(row=curr_row, column=12, value=r["Descrição Litológica / Observações"]).alignment = al_left

        for col_i in range(1, 13):
            c_cell = ws.cell(row=curr_row, column=col_i)
            if col_i != 8: c_cell.font = font_td
            c_cell.border = border_thin
        curr_row += 1

    ws.cell(row=curr_row, column=1, value="TOTAIS / MÉDIAS OPERACIONAIS:").font = font_tot
    ws.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=4)
    ws.cell(row=curr_row, column=1).alignment = al_left

    ws.cell(row=curr_row, column=5, value=f"{progresso_total:.2f} m".replace('.', ',')).alignment = al_right
    ws.cell(row=curr_row, column=6, value=f"{df['Acumulado (m)'].max():.2f} m".replace('.', ',')).alignment = al_right
    ws.cell(row=curr_row, column=7, value=f"{recup_tot_m:.2f} m".replace('.', ',')).alignment = al_right
    ws.cell(row=curr_row, column=8, value=f"{media_rec:.1f}%".replace('.', ',')).alignment = al_right
    ws.cell(row=curr_row, column=9, value=ult_cx).alignment = al_center
    ws.cell(row=curr_row, column=10, value=f"{total_paradas:.1f} h".replace('.', ',')).alignment = al_center
    ws.cell(row=curr_row, column=11, value=f"Diesel: {diesel_input} L").alignment = al_left
    ws.cell(row=curr_row, column=12, value="Furo finalizado no turno com alta recuperação.").alignment = al_left

    for col_i in range(1, 13):
        c_tot = ws.cell(row=curr_row, column=col_i)
        c_tot.font = font_tot
        c_tot.fill = fill_tot
        c_tot.border = Border(top=Side(style='medium', color="0284C7"), bottom=Side(style='medium', color="0284C7"))

    widths = [6, 14, 10, 10, 12, 13, 11, 11, 8, 10, 22, 38]
    for idx, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(idx)].width = w

    wb.save(buf_excel)
    st.download_button(
        "📊 Baixar Planilha Excel Identica (.xlsx)",
        data=buf_excel.getvalue(),
        file_name=f"Boletim_DrillData_{furo_id}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ==========================================
# 2. PDF DRILLDATA IDÊNTICO AO MODELO
# ==========================================
with col_dl2:
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

    # Desenho vetorial do Ícone da Picareta DRILLDATA
    def draw_pickaxe_icon():
        d = Drawing(24, 24)
        g = Group()
        g.add(Polygon([2,20, 8,22, 22,8, 20,2], fillColor=colors.HexColor('#10B981'), strokeColor=None))
        g.add(Polygon([10,10, 4,16, 2,14, 8,8], fillColor=colors.HexColor('#059669'), strokeColor=None))
        d.add(g)
        return d

    buf_pdf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf_pdf, pagesize=landscape(A4),
        leftMargin=0.8*cm, rightMargin=0.8*cm,
        topMargin=0.8*cm, bottomMargin=1.0*cm
    )
    elements = []

    st_title = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor('#10B981'))
    st_subtitle = ParagraphStyle('H2', fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#94A3B8'))
    
    st_meta_lbl = ParagraphStyle('ML', fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.HexColor('#0F172A'))

    st_kpi_lbl = ParagraphStyle('KL', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=0, textColor=colors.HexColor('#475569'))
    st_kpi_val = ParagraphStyle('KV', fontName='Helvetica-Bold', fontSize=11, leading=13, alignment=0)

    st_th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=1, textColor=colors.white)
    st_td = ParagraphStyle('TD', fontName='Helvetica', fontSize=6.5, leading=8, alignment=1, textColor=colors.HexColor('#0F172A'))
    st_td_left = ParagraphStyle('TDL', fontName='Helvetica', fontSize=6.5, leading=8, alignment=0, textColor=colors.HexColor('#0F172A'))
    st_td_rec = ParagraphStyle('TDR', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=1, textColor=colors.HexColor('#059669'))
    st_tot = ParagraphStyle('TOT', fontName='Helvetica-Bold', fontSize=6.5, leading=8, alignment=0, textColor=colors.HexColor('#0F172A'))

    # 1. BANNER CABEÇALHO
    h_text_cell = [
        Paragraph("<b>DRILLDATA</b>", st_title),
        Paragraph("Relatório Técnico & Boletim Diário de Sondagem", st_subtitle)
    ]
    
    header_left_box = Table([[draw_pickaxe_icon(), h_text_cell]], colWidths=[0.8*cm, 8.4*cm])
    header_left_box.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))

    t_h_left = Table([[header_left_box]], colWidths=[9.4*cm])
    t_h_left.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
        ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
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
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))

    header_full = Table([[t_h_left, t_h_right]], colWidths=[9.4*cm, 18.7*cm])
    header_full.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(header_full)
    elements.append(Spacer(1, 6))

    # 2. CARDS KPIS
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

    # 3. TABELA COM LARGURAS EXATAS (CABEÇALHO EM UMA LINHA)
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
        Paragraph(f"<b>{recup_tot_m:.2f} m</b>".replace('.', ','), st_td), Paragraph(f"<b>{media_rec:.1f}%</b>".replace('.', ','), st_td_rec),
        Paragraph(f"<b>{ult_cx}</b>", st_td), Paragraph(f"<b>{total_paradas:.1f} h</b>".replace('.', ','), st_td),
        Paragraph(f"<b>Diesel: {diesel_input} L</b>", st_td_left), Paragraph("Furo finalizado no turno com alta recuperação.", st_td_left)
    ])

    # Larguras ajustadas para caber perfeitamente na página
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

    # 4. ASSINATURAS
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
        "📄 Baixar Relatório PDF Identico (.pdf)",
        data=buf_pdf.getvalue(),
        file_name=f"Relatorio_DrillData_{furo_id}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
