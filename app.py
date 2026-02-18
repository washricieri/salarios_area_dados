import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

px.defaults.template = "plotly_white"

# =====================================================
# ESTILO PERSONALIZADO
# =====================================================

st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        h1, h2, h3 {
            font-weight: 700;
        }
        .stMetric {
            background-color: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0px 3px 8px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# CARREGAMENTO DOS DADOS COM CACHE
# =====================================================

@st.cache_data
def load_data():
    return pd.read_csv(
        "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
    )

df = load_data()

# =====================================================
# SIDEBAR - FILTROS
# =====================================================

st.sidebar.header("🔎 Filtros")
st.sidebar.markdown("Refine sua análise utilizando os filtros abaixo:")

anos = st.sidebar.multiselect(
    "Ano",
    sorted(df["ano"].unique()),
    default=sorted(df["ano"].unique())
)

senioridades = st.sidebar.multiselect(
    "Senioridade",
    sorted(df["senioridade"].unique()),
    default=sorted(df["senioridade"].unique())
)

contratos = st.sidebar.multiselect(
    "Tipo de Contrato",
    sorted(df["contrato"].unique()),
    default=sorted(df["contrato"].unique())
)

tamanhos = st.sidebar.multiselect(
    "Tamanho da Empresa",
    sorted(df["tamanho_empresa"].unique()),
    default=sorted(df["tamanho_empresa"].unique())
)

# =====================================================
# APLICAÇÃO DOS FILTROS
# =====================================================

df_filtrado = df[
    (df["ano"].isin(anos)) &
    (df["senioridade"].isin(senioridades)) &
    (df["contrato"].isin(contratos)) &
    (df["tamanho_empresa"].isin(tamanhos))
]

# =====================================================
# TÍTULO E CONTEXTO DO PROJETO
# =====================================================

st.title("📊 Dashboard de Análise de Salários na Área de Dados")

st.markdown("""
### 🎯 Objetivo do Projeto

Este dashboard foi desenvolvido para analisar tendências salariais na área de dados,
identificando como fatores como **senioridade, tipo de contrato, localização e tamanho da empresa**
impactam a remuneração.

**Tecnologias utilizadas:**
- Python
- Pandas
- Streamlit
- Plotly
""")

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# =====================================================
# KPIs
# =====================================================

st.subheader("📌 Métricas Gerais (Salário anual em USD)")

salario_medio = df_filtrado["usd"].mean()
salario_maximo = df_filtrado["usd"].max()
total_registros = df_filtrado.shape[0]
cargo_mais_frequente = (
    df_filtrado["cargo"].mode().iloc[0]
    if not df_filtrado["cargo"].mode().empty
    else "-"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Salário Médio", f"${salario_medio:,.0f}")
col2.metric("🏆 Salário Máximo", f"${salario_maximo:,.0f}")
col3.metric("📊 Total de Registros", f"{total_registros:,}")
col4.metric("👔 Cargo Mais Frequente", cargo_mais_frequente)

st.divider()

# =====================================================
# INSIGHTS AUTOMÁTICOS
# =====================================================

st.subheader("🧠 Principais Insights")

top_cargos = (
    df_filtrado.groupby("cargo")["usd"]
    .mean()
    .nlargest(10)
    .sort_values()
    .reset_index()
)

col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    📈 O cargo com maior média salarial entre os 10 principais é:
    **{top_cargos.iloc[-1]['cargo']}**

    💵 Média salarial desse cargo:
    **${top_cargos.iloc[-1]['usd']:,.0f}**
    """)

with col2:
    dispersao = salario_maximo - salario_medio
    st.success(f"""
    💰 A diferença entre o salário máximo e o salário médio é de:

    **${dispersao:,.0f}**

    Isso indica uma alta dispersão salarial no mercado.
    """)

st.divider()

# =====================================================
# GRÁFICOS
# =====================================================

st.subheader("📈 Análises Visuais")

col1, col2 = st.columns(2)

with col1:
    fig_cargos = px.bar(
        top_cargos,
        x="usd",
        y="cargo",
        orientation="h",
        labels={"usd": "Média salarial anual (USD)", "cargo": ""},
        title="Top 10 cargos por salário médio"
    )
    fig_cargos.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_cargos, use_container_width=True)

with col2:
    fig_hist = px.histogram(
        df_filtrado,
        x="usd",
        nbins=30,
        title="Distribuição de Salários",
        labels={"usd": "Faixa salarial (USD)"}
    )
    fig_hist.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_hist, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    remoto = (
        df_filtrado["remoto"]
        .value_counts()
        .rename_axis("tipo_trabalho")
        .reset_index(name="quantidade")
    )

    fig_remoto = px.pie(
        remoto,
        names="tipo_trabalho",
        values="quantidade",
        hole=0.5,
        title="Proporção dos Tipos de Trabalho"
    )
    fig_remoto.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_remoto, use_container_width=True)

with col4:
    df_ds = df_filtrado[df_filtrado["cargo"] == "Data Scientist"]

    if not df_ds.empty:
        media_pais = df_ds.groupby("residencia_iso3")["usd"].mean().reset_index()

        fig_paises = px.choropleth(
            media_pais,
            locations="residencia_iso3",
            color="usd",
            color_continuous_scale="Blues",
            title="Salário Médio de Cientista de Dados por País",
        )
        fig_paises.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_paises, use_container_width=True)
    else:
        st.info("Nenhum registro encontrado para Data Scientist.")

st.divider()

# =====================================================
# TABELA DETALHADA
# =====================================================

st.subheader("📄 Dados Detalhados")
st.dataframe(df_filtrado, use_container_width=True, height=400)

