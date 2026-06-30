import os
import pandas as pd
import streamlit as st
import plotly.express as px

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(page_title="USDA Trigo", layout="wide")

ARQUIVO = "psd_trigo.csv"

if not os.path.exists(ARQUIVO):
    st.error("Arquivo 'psd_trigo.csv' não encontrado.")
    st.stop()

# ============================================================
# DICIONÁRIOS
# ============================================================

PRODUTOS_VALIDOS = {
    "Wheat": "Trigo",
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
    "India": "Índia",
    "Russia": "Rússia",
    "Ukraine": "Ucrânia",
    "Canada": "Canadá",
    "Australia": "Austrália",
    "Pakistan": "Paquistão",
    "Turkey": "Turquia",
    "Kazakhstan": "Cazaquistão",
    "United Kingdom": "Reino Unido",
    "Egypt": "Egito",
    "Iran": "Irã",
    "Japan": "Japão",
    "Mexico": "México",
    "Morocco": "Marrocos",
    "Algeria": "Argélia",
    "Indonesia": "Indonésia",
    "Bangladesh": "Bangladesh",
    "South Korea": "Coreia do Sul",
    "Thailand": "Tailândia",
    "Vietnam": "Vietnã",
}

# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family:'Inter', sans-serif;
}

.stApp {
    background:#f4f6f9;
    color:#1e293b;
}

.block-container {
    padding-top:1.5rem;
    padding-bottom:2rem;
    max-width:1400px;
}

h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
label {
    color:#0f172a !important;
}

h1 {
    font-weight:800 !important;
    letter-spacing:-.02em;
}

.stCaptionContainer, .stCaptionContainer p {
    color:#64748b !important;
}

.stSelectbox label,
.stSlider label,
.stMultiSelect label {
    color:#334155 !important;
    font-weight:600;
    font-size:13px;
    text-transform:uppercase;
    letter-spacing:.03em;
}

/* Caixas de seleção */
[data-baseweb="select"] {
    background:#ffffff !important;
    border-radius:10px;
    border:1px solid #e2e8f0 !important;
}

[data-baseweb="select"] div,
[data-baseweb="select"] span {
    color:#0f172a !important;
}

/* Dropdown aberto */
[role="listbox"] div,
[role="option"],
[role="option"] div,
[role="option"] span {
    color:#0f172a !important;
    background:#ffffff !important;
}

/* Abas */
.stTabs [data-baseweb="tab-list"] {
    gap:4px;
    background:#ffffff;
    padding:6px;
    border-radius:14px;
    border:1px solid #e2e8f0;
}

.stTabs [data-baseweb="tab"] {
    color:#475569;
    font-weight:600;
    border-radius:10px;
    padding:8px 16px;
}

.stTabs [aria-selected="true"] {
    background:#0f3d63 !important;
    color:#ffffff !important;
}

/* Cards executivos — versão discreta/profissional */
.card {
    position:relative;
    overflow:hidden;
    padding:18px 18px 16px 18px;
    border-radius:16px;
    color:#0f172a;
    background:#ffffff;
    box-shadow:0px 4px 14px rgba(15,23,42,0.045);
    min-height:112px;
    border:1px solid #e5eaf1;
}

.card::before {
    content:"";
    position:absolute;
    left:0;
    top:0;
    width:4px;
    height:100%;
    background:#0f3d63;
}

.card-green::before  { background:#1e6a3c; }
.card-blue::before   { background:#0f3d63; }
.card-orange::before { background:#d97706; }
.card-dark::before   { background:#64748b; }

.card-title {
    color:#64748b !important;
    font-size:11.5px;
    text-transform:uppercase;
    letter-spacing:.08em;
    font-weight:700;
}

.card-value {
    color:#0f172a !important;
    font-size:25px;
    font-weight:800;
    margin-top:8px;
    letter-spacing:-.02em;
}

.card-delta {
    color:#64748b !important;
    font-size:11.5px;
    margin-top:8px;
    line-height:1.35;
}

.insight-box {
    background:#ffffff;
    border:1px solid #e2e8f0;
    padding:22px;
    border-radius:18px;
    color:#1e293b;
    box-shadow:0px 6px 18px rgba(15,23,42,0.06);
}

.insight-box h3 {
    color:#0f3d63 !important;
    font-weight:800;
}

.insight-box p {
    color:#334155 !important;
    line-height:1.7;
}

/* Cartões de gráfico */
div[data-testid="stPlotlyChart"] {
    background:#ffffff;
    border-radius:18px;
    padding:8px;
    border:1px solid #e2e8f0;
    box-shadow:0px 6px 18px rgba(15,23,42,0.05);
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
</style>
""", unsafe_allow_html=True)

# Paleta corporativa usada em todos os gráficos (ótima para apresentações)
PALETA = ["#0b3d63", "#15a86b", "#e08a1f", "#9333ea", "#0891b2",
          "#dc2626", "#475569", "#ca8a04", "#16a34a", "#2563eb"]

# ============================================================
# FUNÇÕES
# ============================================================

def fmt(v, casas=1):
    if v is None or pd.isna(v):
        return "-"
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


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

    # Mantém apenas trigo
    df = df[df["Commodity"].isin(PRODUTOS_VALIDOS.keys())].copy()

    if df.empty:
        st.error("Nenhum dado de trigo foi encontrado no arquivo.")
        st.stop()

    # Traduções
    df["Produto"] = df["Commodity"].map(PRODUTOS_VALIDOS)
    df["País"] = df["Country"].map(TRAD_PAIS).fillna(df["Country"])
    df["Indicador"] = df["Attribute"].map(TRAD_ATTR).fillna(df["Attribute"])

    # Se existir World no arquivo, usa o World oficial.
    # Se não existir, cria Mundo pela soma dos países.
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


def variacao(base, attr):
    s = base[base["Attribute"] == attr].sort_values("Year")
    if len(s) < 2:
        return "Sem comparação"

    atual = s["Value"].iloc[-1]
    anterior = s["Value"].iloc[-2]

    if anterior == 0 or pd.isna(anterior):
        return "Sem comparação"

    var = ((atual / anterior) - 1) * 100
    sinal = "+" if var >= 0 else ""

    return f"{sinal}{var:.1f}% vs ano anterior".replace(".", ",")


def cagr(base, attr):
    s = base[base["Attribute"] == attr].sort_values("Year")
    if len(s) < 2:
        return None

    ini = s["Value"].iloc[0]
    fim = s["Value"].iloc[-1]
    anos = s["Year"].iloc[-1] - s["Year"].iloc[0]

    if ini <= 0 or anos <= 0:
        return None

    return ((fim / ini) ** (1 / anos) - 1) * 100


def aplicar_layout(fig, h=500):
    """Layout padrão AgroBasis: limpo, exportável e com watermark discreta."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#1e293b", size=13, family="Inter, Arial, sans-serif"),
        title_font=dict(color="#0f172a", size=20, family="Inter, Arial, sans-serif"),
        title=dict(x=0.015, xanchor="left", y=0.96),
        xaxis=dict(
            title_font=dict(size=12, color="#475569"),
            tickfont=dict(size=11, color="#475569"),
            gridcolor="#f1f5f9",
            linecolor="#cbd5e1",
            showline=True,
            mirror=False,
            zeroline=False,
            ticks="outside",
            tickcolor="#cbd5e1",
        ),
        yaxis=dict(
            title_font=dict(size=12, color="#475569"),
            tickfont=dict(size=11, color="#475569"),
            gridcolor="#eef2f7",
            linecolor="#cbd5e1",
            showline=True,
            mirror=False,
            zeroline=False,
            ticks="outside",
            tickcolor="#cbd5e1",
        ),
        legend=dict(
            font=dict(size=11, color="#334155"),
            bgcolor="rgba(255,255,255,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            itemclick="toggleothers",
            itemdoubleclick="toggle"
        ),
        colorway=PALETA,
        margin=dict(l=64, r=34, t=82, b=58),
        height=h,
        hoverlabel=dict(bgcolor="#0f172a", font_color="#ffffff", font_size=12),
        uniformtext_minsize=9,
        uniformtext_mode="hide",
    )

    fig.update_traces(
        hovertemplate=None,
        marker_line_width=0,
    )

    # Watermark central discreta, aparece também no PNG baixado pelo usuário.
    fig.add_annotation(
        text="AgroBasis",
        xref="paper", yref="paper",
        x=0.5, y=0.52,
        showarrow=False,
        font=dict(size=54, color="rgba(15, 61, 99, 0.075)", family="Inter, Arial, sans-serif"),
        xanchor="center",
        yanchor="middle",
        textangle=0
    )

    # Assinatura técnica no rodapé.
    fig.add_annotation(
        text="Fonte: USDA PSD • Elaboração: AgroBasis",
        xref="paper", yref="paper",
        x=1, y=-0.16,
        showarrow=False,
        font=dict(size=10, color="#94a3b8"),
        xanchor="right"
    )
    return fig


def aplicar_linha_profissional(fig, cor=None):
    """Padroniza linhas para leitura em tela e exportação em apresentações."""
    linha = dict(width=3.2, shape="spline", smoothing=0.35)
    if cor:
        linha["color"] = cor
    fig.update_traces(
        mode="lines+markers",
        line=linha,
        marker=dict(size=6.5, line=dict(width=1.2, color="#ffffff")),
    )
    return fig


def aplicar_barras_profissionais(fig, cor=None, texto=False):
    """Padroniza barras para PNG/PPT, com cantos visuais limpos e rótulos opcionais."""
    kwargs = dict(marker_line_width=0, opacity=0.92)
    if cor:
        kwargs["marker_color"] = cor
    if texto:
        kwargs.update(texttemplate="%{x:.1f}", textposition="outside", cliponaxis=False)
    fig.update_traces(**kwargs)
    return fig


# Configuração padrão para exportação de imagens em alta resolução (ideal para PPT)
PLOTLY_CONFIG = {
    "displaylogo": False,
    "toImageButtonOptions": {
        "format": "png",
        "filename": "agrobasis_usda_trigo_grafico",
        "scale": 5
    },
    "modeBarButtonsToRemove": ["lasso2d", "select2d"]
}


# ============================================================
# APP
# ============================================================

df = carregar_dados()

st.title("🌾 USDA Trigo")
st.caption("USDA PSD | Trigo | Produção, consumo, exportações, importações, estoques, estoque/uso, market share e ranking mundial")

produtos = sorted(df["Produto"].dropna().unique())
paises = ["Mundo"] + sorted([p for p in df["País"].dropna().unique() if p != "Mundo"])
indicadores = sorted(df["Indicador"].dropna().unique())

c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.4])

with c1:
    produto = st.selectbox(
        "Produto",
        produtos,
        index=produtos.index("Trigo") if "Trigo" in produtos else 0
    )

with c2:
    pais = st.selectbox(
        "País / Região",
        paises,
        index=0
    )

with c3:
    indicador = st.selectbox(
        "Indicador principal",
        indicadores,
        index=indicadores.index("Produção") if "Produção" in indicadores else 0
    )

base_inicial = df[
    (df["Produto"] == produto) &
    (df["País"] == pais)
].copy()

anos = sorted(base_inicial["Year"].dropna().unique())

if not anos:
    st.warning("Não há dados disponíveis para essa combinação.")
    st.stop()

with c4:
    ano_ini, ano_fim = st.select_slider(
        "Período",
        options=anos,
        value=(anos[0], anos[-1])
    )

base = base_inicial[
    (base_inicial["Year"] >= ano_ini) &
    (base_inicial["Year"] <= ano_fim)
].copy()

base_ind = base[base["Indicador"] == indicador]
attr_indicador = base_ind["Attribute"].iloc[0] if not base_ind.empty else "Production"

producao = valor(base, "Production")
consumo = valor(base, "Domestic Consumption")
exportacao = valor(base, "Exports")
importacao = valor(base, "Imports")
estoque = valor(base, "Ending Stocks")
feed = valor(base, "Feed Dom. Consumption")
fsi = valor(base, "FSI Consumption")

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
        delta = variacao(base, attr) if attr else "Período selecionado"
        st.markdown(f"""
        <div class="card {classe}">
            <div class="card-title">{titulo}</div>
            <div class="card-value">{fmt(v, 2 if unid != "1000 MT" else 1)}</div>
            <div class="card-delta">{unid} | {delta}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

tabs = st.tabs([
    "📈 Visão Executiva",
    "⚖️ Balanço",
    "🌍 Market Share",
    "🏆 Rankings",
    "📊 Diagnóstico",
    "📋 Dados"
])

with tabs[0]:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        base_graf = base[base["Indicador"] == indicador].sort_values("Year")

        fig = px.line(
            base_graf,
            x="Year",
            y="Value",
            markers=True,
            title=f"Evolução — {indicador} | {produto} | {pais}"
        )
        aplicar_linha_profissional(fig, "#1e6a3c")
        fig.update_xaxes(title_text="Ano")
        fig.update_yaxes(title_text="Valor")
        st.plotly_chart(aplicar_layout(fig, 500), use_container_width=True, config=PLOTLY_CONFIG)

    with col_b:
        st.markdown("""
        <div class="insight-box">
            <h3>Leitura rápida</h3>
            <p>Este painel mostra a trajetória do indicador selecionado e sua relação com os principais fundamentos:
            produção, consumo doméstico, consumo para ração, exportações, importações e estoques.</p>
            <p>Para análise de preço, acompanhe principalmente estoque/uso, exportações, importações,
            consumo para ração e participação dos grandes players globais: Rússia, União Europeia, EUA, Canadá,
            Austrália, Argentina e Ucrânia.</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Comparação internacional")

    padrao = [p for p in ["Mundo", "Rússia", "União Europeia", "China", "Índia", "Estados Unidos", "Canadá", "Austrália", "Argentina", "Ucrânia"] if p in paises]

    paises_comp = st.multiselect(
        "Países/regiões para comparação",
        paises,
        default=padrao
    )

    comp = df[
        (df["Produto"] == produto) &
        (df["País"].isin(paises_comp)) &
        (df["Indicador"] == indicador) &
        (df["Year"] >= ano_ini) &
        (df["Year"] <= ano_fim)
    ].copy()

    fig_comp = px.line(
        comp,
        x="Year",
        y="Value",
        color="País",
        markers=True,
        title=f"Comparativo Internacional — {indicador} | {produto}"
    )
    aplicar_linha_profissional(fig_comp)
    fig_comp.update_xaxes(title_text="Ano")
    fig_comp.update_yaxes(title_text="Valor")
    st.plotly_chart(aplicar_layout(fig_comp, 520), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[1]:
    st.subheader("Balanço de Oferta e Demanda")

    attrs = [
        "Beginning Stocks",
        "Production",
        "Imports",
        "Total Supply",
        "Feed Dom. Consumption",
        "FSI Consumption",
        "Domestic Consumption",
        "Exports",
        "Ending Stocks"
    ]

    bal = base[base["Attribute"].isin(attrs)].copy()

    fig_bal = px.line(
        bal,
        x="Year",
        y="Value",
        color="Indicador",
        markers=True,
        title=f"Balanço USDA — {produto} | {pais}"
    )
    aplicar_linha_profissional(fig_bal)
    st.plotly_chart(aplicar_layout(fig_bal, 540), use_container_width=True, config=PLOTLY_CONFIG)

    pivot = base.pivot_table(
        index="Year",
        columns="Attribute",
        values="Value",
        aggfunc="sum"
    ).reset_index()

    col1, col2 = st.columns(2)

    with col1:
        if "Ending Stocks" in pivot.columns and "Domestic Consumption" in pivot.columns:
            pivot["Estoque/Uso (%)"] = pivot["Ending Stocks"] / pivot["Domestic Consumption"] * 100
            fig_su = px.bar(pivot, x="Year", y="Estoque/Uso (%)", title="Estoque/Uso")
            aplicar_barras_profissionais(fig_su, "#d97706")
            st.plotly_chart(aplicar_layout(fig_su, 420), use_container_width=True, config=PLOTLY_CONFIG)

    with col2:
        if {"Production", "Domestic Consumption"}.issubset(pivot.columns):
            pivot["Produção - Consumo"] = pivot["Production"] - pivot["Domestic Consumption"]
            fig_gap = px.bar(
                pivot,
                x="Year",
                y="Produção - Consumo",
                title="Superávit/Déficit: Produção - Consumo"
            )
            aplicar_barras_profissionais(fig_gap, "#0e7490")
            st.plotly_chart(aplicar_layout(fig_gap, 420), use_container_width=True, config=PLOTLY_CONFIG)

    st.dataframe(pivot, use_container_width=True)

with tabs[2]:
    st.subheader("Market Share Mundial")

    ano_ms = st.selectbox(
        "Ano para análise de participação",
        sorted(df["Year"].dropna().unique(), reverse=True)
    )

    ms = df[
        (df["Produto"] == produto) &
        (df["Indicador"] == indicador) &
        (df["Year"] == ano_ms) &
        (df["País"] != "Mundo")
    ].copy()

    ms = ms[ms["Value"] > 0].sort_values("Value", ascending=False)
    total = ms["Value"].sum()
    ms["Market Share (%)"] = ms["Value"] / total * 100 if total else 0

    c1, c2 = st.columns(2)

    with c1:
        fig_tree = px.treemap(
            ms.head(20),
            path=["País"],
            values="Value",
            color="Market Share (%)",
            title=f"Market Share — {indicador} | {produto} | {ano_ms}",
            color_continuous_scale="Greens"
        )
        st.plotly_chart(aplicar_layout(fig_tree, 520), use_container_width=True, config=PLOTLY_CONFIG)

    with c2:
        fig_ms = px.bar(
            ms.head(15),
            x="Market Share (%)",
            y="País",
            orientation="h",
            title="Top 15 — Participação Mundial"
        )
        aplicar_barras_profissionais(fig_ms, "#1e6a3c", texto=True)
        fig_ms.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(aplicar_layout(fig_ms, 520), use_container_width=True, config=PLOTLY_CONFIG)

    st.dataframe(ms[["País", "Value", "Market Share (%)"]].head(30), use_container_width=True)

with tabs[3]:
    st.subheader("Ranking Mundial")

    ano_rank = st.selectbox(
        "Ano do ranking",
        sorted(df["Year"].dropna().unique(), reverse=True),
        key="rank"
    )

    rank = df[
        (df["Produto"] == produto) &
        (df["Indicador"] == indicador) &
        (df["Year"] == ano_rank) &
        (df["País"] != "Mundo")
    ].copy()

    rank = rank[rank["Value"] > 0].sort_values("Value", ascending=False)

    fig_rank = px.bar(
        rank.head(20),
        x="Value",
        y="País",
        orientation="h",
        title=f"Top 20 — {indicador} | {produto} | {ano_rank}"
    )
    aplicar_barras_profissionais(fig_rank, "#1e6a3c", texto=True)
    fig_rank.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(aplicar_layout(fig_rank, 560), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[4]:
    st.subheader("Diagnóstico Fundamentalista")

    pivot = base.pivot_table(
        index="Year",
        columns="Attribute",
        values="Value",
        aggfunc="sum"
    ).reset_index()

    c1, c2 = st.columns(2)

    with c1:
        if {"Exports", "Production"}.issubset(pivot.columns):
            pivot["Exportação/Produção (%)"] = pivot["Exports"] / pivot["Production"] * 100
            fig = px.line(
                pivot,
                x="Year",
                y="Exportação/Produção (%)",
                markers=True,
                title="Exportação / Produção"
            )
            aplicar_linha_profissional(fig, "#d97706")
            st.plotly_chart(aplicar_layout(fig, 440), use_container_width=True, config=PLOTLY_CONFIG)

    with c2:
        if {"Imports", "Domestic Consumption"}.issubset(pivot.columns):
            pivot["Importação/Consumo (%)"] = pivot["Imports"] / pivot["Domestic Consumption"] * 100
            fig = px.line(
                pivot,
                x="Year",
                y="Importação/Consumo (%)",
                markers=True,
                title="Importação / Consumo"
            )
            aplicar_linha_profissional(fig, "#b91c1c")
            st.plotly_chart(aplicar_layout(fig, 440), use_container_width=True, config=PLOTLY_CONFIG)

    c3, c4 = st.columns(2)

    with c3:
        if {"Feed Dom. Consumption", "Domestic Consumption"}.issubset(pivot.columns):
            pivot["Ração/Consumo (%)"] = pivot["Feed Dom. Consumption"] / pivot["Domestic Consumption"] * 100
            fig = px.line(
                pivot,
                x="Year",
                y="Ração/Consumo (%)",
                markers=True,
                title="Consumo para Ração / Consumo Total"
            )
            aplicar_linha_profissional(fig, "#1e6a3c")
            st.plotly_chart(aplicar_layout(fig, 440), use_container_width=True, config=PLOTLY_CONFIG)

    with c4:
        if {"FSI Consumption", "Domestic Consumption"}.issubset(pivot.columns):
            pivot["FSI/Consumo (%)"] = pivot["FSI Consumption"] / pivot["Domestic Consumption"] * 100
            fig = px.line(
                pivot,
                x="Year",
                y="FSI/Consumo (%)",
                markers=True,
                title="FSI / Consumo Total"
            )
            aplicar_linha_profissional(fig, "#0e7490")
            st.plotly_chart(aplicar_layout(fig, 440), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[5]:
    st.subheader("Base filtrada")

    st.dataframe(
        base[["Produto", "País", "Year", "Indicador", "Unit", "Value"]],
        use_container_width=True
    )

    csv = base.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Baixar base filtrada",
        csv,
        file_name=f"agrobasis_trigo_{produto}_{pais}.csv",
        mime="text/csv"
    )
