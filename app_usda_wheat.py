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

# Atributos cuja unidade original do USDA PSD é "1000 MT" (mil toneladas).
# Área Colhida (1000 HA) e Produtividade (MT/HA, uma razão) ficam de fora
# de propósito: converter esses dois pra "milhões de toneladas" produziria
# um número tecnicamente errado.
ATRIBUTOS_VOLUME_TONELADAS = {
    "Production", "Domestic Consumption", "Exports", "Imports",
    "Ending Stocks", "Beginning Stocks", "Total Supply",
    "Feed Dom. Consumption", "FSI Consumption",
    "Food, Seed, Industrial Consumption",
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
# CORES OFICIAIS AGROBASIS
# ============================================================
# Constantes centralizadas — mesmo Design System dos dashboards USDA
# Complexo Soja e USDA Milho.
VERDE_PRINCIPAL = "#1E4812"
VERDE_SECUNDARIO = "#54931B"
TEXTO = "#222222"
DOURADO = "#A17149"
PRETO = "#000000"
FUNDO = "#F8FAF8"
BORDA = "#E7ECE8"
OLIVA = "#6B7F3A"          # verde-oliva da paleta estendida — acento terciário
MARROM_ESCURO = "#8A6A4F"  # marrom escuro da paleta estendida — escalas divergentes

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
    background:{FUNDO};
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

/* Caixas de seleção */
[data-baseweb="select"] {{
    background:#ffffff !important;
    border-radius:10px;
    border:1px solid {BORDA} !important;
}}

[data-baseweb="select"] div,
[data-baseweb="select"] span {{
    color:{TEXTO} !important;
}}

/* Dropdown aberto */
[role="listbox"] div,
[role="option"],
[role="option"] div,
[role="option"] span {{
    color:{TEXTO} !important;
    background:#ffffff !important;
}}

/* Abas */
.stTabs [data-baseweb="tab-list"] {{
    gap:4px;
    background:#ffffff;
    padding:6px;
    border-radius:14px;
    border:1px solid {BORDA};
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
    color:{VERDE_PRINCIPAL};
}}

.stTabs [aria-selected="true"] {{
    background:{VERDE_PRINCIPAL} !important;
    color:#ffffff !important;
}}

.stTabs [aria-selected="true"]:hover {{
    background:{VERDE_SECUNDARIO} !important;
    color:#ffffff !important;
}}

/* Cards executivos — discretos, fundo claro com leve destaque colorido */
.card {{
    padding:16px 18px;
    border-radius:16px;
    background:#ffffff;
    border:1px solid {BORDA};
    border-left:4px solid var(--accent, {VERDE_PRINCIPAL});
    box-shadow:0px 2px 8px rgba(30,72,18,0.05);
    min-height:104px;
}}

.card-green  {{ --accent:{VERDE_PRINCIPAL}; }}
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
    border:1px solid {BORDA};
    border-left:3px solid {DOURADO};
    padding:22px;
    border-radius:16px;
    color:{TEXTO};
    box-shadow:0px 6px 18px rgba(30,72,18,0.05);
}}

.insight-box h3 {{
    color:{VERDE_PRINCIPAL} !important;
    font-weight:800;
}}

.insight-box p {{
    color:#4a4a4a !important;
    line-height:1.7;
}}

/* Cartões de gráfico */
div[data-testid="stPlotlyChart"] {{
    background:#ffffff;
    border-radius:18px;
    padding:8px;
    border:1px solid {BORDA};
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
    border:1px solid {BORDA};
}}

.stButton > button,
.stDownloadButton > button {{
    background:#ffffff;
    color:{VERDE_PRINCIPAL};
    font-family:'Geist', Arial, sans-serif;
    border:1px solid {VERDE_PRINCIPAL};
    border-radius:10px;
    font-weight:700;
    min-height:40px;
    margin-top:25px;
    transition:background .15s ease, color .15s ease;
}}

.stButton > button:hover,
.stDownloadButton > button:hover {{
    background:{VERDE_SECUNDARIO};
    color:#ffffff;
    border-color:{VERDE_SECUNDARIO};
}}
</style>
""", unsafe_allow_html=True)

# Paleta oficial AgroBasis — mesma usada em todos os dashboards do ecossistema
PALETA = [VERDE_PRINCIPAL, VERDE_SECUNDARIO, DOURADO, TEXTO, PRETO, OLIVA, MARROM_ESCURO]

# ============================================================
# FUNÇÕES
# ============================================================

def fmt(v, casas=1):
    if v is None or pd.isna(v):
        return "-"
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_plotly(v, casas=1, sufixo=""):
    """Formata números para rótulos dentro dos gráficos."""
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


def anos_lista(serie, reverse=False):
    """Retorna anos únicos como int nativo do Python, nunca numpy.int64.

    Referência oficial: streamlit/streamlit#6815 — o motor de widgets do
    Streamlit (validação de tipo + serialização de session_state entre
    reruns) trata numpy.int64 como tipo incompatível com int em vários
    pontos internos, causando ValueError/TypeError intermitentes que só
    se manifestam ao interagir com o widget (ex.: arrastar um slider),
    porque pandas.Series.unique() SEMPRE retorna numpy.int64, mesmo após
    .astype(int) na Series original (astype converte o dtype da coluna,
    não o tipo escalar devolvido por unique()/max()/min()).
    """
    return sorted((int(a) for a in serie.dropna().unique()), reverse=reverse)


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
        font=dict(color=TEXTO, size=13, family="Geist, Arial, sans-serif"),
        title_font=dict(color=TEXTO, size=20, family="Geist, Arial, sans-serif"),
        title=dict(x=0.015, xanchor="left", y=0.96),
        xaxis=dict(
            title_font=dict(size=12, color="#6b6b6b"),
            tickfont=dict(size=11, color="#6b6b6b"),
            gridcolor="rgba(34,34,34,0.06)",
            linecolor=BORDA,
            showline=True,
            mirror=False,
            zeroline=False,
            ticks="outside",
            tickcolor=BORDA,
        ),
        yaxis=dict(
            title_font=dict(size=12, color="#6b6b6b"),
            tickfont=dict(size=11, color="#6b6b6b"),
            gridcolor="rgba(34,34,34,0.06)",
            linecolor=BORDA,
            showline=True,
            mirror=False,
            zeroline=False,
            ticks="outside",
            tickcolor=BORDA,
        ),
        legend=dict(
            font=dict(size=11, color=TEXTO),
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
        hoverlabel=dict(bgcolor=VERDE_PRINCIPAL, font_color="#ffffff", font_size=12),
        uniformtext_minsize=9,
        uniformtext_mode="hide",
    )

    # hovertemplate=None é válido para todos os tipos de trace (scatter, bar,
    # heatmap etc.) e pode ser aplicado globalmente com segurança.
    fig.update_traces(hovertemplate=None)

    # marker_line_width=0 NÃO existe no schema de traces do tipo Heatmap
    # (usado pelo px.imshow no mapa de calor da aba Análises) — só existe em
    # traces com "marker" (bar, scatter, box, violin...). Aplicar globalmente
    # via update_traces() derruba o app inteiro com ValueError assim que uma
    # figura mista (ex.: heatmap) passa por aqui. Aplicamos trace a trace e
    # ignoramos silenciosamente os tipos que não suportam a propriedade.
    for _trace in fig.data:
        try:
            _trace.marker.line.width = 0
        except (AttributeError, ValueError):
            pass

    # Watermark central discreta, aparece também no PNG baixado pelo usuário.
    fig.add_annotation(
        text="AgroBasis",
        xref="paper", yref="paper",
        x=0.5, y=0.52,
        showarrow=False,
        font=dict(size=54, color="rgba(30, 72, 18, 0.075)", family="Geist, Arial, sans-serif"),
        xanchor="center",
        yanchor="middle",
        textangle=0
    )

    # Assinatura técnica no rodapé.
    fig.add_annotation(
        text="Fonte: USDA PSD · Elaboração: AgroBasis",
        xref="paper", yref="paper",
        x=1, y=-0.16,
        showarrow=False,
        font=dict(size=10, color="#8a8a8a"),
        xanchor="right"
    )
    return fig


def aplicar_linha_profissional(fig, cor=None, mostrar_rotulos=True, casas=1, percentual=False):
    """Padroniza linhas para leitura em tela e exportação em apresentações.

    Regra AgroBasis:
    - até 8 anos selecionados: mostra valores;
    - acima de 8 anos: oculta valores para evitar sobreposição.
    """
    sufixo = "%" if percentual else ""
    for tr in fig.data:
        linha = dict(width=3.2, shape="spline", smoothing=0.35)
        if cor:
            linha["color"] = cor

        tr.line = linha
        tr.marker = dict(size=6.5, line=dict(width=1.2, color="#ffffff"))
        tr.cliponaxis = False

        if mostrar_rotulos:
            tr.mode = "lines+markers+text"
            tr.text = [fmt_plotly(v, casas, sufixo) for v in tr.y]
            tr.texttemplate = "%{text}"
            tr.textposition = "top center"
            tr.textfont = dict(size=10.5, color=TEXTO)
        else:
            tr.mode = "lines+markers"
            tr.text = None
            tr.texttemplate = None

    return fig


def aplicar_barras_profissionais(fig, cor=None, texto=False, orientacao="v", mostrar_rotulos=True, casas=1, percentual=False):
    """Padroniza barras para PNG/PPT, com rótulos opcionais."""
    sufixo = "%" if percentual else ""

    for tr in fig.data:
        tr.marker.line.width = 0
        tr.opacity = 0.92
        if cor:
            tr.marker.color = cor

        if texto and mostrar_rotulos:
            valores = tr.x if orientacao == "h" else tr.y
            tr.text = [fmt_plotly(v, casas, sufixo) for v in valores]
            tr.texttemplate = "%{text}"
            tr.textposition = "outside"
            tr.textfont = dict(size=11.5, color=TEXTO)
            tr.cliponaxis = False
        else:
            tr.text = None
            tr.texttemplate = None
            tr.cliponaxis = False

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

st.title("Trigo USDA")
st.caption("Fundamentos globais do trigo: produção, consumo, exportações, estoques e relações de mercado com dados oficiais do USDA PSD.")

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

anos = anos_lista(base_inicial["Year"])

if not anos:
    st.warning("Não há dados disponíveis para essa combinação.")
    st.stop()

# Abre o dashboard nos últimos 8 anos, mas permite alterar livremente a faixa.
periodo_padrao = (anos[-8], anos[-1]) if len(anos) >= 8 else (anos[0], anos[-1])

# Inicialização
if "periodo_trigo" not in st.session_state:
    st.session_state.periodo_trigo = periodo_padrao

# Se mudar produto/país e o período salvo ficar fora das opções disponíveis,
# reseta para o padrão em vez de prender o slider.
_periodo_salvo = st.session_state.periodo_trigo

if (
    not isinstance(_periodo_salvo, (tuple, list))
    or len(_periodo_salvo) != 2
    or _periodo_salvo[0] not in anos
    or _periodo_salvo[1] not in anos
):
    st.session_state.periodo_trigo = periodo_padrao

with c4:
    p_col, b_col = st.columns([2.2, 1])

    # Botão
    with b_col:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("Todo o Histórico", key="btn_historico_trigo", use_container_width=True):
            st.session_state.periodo_trigo = (anos[0], anos[-1])

    # Slider sem key fixa: usa value vindo do session_state e depois atualiza manualmente.
    # Isso evita o comportamento em que o slider fica preso no padrão ou no histórico completo.
    with p_col:
        periodo = st.select_slider(
            "Período",
            options=anos,
            value=st.session_state.periodo_trigo
        )

# Atualiza somente após o usuário mover
st.session_state.periodo_trigo = periodo

ano_ini, ano_fim = periodo

base = base_inicial[
    (base_inicial["Year"] >= ano_ini) &
    (base_inicial["Year"] <= ano_fim)
].copy()

# Mostra rótulos somente em períodos curtos, úteis para PNG/PPT.
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

# Indicador principal em toneladas? Se sim, todo o dashboard converte
# 1000 MT -> milhões de toneladas (MM/t) para leitura executiva/PPT.
converter_mm = eh_volume_toneladas(attr_indicador)

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
    if converter_mm:
        base_graf["Value"] = base_graf["Value"] / 1000

    fig = px.line(
        base_graf,
        x="Year",
        y="Value",
        markers=True,
        title=f"Evolução — {indicador} | {produto} | {pais}"
    )
    aplicar_linha_profissional(fig, VERDE_SECUNDARIO, casas=0 if converter_mm else 1, mostrar_rotulos=mostrar_rotulos_periodo)
    fig.update_xaxes(title_text="Ano")
    fig.update_yaxes(title_text="Valor (milhões de toneladas | MM/t)" if converter_mm else "Valor")
    st.plotly_chart(aplicar_layout(fig, 560), use_container_width=True, config=PLOTLY_CONFIG)

    st.subheader(f"Painel Executivo — {produto} | {pais}")

    cards = [
        ("Produção", producao / 1000 if producao else producao, "Production", "MM/t", "card-green"),
        ("Consumo Doméstico", consumo / 1000 if consumo else consumo, "Domestic Consumption", "MM/t", "card-blue"),
        ("Consumo Ração", feed / 1000 if feed else feed, "Feed Dom. Consumption", "MM/t", "card-orange"),
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

    # Padrão dinâmico: os 2 países de maior expressão no indicador/ano final
    # do período selecionado, + Brasil (sempre presente como referência local).
    #
    # BUG CORRIGIDO: este multiselect não tinha key= explícita, e "padrao"
    # (o default) era recalculado a cada rerun a partir de ano_fim. Sem key,
    # o Streamlit gera um id interno cujo hash depende do próprio "default" —
    # ao arrastar o slider de período, ano_fim muda, padrao muda, o id muda,
    # e o Streamlit não consegue reconciliar o widget entre a rodada anterior
    # e a atual (mesmo erro estrutural do select_slider sem key, só que aqui
    # disparado pelo recurso "top 2 + Brasil"). Com key= fixa, o Streamlit só
    # consulta default= na primeira montagem da sessão; depois disso, o valor
    # vem de st.session_state, imune a mudanças de "padrao" em reruns seguintes.
    ranking_top = df[
        (df["Produto"] == produto) &
        (df["Indicador"] == indicador) &
        (df["Year"] == ano_fim) &
        (df["País"] != "Mundo")
    ].sort_values("Value", ascending=False)

    top2 = ranking_top["País"].head(2).tolist()
    padrao = list(dict.fromkeys(top2 + (["Brasil"] if "Brasil" in paises else [])))

    paises_comp = st.multiselect(
        "Países/regiões para comparação",
        paises,
        default=padrao,
        key="paises_comp_trigo"
    )

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
    aplicar_linha_profissional(fig_comp, casas=0 if converter_mm else 1, mostrar_rotulos=mostrar_rotulos_periodo)
    fig_comp.update_xaxes(title_text="Ano")
    fig_comp.update_yaxes(title_text="Valor (milhões de toneladas | MM/t)" if converter_mm else "Valor")
    st.plotly_chart(aplicar_layout(fig_comp, 520), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[1]:
    st.subheader("Balanço de Oferta e Demanda")

    # Gráfico de barras ano a ano: Produção (oferta) x Consumo Doméstico (demanda).
    # Substitui o gráfico de linha com 9 séries, que em janelas longas sobrepõe
    # marcadores e rótulos e perde legibilidade — especialmente como imagem
    # estática exportada para apresentação.
    attrs_oferta_demanda = ["Production", "Domestic Consumption"]
    bal = base[base["Attribute"].isin(attrs_oferta_demanda)].copy()
    bal["Value_MMt"] = bal["Value"] / 1000  # 1000 MT -> milhões de toneladas (MM/t)

    fig_bal = px.bar(
        bal,
        x="Year",
        y="Value_MMt",
        color="Indicador",
        barmode="group",
        title=f"Oferta x Demanda (ano a ano) — {produto} | {pais}",
        color_discrete_map={"Produção": VERDE_PRINCIPAL, "Consumo Doméstico": DOURADO}
    )
    aplicar_barras_profissionais(fig_bal, texto=True, mostrar_rotulos=mostrar_rotulos_periodo, casas=0)
    fig_bal.update_xaxes(title_text="Ano", type="category")
    fig_bal.update_yaxes(title_text="Valor (milhões de toneladas | MM/t)")
    st.plotly_chart(aplicar_layout(fig_bal, 560), use_container_width=True, config=PLOTLY_CONFIG)

    pivot = base.pivot_table(
        index="Year",
        columns="Attribute",
        values="Value",
        aggfunc="sum"
    ).reset_index()

    if "Ending Stocks" in pivot.columns and "Domestic Consumption" in pivot.columns:
        pivot["Estoque/Uso (%)"] = pivot["Ending Stocks"] / pivot["Domestic Consumption"] * 100
        fig_su = px.bar(pivot, x="Year", y="Estoque/Uso (%)", title="Estoque/Uso")
        aplicar_barras_profissionais(fig_su, DOURADO, texto=True, mostrar_rotulos=mostrar_rotulos_periodo, percentual=True)
        fig_su.update_xaxes(type="category")
        st.plotly_chart(aplicar_layout(fig_su, 520), use_container_width=True, config=PLOTLY_CONFIG)

    if {"Production", "Domestic Consumption"}.issubset(pivot.columns):
        pivot["Produção - Consumo (MM/t)"] = (pivot["Production"] - pivot["Domestic Consumption"]) / 1000
        fig_gap = px.bar(
            pivot,
            x="Year",
            y="Produção - Consumo (MM/t)",
            title="Superávit/Déficit: Produção - Consumo"
        )
        aplicar_barras_profissionais(fig_gap, OLIVA, texto=True, mostrar_rotulos=mostrar_rotulos_periodo, casas=0)
        fig_gap.update_xaxes(type="category")
        fig_gap.update_yaxes(title_text="Valor (milhões de toneladas | MM/t)")
        st.plotly_chart(aplicar_layout(fig_gap, 520), use_container_width=True, config=PLOTLY_CONFIG)

    st.dataframe(pivot, use_container_width=True)

with tabs[2]:
    st.subheader("Market Share Mundial")

    ano_ms = st.selectbox(
        "Ano para análise de participação",
        anos_lista(df["Year"], reverse=True)
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
        aplicar_barras_profissionais(fig_ms_top, VERDE_PRINCIPAL, texto=True, orientacao="h", casas=0 if converter_mm else 1)
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
        aplicar_barras_profissionais(fig_ms, VERDE_SECUNDARIO, texto=True, orientacao="h", percentual=True)
        fig_ms.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(aplicar_layout(fig_ms, 520), use_container_width=True, config=PLOTLY_CONFIG)

    st.dataframe(ms[["País", "Value", "Market Share (%)"]].head(30), use_container_width=True)

with tabs[3]:
    st.subheader("Ranking Mundial")

    ano_rank = st.selectbox(
        "Ano do ranking",
        anos_lista(df["Year"], reverse=True),
        key="rank"
    )

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
    aplicar_barras_profissionais(fig_rank, VERDE_SECUNDARIO, texto=True, orientacao="h", casas=0 if converter_mm else 1)
    fig_rank.update_layout(yaxis={"categoryorder": "total ascending"})
    fig_rank.update_xaxes(title_text="Milhões de toneladas (MM/t)" if converter_mm else "Valor")
    st.plotly_chart(aplicar_layout(fig_rank, 560), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[4]:
    st.subheader("Diagnóstico Fundamentalista")

    pivot = base.pivot_table(
        index="Year",
        columns="Attribute",
        values="Value",
        aggfunc="sum"
    ).reset_index()

    if {"Exports", "Production"}.issubset(pivot.columns):
        pivot["Exportação/Produção (%)"] = pivot["Exports"] / pivot["Production"] * 100
        fig = px.line(
            pivot,
            x="Year",
            y="Exportação/Produção (%)",
            markers=True,
            title="Exportação / Produção"
        )
        aplicar_linha_profissional(fig, DOURADO, mostrar_rotulos=mostrar_rotulos_periodo, percentual=True)
        st.plotly_chart(aplicar_layout(fig, 540), use_container_width=True, config=PLOTLY_CONFIG)

    if {"Imports", "Domestic Consumption"}.issubset(pivot.columns):
        pivot["Importação/Consumo (%)"] = pivot["Imports"] / pivot["Domestic Consumption"] * 100
        fig = px.line(
            pivot,
            x="Year",
            y="Importação/Consumo (%)",
            markers=True,
            title="Importação / Consumo"
        )
        aplicar_linha_profissional(fig, MARROM_ESCURO, mostrar_rotulos=mostrar_rotulos_periodo, percentual=True)
        st.plotly_chart(aplicar_layout(fig, 540), use_container_width=True, config=PLOTLY_CONFIG)

    if {"Feed Dom. Consumption", "Domestic Consumption"}.issubset(pivot.columns):
        pivot["Ração/Consumo (%)"] = pivot["Feed Dom. Consumption"] / pivot["Domestic Consumption"] * 100
        fig = px.line(
            pivot,
            x="Year",
            y="Ração/Consumo (%)",
            markers=True,
            title="Consumo para Ração / Consumo Total"
        )
        aplicar_linha_profissional(fig, VERDE_SECUNDARIO, mostrar_rotulos=mostrar_rotulos_periodo, percentual=True)
        st.plotly_chart(aplicar_layout(fig, 540), use_container_width=True, config=PLOTLY_CONFIG)

    if {"FSI Consumption", "Domestic Consumption"}.issubset(pivot.columns):
        pivot["FSI/Consumo (%)"] = pivot["FSI Consumption"] / pivot["Domestic Consumption"] * 100
        fig = px.line(
            pivot,
            x="Year",
            y="FSI/Consumo (%)",
            markers=True,
            title="FSI / Consumo Total"
        )
        aplicar_linha_profissional(fig, OLIVA, mostrar_rotulos=mostrar_rotulos_periodo, percentual=True)
        st.plotly_chart(aplicar_layout(fig, 540), use_container_width=True, config=PLOTLY_CONFIG)

with tabs[5]:
    st.subheader("Análises Complementares")

    st.markdown("""
    <div class="insight-box" style="margin-bottom:18px;">
        <h3>O que olhar aqui</h3>
        <p>Esta seção reúne leituras que funcionam bem como imagem estática para apresentações:
        variação ano a ano, maiores altas e quedas por país (CAGR), mapa de calor dos líderes globais
        e concentração de mercado (curva C10).</p>
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
        color_continuous_scale=[MARROM_ESCURO, "#f1f5f9", VERDE_SECUNDARIO],
        color_continuous_midpoint=0
    )
    aplicar_barras_profissionais(fig_yoy, texto=True, mostrar_rotulos=mostrar_rotulos_periodo, percentual=True)
    fig_yoy.update_xaxes(title_text="Ano", type="category")
    fig_yoy.update_layout(coloraxis_showscale=False)
    st.plotly_chart(aplicar_layout(fig_yoy, 460), use_container_width=True, config=PLOTLY_CONFIG)

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
                color_continuous_scale=[MARROM_ESCURO, "#f1f5f9", VERDE_SECUNDARIO],
                color_continuous_midpoint=0
            )
            aplicar_barras_profissionais(fig_cagr, texto=True, orientacao="h", percentual=True)
            fig_cagr.update_layout(coloraxis_showscale=False)
            st.plotly_chart(aplicar_layout(fig_cagr, 460), use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("Sem dados suficientes para calcular o CAGR por país no período selecionado.")

    with col_f:
        top_paises_heat = (
            df[(df["Produto"] == produto) & (df["Indicador"] == indicador) &
               (df["País"] != "Mundo") & (df["Year"] == ano_fim)]
            .sort_values("Value", ascending=False)
            .head(10)["País"].tolist()
        )

        heat = df[
            (df["Produto"] == produto) &
            (df["Indicador"] == indicador) &
            (df["País"].isin(top_paises_heat)) &
            (df["Year"] >= ano_ini) &
            (df["Year"] <= ano_fim)
        ]

        heat_pivot = heat.pivot_table(index="País", columns="Year", values="Value", aggfunc="sum")
        heat_pivot = heat_pivot.reindex(top_paises_heat)
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
                color_continuous_scale="YlGnBu",
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
        fig_conc.update_traces(marker_color=VERDE_PRINCIPAL, textposition="outside", textfont=dict(size=12, color=TEXTO), cliponaxis=False)
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
