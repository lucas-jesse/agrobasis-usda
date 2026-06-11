import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="AgroBasis PRO | Complexo Soja", layout="wide")

PASTA = r"C:\Users\cotrirosa\Desktop\Lucas\Milho"
ARQUIVO = os.path.join(PASTA, "psd_oilseeds.csv")

if not os.path.exists(ARQUIVO):
    st.error("Arquivo 'psd_oilseeds.csv' não encontrado.")
    st.stop()

st.markdown("""
<style>
.stApp {
    background: #0f172a;
    color: #e5e7eb;
}
.block-container {
    padding-top: 1.3rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: #f8fafc;
}
[data-testid="stMetricValue"] {
    color: #f8fafc;
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
    opacity: 0.82;
    text-transform: uppercase;
    letter-spacing: .05em;
}
.card-value {
    font-size: 27px;
    font-weight: 800;
    margin-top: 6px;
}
.card-delta {
    font-size: 12px;
    opacity: 0.88;
    margin-top: 6px;
}
.insight-box {
    background: #111827;
    border: 1px solid #334155;
    padding: 18px;
    border-radius: 18px;
    color: #e5e7eb;
}
.small-muted {
    color: #94a3b8;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
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


df = carregar_dados()

st.title("🌎 AgroBasis PRO — Complexo Soja Global")
st.caption("USDA PSD | Soja em grão, farelo e óleo | Produção, consumo, crush, exportações, estoques, estoque/uso, market share e ranking mundial")

commodities = sorted(df["Commodity"].dropna().unique())
countries = ["Mundo"] + sorted([
    c for c in df["Country"].dropna().unique()
    if c not in ["Mundo", "World"]
])
attributes = sorted(df["Attribute"].dropna().unique())

col1, col2, col3, col4 = st.columns([1.3, 1.2, 1.2, 1.4])

with col1:
    commodity = st.selectbox(
        "Produto",
        commodities,
        index=commodities.index("Oilseed, Soybean") if "Oilseed, Soybean" in commodities else 0
    )

with col2:
    country = st.selectbox("País / Região", countries, index=0)

with col3:
    atributo = st.selectbox(
        "Indicador principal",
        attributes,
        index=attributes.index("Production") if "Production" in attributes else 0
    )

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
area = pegar_valor(base, "Area Harvested")
yield_v = pegar_valor(base, "Yield")

estoque_uso = (estoque / consumo * 100) if estoque and consumo else None
export_prod = (exportacao / producao * 100) if exportacao and producao else None
import_cons = (importacao / consumo * 100) if importacao and consumo else None
cagr_principal = calcular_cagr(base, atributo)

st.subheader(f"Painel Executivo — {commodity} | {country}")

cards = [
    ("Produção", producao, "Production", "1000 MT", "card"),
    ("Consumo", consumo, "Domestic Consumption", "1000 MT", "card-blue"),
    ("Crush", crush, "Crush", "1000 MT", "card-orange"),
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
            title=f"Evolução — {atributo} | {commodity} | {country}"
        )
        fig.update_traces(line=dict(width=4, color="#22C55E"), marker=dict(size=8))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#111827",
            hovermode="x unified",
            height=470
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("""
        <div class="insight-box">
            <h3>Leitura rápida</h3>
            <p class="small-muted">
            Este painel mostra a trajetória do indicador selecionado e sua relação com os principais fundamentos:
            produção, consumo, crush, exportações e estoques.
            </p>
            <p class="small-muted">
            Para análise de preço, acompanhe principalmente: estoque/uso, ritmo de exportação, crescimento do crush
            e concentração do market share global.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Comparação internacional")

    paises_padrao = [
        p for p in ["Mundo", "Brazil", "United States", "Argentina", "China"]
        if p in countries
    ]

    paises_comp = st.multiselect(
        "Países/regiões para comparação",
        countries,
        default=paises_padrao
    )

    base_comp = df[
        (df["Commodity"] == commodity) &
        (df["Country"].isin(paises_comp)) &
        (df["Attribute"] == atributo) &
        (df["Year"] >= ano_ini) &
        (df["Year"] <= ano_fim)
    ].copy()

    fig_comp = px.line(
        base_comp,
        x="Year",
        y="Value",
        color="Country",
        markers=True,
        title=f"Comparativo Internacional — {atributo} | {commodity}"
    )
    fig_comp.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#111827",
        hovermode="x unified",
        height=500
    )
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

    fig_bal = px.line(
        balanco,
        x="Year",
        y="Value",
        color="Attribute",
        markers=True,
        title=f"Balanço USDA — {commodity} | {country}"
    )
    fig_bal.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#111827",
        hovermode="x unified",
        height=520
    )
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

            fig_su = px.bar(
                pivot,
                x="Year",
                y="Estoque/Uso (%)",
                title="Estoque/Uso"
            )
            fig_su.update_traces(marker_color="#F59E0B")
            fig_su.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0f172a",
                plot_bgcolor="#111827",
                height=420
            )
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
            fig_gap.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0f172a",
                plot_bgcolor="#111827",
                height=420
            )
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

    base_ms = base_ms.sort_values("Value", ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        fig_tree = px.treemap(
            base_ms.head(20),
            path=["Country"],
            values="Value",
            color="Market Share (%)",
            title=f"Market Share — {atributo} | {commodity} | {ano_ms}",
            color_continuous_scale="Greens"
        )
        fig_tree.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            height=520
        )
        st.plotly_chart(fig_tree, use_container_width=True)

    with col2:
        fig_bar_ms = px.bar(
            base_ms.head(15),
            x="Market Share (%)",
            y="Country",
            orientation="h",
            title="Top 15 — Participação Mundial"
        )
        fig_bar_ms.update_traces(marker_color="#22C55E")
        fig_bar_ms.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#111827",
            yaxis={"categoryorder": "total ascending"},
            height=520
        )
        st.plotly_chart(fig_bar_ms, use_container_width=True)

    st.dataframe(
        base_ms[["Country", "Value", "Market Share (%)"]].head(30),
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
    ranking = ranking.sort_values("Value", ascending=False)

    fig_rank = px.bar(
        ranking.head(20),
        x="Value",
        y="Country",
        orientation="h",
        title=f"Top 20 — {atributo} | {commodity} | {ano_rank}"
    )
    fig_rank.update_traces(marker_color="#10B981")
    fig_rank.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#111827",
        yaxis={"categoryorder": "total ascending"},
        height=560
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    crescimento = cagr_por_pais(df, commodity, atributo, ano_ini, ano_fim)

    if not crescimento.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig_cagr = px.bar(
                crescimento.head(15),
                x="CAGR (%)",
                y="Country",
                orientation="h",
                title=f"Top CAGR — {atributo} | {ano_ini} a {ano_fim}"
            )
            fig_cagr.update_traces(marker_color="#F59E0B")
            fig_cagr.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0f172a",
                plot_bgcolor="#111827",
                yaxis={"categoryorder": "total ascending"},
                height=500
            )
            st.plotly_chart(fig_cagr, use_container_width=True)

        with col2:
            abs_growth = crescimento.sort_values("Variação Absoluta", ascending=False).head(15)

            fig_abs = px.bar(
                abs_growth,
                x="Variação Absoluta",
                y="Country",
                orientation="h",
                title="Maiores aumentos absolutos"
            )
            fig_abs.update_traces(marker_color="#38BDF8")
            fig_abs.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0f172a",
                plot_bgcolor="#111827",
                yaxis={"categoryorder": "total ascending"},
                height=500
            )
            st.plotly_chart(fig_abs, use_container_width=True)

        st.dataframe(crescimento.head(40), use_container_width=True)
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
            fig_ep.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0f172a",
                plot_bgcolor="#111827",
                height=440
            )
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
            fig_ic.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0f172a",
                plot_bgcolor="#111827",
                height=440
            )
            st.plotly_chart(fig_ic, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <h3>Como usar em análise de mercado</h3>
        <p class="small-muted">
        • Estoque/Uso baixo tende a indicar menor margem de segurança no balanço.<br>
        • Exportação/Produção mostra dependência do mercado externo.<br>
        • Importação/Consumo mostra vulnerabilidade de abastecimento.<br>
        • Crescimento do crush indica mudança estrutural na demanda industrial.<br>
        • Market share mostra concentração geopolítica da oferta e do comércio.
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab6:
    st.subheader("Base filtrada")

    st.dataframe(base, use_container_width=True)

    csv = base.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Baixar base filtrada",
        csv,
        file_name=f"agrobasis_usda_complexo_soja_{commodity}_{country}.csv",
        mime="text/csv"
    )