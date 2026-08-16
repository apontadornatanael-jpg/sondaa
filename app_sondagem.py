import io
import pandas as pd
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import streamlit as st

st.set_page_config(
    page_title="Boletim de Sondagem Rotativa", page_icon="🚜", layout="wide"
)

st.title("🚜 Gerador de Boletim de Sondagem Rotativa")
st.markdown(
    "Preencha os dados abaixo e clique no botão para gerar a planilha Excel profissional."
)

# --- CABEÇALHO ---
st.header("1. Informações Gerais do Furo")
col1, col2, col3, col4 = st.columns(4)
with col1:
    modelo_sonda = st.text_input("Modelo Sonda", "LM 75")
    cliente = st.text_input("Cliente", "ATLAS LITHIUM")
    data_boletim = st.date_input("Data")
with col2:
    num_sonda = st.text_input("Nº Sonda", "04")
    area = st.text_input("Área", "ABELHAS")
    turno = st.selectbox("Turno", ["1º", "2º", "3º"])
with col3:
    furo_num = st.text_input("Furo Nº", "DHAB 109")
    azimute = st.number_input("Azimute (°)", value=290)
    angulo = st.number_input("Ângulo (°)", value=60)
with col4:
    horimetro_ini = st.number_input("Horímetro Inicial", value=319.9)
    horimetro_fin = st.number_input("Horímetro Final", value=330.2)

# --- PEÇA DE CORTE ---
st.header("2. Peça de Corte")
col_p1, col_p2, col_p3, col_p4 = st.columns(4)
with col_p1:
    diam_p = st.text_input("Diâmetro", "NQ")
with col_p2:
    coroa_num = st.text_input("Coroa Nº", "89173-17")
with col_p3:
    calib = st.text_input("Calib", "138217")
with col_p4:
    outros_p = st.text_input("Outros", "")

# --- DADOS DE PERFURAÇÃO ---
st.header("3. Perfuração e Recuperação")
st.caption(
    "Insira as manobras de perfuração. O avanço e a taxa de recuperação % serão calculados automaticamente."
)

dados_padrao_perf = [
    {"De": 44.10, "Até": 47.20, "Recuperado": 3.10, "Material": ""},
    {"De": 47.20, "Até": 50.20, "Recuperado": 3.00, "Material": ""},
    {"De": 50.20, "Até": 53.30, "Recuperado": 3.10, "Material": ""},
    {"De": 53.30, "Até": 56.45, "Recuperado": 3.15, "Material": ""},
    {"De": 56.45, "Até": 59.45, "Recuperado": 3.00, "Material": ""},
]

df_perf_edited = st.data_editor(
    pd.DataFrame(dados_padrao_perf), num_rows="dynamic", use_container_width=True
)

# --- SERVIÇOS E HORÁRIOS ---
st.header("4. Descrição dos Serviços e Horários")
dados_padrao_serv = [
    {
        "Descrição": "C/SSMA",
        "Hora Inicial": "07:00",
        "Hora Final": "07:15",
        "Tempo (h)": "0:15",
    },
    {
        "Descrição": "Manutenção Preventiva",
        "Hora Inicial": "07:15",
        "Hora Final": "07:30",
        "Tempo (h)": "0:15",
    },
    {
        "Descrição": "Perfurando",
        "Hora Inicial": "07:30",
        "Hora Final": "12:00",
        "Tempo (h)": "4:30",
    },
    {
        "Descrição": "Refeição",
        "Hora Inicial": "12:00",
        "Hora Final": "13:00",
        "Tempo (h)": "1:00",
    },
    {
        "Descrição": "Perfurando",
        "Hora Inicial": "13:00",
        "Hora Final": "18:00",
        "Tempo (h)": "5:00",
    },
]

df_serv_edited = st.data_editor(
    pd.DataFrame(dados_padrao_serv), num_rows="dynamic", use_container_width=True
)

# --- INSUMOS E RODAPÉ ---
st.header("5. Insumos, Revestimento e Observações")
col_i1, col_i2, col_i3 = st.columns(3)
with col_i1:
    diesel_sonda = st.text_input("Óleo Diesel (Sonda)", "125L")
    diesel_torre = st.text_input("Óleo Diesel (Torre)", "")
    diesel_bomba = st.text_input("Óleo Diesel (Bomba)", "")
with col_i2:
    rev_diam = st.text_input("Revestimento Diâmetro", "HQ")
    rev_de = st.number_input("Revestimento De (m)", value=0.00)
    rev_ate = st.number_input("Revestimento Até (m)", value=34.40)
with col_i3:
    num_caixa = st.text_input("Última Caixa do Furo", "32")

obs = st.text_area("Observações", "")


# --- FUNÇÃO GERADORA DE EXCEL ---
def gerar_excel_profissional():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Boletim de Sondagem"
    ws.views.sheetView[0].showGridLines = True

    fonte_titulo = Font(name="Calibri", size=14, bold=True, color="1F4E78")
    fonte_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    fonte_sub = Font(name="Calibri", size=10, bold=True, color="1F4E78")
    fonte_normal = Font(name="Calibri", size=10)

    fill_header = PatternFill(
        start_color="1F4E78", end_color="1F4E78", fill_type="solid"
    )

    thin_border = Border(
        left=Side(style="thin", color="D3D3D3"),
        right=Side(style="thin", color="D3D3D3"),
        top=Side(style="thin", color="D3D3D3"),
        bottom=Side(style="thin", color="D3D3D3"),
    )

    ws.merge_cells("A1:K1")
    ws["A1"] = "BOLETIM DE SONDAGEM ROTATIVA"
    ws["A1"].font = fonte_titulo
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

    cabecalhos_info = [
        ("A3", f"Modelo Sonda: {modelo_sonda}"),
        ("C3", f"Nº Sonda: {num_sonda}"),
        ("E3", f"Turno: {turno}"),
        ("G3", f"Azimute: {azimute}°"),
        ("I3", f"Data: {data_boletim.strftime('%d/%m/%Y')}"),
        ("A4", f"Cliente: {cliente}"),
        ("C4", f"Área: {area}"),
        ("E4", f"Furo Nº: {furo_num}"),
        ("G4", f"Ângulo: {angulo}°"),
        ("I4", f"Horímetro: {horimetro_ini} - {horimetro_fin}"),
    ]

    for cell_ref, text in cabecalhos_info:
        ws[cell_ref] = text
        ws[cell_ref].font = fonte_sub

    headers_perf = [
        "De (m)",
        "Até (m)",
        "Avanço (m)",
        "Recuperado (m)",
        "Total (m)",
        "% Rec.",
        "Material Perfurado",
    ]
    ws.append([])
    ws.append(headers_perf)
    start_row_perf = 6

    for col_idx, h in enumerate(headers_perf, 1):
        cell = ws.cell(row=start_row_perf, column=col_idx)
        cell.font = fonte_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center")

    rec_acumulada = 0.0
    for idx, row in df_perf_edited.iterrows():
        de = row.get("De", 0.0)
        ate = row.get("Até", 0.0)
        rec = row.get("Recuperado", 0.0)
        avanco = round(ate - de, 2)
        rec_acumulada += rec
        pct_rec = round((rec / avanco * 100), 1) if avanco > 0 else 0.0

        r_data = [
            de,
            ate,
            avanco,
            rec,
            round(rec_acumulada, 2),
            f"{pct_rec}%",
            row.get("Material", ""),
        ]
        ws.append(r_data)

    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=11):
        for cell in row:
            if cell.value:
                cell.border = thin_border
                if not cell.font.bold:
                    cell.font = fonte_normal

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


st.markdown("---")
if st.button("🚀 Gerar e Baixar Planilha Excel"):
    excel_file = gerar_excel_profissional()
    st.download_button(
        label="📥 Download Planilha (.xlsx)",
        data=excel_file,
        file_name=f"Boletim_Sondagem_{furo_num}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
