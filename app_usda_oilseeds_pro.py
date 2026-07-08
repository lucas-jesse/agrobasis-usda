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

# Atributos cuja unidade original do USDA PSD é "1000 MT" (mil toneladas).
# Área Colhida (1000 HA) e Produtividade (MT/HA, uma razão) ficam de fora
# de propósito: converter esses dois pra "milhões de toneladas" produziria
# um número tecnicamente errado.
ATRIBUTOS_VOLUME_TONELADAS = {
    "Production", "Domestic Consumption", "Crush", "Exports", "Imports",
    "Ending Stocks", "Beginning Stocks", "Total Supply",
    "Food Use Dom. Cons.", "Feed Waste Dom. Cons.", "Industrial Dom. Cons.",
    "TY Exports", "TY Imports",
}


def eh_volume_toneladas(attribute: str) -> bool:
    """True se o Attribute (nome original em inglês) for medido em 1000 MT."""
    return attribute in ATRIBUTOS_VOLUME_TONELADAS

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
# CORES OFICIAIS AGROBASIS
# ============================================================
# Constantes centralizadas — usar sempre estas em vez de hex direto,
# tanto no CSS quanto nos gráficos Plotly.
VERDE_ESCURO = "#1E4812"
VERDE_MEDIO = "#54931B"
TEXTO = "#222222"
DOURADO = "#A17149"
PRETO = "#000000"
OLIVA = "#6B7F3A"        # verde-oliva da paleta estendida — usado como acento terciário
MARROM_ESCURO = "#8A6A4F"  # marrom mais escuro da paleta estendida — usado em escalas divergentes

# ============================================================
# ESTILO
# ============================================================

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&family=Sora:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family:'Geist', Arial, sans-serif;
}}

.stApp {{
    background:#f7f8f5;
    color:{TEXTO};
}}

.block-container {{
    padding-top:1.5rem;
    padding-bottom:2rem;
    max-width:1400px;
}}

h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
label {{
    color:{TEXTO} !important;
    font-family:'Geist', Arial, sans-serif;
}}

h1 {{
    font-weight:800 !important;
    letter-spacing:-.02em;
}}

.stCaptionContainer, .stCaptionContainer p {{
    color:#6b6b6b !important;
    font-family:'Sora', Arial, sans-serif;
}}

.stSelectbox label,
.stSlider label,
.stMultiSelect label {{
    color:{TEXTO} !important;
    font-family:'Sora', Arial, sans-serif;
    font-weight:600;
    font-size:12.5px;
    text-transform:uppercase;
    letter-spacing:.05em;
}}

[data-baseweb="select"] {{
    background:#ffffff !important;
    border-radius:10px;
    border:1px solid #e5e7eb !important;
}}

[data-baseweb="select"] div,
[data-baseweb="select"] span {{
    color:{TEXTO} !important;
}}

[role="listbox"] div,
[role="option"],
[role="option"] div,
[role="option"] span {{
    color:{TEXTO} !important;
    background:#ffffff !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap:4px;
    background:#ffffff;
    padding:6px;
    border-radius:14px;
    border:1px solid #e5e7eb;
}}

.stTabs [data-baseweb="tab"] {{
    color:#6b6b6b;
    font-family:'Geist', Arial, sans-serif;
    font-weight:600;
    border-radius:10px;
    padding:8px 16px;
    transition:background .15s ease, color .15s ease;
}}

.stTabs [data-baseweb="tab"]:hover {{
    background:rgba(84,147,27,0.10);
    color:{VERDE_ESCURO};
}}

.stTabs [aria-selected="true"] {{
    background:{VERDE_ESCURO} !important;
    color:#ffffff !important;
}}

.stTabs [aria-selected="true"]:hover {{
    background:{VERDE_MEDIO} !important;
    color:#ffffff !important;
}}

.card {{
    padding:16px 18px;
    border-radius:16px;
    background:#ffffff;
    border:1px solid #e5e7eb;
    border-left:4px solid var(--accent, {VERDE_ESCURO});
    box-shadow:0px 2px 8px rgba(30,72,18,0.05);
    min-height:104px;
}}

.card-green  {{ --accent:{VERDE_ESCURO}; }}
.card-blue   {{ --accent:{OLIVA}; }}
.card-orange {{ --accent:{DOURADO}; }}
.card-dark   {{ --accent:{PRETO}; }}

.card-title {{
    color:#7a7a7a !important;
    font-family:'Sora', Arial, sans-serif;
    font-size:11px;
    text-transform:uppercase;
    letter-spacing:.06em;
    font-weight:700;
}}

.card-value {{
    color:{TEXTO} !important;
    font-family:'Geist', Arial, sans-serif;
    font-size:23px;
    font-weight:800;
    margin-top:6px;
}}

.card-delta {{
    color:#9a9a9a !important;
    font-family:'Sora', Arial, sans-serif;
    font-size:11.5px;
    margin-top:5px;
}}

.insight-box {{
    background:#ffffff;
    border:1px solid #e5e7eb;
    border-left:3px solid {DOURADO};
    padding:22px;
    border-radius:16px;
    color:{TEXTO};
    box-shadow:0px 6px 18px rgba(30,72,18,0.05);
}}

.insight-box h3 {{
    color:{VERDE_ESCURO} !important;
    font-weight:800;
}}

.insight-box p {{
    color:#4a4a4a !important;
    line-height:1.7;
}}

div[data-testid="stPlotlyChart"] {{
    background:#ffffff;
    border-radius:18px;
    padding:8px;
    border:1px solid #e5e7eb;
    box-shadow:0px 6px 18px rgba(30,72,18,0.04);
}}

div[data-testid="stDataFrame"] {{
    color:{TEXTO} !important;
    background:#ffffff;
    border-radius:14px;
}}

div[data-testid="stExpander"] {{
    background:#ffffff;
    border-radius:14px;
    border:1px solid #e5e7eb;
}}

.stButton > button,
.stDownloadButton > button {{
    background:#ffffff;
    color:{VERDE_ESCURO};
    font-family:'Geist', Arial, sans-serif;
    border:1px solid {VERDE_ESCURO};
    border-radius:10px;
    font-weight:700;
    min-height:40px;
    margin-top:25px;
    transition:background .15s ease, color .15s ease;
}}

.stButton > button:hover,
.stDownloadButton > button:hover {{
    background:{VERDE_MEDIO};
    color:#ffffff;
    border-color:{VERDE_MEDIO};
}}
</style>
""", unsafe_allow_html=True)

PALETA = [VERDE_ESCURO, VERDE_MEDIO, DOURADO, TEXTO, PRETO, OLIVA, MARROM_ESCURO]

# ============================================================
# FUNÇÕES
# ============================================================

def fmt(v, casas=1):
    if v is None or pd.isna(v):
        return "-"
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_plotly(v, casas=1, sufixo=""):
    if v is None or pd.isna(v):
        return ""
    txt = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{txt}{sufixo}"


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
        st.error("Nenhum dado do complexo soja foi encontrado no arquivo.")
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


def aplicar_rotulos_linha(fig, casas=1, percentual=False, mostrar_rotulos=True):
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
            tr.textfont = dict(size=11, color=TEXTO)
        else:
            tr.mode = "lines+markers"
            tr.text = None
            tr.texttemplate = None

    return fig


def aplicar_rotulos_barra(fig, casas=1, percentual=False, orientacao="v", mostrar_rotulos=True):
    if not mostrar_rotulos:
        fig.update_traces(text=None, texttemplate=None, cliponaxis=False)
        return fig

    sufixo = "%" if percentual else ""

    for tr in fig.data:
        valores = tr.x if orientacao == "h" else tr.y
        tr.text = [fmt_plotly(v, casas, sufixo) for v in valores]
        tr.texttemplate = "%{text}"
        tr.textposition = "outside"
        tr.textfont = dict(size=12, color=TEXTO)
        tr.cliponaxis = False

    return fig


def aplicar_layout(fig, h=500, fonte="Fonte: USDA PSD · Elaboração: AgroBasis"):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color=TEXTO, size=14, family="Geist, Arial, sans-serif"),
        title_font=dict(color=TEXTO, size=20, family="Geist, Arial, sans-serif"),
        title=dict(x=0.02, xanchor="left", y=0.96, yanchor="top"),
        xaxis=dict(
            color="#6b6b6b",
            gridcolor="rgba(34,34,34,0.08)",
            linecolor="#e5e7eb",
            zeroline=False,
            ticks="outside",
            tickfont=dict(size=12),
            title_font=dict(size=13, color="#6b6b6b")
        ),
        yaxis=dict(
            color="#6b6b6b",
            gridcolor="rgba(34,34,34,0.08)",
            linecolor="#e5e7eb",
            zeroline=False,
            ticks="outside",
            tickfont=dict(size=12),
            title_font=dict(size=13, color="#6b6b6b")
        ),
        legend=dict(
            font=dict(color=TEXTO, size=12),
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
        hoverlabel=dict(bgcolor=VERDE_ESCURO, font_color="#ffffff", font_size=13),
        uniformtext_minsize=10,
        uniformtext_mode="show"
    )

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
            font=dict(size=66, color="rgba(30,72,18,0.035)"),
            xanchor="center",
            yanchor="middle"
        )

    fig.add_annotation(
        text=fonte,
        xref="paper", yref="paper",
        x=1, y=-0.18,
        showarrow=False,
        font=dict(size=11, color="#8a8a8a"),
        xanchor="right"
    )
    return fig


PLOTLY_CONFIG = {
    "displaylogo": False,
    "toImageButtonOptions": {
        "format": "png",
        "filename": "agrobasis_complexo_soja_grafico",
        "scale": 5
    },
    "modeBarButtonsToRemove": ["lasso2d", "select2d"]
}

# ============================================================
# APP
# ============================================================

df = carregar_dados()

st.title("Complexo Soja USDA")
st.caption("Fundamentos globais da soja, farelo e óleo: produção, consumo, esmagamento, exportações, estoques e relações de mercado.")

produtos = sorted(df["Produto"].dropna().unique())
paises = ["Mundo"] + sorted([p for p in df["País"].dropna().unique() if p != "Mundo"])
indicadores = sorted(df["Indicador"].dropna().unique())

c1, c2, c3, c4, c5 = st.columns([1.15, 1.15, 1.15, 1.35, 0.9])

with c1:
    produto = st.selectbox(
        "Produto",
        produtos,
        index=produtos.index("Soja em Grão") if "Soja em Grão" in produtos else 0
    )

with c2:
    pais = st.selectbox("País / Região", paises, index=0)

with c3:
    indicador = st.selectbox(
        "Indicador principal",
        indicadores,
        index=indicadores.index("Produção") if "Produção" in indicadores else 0
    )

base_inicial = df[(df["Produto"] == produto) & (df["País"] == pais)].copy()
anos = sorted(base_inicial["Year"].dropna().unique())

if not anos:
    st.warning("Não há dados disponíveis para essa combinação.")
    st.stop()

if "usar_historico_completo_soja" not in st.session_state:
    st.session_state["usar_historico_completo_soja"] = False

with c5:
    if st.button("Todo o Histórico", use_container_width=True):
        st.session_state["usar_historico_completo_soja"] = True

if len(anos) >= 8:
    periodo_8_anos = (anos[-8], anos[-1])
else:
    periodo_8_anos = (anos[0], anos[-1])

periodo_padrao = (anos[0], anos[-1]) if st.session_state["usar_historico_completo_soja"] else periodo_8_anos

with c4:
    ano_ini, ano_fim = st.select_slider(
        "Período",
        options=anos,
        value=periodo_padrao
    )

base = base_inicial[(base_inicial["Year"] >= ano_ini) & (base_inicial["Year"] <= ano_fim)].copy()

qtd_anos_selecionados = len(sorted(base["Year"].dropna().unique()))
mostrar_rotulos_periodo = qtd_anos_selecionados <= 8

base_ind = base[base["Indicador"] == indicador]
attr_indicador = base_ind["Attribute"].iloc[0] if not base_ind.empty else "Production"

producao = valor(base, "Production")
consumo = valor(base, "Domestic Consumption")
crush = valor(base, "Crush")
exportacao = valor(base, "Exports")
importacao = valor(base, "Imports")
estoque = valor(base, "Ending Stocks")

estoque_uso = (estoque / consumo * 100) if estoque and consumo else None
export_prod = (exportacao / producao * 100) if exportacao and producao else None
crush_prod = (crush / producao * 100) if crush and producao else None
cagr_ind = cagr(base, attr_indicador)

st.divider()

tabs = st.tabs([
    "Visão Executiva",
    "Balanço",
    "Market Share",
    "Rankings",
    "Diagnóstico",
    "Análises",
    "Dados"
])

with tabs[0]:
    base_graf = base[base["Indicador"] == indicador].sort_values("Year").copy()
    converter_mm = eh_volume_toneladas(attr_indicador)
    if converter_mm:
        base_graf["Value"] = base_graf["Value"] / 1000
    fig = px.line(
        base_graf,
        x="Year",
        y="Value",
        markers=True,
        title=f"Evolução — {indicador} | {produto} | {pais}"
    )
    fig.update_traces(line=dict(width=5, color=VERDE_MEDIO), marker=dict(size=10, line=dict(width=1.5, color="#ffffff")))
    aplicar_rotulos_linha(fig, casas=0 if converter_mm else 1, mostrar_rotulos=mostrar_rotulos_periodo)
    fig.update_xaxes(title_text="Ano")
    fig.update_yaxes(title_text="Valor (milhões de toneladas | MM/t)" if converter_mm else "Valor")
    st.plotly_chart(aplicar_layout(fig, 560), use_container_width=True, config=PLOTLY_CONFIG)

    st.subheader(f"Painel Executivo — {produto} | {pais}")

    cards = [
        ("Produção", producao / 1000 if producao else producao, "Production", "MM/t", "card-green"),
        ("Consumo Doméstico", consumo / 1000 if consumo else consumo, "Domestic Consumption", "MM/t", "card-blue"),
        ("Esmagamento", crush / 1000 if crush else crush, "Crush", "MM/t", "card-orange"),
        ("Exportações", exportacao / 1000 if exportacao else exportacao, "Exports", "MM/t", "card-green"),
        ("Estoque Final", estoque / 1000 if estoque else estoque, "Ending Stocks", "MM/t", "card-dark"),
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
                <div class="card-value">{fmt(v, 0 if unid == "MM/t" else 2)}</div>
                <div class="card-delta">{unid} | {delta}</div>
            </div>
            """, unsafe_allow_html=True)

    st.subheader("Comparação internacional")
    padrao = [p for p in ["Estados Unidos", "Brasil", "Argentina"] if p in paises]
    paises_comp = st.multiselect("Países/regiões para comparação", paises, default=padrao)

    comp = df[
        (df["Produto"] == produto) &
        (df["País"].isin(paises_comp)) &
        (df["Indicador"] == indicador) &
        (df["Year"] >= ano_ini) &
        (df["Year"] <= ano_fim)
    ].copy()

    if converter_mm:
        comp["Value"] = comp["Value"] / 1000

    fig_comp = px.line(
        comp,
        x="Year",
        y="Value",
        color="País",
        markers=True,
        title=f"Comparativo Internacional — {indicador} | {produto}"
    )
    aplicar_rotulos_linha(fig_comp, casas=0 if converter_mm else 1, mostrar_rotulos=mostrar_rotulos_periodo)
    fig_comp.update_xaxes(title_text="Ano")
    fig_comp.update_yaxes(title_text="Valor (milhões de toneladas | MM/t)" if converter_mm else "Valor")
    st.plotly_chart(aplicar_layout(fig_comp, 520), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[1]:
    st.subheader("Balanço de Oferta e Demanda")

    # Nota: usamos "Production" (Produção) em vez de "Total Supply" (Oferta Total)
    # porque Total Supply = Estoque Inicial + Produção + Importações — ou seja,
    # carrega o estoque que sobrou do ano anterior e infla o número. Produção é
    # a comparação justa "o que foi ofertado neste ano" vs "o que foi consumido".
    attrs_oferta_demanda = ["Production", "Domestic Consumption"]
    bal = base[base["Attribute"].isin(attrs_oferta_demanda)].copy()
    bal["Value_MMt"] = bal["Value"] / 1000  # 1000 MT -> milhões de toneladas (MM/t)

    fig_bal = px.bar(
        bal,
        x="Year",
        y="Value_MMt",
        color="Indicador",
        barmode="group",
        title=f"Produção x Consumo Doméstico (ano a ano) — {produto} | {pais}",
        color_discrete_map={"Produção": VERDE_ESCURO, "Consumo Doméstico": DOURADO}
    )
    aplicar_rotulos_barra(fig_bal, casas=0, mostrar_rotulos=mostrar_rotulos_periodo)
    fig_bal.update_xaxes(title_text="Ano", type="category")
    fig_bal.update_yaxes(title_text="Valor (milhões de toneladas | MM/t)")
    st.plotly_chart(aplicar_layout(fig_bal, 560), use_container_width=True, config=PLOTLY_CONFIG)

    pivot = base.pivot_table(index="Year", columns="Attribute", values="Value", aggfunc="sum").reset_index()

    if "Ending Stocks" in pivot.columns and "Domestic Consumption" in pivot.columns:
        pivot["Estoque/Uso (%)"] = pivot["Ending Stocks"] / pivot["Domestic Consumption"] * 100
        fig_su = px.bar(pivot, x="Year", y="Estoque/Uso (%)", title="Estoque/Uso")
        fig_su.update_traces(marker_color=DOURADO)
        aplicar_rotulos_barra(fig_su, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
        fig_su.update_xaxes(type="category")
        st.plotly_chart(aplicar_layout(fig_su, 500), use_container_width=True, config=PLOTLY_CONFIG)

    if {"Production", "Domestic Consumption"}.issubset(pivot.columns):
        pivot["Produção - Consumo (MM/t)"] = (pivot["Production"] - pivot["Domestic Consumption"]) / 1000
        fig_gap = px.bar(pivot, x="Year", y="Produção - Consumo (MM/t)", title="Superávit/Déficit: Produção - Consumo")
        fig_gap.update_traces(marker_color=OLIVA)
        aplicar_rotulos_barra(fig_gap, casas=0, mostrar_rotulos=mostrar_rotulos_periodo)
        fig_gap.update_xaxes(type="category")
        fig_gap.update_yaxes(title_text="Valor (milhões de toneladas | MM/t)")
        st.plotly_chart(aplicar_layout(fig_gap, 500), use_container_width=True, config=PLOTLY_CONFIG)

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
    ms["Value_display"] = ms["Value"] / 1000 if converter_mm else ms["Value"]

    c1, c2 = st.columns(2)

    with c1:
        fig_ms_top = px.bar(
            ms.head(15),
            x="Value_display",
            y="País",
            orientation="h",
            title=f"Top 15 — Volume | {indicador} | {produto} | {ano_ms}"
        )
        fig_ms_top.update_traces(marker_color=VERDE_ESCURO)
        aplicar_rotulos_barra(fig_ms_top, casas=0 if converter_mm else 1, orientacao="h")
        fig_ms_top.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_ms_top.update_xaxes(title_text="Milhões de toneladas (MM/t)" if converter_mm else "Valor")
        st.plotly_chart(aplicar_layout(fig_ms_top, 520), use_container_width=True, config=PLOTLY_CONFIG)

    with c2:
        fig_ms = px.bar(
            ms.head(15),
            x="Market Share (%)",
            y="País",
            orientation="h",
            title="Top 15 — Participação Mundial"
        )
        fig_ms.update_traces(marker_color=VERDE_MEDIO)
        aplicar_rotulos_barra(fig_ms, casas=1, percentual=True, orientacao="h")
        fig_ms.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(aplicar_layout(fig_ms, 520), use_container_width=True, config=PLOTLY_CONFIG)

    st.dataframe(ms[["País", "Value", "Market Share (%)"]].head(30), use_container_width=True)

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
    rank["Value_display"] = rank["Value"] / 1000 if converter_mm else rank["Value"]

    fig_rank = px.bar(
        rank.head(20),
        x="Value_display",
        y="País",
        orientation="h",
        title=f"Top 20 — {indicador} | {produto} | {ano_rank}"
    )
    fig_rank.update_traces(marker_color=VERDE_MEDIO)
    aplicar_rotulos_barra(fig_rank, casas=0 if converter_mm else 1, orientacao="h")
    fig_rank.update_layout(yaxis={"categoryorder": "total ascending"})
    fig_rank.update_xaxes(title_text="Milhões de toneladas (MM/t)" if converter_mm else "Valor")
    st.plotly_chart(aplicar_layout(fig_rank, 560), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[4]:
    st.subheader("Diagnóstico Fundamentalista")

    pivot = base.pivot_table(index="Year", columns="Attribute", values="Value", aggfunc="sum").reset_index()

    if {"Exports", "Production"}.issubset(pivot.columns):
        pivot["Exportação/Produção (%)"] = pivot["Exports"] / pivot["Production"] * 100
        fig = px.line(pivot, x="Year", y="Exportação/Produção (%)", markers=True, title="Exportação / Produção")
        fig.update_traces(line=dict(width=5, color=DOURADO), marker=dict(size=10, line=dict(width=1.5, color="#ffffff")))
        aplicar_rotulos_linha(fig, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
        st.plotly_chart(aplicar_layout(fig, 540), use_container_width=True, config=PLOTLY_CONFIG)

    if {"Imports", "Domestic Consumption"}.issubset(pivot.columns):
        pivot["Importação/Consumo (%)"] = pivot["Imports"] / pivot["Domestic Consumption"] * 100
        fig = px.line(pivot, x="Year", y="Importação/Consumo (%)", markers=True, title="Importação / Consumo")
        fig.update_traces(line=dict(width=5, color=MARROM_ESCURO), marker=dict(size=10, line=dict(width=1.5, color="#ffffff")))
        aplicar_rotulos_linha(fig, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
        st.plotly_chart(aplicar_layout(fig, 540), use_container_width=True, config=PLOTLY_CONFIG)

    if {"Crush", "Production"}.issubset(pivot.columns):
        pivot["Esmagamento/Produção (%)"] = pivot["Crush"] / pivot["Production"] * 100
        fig = px.line(pivot, x="Year", y="Esmagamento/Produção (%)", markers=True, title="Esmagamento / Produção")
        fig.update_traces(line=dict(width=5, color=VERDE_MEDIO), marker=dict(size=10, line=dict(width=1.5, color="#ffffff")))
        aplicar_rotulos_linha(fig, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
        st.plotly_chart(aplicar_layout(fig, 540), use_container_width=True, config=PLOTLY_CONFIG)

    if {"Crush", "Domestic Consumption"}.issubset(pivot.columns):
        pivot["Esmagamento/Consumo (%)"] = pivot["Crush"] / pivot["Domestic Consumption"] * 100
        fig = px.line(pivot, x="Year", y="Esmagamento/Consumo (%)", markers=True, title="Esmagamento / Consumo Doméstico")
        fig.update_traces(line=dict(width=5, color=OLIVA), marker=dict(size=10, line=dict(width=1.5, color="#ffffff")))
        aplicar_rotulos_linha(fig, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
        st.plotly_chart(aplicar_layout(fig, 540), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[5]:
    st.subheader("Análises Complementares")

    st.markdown("""
    <div class="insight-box" style="margin-bottom:18px;">
        <h3>O que olhar aqui</h3>
        <p>Esta seção foca em gráficos que funcionam bem como imagem estática para apresentações:
        variação anual, maiores altas e quedas, mapa de calor e concentração dos líderes globais.</p>
    </div>
    """, unsafe_allow_html=True)

    yoy_base = base[base["Indicador"] == indicador].sort_values("Year").copy()
    yoy_base["Variação YoY (%)"] = yoy_base["Value"].pct_change() * 100

    fig_yoy = px.bar(
        yoy_base.dropna(subset=["Variação YoY (%)"]),
        x="Year",
        y="Variação YoY (%)",
        title=f"Variação Ano a Ano — {indicador} | {produto} | {pais}",
        color="Variação YoY (%)",
        color_continuous_scale=[MARROM_ESCURO, "#f1f5f9", VERDE_MEDIO],
        color_continuous_midpoint=0
    )
    aplicar_rotulos_barra(fig_yoy, casas=1, percentual=True, mostrar_rotulos=mostrar_rotulos_periodo)
    fig_yoy.update_xaxes(title_text="Ano")
    fig_yoy.update_layout(coloraxis_showscale=False)
    st.plotly_chart(aplicar_layout(fig_yoy, 420), use_container_width=True, config=PLOTLY_CONFIG)

    col_e, col_f = st.columns(2)

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
            ranking_cagr = pd.concat([top_cresce, top_cai]).drop_duplicates(subset="País").sort_values("CAGR (% a.a.)")

            fig_cagr = px.bar(
                ranking_cagr,
                x="CAGR (% a.a.)",
                y="País",
                orientation="h",
                title=f"Maiores Altas e Quedas (CAGR) — {indicador}",
                color="CAGR (% a.a.)",
                color_continuous_scale=[MARROM_ESCURO, "#f1f5f9", VERDE_MEDIO],
                color_continuous_midpoint=0
            )
            aplicar_rotulos_barra(fig_cagr, casas=1, percentual=True, orientacao="h")
            fig_cagr.update_layout(coloraxis_showscale=False)
            st.plotly_chart(aplicar_layout(fig_cagr, 460), use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("Sem dados suficientes para calcular o CAGR por país no período selecionado.")

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

        heat_pivot = heat.pivot_table(index="País", columns="Year", values="Value", aggfunc="sum").reindex(top_paises)
        if converter_mm:
            heat_pivot = heat_pivot / 1000

        if not heat_pivot.empty:
            titulo_heat = f"Mapa de Calor — Top 10 Países | {indicador}"
            if converter_mm:
                titulo_heat += " (MM/t)"
            fig_heat = px.imshow(
                heat_pivot,
                aspect="auto",
                text_auto=".0f" if mostrar_rotulos_periodo else False,
                color_continuous_scale="YlGn",
                title=titulo_heat
            )
            fig_heat.update_xaxes(title_text="Ano")
            fig_heat.update_yaxes(title_text="")
            st.plotly_chart(aplicar_layout(fig_heat, 460), use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("Sem dados suficientes para montar o mapa de calor.")

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

        fig_conc = px.bar(
            conc_top10,
            x="País",
            y="Share (%)",
            title=f"Concentração de Mercado — Top 10 | {indicador} | {ano_fim}",
            text=conc_top10["Share (%)"].round(1).astype(str) + "%"
        )
        fig_conc.update_traces(marker_color=VERDE_ESCURO, textposition="outside", textfont=dict(size=12, color=TEXTO), cliponaxis=False)
        fig_conc.add_scatter(
            x=conc_top10["País"],
            y=conc_top10["Acumulado (%)"],
            mode="lines+markers+text",
            text=conc_top10["Acumulado (%)"].round(1).astype(str) + "%",
            textposition="top center",
            name="Participação acumulada (%)",
            line=dict(color=DOURADO, width=3),
            yaxis="y2"
        )
        fig_conc.update_layout(yaxis2=dict(overlaying="y", side="right", title="Acumulado (%)", range=[0, 105], showgrid=False))
        st.plotly_chart(aplicar_layout(fig_conc, 460), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[6]:
    st.subheader("Base filtrada")

    st.dataframe(base[["Produto", "País", "Year", "Indicador", "Unit", "Value"]], use_container_width=True)

    csv = base.to_csv(index=False).encode("utf-8-sig")
    st.download_button("Baixar base filtrada", csv, file_name=f"agrobasis_{produto}_{pais}.csv", mime="text/csv")
