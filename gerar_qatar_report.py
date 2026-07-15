"""Gerador do relatório PDF Qatar Airways — Onfly."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image,
)
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

# ── Cores ──────────────────────────────────────────────────────────────────
ONFLY_BLUE   = colors.HexColor('#1890FF')
ONFLY_LIGHT  = colors.HexColor('#E8F4FF')
ONFLY_ORANGE = colors.HexColor('#FF6B00')
DARK         = colors.HexColor('#1A1A2E')
MID_GRAY     = colors.HexColor('#6C757D')
LIGHT_GRAY   = colors.HexColor('#F8F9FA')
TABLE_ALT    = colors.HexColor('#F0F7FF')
WHITE        = colors.white

# ── Dados ──────────────────────────────────────────────────────────────────
# (ano_label, reservas, volume_vendas)
VOLUME_ANUAL = [
    ('2019',    1,    4_300),
    ('2021',    3,   31_696),
    ('2022',   32,  293_729),
    ('2023',   36,  431_675),
    ('2024',  103, 1_645_977),
    ('2025',  219, 2_862_341),
    ('2026*', 103, 1_109_891),
]

AEROPORTOS = {
    'GRU': 'São Paulo (Guarulhos)', 'PVG': 'Shanghai (Pudong)',
    'HKG': 'Hong Kong',            'CAN': 'Guangzhou',
    'MAO': 'Manaus',               'PKX': 'Beijing (Daxing)',
    'DOH': 'Doha',                 'BOM': 'Mumbai',
    'JFK': 'Nova York (JFK)',      'DXB': 'Dubai',
    'DEL': 'Nova Delhi',           'CGK': 'Jacarta',
}

MERCADOS = [
    ('GRU/PVG', 31,  338_532),
    ('GRU/HKG', 21,  233_973),
    ('GRU/CAN', 15,  208_980),
    ('CAN/MAO',  9,  199_147),
    ('GRU/PKX',  5,  124_505),
    ('DOH/BOM',  3,  107_998),
    ('JFK/DXB',  3,   98_141),
    ('GRU/DEL',  6,   83_754),
    ('GRU/CGK',  2,   81_494),
    ('PVG/GRU', 11,   76_962),
]

# (cliente, cnpj, reservas, volume_vendas)
CLIENTES_QATAR = [
    ('Minerva Foods',                      '67.620.377/0001-14', 24,  277_380),
    ('GAC Motor Brasil Ltda.',             '54.930.335/0001-38', 11,  121_450),
    ('Elgin',                              '07.023.429/0004-96', 16,   93_655),
    ('Filial São Paulo',                   '08.517.600/0003-03',  1,   62_720),
    ('Instituto Mauá de Tecnologia (IMT)', '60.749.736/0002-70',  3,   62_334),
    ('Multilaser Industrial S.A.',         '59.717.553/0001-02', 11,   55_589),
    ('Heinz Brasil S.A.',                  '50.955.707/0001-20',  2,   54_250),
    ('Two Square Transmission',            '28.704.797/0001-27',  3,   53_999),
    ('Suntrans Brasil',                    '08.017.952/0001-20',  5,   49_380),
    ('Uni.Co Comércio S/A',                '00.399.603/0001-08',  4,   47_724),
    ('Sabesp',                             '43.776.517/0001-80',  2,   46_875),
    ('Fundação Faculdade de Medicina',     '56.577.059/0001-00',  5,   46_341),
    ('AGCO',                               '55.962.369/0001-77',  5,   45_192),
    ('Abrint',                             '11.369.542/0001-52',  5,   42_843),
    ('Chint Power Systems Brazil',         '48.487.366/0001-63',  8,   41_751),
]

# (cliente, cnpj, reservas, volume_vendas)
CLIENTES_OPORTUNIDADE = [
    ('Minerva Foods',                              '67.620.377/0001-14', 225,  2_677_020),
    ('AGCO',                                       '55.962.369/0001-77', 310,  2_370_968),
    ('TSEA Energia',                               '08.870.769/0001-72', 245,  1_444_559),
    ('Heinz Brasil S.A.',                          '50.955.707/0001-20', 101,  1_296_151),
    ('BR Influenciadores Marketing Ltda.',         '25.018.794/0001-41',  34,  1_217_879),
    ('Blip',                                       '04.413.729/0001-40', 108,    854_714),
    ('Multilaser Industrial S.A.',                 '59.717.553/0001-02',  54,    816_544),
    ('Adler Pelzer Pernambuco',                    '20.907.030/0001-93',  16,    642_566),
    ('ISE — Centro de Ext. Universitária',         '03.488.576/0001-38',  66,    619_147),
    ('Assoc. Adm. Faixa de 3,5 GHz — EAF',        '45.282.870/0001-39',  20,    596_927),
]

KPI_12M = dict(reservas=243, volume_vendas=2_751_207)

# ── Helpers ────────────────────────────────────────────────────────────────
def brl(v):
    return "R$ " + f"{int(round(v)):,}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_bar(v):
    if v >= 1_000_000:
        return f"R${v/1e6:.1f}M"
    return f"R${int(v/1000)}K"

def rota_label(cod):
    partes = cod.split('/')
    if len(partes) == 2:
        o, d = partes
        return f"{AEROPORTOS.get(o, o)} ({o})  →  {AEROPORTOS.get(d, d)} ({d})"
    return cod

def make_table_style(num_rows, right_cols=None):
    right_cols = right_cols or []
    cmds = [
        ('BACKGROUND',    (0, 0), (-1, 0),  ONFLY_BLUE),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  WHITE),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  8),
        ('ALIGN',         (0, 0), (-1, 0),  'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  5),
        ('TOPPADDING',    (0, 0), (-1, 0),  5),
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, -1), 7.5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('TOPPADDING',    (0, 1), (-1, -1), 3),
        ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#C5DEFF')),
        ('LINEBELOW',     (0, 0), (-1, 0),  1.2, ONFLY_BLUE),
        ('ALIGN',         (0, 1), (0, -1),  'CENTER'),
    ]
    for row in range(1, num_rows):
        bg = WHITE if row % 2 == 1 else TABLE_ALT
        cmds.append(('BACKGROUND', (0, row), (-1, row), bg))
    for col in right_cols:
        cmds.append(('ALIGN', (col, 1), (col, -1), 'RIGHT'))
    return TableStyle(cmds)

# ── Estilos ────────────────────────────────────────────────────────────────
s_title   = ParagraphStyle('t',  fontSize=18, fontName='Helvetica-Bold',
                             textColor=ONFLY_BLUE, leading=24, alignment=TA_CENTER, spaceAfter=3)
s_sub     = ParagraphStyle('s',  fontSize=9, fontName='Helvetica',
                             textColor=MID_GRAY, leading=13, alignment=TA_CENTER, spaceAfter=2)
s_section = ParagraphStyle('sc', fontSize=11, fontName='Helvetica-Bold',
                             textColor=ONFLY_BLUE, leading=15, spaceBefore=6, spaceAfter=3)
s_body    = ParagraphStyle('b',  fontSize=8, fontName='Helvetica',
                             textColor=DARK, leading=12, spaceAfter=3)
s_note    = ParagraphStyle('n',  fontSize=7, fontName='Helvetica',
                             textColor=MID_GRAY, leading=10, spaceAfter=3)
s_kpi_lb  = ParagraphStyle('kl', fontSize=7, fontName='Helvetica',
                             textColor=MID_GRAY, alignment=TA_CENTER, leading=10)
s_kpi_val = ParagraphStyle('kv', fontSize=14, fontName='Helvetica-Bold',
                             textColor=ONFLY_BLUE, alignment=TA_CENTER, leading=18)
s_kpi_sub = ParagraphStyle('ks', fontSize=7, fontName='Helvetica',
                             textColor=MID_GRAY, alignment=TA_CENTER, leading=10)

# ── Documento ─────────────────────────────────────────────────────────────
OUTPUT  = "/Users/possatto/Documents/Claude/onfly_dashboard/qatar_report.pdf"

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=1.5*cm, rightMargin=1.5*cm,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
    title="Relatório Qatar Airways — Onfly", author="Onfly Travel Technology",
)
PAGE_W  = A4[0] - 3*cm
LOGO_PATH = "/Users/possatto/Documents/Claude/onfly_dashboard/assets/logo_final.png"

story = []

# ══════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ══════════════════════════════════════════════════════════════════════════
# logo_final.png: 998×409px → ratio 2.44:1; width=3.5cm → height=1.43cm
logo = Image(LOGO_PATH, width=3.5*cm, height=1.43*cm)
logo_row = Table([[logo, '']], colWidths=[4*cm, PAGE_W - 4*cm])
logo_row.setStyle(TableStyle([
    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ('LEFTPADDING',   (0,0), (0,-1),  0),
    ('RIGHTPADDING',  (0,0), (0,-1),  0),
    ('TOPPADDING',    (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
]))
story.append(logo_row)
story.append(Spacer(1, 0.2*cm))

banner = Table(
    [[Paragraph('<font color="white"><b>RELATÓRIO ESTRATÉGICO DE PARCERIA</b></font>',
                ParagraphStyle('bn', fontSize=10, fontName='Helvetica-Bold',
                               textColor=WHITE, alignment=TA_CENTER))]],
    colWidths=[PAGE_W],
)
banner.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,-1), ONFLY_BLUE),
    ('TOPPADDING',    (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
]))
story.append(banner)
story.append(Spacer(1, 0.25*cm))
story.append(Paragraph("Qatar Airways", s_title))
story.append(Paragraph("Parceria Estratégica com Onfly Travel Technology", s_sub))
story.append(Paragraph("Emitido em 11 de junho de 2026", s_sub))
story.append(Spacer(1, 0.2*cm))
story.append(HRFlowable(width=PAGE_W, thickness=1, color=ONFLY_BLUE, spaceAfter=0.3*cm))

# ── KPI Cards ──────────────────────────────────────────────────────────
ticket_medio = KPI_12M['volume_vendas'] / KPI_12M['reservas']
kpi_data = [
    [Paragraph("Volume de Vendas",     s_kpi_lb),
     Paragraph("Reservas Emitidas",    s_kpi_lb),
     Paragraph("Ticket Médio",         s_kpi_lb),
     Paragraph("Clientes Ativos",      s_kpi_lb)],
    [Paragraph(brl(KPI_12M['volume_vendas']), s_kpi_val),
     Paragraph(f"{KPI_12M['reservas']:,}",    s_kpi_val),
     Paragraph(brl(ticket_medio),             s_kpi_val),
     Paragraph("15+",                         s_kpi_val)],
    [Paragraph("últ. 12 meses", s_kpi_sub),
     Paragraph("últ. 12 meses", s_kpi_sub),
     Paragraph("por reserva",   s_kpi_sub),
     Paragraph("últ. 12 meses", s_kpi_sub)],
]
kpi_t = Table(kpi_data, colWidths=[PAGE_W/4]*4)
kpi_t.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,-1), LIGHT_GRAY),
    ('TOPPADDING',    (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LINEABOVE',     (0,0), (-1,0),  2, ONFLY_BLUE),
    ('LINEBELOW',     (0,-1),(-1,-1), 2, ONFLY_BLUE),
    ('LINEBEFORE',    (1,0), (3,-1),  0.5, colors.HexColor('#C5DEFF')),
]))
story.append(kpi_t)
story.append(Spacer(1, 0.35*cm))

# ══════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 — EVOLUÇÃO DO VOLUME
# ══════════════════════════════════════════════════════════════════════════
story.append(HRFlowable(width=PAGE_W, thickness=0.5, color=ONFLY_BLUE, spaceAfter=0))
story.append(Paragraph("1. Evolução do Volume de Vendas", s_section))
story.append(Paragraph("O ano de 2026 refere-se ao período de janeiro a junho.", s_body))
story.append(Spacer(1, 0.15*cm))

# Gráfico com labels acima das barras
anos_g = ['2022', '2023', '2024', '2025', '2026*']
vals_g = [293_729, 431_675, 1_645_977, 2_862_341, 1_109_891]
CHART_W  = float(PAGE_W)
CHART_H  = 130
BC_X, BC_Y = 38, 18
BC_W, BC_H = CHART_W - 55, 95

drw = Drawing(CHART_W, CHART_H)
bc = VerticalBarChart()
bc.x, bc.y = BC_X, BC_Y
bc.width, bc.height = BC_W, BC_H
bc.data = [vals_g]
bc.categoryAxis.categoryNames = anos_g
bc.bars[0].fillColor   = ONFLY_BLUE
bc.bars[0].strokeColor = None
bc.valueAxis.valueMin  = 0
bc.valueAxis.valueMax  = 3_300_000
bc.valueAxis.valueStep = 800_000
bc.valueAxis.labelTextFormat = lambda v: f"R${v/1e6:.1f}M"
bc.valueAxis.labels.fontSize  = 7
bc.valueAxis.labels.fontName  = 'Helvetica'
bc.categoryAxis.labels.fontSize = 7.5
bc.categoryAxis.labels.fontName = 'Helvetica'
bc.barSpacing = 2
drw.add(bc)

# Labels acima de cada barra
n_bars = len(vals_g)
bar_group_w = BC_W / n_bars
for i, v in enumerate(vals_g):
    bar_center_x = BC_X + (i + 0.5) * bar_group_w
    bar_top_y    = BC_Y + BC_H * (v / 3_300_000)
    lbl = String(bar_center_x, bar_top_y + 3, fmt_bar(v),
                 fontName='Helvetica-Bold', fontSize=7,
                 textAnchor='middle', fillColor=DARK)
    drw.add(lbl)

story.append(drw)
story.append(Spacer(1, 0.1*cm))

# Tabela simplificada: Ano | Reservas | Volume de Vendas
vol_header = ['Ano', 'Reservas', 'Volume de Vendas']
vol_rows = [vol_header]
for ano, res, vol in VOLUME_ANUAL:
    vol_rows.append([ano, f"{res:,}" if isinstance(res, int) else res, brl(vol)])
vol_t = Table(vol_rows, colWidths=[2*cm, 3*cm, 4.5*cm])
vol_t.setStyle(make_table_style(len(vol_rows), right_cols=[2]))
story.append(vol_t)
story.append(Paragraph("* Janeiro a junho de 2026.", s_note))

# ══════════════════════════════════════════════════════════════════════════
# SEÇÃO 2 — PRINCIPAIS MERCADOS
# ══════════════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(HRFlowable(width=PAGE_W, thickness=0.5, color=ONFLY_BLUE, spaceAfter=0))
story.append(Paragraph("2. 10 Principais Mercados", s_section))
story.append(Paragraph(
    "Rotas voadas pelos clientes Onfly via Qatar Airways nos <b>últimos 12 meses</b> "
    "(jun/2025 – jun/2026), ordenadas por Volume de Vendas. "
    "Inclui trechos de conexão operados pela Qatar.",
    s_body,
))
story.append(Spacer(1, 0.2*cm))

merc_header = ['#', 'Rota (IATA)', 'Origem → Destino', 'Reservas', 'Volume de Vendas']
merc_rows = [merc_header]
for i, (cod, res, vol) in enumerate(MERCADOS, 1):
    merc_rows.append([str(i), cod, rota_label(cod), f"{res:,}", brl(vol)])
merc_t = Table(merc_rows, colWidths=[0.7*cm, 2.1*cm, 9*cm, 1.7*cm, 3.1*cm])
merc_t.setStyle(make_table_style(len(merc_rows), right_cols=[4]))
story.append(merc_t)

# ══════════════════════════════════════════════════════════════════════════
# SEÇÃO 3 — PRINCIPAIS CLIENTES QATAR
# ══════════════════════════════════════════════════════════════════════════
story.append(Spacer(1, 0.4*cm))
story.append(HRFlowable(width=PAGE_W, thickness=0.5, color=ONFLY_BLUE, spaceAfter=0))
story.append(Paragraph("3. 15 Principais Clientes — Qatar Airways", s_section))
story.append(Paragraph(
    "Empresas que mais emitiram voos Qatar Airways via Onfly nos <b>últimos 12 meses</b>, "
    "ordenadas por Volume de Vendas.",
    s_body,
))
story.append(Spacer(1, 0.2*cm))

cli_header = ['#', 'Cliente', 'CNPJ', 'Reservas', 'Volume de Vendas']
cli_rows = [cli_header]
for i, (nome, cnpj, res, vol) in enumerate(CLIENTES_QATAR, 1):
    cli_rows.append([str(i), nome, cnpj, f"{res:,}", brl(vol)])
total_cli_vol = sum(v for _, _, _, v in CLIENTES_QATAR)
total_cli_res = sum(r for _, _, r, _ in CLIENTES_QATAR)
cli_rows.append(['', 'TOTAL (top 15)', '', f"{total_cli_res:,}", brl(total_cli_vol)])
cli_t = Table(cli_rows, colWidths=[0.7*cm, 6.8*cm, 3.5*cm, 1.5*cm, 3.1*cm])
sty = make_table_style(len(cli_rows), right_cols=[4])
sty.add('FONTNAME',   (0, len(cli_rows)-1), (-1, len(cli_rows)-1), 'Helvetica-Bold')
sty.add('LINEABOVE',  (0, len(cli_rows)-1), (-1, len(cli_rows)-1), 0.8, ONFLY_BLUE)
sty.add('BACKGROUND', (0, len(cli_rows)-1), (-1, len(cli_rows)-1), ONFLY_LIGHT)
cli_t.setStyle(sty)
story.append(cli_t)

# ══════════════════════════════════════════════════════════════════════════
# SEÇÃO 4 — OPORTUNIDADE
# ══════════════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(HRFlowable(width=PAGE_W, thickness=0.5, color=ONFLY_BLUE, spaceAfter=0))
story.append(Paragraph("4. Oportunidade: Clientes nos Destinos Qatar com Outra Cia Aérea", s_section))
story.append(Paragraph(
    "Clientes da base Onfly que viajaram para <b>destinos operados pela Qatar Airways</b> "
    "utilizando <b>outras companhias aéreas</b> nos últimos 12 meses. "
    "Estes clientes demonstram demanda real para os destinos da Qatar e representam "
    "potencial direto de conversão.",
    s_body,
))
story.append(Spacer(1, 0.25*cm))

total_opp_res = sum(r for _, _, r, _ in CLIENTES_OPORTUNIDADE)
total_opp_vol = sum(v for _, _, _, v in CLIENTES_OPORTUNIDADE)
opp_kpi_data = [
    [Paragraph("Volume de Vendas",        s_kpi_lb),
     Paragraph("Reservas de Oportunidade", s_kpi_lb),
     Paragraph("Clientes Identificados",   s_kpi_lb)],
    [Paragraph(brl(total_opp_vol),        s_kpi_val),
     Paragraph(f"{total_opp_res:,}",      s_kpi_val),
     Paragraph(f"{len(CLIENTES_OPORTUNIDADE)}", s_kpi_val)],
    [Paragraph("últ. 12 meses (top 10)", s_kpi_sub),
     Paragraph("últ. 12 meses (top 10)", s_kpi_sub),
     Paragraph("com demanda nos destinos Qatar", s_kpi_sub)],
]
opp_kpi_t = Table(opp_kpi_data, colWidths=[PAGE_W/3]*3)
opp_kpi_t.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,-1), LIGHT_GRAY),
    ('TOPPADDING',    (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LINEABOVE',     (0,0), (-1,0),  2, ONFLY_BLUE),
    ('LINEBELOW',     (0,-1),(-1,-1), 2, ONFLY_BLUE),
    ('LINEBEFORE',    (1,0), (2,-1),  0.5, colors.HexColor('#C5DEFF')),
]))
story.append(opp_kpi_t)
story.append(Spacer(1, 0.3*cm))

opp_header = ['#', 'Cliente', 'CNPJ', 'Reservas', 'Volume de Vendas']
opp_rows = [opp_header]
for i, (nome, cnpj, res, vol) in enumerate(CLIENTES_OPORTUNIDADE, 1):
    opp_rows.append([str(i), nome, cnpj, f"{res:,}", brl(vol)])
opp_rows.append(['', 'TOTAL (top 10)', '', f"{total_opp_res:,}", brl(total_opp_vol)])
opp_t = Table(opp_rows, colWidths=[0.7*cm, 6.8*cm, 3.5*cm, 1.5*cm, 3.1*cm])
sty2 = make_table_style(len(opp_rows), right_cols=[4])
sty2.add('FONTNAME',   (0, len(opp_rows)-1), (-1, len(opp_rows)-1), 'Helvetica-Bold')
sty2.add('LINEABOVE',  (0, len(opp_rows)-1), (-1, len(opp_rows)-1), 0.8, ONFLY_BLUE)
sty2.add('BACKGROUND', (0, len(opp_rows)-1), (-1, len(opp_rows)-1), ONFLY_LIGHT)
opp_t.setStyle(sty2)
story.append(opp_t)

story.append(Spacer(1, 0.4*cm))
story.append(HRFlowable(width=PAGE_W, thickness=0.5,
                         color=colors.HexColor('#C5DEFF'), spaceAfter=4))
story.append(Paragraph(
    "Relatório gerado automaticamente pela plataforma Onfly Analytics — junho/2026. "
    "Volume de Vendas = Onfly Amount Currency BRL − Taxas Aeroportuárias (amount_taxes_v3). "
    "Período de análise: junho/2025 – junho/2026.",
    s_note,
))

# ── Build ──────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF gerado com sucesso: {OUTPUT}")
