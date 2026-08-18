import os
from weasyprint import HTML

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Técnico & Boletim Diário de Sondagem - DRILLDATA</title>
    <style>
        *, *::before, *::after {
            box-sizing: border-box;
        }

        @page {
            size: A4 landscape;
            margin: 10mm 12mm 12mm 12mm;
            @bottom-right {
                content: "Página " counter(page) " de " counter(pages);
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 8pt;
                color: #555555;
            }
            @bottom-left {
                content: "DrillData — Sistema Digital de Sondagem Mineral";
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 8pt;
                color: #555555;
            }
        }

        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #1a202c;
            background-color: #ffffff;
            font-size: 8.5pt;
        }

        /* HEADER SECTION */
        .header-container {
            display: table;
            width: 100%;
            margin-bottom: 8px;
            border-bottom: 2px solid #0d9488;
            padding-bottom: 6px;
        }

        .header-left {
            display: table-cell;
            vertical-align: middle;
            width: 20%;
        }

        .logo-box {
            font-size: 16pt;
            font-weight: 900;
            color: #0d9488;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .header-center {
            display: table-cell;
            vertical-align: middle;
            text-align: center;
            width: 60%;
        }

        .header-title {
            font-size: 13pt;
            font-weight: bold;
            color: #0f172a;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .header-right {
            display: table-cell;
            vertical-align: middle;
            text-align: right;
            width: 20%;
            font-size: 7.5pt;
            color: #64748b;
        }

        /* METADATA GRID */
        .meta-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 8px;
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
        }

        .meta-table td {
            padding: 4px 8px;
            border: 1px solid #e2e8f0;
            font-size: 8pt;
            width: 33.33%;
        }

        .meta-label {
            font-weight: bold;
            color: #334155;
        }

        .meta-value {
            color: #0f172a;
        }

        /* KPI CARDS */
        .kpi-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 6px 0;
            margin-bottom: 8px;
            margin-left: -6px;
            margin-right: -6px;
        }

        .kpi-card {
            display: table-cell;
            width: 25%;
            background-color: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 4px;
            padding: 6px;
            text-align: center;
        }

        .kpi-card.warning {
            background-color: #fffbe0;
            border-color: #fef08a;
        }

        .kpi-title {
            font-size: 7pt;
            font-weight: bold;
            color: #166534;
            text-transform: uppercase;
            margin-bottom: 2px;
        }

        .kpi-card.warning .kpi-title {
            color: #854d0e;
        }

        .kpi-value {
            font-size: 13pt;
            font-weight: bold;
            color: #15803d;
        }

        .kpi-card.warning .kpi-value {
            color: #a16207;
        }

        /* MAIN DATA TABLE */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 8px;
            font-size: 7.5pt;
        }

        .data-table th {
            background-color: #0d9488;
            color: #ffffff;
            font-weight: bold;
            text-align: center;
            padding: 5px 3px;
            border: 1px solid #0f766e;
            vertical-align: middle;
            font-size: 7.5pt;
        }

        .data-table td {
            padding: 4px 3px;
            border: 1px solid #cbd5e1;
            text-align: center;
            vertical-align: middle;
        }

        .data-table tr:nth-child(even) {
            background-color: #f8fafc;
        }

        .data-table td.desc {
            text-align: left;
            font-size: 7pt;
        }

        .totals-row td {
            background-color: #e2e8f0;
            font-weight: bold;
            border-top: 2px solid #0d9488;
            color: #0f172a;
        }

        /* SIGNATURE SECTION */
        .signatures-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
        }

        .signatures-table td {
            width: 33.33%;
            text-align: center;
            vertical-align: top;
            padding: 0 10px;
        }

        .line {
            border-top: 1px solid #475569;
            margin-bottom: 3px;
            width: 85%;
            margin-left: auto;
            margin-right: auto;
        }

        .sig-name {
            font-weight: bold;
            font-size: 8pt;
            color: #0f172a;
        }

        .sig-role {
            font-size: 7.5pt;
            color: #475569;
        }

        .sig-company {
            font-size: 7pt;
            color: #64748b;
            font-style: italic;
        }
    </style>
</head>
<body>

    <!-- HEADER -->
    <div class="header-container">
        <div class="header-left">
            <div class="logo-box">DRILLDATA</div>
        </div>
        <div class="header-center">
            <div class="header-title">Relatório Técnico & Boletim Diário de Sondagem</div>
        </div>
        <div class="header-right">
            <span>Sistema Digital de Sondagem</span>
        </div>
    </div>

    <!-- METADATA -->
    <table class="meta-table">
        <tr>
            <td><span class="meta-label">Projeto/Cliente:</span> <span class="meta-value">Mineração Santa Rita</span></td>
            <td><span class="meta-label">Furo:</span> <span class="meta-value"><b>DDH-024</b></span></td>
            <td><span class="meta-label">Data:</span> <span class="meta-value">17/08/2026</span></td>
        </tr>
        <tr>
            <td><span class="meta-label">Sonda:</span> <span class="meta-value">CS14 Core Drill</span></td>
            <td><span class="meta-label">Inclin./Azimute:</span> <span class="meta-value">-60° / 180°</span></td>
            <td><span class="meta-label">Turno:</span> <span class="meta-value">Diurno</span></td>
        </tr>
        <tr>
            <td><span class="meta-label">Sondador Responsável:</span> <span class="meta-value">Natanael Souza</span></td>
            <td><span class="meta-label">Coordenadas:</span> <span class="meta-value">E: 245120 | N: 9284100</span></td>
            <td><span class="meta-label">Última Caixa:</span> <span class="meta-value">Nº 04</span></td>
        </tr>
    </table>

    <!-- KPIS -->
    <table class="kpi-table">
        <tr>
            <td class="kpi-card">
                <div class="kpi-title">PROGRESSO TOTAL PERFURADO</div>
                <div class="kpi-value">18,00 m</div>
            </td>
            <td class="kpi-card">
                <div class="kpi-title">MÉDIA DE RECUPERAÇÃO</div>
                <div class="kpi-value">96.8 %</div>
            </td>
            <td class="kpi-card warning">
                <div class="kpi-title">TOTAL HORAS PARADAS</div>
                <div class="kpi-value">2,5 h</div>
            </td>
            <td class="kpi-card">
                <div class="kpi-title">CONSUMO TOTAL DIESEL</div>
                <div class="kpi-value">105 L</div>
            </td>
        </tr>
    </table>

    <!-- TABLE -->
    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 3%;">Item</th>
                <th style="width: 8%;">Horário</th>
                <th style="width: 5%;">De (m)</th>
                <th style="width: 5%;">Até (m)</th>
                <th style="width: 5%;">Avanço (m)</th>
                <th style="width: 6%;">Acumulado (m)</th>
                <th style="width: 6%;">Recup. (m)</th>
                <th style="width: 6%;">Recup. (%)</th>
                <th style="width: 4%;">Nº Cx</th>
                <th style="width: 5%;">Parado</th>
                <th style="width: 15%;">Motivo Parada</th>
                <th style="width: 32%;">Descrição Litológica / Observações</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td>07:00 - 08:15</td>
                <td>0,00</td>
                <td>1,50</td>
                <td>1,50</td>
                <td>1,50</td>
                <td>1,45</td>
                <td>96,7%</td>
                <td>01</td>
                <td>0,0 h</td>
                <td>Troca de Broca</td>
                <td class="desc">Início do furo HQ. Solo de alteração/saprolito.</td>
            </tr>
            <tr>
                <td>2</td>
                <td>08:15 - 09:30</td>
                <td>1,50</td>
                <td>3,00</td>
                <td>1,50</td>
                <td>3,00</td>
                <td>1,50</td>
                <td>100,0%</td>
                <td>01</td>
                <td>0,0 h</td>
                <td>Nenhuma</td>
                <td class="desc">Saprolito avermelhado com fragmentos de quartzo.</td>
            </tr>
            <tr>
                <td>3</td>
                <td>09:30 - 11:00</td>
                <td>3,00</td>
                <td>6,00</td>
                <td>3,00</td>
                <td>6,00</td>
                <td>2,85</td>
                <td>95,0%</td>
                <td>02</td>
                <td>0,0 h</td>
                <td>Nenhuma</td>
                <td class="desc">Passagem para rocha alterada (Xisto friável).</td>
            </tr>
            <tr>
                <td>4</td>
                <td>11:00 - 12:00</td>
                <td>6,00</td>
                <td>7,50</td>
                <td>1,50</td>
                <td>7,50</td>
                <td>1,50</td>
                <td>100,0%</td>
                <td>02</td>
                <td>1,0 h</td>
                <td>Manutenção Mecânica</td>
                <td class="desc">Ajuste na bomba de lama / VAZAMENTO.</td>
            </tr>
            <tr>
                <td>5</td>
                <td>13:00 - 14:30</td>
                <td>7,50</td>
                <td>10,50</td>
                <td>3,00</td>
                <td>10,50</td>
                <td>2,95</td>
                <td>98,3%</td>
                <td>03</td>
                <td>0,0 h</td>
                <td>Nenhuma</td>
                <td class="desc">Rocha sã (Gnaisse cinza médio). Transição NQ.</td>
            </tr>
            <tr>
                <td>6</td>
                <td>14:30 - 15:45</td>
                <td>10,50</td>
                <td>13,50</td>
                <td>3,00</td>
                <td>13,50</td>
                <td>3,00</td>
                <td>100,0%</td>
                <td>03</td>
                <td>0,0 h</td>
                <td>Nenhuma</td>
                <td class="desc">Rocha sã maciça, excelente RQD.</td>
            </tr>
            <tr>
                <td>7</td>
                <td>15:45 - 16:30</td>
                <td>13,50</td>
                <td>15,00</td>
                <td>1,50</td>
                <td>15,00</td>
                <td>1,48</td>
                <td>98,7%</td>
                <td>04</td>
                <td>0,5 h</td>
                <td>Aguardando Água</td>
                <td class="desc">Caminhão pipa em reabastecimento.</td>
            </tr>
            <tr>
                <td>8</td>
                <td>16:30 - 17:30</td>
                <td>15,00</td>
                <td>18,00</td>
                <td>3,00</td>
                <td>18,00</td>
                <td>3,00</td>
                <td>100,0%</td>
                <td>04</td>
                <td>0,0 h</td>
                <td>Nenhuma</td>
                <td class="desc">Fim do turno. Preservação do testemunho.</td>
            </tr>
            <tr class="totals-row">
                <td colspan="4" style="text-align: right;">TOTAIS / MÉDIAS OPERACIONAIS:</td>
                <td>18,00 m</td>
                <td>18,00 m</td>
                <td>17,28 m</td>
                <td>96.8%</td>
                <td>Nº 04</td>
                <td>2,5 h</td>
                <td>Diesel: 105 L</td>
                <td class="desc" style="font-weight: bold;">Furo finalizado no turno com alta recuperação.</td>
            </tr>
        </tbody>
    </table>

    <!-- SIGNATURES -->
    <table class="signatures-table">
        <tr>
            <td>
                <div class="line"></div>
                <div class="sig-name">Natanael Souza</div>
                <div class="sig-role">Sondador / Operador Responsável</div>
            </td>
            <td>
                <div class="line"></div>
                <div class="sig-name">Eng. Geotécnico / Geólogo</div>
                <div class="sig-role">Fiscalização de Campo</div>
            </td>
            <td>
                <div class="line"></div>
                <div class="sig-name">Supervisão de Operações</div>
                <div class="sig-company">Mineração Santa Rita</div>
            </td>
        </tr>
    </table>

</body>
</html>
"""

# Salva o arquivo HTML e renderiza em PDF
with open("relatorio.html", "w", encoding="utf-8") as f:
    f.write(html_content)

HTML("relatorio.html").write_pdf("relatorio_drilldata_furo_DDH-024.pdf")
print("PDF gerado com sucesso!")
