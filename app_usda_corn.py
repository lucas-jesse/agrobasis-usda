import os
import pandas as pd
import streamlit as st
import plotly.express as px

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(page_title="USDA Milho", layout="wide")

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
    background:#92400e !important;
    color:#ffffff !important;
}

/* Cards executivos — discretos, fundo claro com leve destaque colorido */
.card {
    padding:16px 18px;
    border-radius:14px;
    background:#ffffff;
    border:1px solid #e7eaef;
    border-left:4px solid var(--accent, #92400e);
    box-shadow:0px 2px 8px rgba(15,23,42,0.04);
    min-height:104px;
}

.card-green  { --accent:#15a86b; }
.card-blue   { --accent:#0b3d63; }
.card-orange { --accent:#c2730f; }
.card-dark   { --accent:#475569; }

.card-title {
    color:#64748b !important;
    font-size:11.5px;
    text-transform:uppercase;
    letter-spacing:.06em;
    font-weight:700;
}

.card-value {
    color:#0f172a !important;
    font-size:23px;
    font-weight:800;
    margin-top:6px;
}

.card-delta {
    color:#94a3b8 !important;
    font-size:11.5px;
    margin-top:5px;
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
    color:#92400e !important;
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

# Paleta corporativa usada em todos os gráficos (tons de milho/terra — ótima para apresentações)
PALETA = ["#c2730f", "#0b3d63", "#15a86b", "#9333ea", "#0891b2",
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

    # Mantém apenas milho
    df = df[df["Commodity"].isin(PRODUTOS_VALIDOS.keys())].copy()

    if df.empty:
        st.error("Nenhum dado de milho foi encontrado no arquivo.")
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


def fmt_plotly(v, casas=1, sufixo=""):
    """Formata número para rótulos dentro dos gráficos."""
    if v is None or pd.isna(v):
        return ""
    txt = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{txt}{sufixo}"


def preparar_rotulos(df, coluna="Value", casas=1, sufixo=""):
    df = df.copy()
    df["Rotulo"] = df[coluna].apply(lambda x: fmt_plotly(x, casas, sufixo))
    return df


def aplicar_rotulos_linha(fig, casas=1, percentual=False, mostrar_rotulos=True):
    """Deixa linhas prontas para PPT.

    Regra visual: rótulos aparecem apenas quando o período selecionado tem
    até 8 anos. Em séries longas, os rótulos são ocultados para evitar
    sobreposição e poluição visual.
    """
    sufixo = "%" if percentual else ""

    for tr in fig.data:
        tr.line.width = 4
        tr.marker.size = 9
        tr.marker.line = dict(width=1.4, color="#ffffff")
        tr.cliponaxis = False

        if mostrar_rotulos:
            tr.mode = "lines+markers+text"
            tr.text = [fmt_plotly(v, casas, sufixo) for v in tr.y]
            tr.texttemplate = "%{text}"
            tr.textposition = "top center"
            tr.textfont = dict(size=11, color="#334155")
        else:
            tr.mode = "lines+markers"
            tr.text = None
            tr.texttemplate = None

    return fig


def aplicar_rotulos_barra(fig, casas=1, percentual=False, orientacao="v", mostrar_rotulos=True):
    """Adiciona valores nas barras quando isso melhora a leitura da imagem."""
    if not mostrar_rotulos:
        fig.update_traces(text=None, texttemplate=None, cliponaxis=False)
        return fig

    sufixo = "%" if percentual else ""

    for tr in fig.data:
        valores = tr.x if orientacao == "h" else tr.y
        tr.text = [fmt_plotly(v, casas, sufixo) for v in valores]
        tr.texttemplate = "%{text}"
        tr.textposition = "outside"
        tr.textfont = dict(size=12, color="#334155")
        tr.cliponaxis = False

    return fig


def aplicar_layout(fig, h=500, fonte="Fonte: USDA PSD • Elaboração: AgroBasis"):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#1e293b", size=14, family="Inter, Arial, sans-serif"),
        title_font=dict(color="#0f172a", size=20, family="Inter, Arial, sans-serif"),
        title=dict(x=0.02, xanchor="left", y=0.96, yanchor="top"),
        xaxis=dict(
            color="#334155",
            gridcolor="rgba(148,163,184,0.18)",
            linecolor="#cbd5e1",
            zeroline=False,
            ticks="outside",
            tickfont=dict(size=12),
            title_font=dict(size=13, color="#475569")
        ),
        yaxis=dict(
            color="#334155",
            gridcolor="rgba(148,163,184,0.18)",
            linecolor="#cbd5e1",
            zeroline=False,
            ticks="outside",
            tickfont=dict(size=12),
            title_font=dict(size=13, color="#475569")
        ),
        legend=dict(
            font=dict(color="#334155", size=12),
            bgcolor="rgba(255,255,255,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        colorway=PALETA,
        margin=dict(l=70, r=50, t=88, b=68),
        height=h,
        hoverlabel=dict(bgcolor="#0f172a", font_color="#ffffff", font_size=13),
        uniformtext_minsize=10,
        uniformtext_mode="show"
    )

    # Marca d'água central. Se existir um arquivo logo_agrobasis.png na pasta do app,
    # o Plotly usa a imagem. Se não existir, usa texto como fallback.
    logo_path = "logo_agrobasis.png"
    if os.path.exists(logo_path):
        fig.add_layout_image(
            dict(
                source=logo_path,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                sizex=0.48,
                sizey=0.48,
                xanchor="center",
                yanchor="middle",
                opacity=0.035,
                layer="below"
            )
        )
    else:
        fig.add_annotation(
            text="<b>AgroBasis</b>",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=66, color="rgba(20,83,45,0.035)"),
            xanchor="center",
            yanchor="middle"
        )

    fig.add_annotation(
        text=fonte,
        xref="paper", yref="paper",
        x=1, y=-0.18,
        showarrow=False,
        font=dict(size=11, color="#64748b"),
        xanchor="right"
    )
    return fig


# Configuração padrão para exportação de imagens em alta resolução (ideal para PPT)
PLOTLY_CONFIG = {
    "displaylogo": False,
    "toImageButtonOptions": {
        "format": "png",
        "filename": "agrobasis_milho_grafico",
        "scale": 5
    },
    "modeBarButtonsToRemove": ["lasso2d", "select2d"]
}


# ============================================================
# APP
# ============================================================

df = carregar_dados()

st.title("🌽 USDA Milho")
st.caption("USDA PSD | Milho | Produção, consumo, exportações, importações, estoques, estoque/uso, market share e ranking mundial")

produtos = sorted(df["Produto"].dropna().unique())
paises = ["Mundo"] + sorted([p for p in df["País"].dropna().unique() if p != "Mundo"])
indicadores = sorted(df["Indicador"].dropna().unique())

c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.4])

with c1:
    produto = st.selectbox(
        "Produto",
        produtos,
        index=produtos.index("Milho") if "Milho" in produtos else 0
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

# Período padrão: últimos 8 anos disponíveis.
# Isso faz o dashboard abrir limpo, com rótulos visíveis e pronto para apresentações.
if len(anos) >= 8:
    periodo_padrao = (anos[-8], anos[-1])
else:
    periodo_padrao = (anos[0], anos[-1])

with c4:
    col_periodo, col_hist = st.columns([3, 1])

    with col_periodo:
        ano_ini, ano_fim = st.select_slider(
            "Período",
            options=anos,
            value=periodo_padrao,
            key="periodo_slider"
        )

    with col_hist:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        historico_completo = st.button(
            "Todo o Histórico",
            use_container_width=True,
            help="Exibe todo o histórico disponível. Em períodos acima de 8 anos, os valores nos gráficos são ocultados para evitar sobreposição."
        )

if historico_completo:
    ano_ini, ano_fim = anos[0], anos[-1]

base = base_inicial[
    (base_inicial["Year"] >= ano_ini) &
    (base_inicial["Year"] <= ano_fim)
].copy()

# Regra para rótulos em gráficos temporais:
# até 8 anos = mostra os valores; acima disso = oculta para evitar sobreposição.
qtd_anos_selecionados = len(sorted(base["Year"].dropna().unique()))
mostrar_rotulos_periodo = qtd_anos_selecionados <= 8

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
    "🔎 Análises",
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
        fig.update_traces(line=dict(width=5, color="#15a86b"), marker=dict(size=10, line=dict(width=1.5, color="#ffffff")))
        aplicar_rotulos_linha(fig, casas=1, mostrar_rotulos=mostrar_rotulos_periodo)
        fig.update_xaxes(title_text="Ano")
        fig.update_yaxes(title_text="Valor")
        st.plotly_chart(aplicar_layout(fig, 500), use_container_width=True, config=PLOTLY_CONFIG)

    with col_b:
        st.markdown("""
        <div class="insight-box">
            <h3>Leitura rápida</h3>
            <p>Este painel mostra a trajetória do indicador selecionado e sua relação com os principais fundamentos:
            produção, consumo doméstico, consumo para ração, exportações, importações e estoques.</p>
            <p>Para análise de preço, acompanhe principalmente estoque/uso, exportação/produção,
            ritmo de consumo, participação dos EUA, Brasil, Argentina e Ucrânia nas exportações globais.</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Comparação internacional")

    padrao = [p for p in ["Mundo", "Estados Unidos", "China", "Brasil", "Argentina", "Ucrânia"] if p in paises]

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
    aplicar_rotulos_linha(fig_comp, casas=1, mostrar_rotulos=mostrar_rotulos_periodo)
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
    aplicar_rotulos_linha(fig_bal, casas=1, mostrar_rotulos=mostrar_rotulos_periodo)
    st.plotly_chart(aplicar_layout(fig_bal, 560), use_container_width=True, config=PLOTLY_CONFIG)

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
            fig_su.update_traces(marker_color="#c2730f")
            aplicar_rotulos_barra(fig_su, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
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
            fig_gap.update_traces(marker_color="#0891b2")
            aplicar_rotulos_barra(fig_gap, casas=1, mostrar_rotulos=mostrar_rotulos_periodo)
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
        fig_ms.update_traces(marker_color="#15a86b")
        aplicar_rotulos_barra(fig_ms, casas=1, percentual=True, orientacao="h")
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
    fig_rank.update_traces(marker_color="#15a86b")
    aplicar_rotulos_barra(fig_rank, casas=1, orientacao="h")
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
            fig.update_traces(line=dict(width=5, color="#c2730f"), marker=dict(size=10, line=dict(width=1.5, color="#ffffff")))
            aplicar_rotulos_linha(fig, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
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
            fig.update_traces(line=dict(width=5, color="#dc2626"), marker=dict(size=10, line=dict(width=1.5, color="#ffffff")))
            aplicar_rotulos_linha(fig, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
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
            fig.update_traces(line=dict(width=5, color="#15a86b"), marker=dict(size=10, line=dict(width=1.5, color="#ffffff")))
            aplicar_rotulos_linha(fig, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
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
            fig.update_traces(line=dict(width=5, color="#0891b2"), marker=dict(size=10, line=dict(width=1.5, color="#ffffff")))
            aplicar_rotulos_linha(fig, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
            st.plotly_chart(aplicar_layout(fig, 440), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[5]:
    st.subheader("Análises Complementares")

    st.markdown("""
    <div class="insight-box" style="margin-bottom:18px;">
        <h3>O que olhar aqui</h3>
        <p>Três leituras adicionais sobre o indicador selecionado: o ritmo de variação ano a ano,
        quais países mais cresceram (ou recuaram) no período e como a evolução se compara entre os
        principais players ao mesmo tempo — útil para identificar mudanças estruturais de mercado.</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- 1) Variação ano a ano (YoY) do indicador selecionado ----
    yoy_base = base[base["Indicador"] == indicador].sort_values("Year").copy()
    yoy_base["Variação YoY (%)"] = yoy_base["Value"].pct_change() * 100

    fig_yoy = px.bar(
        yoy_base.dropna(subset=["Variação YoY (%)"]),
        x="Year",
        y="Variação YoY (%)",
        title=f"Variação Ano a Ano — {indicador} | {produto} | {pais}",
        color="Variação YoY (%)",
        color_continuous_scale=["#dc2626", "#f1f5f9", "#15a86b"],
        color_continuous_midpoint=0
    )
    aplicar_rotulos_barra(fig_yoy, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
    fig_yoy.update_xaxes(title_text="Ano")
    fig_yoy.update_layout(coloraxis_showscale=False)
    st.plotly_chart(aplicar_layout(fig_yoy, 420), use_container_width=True, config=PLOTLY_CONFIG)

    col_e, col_f = st.columns(2)

    # ---- 2) Ranking de crescimento (CAGR) por país no período ----
    with col_e:
        cagr_rows = []
        base_periodo = df[
            (df["Produto"] == produto) &
            (df["Indicador"] == indicador) &
            (df["País"] != "Mundo") &
            (df["Year"] >= ano_ini) &
            (df["Year"] <= ano_fim)
        ]

        for pais_i, grupo in base_periodo.groupby("País"):
            g = grupo.sort_values("Year")
            if len(g) < 2:
                continue
            ini_v = g["Value"].iloc[0]
            fim_v = g["Value"].iloc[-1]
            n_anos = g["Year"].iloc[-1] - g["Year"].iloc[0]
            if ini_v and ini_v > 0 and n_anos > 0 and fim_v >= 0:
                taxa = ((fim_v / ini_v) ** (1 / n_anos) - 1) * 100
                cagr_rows.append({"País": pais_i, "CAGR (% a.a.)": taxa, "Valor Final": fim_v})

        cagr_df = pd.DataFrame(cagr_rows)

        if not cagr_df.empty:
            cagr_df = cagr_df[cagr_df["Valor Final"] > cagr_df["Valor Final"].quantile(0.3)]
            top_cresce = cagr_df.sort_values("CAGR (% a.a.)", ascending=False).head(8)
            top_cai = cagr_df.sort_values("CAGR (% a.a.)", ascending=True).head(8)
            ranking_cagr = pd.concat([top_cresce, top_cai]).drop_duplicates(subset="País")
            ranking_cagr = ranking_cagr.sort_values("CAGR (% a.a.)")

            fig_cagr = px.bar(
                ranking_cagr,
                x="CAGR (% a.a.)",
                y="País",
                orientation="h",
                title=f"Maiores Altas e Quedas (CAGR) — {indicador}",
                color="CAGR (% a.a.)",
                color_continuous_scale=["#dc2626", "#f1f5f9", "#15a86b"],
                color_continuous_midpoint=0
            )
            aplicar_rotulos_barra(fig_cagr, casas=1, percentual=True, orientacao="h")
            fig_cagr.update_layout(coloraxis_showscale=False)
            st.plotly_chart(aplicar_layout(fig_cagr, 460), use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("Sem dados suficientes para calcular o CAGR por país no período selecionado.")

    # ---- 3) Heatmap comparativo entre os principais países ----
    with col_f:
        top_paises = (
            df[(df["Produto"] == produto) & (df["Indicador"] == indicador) &
               (df["País"] != "Mundo") & (df["Year"] == ano_fim)]
            .sort_values("Value", ascending=False)
            .head(10)["País"].tolist()
        )

        heat = df[
            (df["Produto"] == produto) &
            (df["Indicador"] == indicador) &
            (df["País"].isin(top_paises)) &
            (df["Year"] >= ano_ini) &
            (df["Year"] <= ano_fim)
        ]

        heat_pivot = heat.pivot_table(index="País", columns="Year", values="Value", aggfunc="sum")
        heat_pivot = heat_pivot.reindex(top_paises)

        if not heat_pivot.empty:
            fig_heat = px.imshow(
                heat_pivot,
                aspect="auto",
                text_auto=".0f",
                color_continuous_scale="YlOrBr",
                title=f"Mapa de Calor — Top 10 Países | {indicador}"
            )
            fig_heat.update_xaxes(title_text="Ano")
            fig_heat.update_yaxes(title_text="")
            st.plotly_chart(aplicar_layout(fig_heat, 460), use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("Sem dados suficientes para montar o mapa de calor.")

    # ---- 4) Concentração de mercado (participação acumulada dos líderes) ----
    conc = df[
        (df["Produto"] == produto) &
        (df["Indicador"] == indicador) &
        (df["País"] != "Mundo") &
        (df["Year"] == ano_fim)
    ].copy()
    conc = conc[conc["Value"] > 0].sort_values("Value", ascending=False)

    if not conc.empty:
        total_conc = conc["Value"].sum()
        conc["Share (%)"] = conc["Value"] / total_conc * 100
        conc["Acumulado (%)"] = conc["Share (%)"].cumsum()
        conc_top10 = conc.head(10).copy()
        conc_top10["Posição"] = range(1, len(conc_top10) + 1)

        fig_conc = px.bar(
            conc_top10,
            x="País",
            y="Share (%)",
            title=f"Concentração de Mercado — Top 10 | {indicador} | {ano_fim}",
            text=conc_top10["Acumulado (%)"].round(1).astype(str) + "%"
        )
        fig_conc.update_traces(marker_color="#c2730f", textposition="outside", textfont=dict(size=12, color="#334155"), cliponaxis=False)
        fig_conc.add_scatter(
            x=conc_top10["País"],
            y=conc_top10["Acumulado (%)"],
            mode="lines+markers+text",
            text=conc_top10["Acumulado (%)"].round(1).astype(str) + "%",
            textposition="top center",
            name="Participação acumulada (%)",
            line=dict(color="#0b3d63", width=3),
            yaxis="y2"
        )
        fig_conc.update_layout(
            yaxis2=dict(overlaying="y", side="right", title="Acumulado (%)", range=[0, 105], showgrid=False)
        )
        st.plotly_chart(aplicar_layout(fig_conc, 460), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[6]:
    st.subheader("Base filtrada")

    st.dataframe(
        base[["Produto", "País", "Year", "Indicador", "Unit", "Value"]],
        use_container_width=True
    )

    csv = base.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Baixar base filtrada",
        csv,
        file_name=f"agrobasis_milho_{produto}_{pais}.csv",
        mime="text/csv"
    )