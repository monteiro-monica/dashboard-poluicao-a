# -*- coding: utf-8 -*-
"""
Dashboard: Poluição do Ar Mundial e Índice de Qualidade do Ar (AQI) — 2014-2025
EQM2009 - Tópicos Especiais III
Professora: Amanda Lemette | Aluna: Mônica Azevedo Monteiro

Como executar:
    pip install -r requirements.txt
    streamlit run app.py
"""

import glob
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Poluição do Ar Mundial & AQI (2014-2025)",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# =============================================================================
# PALETA VISUAL (alinhada ao material da disciplina)
# =============================================================================
NAVY = "#1B2A4A"
NAVY_DARK = "#101A30"
GREEN = "#1FA15B"
GRAY_BG = "#F3F5F8"
CARD_BG = "#FFFFFF"
TEXT_MUTED = "#5B6472"

AQI_ORDER = ["Boa", "Moderada", "Insalubre (Grupos Sensíveis)", "Insalubre", "Muito Insalubre", "Perigosa"]
AQI_COLORS = {
    "Boa": "#2ECC71",
    "Moderada": "#F1C40F",
    "Insalubre (Grupos Sensíveis)": "#E67E22",
    "Insalubre": "#E74C3C",
    "Muito Insalubre": "#8E44AD",
    "Perigosa": "#7B241C",
}

# =============================================================================
# MAPEAMENTOS PARA CONSOLIDAÇÃO DOS DADOS
# =============================================================================
COUNTRY_MAP = {
    "australia": ("Austrália", "Australia", "AUS"),
    "bangladesh": ("Bangladesh", "Bangladesh", "BGD"),
    "brazil": ("Brasil", "Brazil", "BRA"),
    "china": ("China", "China", "CHN"),
    "egypt": ("Egito", "Egypt", "EGY"),
    "ethiopia": ("Etiópia", "Ethiopia", "ETH"),
    "france": ("França", "France", "FRA"),
    "germany": ("Alemanha", "Germany", "DEU"),
    "india": ("Índia", "India", "IND"),
    "indonesia": ("Indonésia", "Indonesia", "IDN"),
    "iran": ("Irã", "Iran", "IRN"),
    "japan": ("Japão", "Japan", "JPN"),
    "mexico": ("México", "Mexico", "MEX"),
    "nigeria": ("Nigéria", "Nigeria", "NGA"),
    "philippines": ("Filipinas", "Philippines", "PHL"),
    "russia": ("Rússia", "Russia", "RUS"),
    "saudi_arabia": ("Arábia Saudita", "Saudi Arabia", "SAU"),
    "south_africa": ("África do Sul", "South Africa", "ZAF"),
    "south_korea": ("Coreia do Sul", "South Korea", "KOR"),
    "thailand": ("Tailândia", "Thailand", "THA"),
    "turkey": ("Turquia", "Turkey", "TUR"),
    "united_kingdom": ("Reino Unido", "United Kingdom", "GBR"),
    "usa": ("Estados Unidos", "United States", "USA"),
    "vietnam": ("Vietnã", "Vietnam", "VNM"),
}

RENAME_MAP = {
    "PM2.5 (ug/m3)": "PM2_5",
    "PM10 (ug/m3)": "PM10",
    "NO (ug/m3)": "NO",
    "NO2 (ug/m3)": "NO2",
    "NOx (ppb)": "NOx",
    "NH3 (ug/m3)": "NH3",
    "CO (mg/m3)": "CO",
    "SO2 (ug/m3)": "SO2",
    "O3 (ug/m3)": "O3",
    "Benzene (ug/m3)": "Benzene",
    "Toluene (ug/m3)": "Toluene",
    "Xylene (ug/m3)": "Xylene",
    "Wind_Speed (km/h)": "Wind_Speed",
    "Humidity (%)": "Humidity",
    "Deforestation_Rate_%": "Deforestation_Rate",
    "Industry_Growth_%": "Industry_Growth",
    "City": "Cidade",
    "Date": "Data",
}

UNITS = {
    "PM2_5": "µg/m³", "PM10": "µg/m³", "NO": "µg/m³", "NO2": "µg/m³",
    "NOx": "ppb", "NH3": "µg/m³", "CO": "mg/m³", "SO2": "µg/m³", "O3": "µg/m³",
    "Benzene": "µg/m³", "Toluene": "µg/m³", "Xylene": "µg/m³",
    "Wind_Speed": "km/h", "Humidity": "%", "Deforestation_Rate": "%",
    "Industry_Growth": "%", "CO2_Emission_MT": "Mt", "Population_Density_per_SqKm": "hab/km²",
    "AQI": "",
}

POLLUTANTS = ["PM2_5", "PM10", "NO", "NO2", "NOx", "NH3", "CO", "SO2", "O3", "Benzene", "Toluene", "Xylene"]
METEO = ["Wind_Speed", "Humidity"]
SOCIOECON = ["Deforestation_Rate", "Industry_Growth", "CO2_Emission_MT", "Population_Density_per_SqKm"]
ALL_NUMERIC_VARS = ["AQI"] + POLLUTANTS + METEO + SOCIOECON
DEFAULT_CORR_VARS = ["AQI", "PM2_5", "PM10", "NO2", "SO2", "O3", "CO", "Wind_Speed",
                     "Humidity", "Deforestation_Rate", "Industry_Growth",
                     "CO2_Emission_MT", "Population_Density_per_SqKm"]

VAR_LABELS = {
    "AQI": "AQI", "PM2_5": "PM2.5", "PM10": "PM10", "NO": "NO", "NO2": "NO2",
    "NOx": "NOx", "NH3": "NH3", "CO": "CO", "SO2": "SO2", "O3": "O3",
    "Benzene": "Benzeno", "Toluene": "Tolueno", "Xylene": "Xileno",
    "Wind_Speed": "Vel. do Vento", "Humidity": "Umidade",
    "Deforestation_Rate": "Taxa de Desmatamento", "Industry_Growth": "Crescimento Industrial",
    "CO2_Emission_MT": "Emissão de CO2", "Population_Density_per_SqKm": "Densidade Populacional",
}


# =============================================================================
# CARGA E CONSOLIDAÇÃO DOS DADOS
# =============================================================================
@st.cache_data(show_spinner="Consolidando as 24 bases de dados de poluição do ar...")
def load_data():
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*_air_quality_2014_2025.csv")))
    frames = []
    for fp in files:
        key = os.path.basename(fp).replace("_air_quality_2014_2025.csv", "")
        if key not in COUNTRY_MAP:
            continue
        pais_pt, pais_en, iso3 = COUNTRY_MAP[key]
        df = pd.read_csv(fp)
        df = df.rename(columns={df.columns[0]: "Regiao"})
        df = df.rename(columns=RENAME_MAP)
        df["Pais"] = pais_pt
        df["Pais_EN"] = pais_en
        df["ISO3"] = iso3
        frames.append(df)

    full = pd.concat(frames, ignore_index=True)
    full["Data"] = pd.to_datetime(full["Data"])
    full["Ano"] = full["Data"].dt.year
    full["Mes"] = full["Data"].dt.month

    # Classificação padronizada do AQI (faixas numéricas EPA), pois cada país
    # usa rótulos locais distintos (ex: Índia: "Satisfactory/Poor", China:
    # "Excellent/Lightly Polluted") embora sigam as mesmas faixas numéricas.
    bins = [-np.inf, 50, 100, 150, 200, 300, np.inf]
    full["Qualidade_Ar"] = pd.cut(full["AQI"], bins=bins, labels=AQI_ORDER)

    return full


df_raw = load_data()

# =============================================================================
# CABEÇALHO / ESTILO CUSTOMIZADO
# =============================================================================
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    html, body, [class*="css"]  {{
        font-family: 'Poppins', sans-serif;
    }}
    .stApp {{
        background-color: {GRAY_BG};
    }}
    .main-header {{
        background: linear-gradient(120deg, {NAVY_DARK} 0%, {NAVY} 100%);
        padding: 28px 36px;
        border-radius: 14px;
        margin-bottom: 22px;
        color: white;
    }}
    .main-header h1 {{
        font-size: 30px;
        font-weight: 700;
        margin: 0 0 4px 0;
        color: white;
    }}
    .main-header p {{
        font-size: 14px;
        margin: 0;
        color: #C7CFE0;
    }}
    .kpi-card {{
        background-color: {CARD_BG};
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(20,30,60,0.08);
        text-align: center;
        border-bottom: 4px solid {GREEN};
    }}
    .kpi-value {{
        font-size: 26px;
        font-weight: 700;
        color: {NAVY};
        margin: 2px 0;
    }}
    .kpi-label {{
        font-size: 12.5px;
        color: {TEXT_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }}
    .section-banner {{
        background-color: {NAVY};
        color: white;
        padding: 9px 18px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 15px;
        margin: 6px 0 14px 0;
    }}
    .footer-note {{
        font-size: 12px;
        color: {TEXT_MUTED};
        text-align: center;
        margin-top: 30px;
        padding-top: 14px;
        border-top: 1px solid #DDE2EA;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="main-header">
        <h1>🌍 Poluição do Ar Mundial e Índice de Qualidade do Ar (AQI)</h1>
        <p>Análise exploratória global · 2014–2025 · 24 países em 5 continentes</p>
        <p>EQM2009 – Tópicos Especiais III · Profª Amanda Lemette · Aluna: Mônica Azevedo Monteiro</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================
def br_num(value, decimals=0):
    """Formata número no padrão pt-BR (ponto milhar, vírgula decimal)."""
    if pd.isna(value):
        return "-"
    s = f"{value:,.{decimals}f}"
    s = s.replace(",", "§").replace(".", ",").replace("§", ".")
    return s


def label_with_unit(var):
    u = UNITS.get(var, "")
    base = VAR_LABELS.get(var, var)
    return f"{base} ({u})" if u else base


# =============================================================================
# BARRA LATERAL — FILTROS GLOBAIS
# =============================================================================
with st.sidebar:
    st.markdown("### 🔎 Filtros")

    paises_disponiveis = sorted(df_raw["Pais"].unique().tolist())
    paises_sel = st.multiselect(
        "País(es)", options=paises_disponiveis, default=paises_disponiveis
    )

    ano_min, ano_max = int(df_raw["Ano"].min()), int(df_raw["Ano"].max())
    intervalo_anos = st.slider(
        "Período (ano)", min_value=ano_min, max_value=ano_max,
        value=(ano_min, ano_max), step=1,
    )

    poluente_foco = st.selectbox(
        "Poluente em foco (gráficos de tendência)",
        options=POLLUTANTS, index=0,
        format_func=label_with_unit,
    )

    st.markdown("---")
    with st.expander("ℹ️ Sobre esta base de dados"):
        st.markdown(
            f"""
            **Características da base**
            - 24 países distribuídos em 5 continentes
            - {br_num(len(df_raw))} registros
            - Dados mensais de 2014 a 2025
            - 23 variáveis ambientais e socioeconômicas
            - Sem valores ausentes nas variáveis originais
            - Formato: CSV (UTF-8)

            **Nota metodológica:** a coluna `AQI_Bucket` original usa
            nomenclaturas locais distintas por país (ex.: Índia usa
            *Satisfactory/Poor*, China usa *Excellent/Lightly Polluted*).
            Para permitir comparação justa entre países, a categoria
            **Qualidade do Ar** exibida neste dashboard foi recalculada a
            partir do valor numérico do AQI, usando as faixas padrão:
            Boa (0–50), Moderada (51–100), Insalubre p/ Grupos Sensíveis
            (101–150), Insalubre (151–200), Muito Insalubre (201–300) e
            Perigosa (>300).

            **Fonte:** Kaggle – World Air Pollution & AQI Dataset (2014–2025)
            """
        )

if not paises_sel:
    st.warning("Selecione ao menos um país na barra lateral para visualizar os dados.")
    st.stop()

mask = (
    df_raw["Pais"].isin(paises_sel)
    & df_raw["Ano"].between(intervalo_anos[0], intervalo_anos[1])
)
df = df_raw[mask].copy()

if df.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# =============================================================================
# CARTÕES DE INDICADORES (KPIs)
# =============================================================================
n_paises = df["Pais"].nunique()
n_registros = len(df)
aqi_medio = df["AQI"].mean()
pct_insalubre = (df["Qualidade_Ar"].isin(["Insalubre", "Muito Insalubre", "Perigosa"])).mean() * 100
cidade_mais_poluida = df.groupby("Cidade")["AQI"].mean().idxmax() if not df.empty else "-"

kpi_cols = st.columns(5)
kpis = [
    ("🌎", f"{n_paises}", "Países selecionados"),
    ("🗂️", br_num(n_registros), "Registros no filtro"),
    ("📅", f"{intervalo_anos[0]}–{intervalo_anos[1]}", "Período analisado"),
    ("💨", br_num(aqi_medio, 1), "AQI médio"),
    ("⚠️", f"{br_num(pct_insalubre, 1)}%", "Registros insalubres+"),
]
for col, (icon, value, label) in zip(kpi_cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div style="font-size:22px;">{icon}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

# =============================================================================
# ABAS
# =============================================================================
tab1, tab2, tab3, tab4 = st.tabs(
    ["🌍 Visão Geral Global", "📈 Tendências Temporais", "🔬 Poluentes & Correlações", "🏙️ Países & Cidades"]
)

# -----------------------------------------------------------------------------
# TAB 1 — VISÃO GERAL GLOBAL
# -----------------------------------------------------------------------------
with tab1:
    st.markdown('<div class="section-banner">Distribuição global do AQI</div>', unsafe_allow_html=True)

    col_map, col_pie = st.columns([2, 1])

    with col_map:
        aqi_pais = df.groupby(["Pais", "ISO3"], as_index=False)["AQI"].mean()
        fig_map = px.choropleth(
            aqi_pais, locations="ISO3", color="AQI", hover_name="Pais",
            color_continuous_scale="RdYlGn_r",
            range_color=(aqi_pais["AQI"].min(), aqi_pais["AQI"].max()),
            labels={"AQI": "AQI médio"},
        )
        fig_map.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            geo=dict(showframe=False, showcoastlines=False, bgcolor="rgba(0,0,0,0)"),
            paper_bgcolor="rgba(0,0,0,0)",
            height=420,
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_pie:
        dist = df["Qualidade_Ar"].value_counts().reindex(AQI_ORDER).reset_index()
        dist.columns = ["Qualidade_Ar", "Contagem"]
        fig_pie = px.pie(
            dist, names="Qualidade_Ar", values="Contagem", hole=0.5,
            color="Qualidade_Ar", color_discrete_map=AQI_COLORS,
            category_orders={"Qualidade_Ar": AQI_ORDER},
        )
        fig_pie.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=420, legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('<div class="section-banner">Ranking de países por AQI médio</div>', unsafe_allow_html=True)
    ranking = df.groupby("Pais", as_index=False)["AQI"].mean().sort_values("AQI", ascending=True)
    fig_rank = px.bar(
        ranking, x="AQI", y="Pais", orientation="h",
        color="AQI", color_continuous_scale="RdYlGn_r",
        labels={"AQI": "AQI médio", "Pais": ""},
    )
    fig_rank.update_layout(height=max(380, 22 * len(ranking)), margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_rank, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2 — TENDÊNCIAS TEMPORAIS
# -----------------------------------------------------------------------------
with tab2:
    st.markdown('<div class="section-banner">Evolução do AQI ao longo do tempo (2014–2025)</div>', unsafe_allow_html=True)

    aqi_medio_global = df.groupby("Pais")["AQI"].mean().sort_values(ascending=False)
    default_top5 = aqi_medio_global.head(5).index.tolist()
    paises_comparar = st.multiselect(
        "Países para comparar nas séries temporais (recomendado: até 8)",
        options=sorted(df["Pais"].unique().tolist()),
        default=[p for p in default_top5 if p in df["Pais"].unique()],
    )

    serie = df[df["Pais"].isin(paises_comparar)] if paises_comparar else df
    serie_mensal = (
        serie.groupby([pd.Grouper(key="Data", freq="MS"), "Pais"], as_index=False)["AQI"]
        .mean()
    )
    fig_line = px.line(
        serie_mensal, x="Data", y="AQI", color="Pais",
        labels={"AQI": "AQI médio mensal", "Data": ""},
    )
    fig_line.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown(
        f'<div class="section-banner">Evolução de {label_with_unit(poluente_foco)} ao longo do tempo</div>',
        unsafe_allow_html=True,
    )
    serie_pol = (
        serie.groupby([pd.Grouper(key="Data", freq="MS"), "Pais"], as_index=False)[poluente_foco]
        .mean()
    )
    fig_pol = px.line(
        serie_pol, x="Data", y=poluente_foco, color="Pais",
        labels={poluente_foco: label_with_unit(poluente_foco), "Data": ""},
    )
    fig_pol.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_pol, use_container_width=True)

    st.markdown('<div class="section-banner">Sazonalidade média do AQI por mês</div>', unsafe_allow_html=True)
    sazonal = df.groupby("Mes", as_index=False)["AQI"].mean()
    meses_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    sazonal["Mes_label"] = sazonal["Mes"].apply(lambda m: meses_pt[m - 1])
    fig_saz = px.bar(
        sazonal, x="Mes_label", y="AQI",
        category_orders={"Mes_label": meses_pt},
        color="AQI", color_continuous_scale="RdYlGn_r",
        labels={"AQI": "AQI médio", "Mes_label": ""},
    )
    fig_saz.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
    st.plotly_chart(fig_saz, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 3 — POLUENTES & CORRELAÇÕES
# -----------------------------------------------------------------------------
with tab3:
    st.markdown('<div class="section-banner">Matriz de correlação</div>', unsafe_allow_html=True)

    vars_corr = st.multiselect(
        "Variáveis incluídas na matriz",
        options=ALL_NUMERIC_VARS, default=DEFAULT_CORR_VARS,
        format_func=label_with_unit,
    )

    if len(vars_corr) >= 2:
        corr = df[vars_corr].corr(numeric_only=True)
        corr_labels = [label_with_unit(v) for v in corr.columns]
        fig_corr = px.imshow(
            corr, x=corr_labels, y=corr_labels,
            color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
            text_auto=".2f", aspect="auto",
        )
        fig_corr.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Selecione ao menos duas variáveis para gerar a matriz de correlação.")

    st.markdown('<div class="section-banner">Dispersão entre duas variáveis</div>', unsafe_allow_html=True)
    col_x, col_y = st.columns(2)
    with col_x:
        var_x = st.selectbox("Variável X", options=SOCIOECON + METEO, index=1, format_func=label_with_unit)
    with col_y:
        var_y = st.selectbox("Variável Y", options=["AQI"] + POLLUTANTS, index=0, format_func=label_with_unit)

    amostra = df.sample(min(6000, len(df)), random_state=42) if len(df) > 6000 else df
    fig_scatter = px.scatter(
        amostra, x=var_x, y=var_y, color="Pais", opacity=0.55,
        labels={var_x: label_with_unit(var_x), var_y: label_with_unit(var_y)},
    )

    valid = amostra[[var_x, var_y]].dropna()
    if len(valid) > 2:
        coef = np.polyfit(valid[var_x], valid[var_y], 1)
        x_line = np.linspace(valid[var_x].min(), valid[var_x].max(), 50)
        y_line = coef[0] * x_line + coef[1]
        r = np.corrcoef(valid[var_x], valid[var_y])[0, 1]
        fig_scatter.add_trace(
            go.Scatter(x=x_line, y=y_line, mode="lines", name=f"Tendência (r={r:.2f})",
                        line=dict(color=NAVY_DARK, width=3, dash="dash"))
        )
    fig_scatter.update_layout(height=460, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown('<div class="section-banner">Concentração média de poluentes por país</div>', unsafe_allow_html=True)
    pol_sel = st.multiselect(
        "Poluentes a exibir", options=POLLUTANTS, default=["PM2_5", "PM10", "NO2", "SO2", "O3"],
        format_func=label_with_unit,
    )
    if pol_sel:
        pol_pais = df.groupby("Pais", as_index=False)[pol_sel].mean().melt(
            id_vars="Pais", var_name="Poluente", value_name="Concentração"
        )
        pol_pais["Poluente"] = pol_pais["Poluente"].map(VAR_LABELS)
        fig_pol_pais = px.bar(
            pol_pais, x="Pais", y="Concentração", color="Poluente", barmode="group",
        )
        fig_pol_pais.update_layout(height=440, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.3))
        st.plotly_chart(fig_pol_pais, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4 — PAÍSES & CIDADES
# -----------------------------------------------------------------------------
with tab4:
    st.markdown('<div class="section-banner">Cidades mais e menos poluídas (AQI médio)</div>', unsafe_allow_html=True)

    aqi_cidade = (
        df.groupby(["Pais", "Cidade"], as_index=False)["AQI"]
        .mean()
        .dropna()
    )
    aqi_cidade["Rotulo"] = aqi_cidade["Cidade"] + " (" + aqi_cidade["Pais"] + ")"

    col_top, col_bottom = st.columns(2)
    with col_top:
        st.caption("🔺 15 cidades com pior qualidade do ar")
        piores = aqi_cidade.sort_values("AQI", ascending=False).head(15)
        fig_piores = px.bar(
            piores.sort_values("AQI"), x="AQI", y="Rotulo", orientation="h",
            color="AQI", color_continuous_scale="Reds", labels={"AQI": "AQI médio", "Rotulo": ""},
        )
        fig_piores.update_layout(height=460, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
        st.plotly_chart(fig_piores, use_container_width=True)

    with col_bottom:
        st.caption("🔻 15 cidades com melhor qualidade do ar")
        melhores = aqi_cidade.sort_values("AQI", ascending=True).head(15)
        fig_melhores = px.bar(
            melhores.sort_values("AQI", ascending=False), x="AQI", y="Rotulo", orientation="h",
            color="AQI", color_continuous_scale="Greens_r", labels={"AQI": "AQI médio", "Rotulo": ""},
        )
        fig_melhores.update_layout(height=460, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
        st.plotly_chart(fig_melhores, use_container_width=True)

    st.markdown('<div class="section-banner">Tabela detalhada por região/cidade</div>', unsafe_allow_html=True)
    tabela = (
        df.groupby(["Pais", "Regiao", "Cidade"], as_index=False)
        .agg(
            Registros=("AQI", "count"),
            AQI_medio=("AQI", "mean"),
            PM2_5_medio=("PM2_5", "mean"),
            PM10_medio=("PM10", "mean"),
            CO2_medio=("CO2_Emission_MT", "mean"),
            Densidade_pop=("Population_Density_per_SqKm", "mean"),
        )
        .round(2)
        .sort_values("AQI_medio", ascending=False)
    )
    st.dataframe(tabela, use_container_width=True, height=380)

    csv_bytes = tabela.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 Baixar tabela filtrada (CSV)", data=csv_bytes,
        file_name="poluicao_ar_por_cidade.csv", mime="text/csv",
    )

# =============================================================================
# RODAPÉ
# =============================================================================
st.markdown(
    """
    <div class="footer-note">
        Fonte: Kaggle – World Air Pollution & AQI Dataset (2014–2025) ·
        Dashboard desenvolvido para a disciplina EQM2009 – Tópicos Especiais III (Doutorado)
    </div>
    """,
    unsafe_allow_html=True,
)
