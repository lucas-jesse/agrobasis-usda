import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(page_title="USDA Milho | AgroBasis", layout="wide")

ARQUIVO = "psd_grains_corn.csv"

if not os.path.exists(ARQUIVO):
    st.error("Arquivo 'psd_grains_corn.csv' não encontrado.")
    st.stop()

# ============================================================
# DICIONÁRIOS
# ============================================================

PRODUTOS_VALIDOS = {
    "Corn": "Milho",
}

TRAD_ATTR = {
    "Production": "Produção",
    "Domestic Consumption": "Consumo Doméstico",
    "Exports": "Exportações",
    "Imports": "Importações",
    "Ending Stocks": "Estoque Final",
    "Beginning Stocks": "Estoque Inicial",
    "Total Supply": "Oferta Total",
    "Feed Dom. Consumption": "Consumo para Ração",
    "FSI Consumption": "Consumo FSI",
    "Food, Seed, Industrial Consumption": "Consumo Alimento/Semente/Industrial",
    "Area Harvested": "Área Colhida",
    "Yield": "Produtividade",
    "TY Exports": "Exportações no Ano Comercial",
    "TY Imports": "Importações no Ano Comercial",
}

TRAD_PAIS = {
    "World": "Mundo",
    "Mundo": "Mundo",
    "Brazil": "Brasil",
    "Argentina": "Argentina",
    "United States": "Estados Unidos",
    "China": "China",
    "European Union": "União Europeia",
    "Mexico": "México",
    "Canada": "Canadá",
    "Japan": "Japão",
    "South Korea": "Coreia do Sul",
    "Egypt": "Egito",
    "India": "Índia",
    "Ukraine": "Ucrânia",
    "Russia": "Rússia",
    "South Africa": "África do Sul",
    "Paraguay": "Paraguai",
    "Vietnam": "Vietnã",
    "Indonesia": "Indonésia",
    "Iran": "Irã",
    "Turkey": "Turquia",
    "Colombia": "Colômbia",
    "Peru": "Peru",
    "Chile": "Chile",
    "Thailand": "Tailândia",
}

# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family:'Inter', Arial, sans-serif;
}

.stApp {
    background:linear-gradient(180deg,#ffffff 0%,#f7f9fc 100%);
    color:#0f172a;
}

.block-container {
    padding-top:1.35rem;
    padding-bottom:2.5rem;
    max-width:1450px;
}

h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
label {
    color:#0f172a !important;
}

h1 {
    font-weight:800 !important;
    letter-spacing:-.03em;
    margin-bottom:.1rem;
}

.stCaptionContainer, .stCaptionContainer p {
    color:#64748b !important;
}

.stSelectbox label,
.stSlider label,
.stMultiSelect label {
    color:#334155 !important;
    font-weight:700;
    font-size:12px;
    text-transform:uppercase;
    letter-spacing:.04em;
}

/* Inputs */
[data-baseweb="select"] {
    background:#ffffff !important;
    border-radius:12px;
    border:1px solid #dbe3ee !important;
    box-shadow:0 4px 12px rgba(15,23,42,.04);
}

[data-baseweb="select"] div,
[data-baseweb="select"] span {
    color:#0f172a !important;
}

[role="listbox"] div,
[role="option"],
[role="option"] div,
[role="option"] span {
    color:#0f172a !important;
    background:#ffffff !important;
}

/* Abas */
.stTabs [data-baseweb="tab-list"] {
    gap:6px;
    background:#ffffff;
    padding:6px;
    border-radius:16px;
    border:1px solid #e2e8f0;
    box-shadow:0 6px 18px rgba(15,23,42,.05);
}

.stTabs [data-baseweb="tab"] {
    color:#475569;
    font-weight:700;
    border-radius:12px;
    padding:9px 16px;
}

.stTabs [aria-selected="true"] {
    background:#14532d !important;
    color:#ffffff !important;
}

/* Cards executivos discretos */
.card {
    padding:17px 18px;
    border-radius:18px;
    min-height:112px;
    background:#ffffff;
    border:1px solid #e2e8f0;
    box-shadow:0 6px 18px rgba(15,23,42,.055);
    position:relative;
    overflow:hidden;
}

.card::before {
    content:"";
    position:absolute;
    left:0;
    top:0;
    width:5px;
    height:100%;
    background:#166534;
    opacity:.85;
}

.card-green::before  { background:#166534; }
.card-blue::before   { background:#0b3d63; }
.card-orange::before { background:#d97706; }
.card-dark::before   { background:#475569; }

.card-title {
    color:#64748b !important;
    font-size:11.5px;
    text-transform:uppercase;
    letter-spacing:.07em;
    font-weight:800;
    margin-left:4px;
}

.card-value {
    color:#0f172a !important;
    font-size:25px;
    font-weight:800;
    margin-top:7px;
    margin-left:4px;
    letter-spacing:-.02em;
}

.card-delta {
    color:#64748b !important;
    font-size:12px;
    margin-top:7px;
    margin-left:4px;
}

.insight-box {
    background:#ffffff;
    border:1px solid #e2e8f0;
    padding:21px;
    border-radius:18px;
    color:#1e293b;
    box-shadow:0 6px 18px rgba(15,23,42,.055);
}

.insight-box h3 {
    color:#14532d !important;
    font-weight:800;
    margin-bottom:.5rem;
}

.insight-box p, .insight-box li {
    color:#334155 !important;
    line-height:1.65;
    font-size:14px;
}

.metric-note {
    background:#f8fafc;
    border:1px solid #e2e8f0;
    border-radius:14px;
    padding:14px 16px;
    color:#334155 !important;
    font-size:13px;
    line-height:1.55;
}

/* Containers de gráficos */
div[data-testid="stPlotlyChart"] {
    background:#ffffff;
    border-radius:18px;
    padding:8px;
    border:1px solid #e2e8f0;
    box-shadow:0 6px 18px rgba(15,23,42,.045);
}

div[data-testid="stDataFrame"] {
    color:#0f172a !important;
    background:#ffffff;
    border-radius:14px;
}

div[data-testid="stExpander"] {
    background:#ffffff;
    border-radius:14px;
    border:1px solid #e2e8f0;
}

hr {
    border-color:#e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)

# Paleta AgroBasis para apresentações
PALETA = [
    "#14532d", "#0b3d63", "#d97706", "#2563eb", "#0891b2",
    "#16a34a", "#9333ea", "#dc2626", "#475569", "#ca8a04"
]

PLOTLY_CONFIG = {
    "displaylogo": False,
    "toImageButtonOptions": {
        "format": "png",
        "filename": "agrobasis_milho_grafico",
        "scale": 4,
        "width": 1600,
        "height": 900,
    },
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
}

# ============================================================
# FUNÇÕES
# ============================================================

def fmt(v, casas=1):
    if v is None or pd.isna(v):
        return "-"
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_var(v):
    if v is None or pd.isna(v):
        return "-"
    sinal = "+" if v >= 0 else ""
    return f"{sinal}{v:.1f}%".replace(".", ",")


@st.cache_data(ttl=3600)
def carregar_dados():
    df = pd.read_csv(ARQUIVO)

    df = df.rename(columns={
        "Commodity_Description": "Commodity",
        "Country_Name": "Country",
        "Market_Year": "Year",
        "Attribute_Description": "Attribute",
        "Unit_Description": "Unit",
        "Value": "Value"
    })

    colunas = ["Commodity", "Country", "Year", "Attribute", "Unit", "Value"]
    df = df[colunas].copy()

    df["Commodity"] = df["Commodity"].astype(str).str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()
    df["Attribute"] = df["Attribute"].astype(str).str.strip()
    df["Unit"] = df["Unit"].astype(str).str.strip()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    df = df.dropna(subset=["Year", "Value"])
    df["Year"] = df["Year"].astype(int)

    df = df[df["Commodity"].isin(PRODUTOS_VALIDOS.keys())].copy()

    if df.empty:
        st.error("Nenhum dado de milho foi encontrado no arquivo.")
        st.stop()

    df["Produto"] = df["Commodity"].map(PRODUTOS_VALIDOS)
    df["País"] = df["Country"].map(TRAD_PAIS).fillna(df["Country"])
    df["Indicador"] = df["Attribute"].map(TRAD_ATTR).fillna(df["Attribute"])

    tem_world = (df["Country"] == "World").any()

    if tem_world:
        df.loc[df["Country"] == "World", "País"] = "Mundo"
    else:
        mundo = (
            df.groupby(["Commodity", "Produto", "Year", "Attribute", "Indicador", "Unit"], as_index=False)["Value"]
            .sum()
        )
        mundo["Country"] = "World"
        mundo["País"] = "Mundo"
        df = pd.concat([df, mundo], ignore_index=True)

    return df


def valor(base, attr):
    s = base[base["Attribute"] == attr].sort_values("Year")
    return None if s.empty else s["Value"].iloc[-1]


def serie_attr(base, attr):
    return base[base["Attribute"] == attr].sort_values("Year")[["Year", "Value"]].copy()


def variacao_num(base, attr):
    s = serie_attr(base, attr)
    if len(s) < 2:
        return None
    atual = s["Value"].iloc[-1]
    anterior = s["Value"].iloc[-2]
    if anterior == 0 or pd.isna(anterior):
        return None
    return ((atual / anterior) - 1) * 100


def variacao(base, attr):
    var = variacao_num(base, attr)
    if var is None:
        return "Sem comparação"
    return f"{fmt_var(var)} vs ano anterior"


def cagr(base, attr):
    s = serie_attr(base, attr)
    if len(s) < 2:
        return None

    ini = s["Value"].iloc[0]
    fim = s["Value"].iloc[-1]
    anos = s["Year"].iloc[-1] - s["Year"].iloc[0]

    if ini <= 0 or anos <= 0:
        return None

    return ((fim / ini) ** (1 / anos) - 1) * 100


def pivot_base(base):
    return base.pivot_table(index="Year", columns="Attribute", values="Value", aggfunc="sum").reset_index()


def adicionar_watermark(fig):
    fig.add_annotation(
        text="AgroBasis",
        xref="paper", yref="paper",
        x=0.5, y=0.50,
        showarrow=False,
        font=dict(size=58, color="rgba(20,83,45,0.075)", family="Inter, Arial, sans-serif"),
        xanchor="center",
        yanchor="middle",
        textangle=0,
    )
    fig.add_annotation(
        text="Fonte: USDA PSD • Elaboração: AgroBasis",
        xref="paper", yref="paper",
        x=1, y=-0.16,
        showarrow=False,
        font=dict(size=11, color="#94a3b8"),
        xanchor="right",
    )
    return fig


def aplicar_layout(fig, h=500):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#1e293b", size=13, family="Inter, Arial, sans-serif"),
        title=dict(x=0.02, xanchor="left", font=dict(color="#0f172a", size=19, family="Inter, Arial, sans-serif")),
        xaxis=dict(
            color="#334155",
            gridcolor="#eef2f6",
            linecolor="#cbd5e1",
            zeroline=False,
            title_font=dict(size=12),
        ),
        yaxis=dict(
            color="#334155",
            gridcolor="#eef2f6",
            linecolor="#cbd5e1",
            zeroline=False,
            title_font=dict(size=12),
        ),
        legend=dict(
            font=dict(color="#334155", size=12),
            bgcolor="rgba(255,255,255,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        colorway=PALETA,
        margin=dict(l=60, r=30, t=76, b=62),
        height=h,
        hoverlabel=dict(bgcolor="#0f172a", font_color="#ffffff", font_size=13),
    )
    fig.update_xaxes(showspikes=True, spikethickness=1, spikecolor="#94a3b8")
    fig.update_yaxes(showspikes=True, spikethickness=1, spikecolor="#94a3b8")
    return adicionar_watermark(fig)


def card_html(titulo, v, attr, unid, classe, base):
    delta = variacao(base, attr) if attr else "Período selecionado"
    casas = 2 if unid != "1000 MT" else 1
    return f"""
    <div class="card {classe}">
        <div class="card-title">{titulo}</div>
        <div class="card-value">{fmt(v, casas)}</div>
        <div class="card-delta">{unid} | {delta}</div>
    </div>
    """

# ============================================================
# APP
# ============================================================

df = carregar_dados()

st.title("🌽 USDA Milho")
st.caption("USDA PSD | Oferta e demanda global do milho | Produção, consumo, comércio, estoques, estoque/uso, market share e rankings")

produtos = sorted(df["Produto"].dropna().unique())
paises = ["Mundo"] + sorted([p for p in df["País"].dropna().unique() if p != "Mundo"])
indicadores = sorted(df["Indicador"].dropna().unique())

with st.container():
    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.4])

    with c1:
        produto = st.selectbox("Produto", produtos, index=produtos.index("Milho") if "Milho" in produtos else 0)

    with c2:
        pais = st.selectbox("País / Região", paises, index=0)

    with c3:
        indicador = st.selectbox("Indicador principal", indicadores, index=indicadores.index("Produção") if "Produção" in indicadores else 0)

base_inicial = df[(df["Produto"] == produto) & (df["País"] == pais)].copy()
anos = sorted(base_inicial["Year"].dropna().unique())

if not anos:
    st.warning("Não há dados disponíveis para essa combinação.")
    st.stop()

with c4:
    ano_ini, ano_fim = st.select_slider("Período", options=anos, value=(anos[0], anos[-1]))

base = base_inicial[(base_inicial["Year"] >= ano_ini) & (base_inicial["Year"] <= ano_fim)].copy()
base_ind = base[base["Indicador"] == indicador]
attr_indicador = base_ind["Attribute"].iloc[0] if not base_ind.empty else "Production"

producao = valor(base, "Production")
consumo = valor(base, "Domestic Consumption")
exportacao = valor(base, "Exports")
importacao = valor(base, "Imports")
estoque = valor(base, "Ending Stocks")
feed = valor(base, "Feed Dom. Consumption")
fsi = valor(base, "FSI Consumption")
area = valor(base, "Area Harvested")
yield_ = valor(base, "Yield")

estoque_uso = (estoque / consumo * 100) if estoque and consumo else None
export_prod = (exportacao / producao * 100) if exportacao and producao else None
import_cons = (importacao / consumo * 100) if importacao and consumo else None
cagr_ind = cagr(base, attr_indicador)

st.subheader(f"Painel Executivo — {produto} | {pais}")

cards = [
    ("Produção", producao, "Production", "1000 MT", "card-green"),
    ("Consumo Doméstico", consumo, "Domestic Consumption", "1000 MT", "card-blue"),
    ("Consumo Ração", feed, "Feed Dom. Consumption", "1000 MT", "card-orange"),
    ("Exportações", exportacao, "Exports", "1000 MT", "card-green"),
    ("Estoque Final", estoque, "Ending Stocks", "1000 MT", "card-dark"),
    ("Estoque/Uso", estoque_uso, None, "%", "card-orange"),
    ("Exportação/Produção", export_prod, None, "%", "card-blue"),
    ("CAGR Indicador", cagr_ind, None, "% a.a.", "card-dark"),
]

cols = st.columns(4)
for i, (titulo, v, attr, unid, classe) in enumerate(cards):
    with cols[i % 4]:
        st.markdown(card_html(titulo, v, attr, unid, classe, base), unsafe_allow_html=True)

st.divider()

tabs = st.tabs([
    "📈 Visão Executiva",
    "⚖️ Oferta & Demanda",
    "🌍 Market Share",
    "🏆 Rankings",
    "📊 Diagnóstico",
    "🧭 Análises Extras",
    "📋 Dados"
])

with tabs[0]:
    col_a, col_b = st.columns([2.1, 1])

    with col_a:
        base_graf = base[base["Indicador"] == indicador].sort_values("Year")
        fig = px.line(base_graf, x="Year", y="Value", markers=True, title=f"Evolução — {indicador} | {produto} | {pais}")
        fig.update_traces(line=dict(width=3.4, color="#14532d"), marker=dict(size=7, color="#14532d", line=dict(width=1.5, color="#ffffff")))
        fig.update_xaxes(title_text="Ano")
        fig.update_yaxes(title_text="Valor")
        st.plotly_chart(aplicar_layout(fig, 500), use_container_width=True, config=PLOTLY_CONFIG)

    with col_b:
        var_ind = variacao_num(base, attr_indicador)
        cagr_txt = fmt_var(cagr_ind) if cagr_ind is not None else "-"
        st.markdown(f"""
        <div class="insight-box">
            <h3>Leitura rápida</h3>
            <p>Indicador selecionado: <b>{indicador}</b>.</p>
            <p>Variação anual: <b>{fmt_var(var_ind) if var_ind is not None else '-'}</b><br>
            CAGR no período: <b>{cagr_txt}</b></p>
            <p>Para milho, os pontos mais sensíveis geralmente são estoque/uso, consumo para ração, FSI/etanol, exportações dos EUA/Brasil/Argentina/Ucrânia e ritmo de importação da China.</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Comparação internacional")
    padrao = [p for p in ["Mundo", "Estados Unidos", "China", "Brasil", "Argentina", "Ucrânia"] if p in paises]
    paises_comp = st.multiselect("Países/regiões para comparação", paises, default=padrao)

    comp = df[
        (df["Produto"] == produto) &
        (df["País"].isin(paises_comp)) &
        (df["Indicador"] == indicador) &
        (df["Year"] >= ano_ini) &
        (df["Year"] <= ano_fim)
    ].copy()

    fig_comp = px.line(comp, x="Year", y="Value", color="País", markers=True, title=f"Comparativo Internacional — {indicador} | {produto}")
    fig_comp.update_traces(line=dict(width=3), marker=dict(size=6, line=dict(width=1, color="#ffffff")))
    fig_comp.update_xaxes(title_text="Ano")
    fig_comp.update_yaxes(title_text="Valor")
    st.plotly_chart(aplicar_layout(fig_comp, 535), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[1]:
    st.subheader("Balanço de Oferta e Demanda")
    attrs = [
        "Beginning Stocks", "Production", "Imports", "Total Supply",
        "Feed Dom. Consumption", "FSI Consumption", "Domestic Consumption", "Exports", "Ending Stocks"
    ]
    bal = base[base["Attribute"].isin(attrs)].copy()

    fig_bal = px.line(bal, x="Year", y="Value", color="Indicador", markers=True, title=f"Balanço USDA — {produto} | {pais}")
    fig_bal.update_traces(line=dict(width=2.8), marker=dict(size=6))
    st.plotly_chart(aplicar_layout(fig_bal, 540), use_container_width=True, config=PLOTLY_CONFIG)

    pivot = pivot_base(base)
    col1, col2 = st.columns(2)

    with col1:
        if {"Ending Stocks", "Domestic Consumption"}.issubset(pivot.columns):
            pivot["Estoque/Uso (%)"] = pivot["Ending Stocks"] / pivot["Domestic Consumption"] * 100
            fig_su = go.Figure()
            fig_su.add_bar(x=pivot["Year"], y=pivot["Estoque/Uso (%)"], marker_color="#d97706", name="Estoque/Uso")
            fig_su.add_scatter(x=pivot["Year"], y=pivot["Estoque/Uso (%)"].rolling(3, min_periods=1).mean(), mode="lines+markers", line=dict(color="#0b3d63", width=3), name="Média móvel 3 anos")
            fig_su.update_layout(title="Estoque/Uso com média móvel")
            fig_su.update_yaxes(title_text="%")
            fig_su.update_xaxes(title_text="Ano")
            st.plotly_chart(aplicar_layout(fig_su, 430), use_container_width=True, config=PLOTLY_CONFIG)

    with col2:
        if {"Production", "Domestic Consumption"}.issubset(pivot.columns):
            pivot["Produção - Consumo"] = pivot["Production"] - pivot["Domestic Consumption"]
            cores = ["#14532d" if v >= 0 else "#dc2626" for v in pivot["Produção - Consumo"]]
            fig_gap = px.bar(pivot, x="Year", y="Produção - Consumo", title="Superávit/Déficit: Produção - Consumo")
            fig_gap.update_traces(marker_color=cores)
            fig_gap.update_xaxes(title_text="Ano")
            fig_gap.update_yaxes(title_text="1000 MT")
            st.plotly_chart(aplicar_layout(fig_gap, 430), use_container_width=True, config=PLOTLY_CONFIG)

    if {"Beginning Stocks", "Production", "Imports", "Domestic Consumption", "Exports", "Ending Stocks"}.issubset(pivot.columns):
        ult = pivot.sort_values("Year").iloc[-1]
        fig_waterfall = go.Figure(go.Waterfall(
            name="Balanço",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "total"],
            x=["Estoque Inicial", "Produção", "Importações", "Consumo", "Exportações", "Estoque Final"],
            y=[ult["Beginning Stocks"], ult["Production"], ult["Imports"], -ult["Domestic Consumption"], -ult["Exports"], ult["Ending Stocks"]],
            connector={"line": {"color": "#94a3b8"}},
            increasing={"marker": {"color": "#14532d"}},
            decreasing={"marker": {"color": "#d97706"}},
            totals={"marker": {"color": "#0b3d63"}},
        ))
        fig_waterfall.update_layout(title=f"Waterfall do balanço — {pais} | {int(ult['Year'])}")
        fig_waterfall.update_yaxes(title_text="1000 MT")
        st.plotly_chart(aplicar_layout(fig_waterfall, 470), use_container_width=True, config=PLOTLY_CONFIG)

    st.dataframe(pivot, use_container_width=True)

with tabs[2]:
    st.subheader("Market Share Mundial")
    ano_ms = st.selectbox("Ano para análise de participação", sorted(df["Year"].dropna().unique(), reverse=True))

    ms = df[
        (df["Produto"] == produto) &
        (df["Indicador"] == indicador) &
        (df["Year"] == ano_ms) &
        (df["País"] != "Mundo")
    ].copy()
    ms = ms[ms["Value"] > 0].sort_values("Value", ascending=False)
    total = ms["Value"].sum()
    ms["Market Share (%)"] = ms["Value"] / total * 100 if total else 0
    ms["Share acumulado (%)"] = ms["Market Share (%)"].cumsum()

    c1, c2 = st.columns(2)
    with c1:
        fig_ms = px.bar(ms.head(15), x="Market Share (%)", y="País", orientation="h", title=f"Top 15 — Participação Mundial | {ano_ms}")
        fig_ms.update_traces(marker_color="#14532d", text=ms.head(15)["Market Share (%)"].map(lambda x: f"{x:.1f}%"), textposition="outside")
        fig_ms.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_ms.update_xaxes(title_text="Market Share (%)")
        st.plotly_chart(aplicar_layout(fig_ms, 520), use_container_width=True, config=PLOTLY_CONFIG)

    with c2:
        fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
        top = ms.head(20).copy()
        fig_pareto.add_trace(go.Bar(x=top["País"], y=top["Value"], name="Volume", marker_color="#0b3d63"), secondary_y=False)
        fig_pareto.add_trace(go.Scatter(x=top["País"], y=top["Share acumulado (%)"], name="Share acumulado", mode="lines+markers", line=dict(color="#d97706", width=3)), secondary_y=True)
        fig_pareto.update_layout(title=f"Concentração — {indicador} | {ano_ms}")
        fig_pareto.update_yaxes(title_text="1000 MT", secondary_y=False)
        fig_pareto.update_yaxes(title_text="Share acumulado (%)", secondary_y=True, range=[0, 105])
        st.plotly_chart(aplicar_layout(fig_pareto, 520), use_container_width=True, config=PLOTLY_CONFIG)

    st.dataframe(ms[["País", "Value", "Market Share (%)", "Share acumulado (%)"]].head(30), use_container_width=True)

with tabs[3]:
    st.subheader("Ranking Mundial")
    ano_rank = st.selectbox("Ano do ranking", sorted(df["Year"].dropna().unique(), reverse=True), key="rank")

    rank = df[
        (df["Produto"] == produto) &
        (df["Indicador"] == indicador) &
        (df["Year"] == ano_rank) &
        (df["País"] != "Mundo")
    ].copy()
    rank = rank[rank["Value"] > 0].sort_values("Value", ascending=False)

    fig_rank = px.bar(rank.head(20), x="Value", y="País", orientation="h", title=f"Top 20 — {indicador} | {produto} | {ano_rank}")
    fig_rank.update_traces(marker_color="#14532d", text=rank.head(20)["Value"].map(lambda x: fmt(x, 1)), textposition="outside")
    fig_rank.update_layout(yaxis={"categoryorder": "total ascending"})
    fig_rank.update_xaxes(title_text="1000 MT")
    st.plotly_chart(aplicar_layout(fig_rank, 585), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[4]:
    st.subheader("Diagnóstico Fundamentalista")
    pivot = pivot_base(base)

    c1, c2 = st.columns(2)
    with c1:
        if {"Exports", "Production"}.issubset(pivot.columns):
            pivot["Exportação/Produção (%)"] = pivot["Exports"] / pivot["Production"] * 100
            fig = px.line(pivot, x="Year", y="Exportação/Produção (%)", markers=True, title="Exportação / Produção")
            fig.update_traces(line=dict(width=3.5, color="#d97706"), marker=dict(size=7))
            st.plotly_chart(aplicar_layout(fig, 440), use_container_width=True, config=PLOTLY_CONFIG)

    with c2:
        if {"Imports", "Domestic Consumption"}.issubset(pivot.columns):
            pivot["Importação/Consumo (%)"] = pivot["Imports"] / pivot["Domestic Consumption"] * 100
            fig = px.line(pivot, x="Year", y="Importação/Consumo (%)", markers=True, title="Importação / Consumo")
            fig.update_traces(line=dict(width=3.5, color="#dc2626"), marker=dict(size=7))
            st.plotly_chart(aplicar_layout(fig, 440), use_container_width=True, config=PLOTLY_CONFIG)

    c3, c4 = st.columns(2)
    with c3:
        if {"Feed Dom. Consumption", "Domestic Consumption"}.issubset(pivot.columns):
            pivot["Ração/Consumo (%)"] = pivot["Feed Dom. Consumption"] / pivot["Domestic Consumption"] * 100
            fig = px.line(pivot, x="Year", y="Ração/Consumo (%)", markers=True, title="Consumo para Ração / Consumo Total")
            fig.update_traces(line=dict(width=3.5, color="#14532d"), marker=dict(size=7))
            st.plotly_chart(aplicar_layout(fig, 440), use_container_width=True, config=PLOTLY_CONFIG)

    with c4:
        if {"FSI Consumption", "Domestic Consumption"}.issubset(pivot.columns):
            pivot["FSI/Consumo (%)"] = pivot["FSI Consumption"] / pivot["Domestic Consumption"] * 100
            fig = px.line(pivot, x="Year", y="FSI/Consumo (%)", markers=True, title="FSI / Consumo Total")
            fig.update_traces(line=dict(width=3.5, color="#0b3d63"), marker=dict(size=7))
            st.plotly_chart(aplicar_layout(fig, 440), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[5]:
    st.subheader("Análises Extras")
    pivot = pivot_base(base)

    c1, c2 = st.columns(2)

    with c1:
        if {"Production", "Area Harvested", "Yield"}.issubset(pivot.columns):
            fig_area_yield = make_subplots(specs=[[{"secondary_y": True}]])
            fig_area_yield.add_trace(go.Bar(x=pivot["Year"], y=pivot["Area Harvested"], name="Área Colhida", marker_color="#cbd5e1"), secondary_y=False)
            fig_area_yield.add_trace(go.Scatter(x=pivot["Year"], y=pivot["Yield"], name="Produtividade", mode="lines+markers", line=dict(color="#14532d", width=3)), secondary_y=True)
            fig_area_yield.update_layout(title=f"Área colhida x Produtividade — {pais}")
            fig_area_yield.update_yaxes(title_text="Área colhida", secondary_y=False)
            fig_area_yield.update_yaxes(title_text="Produtividade", secondary_y=True)
            st.plotly_chart(aplicar_layout(fig_area_yield, 460), use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("Área colhida e/ou produtividade não disponíveis para essa seleção.")

    with c2:
        if "Production" in pivot.columns:
            pivot["Variação Produção (%)"] = pivot["Production"].pct_change() * 100
            fig_yoy = px.bar(pivot.dropna(subset=["Variação Produção (%)"]), x="Year", y="Variação Produção (%)", title="Variação anual da produção")
            cores = ["#14532d" if v >= 0 else "#dc2626" for v in pivot.dropna(subset=["Variação Produção (%)"])["Variação Produção (%)"]]
            fig_yoy.update_traces(marker_color=cores)
            fig_yoy.update_yaxes(title_text="%")
            st.plotly_chart(aplicar_layout(fig_yoy, 460), use_container_width=True, config=PLOTLY_CONFIG)

    c3, c4 = st.columns(2)

    with c3:
        if {"Production", "Domestic Consumption", "Ending Stocks"}.issubset(pivot.columns):
            fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
            fig_combo.add_trace(go.Scatter(x=pivot["Year"], y=pivot["Production"], name="Produção", mode="lines+markers", line=dict(color="#14532d", width=3)), secondary_y=False)
            fig_combo.add_trace(go.Scatter(x=pivot["Year"], y=pivot["Domestic Consumption"], name="Consumo", mode="lines+markers", line=dict(color="#0b3d63", width=3)), secondary_y=False)
            fig_combo.add_trace(go.Bar(x=pivot["Year"], y=pivot["Ending Stocks"], name="Estoque Final", marker_color="rgba(217,119,6,.35)"), secondary_y=True)
            fig_combo.update_layout(title="Produção, consumo e estoques")
            fig_combo.update_yaxes(title_text="Produção / Consumo", secondary_y=False)
            fig_combo.update_yaxes(title_text="Estoque Final", secondary_y=True)
            st.plotly_chart(aplicar_layout(fig_combo, 470), use_container_width=True, config=PLOTLY_CONFIG)

    with c4:
        mundo_ano = df[(df["Produto"] == produto) & (df["Year"] == ano_fim) & (df["País"] != "Mundo")]
        mapa = mundo_ano[mundo_ano["Attribute"].isin(["Production", "Domestic Consumption", "Exports", "Imports"])].pivot_table(
            index="País", columns="Attribute", values="Value", aggfunc="sum"
        ).reset_index()
        if {"Production", "Domestic Consumption", "Exports"}.issubset(mapa.columns):
            mapa = mapa[(mapa["Production"] > 0) | (mapa["Exports"] > 0)].copy()
            mapa["Exportação/Produção (%)"] = mapa["Exports"] / mapa["Production"].replace(0, pd.NA) * 100
            mapa = mapa.dropna(subset=["Exportação/Produção (%)"]).sort_values("Exports", ascending=False).head(20)
            fig_scatter = px.scatter(
                mapa,
                x="Production",
                y="Exportação/Produção (%)",
                size="Exports",
                color="País",
                hover_name="País",
                title=f"Perfil exportador — produção x exportação/produção | {ano_fim}",
            )
            fig_scatter.update_xaxes(title_text="Produção")
            fig_scatter.update_yaxes(title_text="Exportação/Produção (%)")
            st.plotly_chart(aplicar_layout(fig_scatter, 470), use_container_width=True, config=PLOTLY_CONFIG)

    st.markdown("""
    <div class="metric-note">
        <b>Como usar:</b> os gráficos desta aba ajudam a separar crescimento por área/produtividade, identificar anos de choque na produção,
        visualizar aperto ou folga no balanço e comparar o perfil exportador dos principais países.
    </div>
    """, unsafe_allow_html=True)

with tabs[6]:
    st.subheader("Base filtrada")
    st.dataframe(base[["Produto", "País", "Year", "Indicador", "Unit", "Value"]], use_container_width=True)

    csv = base.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar base filtrada",
        csv,
        file_name=f"agrobasis_milho_{produto}_{pais}.csv",
        mime="text/csv"
    )
