import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(page_title="Painel de Alertas DASA", layout="wide")
st.title("📊 Painel de Alertas - Anomalias em Estoque")

# 1. Carregar dados (substitua pelo seu CSV)
@st.cache_data
def load_data():
    # Exemplo com dados simulados (substitua pelo seu CSV real)
    df = pd.read_csv("dados_dasa.csv")  
    # Converter Quantidade para numérico (caso não esteja)
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce")
    return df

df = load_data()

# 2. Sidebar (filtros)
st.sidebar.header("Filtros")
material_selecionado = st.sidebar.selectbox(
    "Material", 
    options=["Todos"] + list(df["Material"].unique()))
show_outliers_only = st.sidebar.checkbox("Mostrar apenas outliers", True)

# 3. Cálculo de outliers (Z-score e IQR)
def calculate_outliers(df):
    # Z-score
    df["Z-score"] = np.abs(stats.zscore(df["Quantidade"]))
    df["Outlier (Z-score)"] = df["Z-score"] > 3
    
    # IQR
    Q1 = df["Quantidade"].quantile(0.25)
    Q3 = df["Quantidade"].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    df["Outlier (IQR)"] = (df["Quantidade"] < limite_inferior) | (df["Quantidade"] > limite_superior)
    
    return df

df = calculate_outliers(df)

# 4. Aplicar filtros
if material_selecionado != "Todos":
    df = df[df["Material"] == material_selecionado]
if show_outliers_only:
    df = df[df["Outlier (Z-score)"] | df["Outlier (IQR)"]]

# 5. Métricas resumidas
col1, col2, col3 = st.columns(3)
col1.metric("Total de Registros", len(df))
col2.metric("Outliers (Z-score)", df["Outlier (Z-score)"].sum())
col3.metric("Outliers (IQR)", df["Outlier (IQR)"].sum())

# 6. Tabela de alertas
st.subheader("🔍 Registros Anômalos")
st.dataframe(df.sort_values("Z-score", ascending=False))

# 7. Gráficos
st.subheader("📈 Visualização")
fig, ax = plt.subplots(figsize=(10, 6))
df["Quantidade"].plot(kind="box", vert=False, ax=ax)
ax.set_title("Distribuição das Quantidades (Boxplot)")
st.pyplot(fig)

# 8. Download dos resultados
st.sidebar.download_button(
    label="Baixar dados filtrados (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="alertas_estoque_dasa.csv"
)