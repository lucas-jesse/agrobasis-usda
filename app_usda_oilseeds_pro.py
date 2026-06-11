import os
import pandas as pd
import streamlit as st
import plotly.express as px

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(page_title="USDA Complexo Soja", layout="wide")

ARQUIVO = "psd_oilseeds.csv"

if not os.path.exists(ARQUIVO):
    st.error("Arquivo 'psd_oilseeds.csv' não encontrado.")
    st.stop()

# ============================================================
# DICIONÁRIOS
# ============================================================

# IMPORTANTE:
# Para evitar distorção no "Mundo", o dashboard usa apenas as séries principais.
# As séries "(Local)" são excluídas porque podem duplicar ou distorcer a soma global.
PRODUTOS_VALIDOS = {
    "Oilseed, Soybean": "Soja em Grão",
    "Meal, Soybean": "Farelo de Soja",
    "Oil, Soybean": "Óleo de Soja",
}

TRAD_ATTR = {
    "Production": "Produção",
    "Domestic Consumption": "Consumo Doméstico",
    "Crush": "Esmagamento",
    "Exports": "Exportações",
    "Imports": "Importações",
    "Ending Stocks": "Estoque Final",
    "Beginning Stocks": "Estoque Inicial",
    "Total Supply": "Oferta Total",
    "Area Harvested": "Área Colhida",
    "Yield": "Produtividade",
    "Food Use Dom. Cons.": "Consumo Alimentar",
    "Feed Waste Dom. Cons.": "Consumo Ração/Perdas",
    "Industrial Dom. Cons.": "Consumo Industrial",
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
    "Paraguay": "Paraguai",
    "India": "Índia",
    "European Union": "União Europeia",
    "Canada": "Canadá",
    "Mexico": "México",
    "Japan": "Japão",
    "Russia": "Rússia",
    "Ukraine": "Ucrânia",
    "Indonesia": "Indonésia",
    "Thailand": "Tailândia",
    "Vietnam": "Vietnã",
    "Turkey": "Turquia",
    "Egypt": "Egito",
    "Iran": "Irã",
    "South Korea": "Coreia do Sul",
    "Taiwan": "Taiwan",
    "Bangladesh": "Bangladesh",
    "Pakistan": "Paquistão",
    "Bolivia": "Bolívia",
    "Uruguay": "Uruguai",
}


# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>
.stApp {
    background:#0f172a;
    color:#ffffff;
}

.block-container {
    padding-top:1rem;
    padding-bottom:2rem;
}

h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
label {
    color:#ffffff !important;
}

.stCaptionContainer, .stCaptionContainer p {
    color:#cbd5e1 !important;
}

.stSelectbox label,
.stSlider label,
.stMultiSelect label {
    color:#ffffff !important;
    font-weight:700;
}

/* Caixas claras com texto escuro */
[data-baseweb="select"] {
    background:#f8fafc !important;
    border-radius:10px;
}

[data-baseweb="select"] div,
[data-baseweb="select"] span {
    color:#111827 !important;
}

/* Dropdown aberto */
[role="listbox"] div,
[role="option"],
[role="option"] div,
[role="option"] span {
    color:#111827 !important;
    background:#ffffff !important;
}

.card {
    padding:20px;
    border-radius:20px;
    color:white;
    box-shadow:0px 6px 22px rgba(0,0,0,0.35);
    min-height:125px;
}

.card-green { background:linear-gradient(135deg,#064E3B,#16A34A); }
.card-blue { background:linear-gradient(135deg,#1E3A8A,#2563EB); }
.card-orange { background:linear-gradient(135deg,#92400E,#D97706); }
.card-dark { background:linear-gradient(135deg,#111827,#334155); }

.card-title {
    color:white !important;
    font-size:13px;
    opacity:.95;
    text-transform:uppercase;
    letter-spacing:.05em;
    font-weight:800;
}

.card-value {
    color:white !important;
    font-size:29px;
    font-weight:900;
    margin-top:6px;
}

.card-delta {
    color:white !important;
    font-size:12px;
    opacity:.95;
    margin-top:6px;
}

.insight-box {
    background:#111827;
    border:1px solid #334155;
    padding:20px;
    border-radius:18px;
    color:white;
}

.insight-box h3 {
    color:white !important;
}

.insight-box p {
    color:#e5e7eb !important;
    line-height:1.65;
}

div[data-testid="stDataFrame"] {
    color:#111827 !important;
}
</style>
""", unsafe_allow_html=True)


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

    # Usa SOMENTE as commodities principais, sem "(Local)"
    df = df[df["Commodity"].isin(PRODUTOS_VALIDOS.keys())].copy()

    if df.empty:
        st.error("Nenhum dado do complexo soja foi encontrado no arquivo.")
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
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#111827",
        font=dict(color="#ffffff", size=14),
        title_font=dict(color="#ffffff", size=20),
        xaxis=dict(color="#ffffff", gridcolor="rgba(255,255,255,0.25)"),
        yaxis=dict(color="#ffffff", gridcolor="rgba(255,255,255,0.25)"),
        legend=dict(font=dict(color="#ffffff")),
        height=h
    )
    return fig


# ============================================================
# APP
# ============================================================

df = carregar_dados()

st.title("🌎 USDA Complexo Soja")
st.caption("USDA PSD | Soja em grão, farelo e óleo | Produção, consumo, esmagamento, exportações, estoques, estoque/uso, market share e ranking mundial")

produtos = sorted(df["Produto"].dropna().unique())
paises = ["Mundo"] + sorted([p for p in df["País"].dropna().unique() if p != "Mundo"])
indicadores = sorted(df["Indicador"].dropna().unique())

c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.4])

with c1:
    produto = st.selectbox(
        "Produto",
        produtos,
        index=produtos.index("Soja em Grão") if "Soja em Grão" in produtos else 0
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
crush = valor(base, "Crush")
exportacao = valor(base, "Exports")
estoque = valor(base, "Ending Stocks")

estoque_uso = (estoque / consumo * 100) if estoque and consumo else None
export_prod = (exportacao / producao * 100) if exportacao and producao else None
cagr_ind = cagr(base, attr_indicador)

st.subheader(f"Painel Executivo — {produto} | {pais}")

cards = [
    ("Produção", producao, "Production", "1000 MT", "card-green"),
    ("Consumo Doméstico", consumo, "Domestic Consumption", "1000 MT", "card-blue"),
    ("Esmagamento", crush, "Crush", "1000 MT", "card-orange"),
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
        fig.update_traces(line=dict(width=4, color="#22C55E"), marker=dict(size=8))
        fig.update_xaxes(title_text="Ano")
        fig.update_yaxes(title_text="Valor")
        st.plotly_chart(aplicar_layout(fig, 500), use_container_width=True)

    with col_b:
        st.markdown("""
        <div class="insight-box">
            <h3>Leitura rápida</h3>
            <p>Este painel mostra a trajetória do indicador selecionado e sua relação com os principais fundamentos:
            produção, consumo, esmagamento, exportações e estoques.</p>
            <p>Para análise de preço, acompanhe principalmente estoque/uso, ritmo de exportação,
            crescimento do esmagamento e concentração do market share global.</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Comparação internacional")

    padrao = [p for p in ["Mundo", "Brasil", "Estados Unidos", "Argentina", "China"] if p in paises]

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
    fig_comp.update_xaxes(title_text="Ano")
    fig_comp.update_yaxes(title_text="Valor")
    st.plotly_chart(aplicar_layout(fig_comp, 520), use_container_width=True)

with tabs[1]:
    st.subheader("Balanço de Oferta e Demanda")

    attrs = [
        "Beginning Stocks",
        "Production",
        "Imports",
        "Total Supply",
        "Crush",
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
    st.plotly_chart(aplicar_layout(fig_bal, 540), use_container_width=True)

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
            fig_su.update_traces(marker_color="#F59E0B")
            st.plotly_chart(aplicar_layout(fig_su, 420), use_container_width=True)

    with col2:
        if {"Production", "Domestic Consumption"}.issubset(pivot.columns):
            pivot["Produção - Consumo"] = pivot["Production"] - pivot["Domestic Consumption"]
            fig_gap = px.bar(
                pivot,
                x="Year",
                y="Produção - Consumo",
                title="Superávit/Déficit: Produção - Consumo"
            )
            fig_gap.update_traces(marker_color="#38BDF8")
            st.plotly_chart(aplicar_layout(fig_gap, 420), use_container_width=True)

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
        st.plotly_chart(aplicar_layout(fig_tree, 520), use_container_width=True)

    with c2:
        fig_ms = px.bar(
            ms.head(15),
            x="Market Share (%)",
            y="País",
            orientation="h",
            title="Top 15 — Participação Mundial"
        )
        fig_ms.update_traces(marker_color="#22C55E")
        fig_ms.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(aplicar_layout(fig_ms, 520), use_container_width=True)

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
    fig_rank.update_traces(marker_color="#10B981")
    fig_rank.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(aplicar_layout(fig_rank, 560), use_container_width=True)

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
            fig.update_traces(line=dict(width=4, color="#F97316"))
            st.plotly_chart(aplicar_layout(fig, 440), use_container_width=True)

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
            fig.update_traces(line=dict(width=4, color="#EF4444"))
            st.plotly_chart(aplicar_layout(fig, 440), use_container_width=True)

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
        file_name=f"agrobasis_{produto}_{pais}.csv",
        mime="text/csv"
    )

