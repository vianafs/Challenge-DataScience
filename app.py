import streamlit as st
import pandas as pd
import plotly.express as px

# Configurações da página
st.set_page_config(page_title="Controle de Estoque de Materiais", layout="wide")

# Carregar os dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv("controle_estoque.csv", sep=",")
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)
    return df

df = carregar_dados()

# Título
st.title("📦 Controle de Estoque de Materiais")

# Filtros
with st.sidebar:
    st.header("🔎 Filtros")
    materiais = st.multiselect("Material", df["Material"].unique(), default=df["Material"].unique())
    locais = st.multiselect("Local", df["Local"].unique(), default=df["Local"].unique())
    responsaveis = st.multiselect("Responsável", df["Responsável"].unique(), default=df["Responsável"].unique())
    tipos = st.multiselect("Tipo de Movimento", df["Tipo"].unique(), default=df["Tipo"].unique())
    df_filtrado = df[
        df["Material"].isin(materiais) &
        df["Local"].isin(locais) &
        df["Responsável"].isin(responsaveis) &
        df["Tipo"].isin(tipos)
    ]

# Mostrar dados
st.subheader("📋 Dados Filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# Gráfico de movimentação por material
st.subheader("📈 Movimentação por Material")
grafico_material = df_filtrado.groupby(["Material", "Tipo"])["Quantidade"].sum().reset_index()
fig1 = px.bar(grafico_material, x="Material", y="Quantidade", color="Tipo", barmode="group")
st.plotly_chart(fig1, use_container_width=True)

# Gráfico de movimentação ao longo do tempo
st.subheader("📊 Movimentação ao Longo do Tempo")
grafico_tempo = df_filtrado.groupby(["Data", "Tipo"])["Quantidade"].sum().reset_index()
fig2 = px.line(grafico_tempo, x="Data", y="Quantidade", color="Tipo", markers=True)
st.plotly_chart(fig2, use_container_width=True)
