import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="AgroBasis PRO | Complexo Soja", layout="wide")

ARQUIVO = "psd_oilseeds.csv"

if not os.path.exists(ARQUIVO):
    st.error("Arquivo 'psd_oilseeds.csv' não encontrado.")
    st.stop()

# =========================
# TRADUÇÕES
# =========================

trad_produtos = {
    "Oilseed, Soybean": "Soja em Grão",
    "Oilseed, Soybean (Local)": "Soja em Grão",
    "Meal, Soybean": "Farelo de Soja",
    "Meal, Soybean (Local)": "Farelo de Soja",
    "Oil, Soybean": "Óleo de Soja",
    "Oil, Soybean (Local)": "Óleo de Soja",
}

trad_indicadores = {
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
}

trad_paises = {
    "World": "Mundo",
    "Brazil": "Brasil",
    "Argentina": "Argentina",
    "United States": "Estados Unidos",
    "China": "China",
    "Paraguay": "Paraguai",
    "India": "Índia",
    "European Union": "União Europeia",
    "Mexico": "México",
    "Canada": "Canadá",
    "Russia": "Rússia",
    "Ukraine": "Ucrânia",
    "Japan": "Japão",
    "Indonesia": "Indonésia",
    "Thailand": "Tailândia",
    "Vietnam": "Vietnã",
}

def t_prod(x):
    return trad_produtos.get(x, x)

def t_attr(x):
    return trad_indicadores.get(x, x)

def t_pais(x):
    return trad_paises.get(x, x)

def original_prod(nome_pt):
    for k, v in trad_produtos.items():
        if v == nome_pt:
            return k
    return nome_pt

def original_attr(nome_pt):
    for k, v in trad_indicadores.items():
        if v == nome_pt:
            return k
    return nome_pt

def original_pais(nome_pt):
    for k, v in trad_paises.items():
        if v == nome_pt:
            return k
    return nome_pt


# =========================
# ESTILO
# =========================

st.markdown("""
<style>
.stApp {
    background: #0f172a;
    color: #ffffff;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #ffffff !important;
}

[data-testid="stMarkdownContainer"] {
    color: #ffffff !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

.stSelectbox label, .stSlider label, .stMultiSelect label {
    color: #ffffff !important;
    font-weight: 600;
}

.card {
    background: linear-gradient(135deg, #064E3B, #16A34A);
    padding: 20px;
    border-radius: 20px;
    color: white;
    box-shadow: 0px 6px 22px rgba(0,0,0,0.35);
    min-height: 125px;
}

.card-blue {
    background: linear-gradient(135deg, #1E3A8A, #2563EB);
}

.card-orange {
    background: linear-gradient(135deg, #92400E, #D97706);
}

.card-dark {
    background: linear-gradient(135deg, #111827, #334155);
}

.card-title {
    font-size: 13px;
    opacity: 0.95;
    text-transform: uppercase;
    letter-spacing: .05em;
    font-weight: 700;
}

.card-value {
    font-size: 29px;
    font-weight: 800;
    margin-top: 6px;
}

.card-delta {
    font-size: 12px;
    opacity: 0.95;
    margin-top: 6px;
}

.insight-box {
    background: #111827;
    border: 1px solid #334155;
    padding: 18px;
    border-radius: 18px;
    color: #ffffff;
}

.small-muted {
    color: #e5e7eb !important;
    font-size: 14px;
    line-height: 1.65;
}
</style>
""", unsafe_allow_html=True)


# =========================
# FUNÇÕES
# =========================

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

    df = df[["Commodity", "Country", "Year", "Attribute", "Unit", "Value"]].copy()

    df["Commodity"] = df["Commodity"].astype(str).str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()
    df["Attribute"] = df["Attribute"].astype(str).str.strip()
    df["Unit"] = df["Unit"].astype(str).str.strip()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    df = df.dropna(subset=["Year", "Value"])
    df["Year"] = df["Year"].astype(int)

    produtos_soja = [
        "Oilseed, Soybean",
        "Oilseed, Soybean (Local)",
        "Meal, Soybean",
        "Meal, Soybean (Local)",
        "Oil, Soybean",
        "Oil, Soybean (Local)"
    ]

    df = df[df["Commodity"].isin(produtos_soja)].copy()

    if df.empty:
        st.error("Nenhum produto do complexo soja foi encontrado na base.")
        st.stop()

    if "World" in df["Country"].unique():
        mundo = df[df["Country"] == "World"].copy()
        mundo["Country"] = "Mundo"
    else:
        mundo = (
            df.groupby(["Commodity", "Year", "Attribute", "Unit"], as_index=False)["Value"]
            .sum()
        )
        mundo["Country"] = "Mundo"

    df = pd.concat([df, mundo], ignore_index=True)

    return df


def fmt(valor, casas=1):
    if valor is None or pd.isna(valor):
        return "-"
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pegar_valor(base, atributo):
    serie = base[base["Attribute"] == atributo].sort_values("Year")
    if serie.empty:
        return None
    return serie["Value"].iloc[-1]


def variacao(base, atributo):
    serie = base[base["Attribute"] == atributo].sort_values("Year")

    if len(serie) < 2:
        return "Sem comparação"

    atual = serie["Value"].iloc[-1]
    anterior = serie["Value"].iloc[-2]

    if anterior == 0 or pd.isna(anterior):
        return "Sem comparação"

    var = ((atual / anterior) - 1) * 100
    sinal = "+" if var >= 0 else ""

    return f"{sinal}{var:.1f}% vs ano anterior".replace(".", ",")


def calcular_cagr(base, atributo):
    serie = base[base["Attribute"] == atributo].sort_values("Year")

    if len(serie) < 2:
        return None

    inicial = serie["Value"].iloc[0]
    final = serie["Value"].iloc[-1]
    anos = serie["Year"].iloc[-1] - serie["Year"].iloc[0]

    if inicial <= 0 or anos <= 0:
        return None

    return ((final / inicial) ** (1 / anos) - 1) * 100


def cagr_por_pais(df, commodity, atributo, ano_ini, ano_fim):
    base = df[
        (df["Commodity"] == commodity) &
        (df["Attribute"] == atributo) &
        (df["Year"].isin([ano_ini, ano_fim])) &
        (~df["Country"].isin(["Mundo", "World"]))
    ].copy()

    pivot = base.pivot_table(
        index="Country",
        columns="Year",
        values="Value",
        aggfunc="sum"
    ).reset_index()

    if ano_ini not in pivot.columns or ano_fim not in pivot.columns:
        return pd.DataFrame()

    anos = ano_fim - ano_ini
    if anos <= 0:
        return pd.DataFrame()

    pivot = pivot[(pivot[ano_ini] > 0) & (pivot[ano_fim] > 0)]
    pivot["CAGR (%)"] = ((pivot[ano_fim] / pivot[ano_ini]) ** (1 / anos) - 1) * 100
    pivot["Variação Absoluta"] = pivot[ano_fim] - pivot[ano_ini]

    return pivot.sort_values("CAGR (%)", ascending=False)


def aplicar_layout(fig, altura=500):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#111827",
        font=dict(color="#ffffff", size=14),
        title_font=dict(color="#ffffff", size=20),
        xaxis=dict(color="#ffffff", gridcolor="rgba(255,255,255,0.25)"),
        yaxis=dict(color="#ffffff", gridcolor="rgba(255,255,255,0.25)"),
        legend=dict(font=dict(color="#ffffff")),
        hovermode="x unified",
        height=altura
    )
    return fig


# =========================
# APP
# =========================

df = carregar_dados()

st.title("🌎 AgroBasis PRO — Complexo Soja Global")
st.caption("USDA PSD | Soja em grão, farelo e óleo | Produção, consumo, esmagamento, exportações, estoques, estoque/uso, market share e ranking mundial")

commodities_orig = sorted(df["Commodity"].dropna().unique())
commodities_pt = sorted(list(set([t_prod(c) for c in commodities_orig])))

countries_orig = ["Mundo"] + sorted([
    c for c in df["Country"].dropna().unique()
    if c not in ["Mundo", "World"]
])
countries_pt = [t_pais(c) for c in countries_orig]

attributes_orig = sorted(df["Attribute"].dropna().unique())
attributes_pt = sorted(list(set([t_attr(a) for a in attributes_orig])))

col1, col2, col3, col4 = st.columns([1.3, 1.2, 1.2, 1.4])

with col1:
    commodity_pt = st.selectbox(
        "Produto",
        commodities_pt,
        index=commodities_pt.index("Soja em Grão") if "Soja em Grão" in commodities_pt else 0
    )

with col2:
    country_pt = st.selectbox(
        "País / Região",
        countries_pt,
        index=countries_pt.index("Mundo") if "Mundo" in countries_pt else 0
    )

with col3:
    atributo_pt = st.selectbox(
        "Indicador principal",
        attributes_pt,
        index=attributes_pt.index("Produção") if "Produção" in attributes_pt else 0
    )

commodity = original_prod(commodity_pt)
country = original_pais(country_pt)
atributo = original_attr(atributo_pt)

df_base = df[
    (df["Commodity"] == commodity) &
    (df["Country"] == country)
].copy()

anos = sorted(df_base["Year"].dropna().unique())

if not anos:
    st.warning("Não há dados disponíveis para essa combinação.")
    st.stop()

with col4:
    ano_ini, ano_fim = st.select_slider(
        "Período",
        options=anos,
        value=(anos[0], anos[-1])
    )

base = df_base[
    (df_base["Year"] >= ano_ini) &
    (df_base["Year"] <= ano_fim)
].copy()

producao = pegar_valor(base, "Production")
consumo = pegar_valor(base, "Domestic Consumption")
crush = pegar_valor(base, "Crush")
exportacao = pegar_valor(base, "Exports")
importacao = pegar_valor(base, "Imports")
estoque = pegar_valor(base, "Ending Stocks")

estoque_uso = (estoque / consumo * 100) if estoque and consumo else None
export_prod = (exportacao / producao * 100) if exportacao and producao else None
cagr_principal = calcular_cagr(base, atributo)

st.subheader(f"Painel Executivo — {commodity_pt} | {country_pt}")

cards = [
    ("Produção", producao, "Production", "1000 MT", "card"),
    ("Consumo Doméstico", consumo, "Domestic Consumption", "1000 MT", "card-blue"),
    ("Esmagamento", crush, "Crush", "1000 MT", "card-orange"),
    ("Exportações", exportacao, "Exports", "1000 MT", "card"),
    ("Estoque Final", estoque, "Ending Stocks", "1000 MT", "card-dark"),
    ("Estoque/Uso", estoque_uso, None, "%", "card-orange"),
    ("Exportação/Produção", export_prod, None, "%", "card-blue"),
    ("CAGR Indicador", cagr_principal, None, "% a.a.", "card-dark")
]

cols = st.columns(4)

for i, (titulo, valor, attr, unidade, classe) in enumerate(cards):
    with cols[i % 4]:
        delta = variacao(base, attr) if attr else "Período selecionado"
        st.markdown(f"""
        <div class="card {classe}">
            <div class="card-title">{titulo}</div>
            <div class="card-value">{fmt(valor, 2 if unidade != "1000 MT" else 1)}</div>
            <div class="card-delta">{unidade} | {delta}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Visão Executiva",
    "⚖️ Balanço",
    "🌍 Market Share",
    "🏆 Rankings",
    "📊 Diagnóstico",
    "📋 Dados"
])

with tab1:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        base_attr = base[base["Attribute"] == atributo].sort_values("Year")

        fig = px.line(
            base_attr,
            x="Year",
            y="Value",
            markers=True,
            title=f"Evolução — {atributo_pt} | {commodity_pt} | {country_pt}"
        )
        fig.update_traces(line=dict(width=4, color="#22C55E"), marker=dict(size=8))
        fig.update_xaxes(title_text="Ano")
        fig.update_yaxes(title_text="Valor")
        fig = aplicar_layout(fig, 470)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("""
        <div class="insight-box">
            <h3>Leitura rápida</h3>
            <p class="small-muted">
            Este painel mostra a trajetória do indicador selecionado e sua relação com os principais fundamentos:
            produção, consumo, esmagamento, exportações e estoques.
            </p>
            <p class="small-muted">
            Para análise de preço, acompanhe principalmente: estoque/uso, ritmo de exportação,
            crescimento do esmagamento e concentração do market share global.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Comparação internacional")

    paises_padrao_pt = [
        p for p in ["Mundo", "Brasil", "Estados Unidos", "Argentina", "China"]
        if p in countries_pt
    ]

    paises_comp_pt = st.multiselect(
        "Países/regiões para comparação",
        countries_pt,
        default=paises_padrao_pt
    )

    paises_comp = [original_pais(p) for p in paises_comp_pt]

    base_comp = df[
        (df["Commodity"] == commodity) &
        (df["Country"].isin(paises_comp)) &
        (df["Attribute"] == atributo) &
        (df["Year"] >= ano_ini) &
        (df["Year"] <= ano_fim)
    ].copy()

    base_comp["País"] = base_comp["Country"].apply(t_pais)

    fig_comp = px.line(
        base_comp,
        x="Year",
        y="Value",
        color="País",
        markers=True,
        title=f"Comparativo Internacional — {atributo_pt} | {commodity_pt}"
    )
    fig_comp.update_traces(line=dict(width=3))
    fig_comp.update_xaxes(title_text="Ano")
    fig_comp.update_yaxes(title_text="Valor")
    fig_comp = aplicar_layout(fig_comp, 500)
    st.plotly_chart(fig_comp, use_container_width=True)

with tab2:
    st.subheader("Balanço de Oferta e Demanda")

    attrs_balanco = [
        "Beginning Stocks",
        "Production",
        "Imports",
        "Total Supply",
        "Crush",
        "Domestic Consumption",
        "Exports",
        "Ending Stocks"
    ]

    balanco = base[base["Attribute"].isin(attrs_balanco)].copy()
    balanco["Indicador"] = balanco["Attribute"].apply(t_attr)

    fig_bal = px.line(
        balanco,
        x="Year",
        y="Value",
        color="Indicador",
        markers=True,
        title=f"Balanço USDA — {commodity_pt} | {country_pt}"
    )
    fig_bal.update_xaxes(title_text="Ano")
    fig_bal.update_yaxes(title_text="Valor")
    fig_bal = aplicar_layout(fig_bal, 520)
    st.plotly_chart(fig_bal, use_container_width=True)

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
            fig_su.update_xaxes(title_text="Ano")
            fig_su.update_yaxes(title_text="%")
            fig_su = aplicar_layout(fig_su, 420)
            st.plotly_chart(fig_su, use_container_width=True)

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
            fig_gap.update_xaxes(title_text="Ano")
            fig_gap.update_yaxes(title_text="1000 MT")
            fig_gap = aplicar_layout(fig_gap, 420)
            st.plotly_chart(fig_gap, use_container_width=True)

    st.subheader("Tabela de balanço")
    st.dataframe(pivot, use_container_width=True)

with tab3:
    st.subheader("Market Share Mundial")

    ano_ms = st.selectbox(
        "Ano para análise de participação",
        sorted(df["Year"].dropna().unique(), reverse=True),
        index=0
    )

    base_ms = df[
        (df["Commodity"] == commodity) &
        (df["Attribute"] == atributo) &
        (df["Year"] == ano_ms) &
        (~df["Country"].isin(["Mundo", "World"]))
    ].copy()

    base_ms = base_ms.dropna(subset=["Value"])
    base_ms = base_ms[base_ms["Value"] > 0]
    total = base_ms["Value"].sum()

    if total > 0:
        base_ms["Market Share (%)"] = base_ms["Value"] / total * 100

    base_ms["País"] = base_ms["Country"].apply(t_pais)
    base_ms = base_ms.sort_values("Value", ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        fig_tree = px.treemap(
            base_ms.head(20),
            path=["País"],
            values="Value",
            color="Market Share (%)",
            title=f"Market Share — {atributo_pt} | {commodity_pt} | {ano_ms}",
            color_continuous_scale="Greens"
        )
        fig_tree = aplicar_layout(fig_tree, 520)
        st.plotly_chart(fig_tree, use_container_width=True)

    with col2:
        fig_bar_ms = px.bar(
            base_ms.head(15),
            x="Market Share (%)",
            y="País",
            orientation="h",
            title="Top 15 — Participação Mundial"
        )
        fig_bar_ms.update_traces(marker_color="#22C55E")
        fig_bar_ms.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_bar_ms.update_xaxes(title_text="%")
        fig_bar_ms.update_yaxes(title_text="País")
        fig_bar_ms = aplicar_layout(fig_bar_ms, 520)
        st.plotly_chart(fig_bar_ms, use_container_width=True)

    st.dataframe(
        base_ms[["País", "Value", "Market Share (%)"]].head(30),
        use_container_width=True
    )

with tab4:
    st.subheader("Ranking e crescimento estrutural")

    ano_rank = st.selectbox(
        "Ano do ranking",
        sorted(df["Year"].dropna().unique(), reverse=True),
        index=0,
        key="rank_ano"
    )

    ranking = df[
        (df["Commodity"] == commodity) &
        (df["Attribute"] == atributo) &
        (df["Year"] == ano_rank) &
        (~df["Country"].isin(["Mundo", "World"]))
    ].copy()

    ranking = ranking.dropna(subset=["Value"])
    ranking["País"] = ranking["Country"].apply(t_pais)
    ranking = ranking.sort_values("Value", ascending=False)

    fig_rank = px.bar(
        ranking.head(20),
        x="Value",
        y="País",
        orientation="h",
        title=f"Top 20 — {atributo_pt} | {commodity_pt} | {ano_rank}"
    )
    fig_rank.update_traces(marker_color="#10B981")
    fig_rank.update_layout(yaxis={"categoryorder": "total ascending"})
    fig_rank.update_xaxes(title_text="Valor")
    fig_rank.update_yaxes(title_text="País")
    fig_rank = aplicar_layout(fig_rank, 560)
    st.plotly_chart(fig_rank, use_container_width=True)

    crescimento = cagr_por_pais(df, commodity, atributo, ano_ini, ano_fim)

    if not crescimento.empty:
        crescimento["País"] = crescimento["Country"].apply(t_pais)
        col1, col2 = st.columns(2)

        with col1:
            fig_cagr = px.bar(
                crescimento.head(15),
                x="CAGR (%)",
                y="País",
                orientation="h",
                title=f"Top CAGR — {atributo_pt} | {ano_ini} a {ano_fim}"
            )
            fig_cagr.update_traces(marker_color="#F59E0B")
            fig_cagr.update_layout(yaxis={"categoryorder": "total ascending"})
            fig_cagr = aplicar_layout(fig_cagr, 500)
            st.plotly_chart(fig_cagr, use_container_width=True)

        with col2:
            abs_growth = crescimento.sort_values("Variação Absoluta", ascending=False).head(15)
            fig_abs = px.bar(
                abs_growth,
                x="Variação Absoluta",
                y="País",
                orientation="h",
                title="Maiores aumentos absolutos"
            )
            fig_abs.update_traces(marker_color="#38BDF8")
            fig_abs.update_layout(yaxis={"categoryorder": "total ascending"})
            fig_abs = aplicar_layout(fig_abs, 500)
            st.plotly_chart(fig_abs, use_container_width=True)

        st.dataframe(crescimento[["País", ano_ini, ano_fim, "CAGR (%)", "Variação Absoluta"]].head(40), use_container_width=True)
    else:
        st.info("Não foi possível calcular CAGR para o período selecionado.")

with tab5:
    st.subheader("Diagnóstico fundamentalista")

    pivot_diag = base.pivot_table(
        index="Year",
        columns="Attribute",
        values="Value",
        aggfunc="sum"
    ).reset_index()

    col1, col2 = st.columns(2)

    with col1:
        if {"Exports", "Production"}.issubset(pivot_diag.columns):
            pivot_diag["Exportação/Produção (%)"] = pivot_diag["Exports"] / pivot_diag["Production"] * 100

            fig_ep = px.line(
                pivot_diag,
                x="Year",
                y="Exportação/Produção (%)",
                markers=True,
                title="Exportação / Produção"
            )
            fig_ep.update_traces(line=dict(width=4, color="#F97316"))
            fig_ep.update_xaxes(title_text="Ano")
            fig_ep.update_yaxes(title_text="%")
            fig_ep = aplicar_layout(fig_ep, 440)
            st.plotly_chart(fig_ep, use_container_width=True)

    with col2:
        if {"Imports", "Domestic Consumption"}.issubset(pivot_diag.columns):
            pivot_diag["Importação/Consumo (%)"] = pivot_diag["Imports"] / pivot_diag["Domestic Consumption"] * 100

            fig_ic = px.line(
                pivot_diag,
                x="Year",
                y="Importação/Consumo (%)",
                markers=True,
                title="Importação / Consumo"
            )
            fig_ic.update_traces(line=dict(width=4, color="#EF4444"))
            fig_ic.update_xaxes(title_text="Ano")
            fig_ic.update_yaxes(title_text="%")
            fig_ic = aplicar_layout(fig_ic, 440)
            st.plotly_chart(fig_ic, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <h3>Como usar em análise de mercado</h3>
        <p class="small-muted">
        • Estoque/Uso baixo tende a indicar menor margem de segurança no balanço.<br>
        • Exportação/Produção mostra dependência do mercado externo.<br>
        • Importação/Consumo mostra vulnerabilidade de abastecimento.<br>
        • Crescimento do esmagamento indica mudança estrutural na demanda industrial.<br>
        • Market share mostra concentração geopolítica da oferta e do comércio.
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab6:
    st.subheader("Base filtrada")

    base_view = base.copy()
    base_view["Produto"] = base_view["Commodity"].apply(t_prod)
    base_view["País"] = base_view["Country"].apply(t_pais)
    base_view["Indicador"] = base_view["Attribute"].apply(t_attr)

    st.dataframe(
        base_view[["Produto", "País", "Year", "Indicador", "Unit", "Value"]],
        use_container_width=True
    )

    csv = base_view.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Baixar base filtrada",
        csv,
        file_name=f"agrobasis_usda_complexo_soja_{commodity_pt}_{country_pt}.csv",
        mime="text/csv"
    )
