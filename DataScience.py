import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy import stats
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

# Configurações da página
st.set_page_config(page_title="Painel de Gestão de Estoque", layout="wide", page_icon="📊")

# --- FUNÇÕES AUXILIARES ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv("controle_estoque.csv")
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)
    return df

def calcular_kpis(df):
    # Top 10 materiais com maior variação (coeficiente de variação)
    cv = df.groupby('Material')['Quantidade'].agg(['mean', 'std'])
    cv['CV'] = (cv['std'] / cv['mean']) * 100
    top_var = cv.nlargest(10, 'CV').reset_index()
    return top_var

def enviar_alerta_email(destinatario, assunto, mensagem):
    try:
        msg = EmailMessage()
        msg['Subject'] = assunto
        msg['From'] = st.secrets["email"]["username"]
        msg['To'] = destinatario
        msg.set_content(mensagem)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(st.secrets["email"]["username"], 
                      st.secrets["email"]["password"])
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")
        return False

def simular_impacto_financeiro(df_filtrado):
    """Função para simular o impacto da falta de registros"""
    with st.expander("📉 Simulação de Impacto Financeiro", expanded=True):
        st.write("""
        **Cenário de Falta de Registros**:
        - Calcula custos operacionais devido a registros incompletos
        - Compara cenários com e sem detecção de anomalias
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            custo_hora_parada = st.number_input("Custo por hora de parada (R$)", 
                                              min_value=50, value=150, step=10)
        with col2:
            horas_paradas_por_falta = st.number_input("Horas paradas por falta", 
                                                    min_value=1, value=8, step=1)
        
        # Identificar dias sem registros
        dias_unicos = pd.to_datetime(df_filtrado['Data']).dt.date.unique()
        todos_dias = pd.date_range(start=min(dias_unicos), end=max(dias_unicos))
        dias_faltantes = [d for d in todos_dias if d.date() not in dias_unicos]
        
        # Calcular impactos
        if dias_faltantes:
            custo_paradas = len(dias_faltantes) * horas_paradas_por_falta * custo_hora_parada
            
            # Identificar materiais com consumo zero mas com estoque (possível falha de registro)
            if 'Saldo' in df_filtrado.columns:
                falhas_registro = df_filtrado[(df_filtrado['Quantidade'] == 0) & 
                                            (df_filtrado['Saldo'] > 0)]
                custo_falhas = len(falhas_registro) * custo_hora_parada * 4  # 4 horas por falha estimada
            else:
                custo_falhas = 0
            
            total_impacto = custo_paradas + custo_falhas
            
            # Exibir resultados
            st.error(f"⚠️ **Dias sem registros completos:** {len(dias_faltantes)}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Custo de Paradas", f"R$ {custo_paradas:,.2f}")
            with col2:
                st.metric("Custo de Falhas", f"R$ {custo_falhas:,.2f}")
            with col3:
                st.metric("Impacto Total Estimado", f"R$ {total_impacto:,.2f}", delta="-Perda")
            
            # Gráfico comparativo
            fig = px.bar(
                x=['Paradas', 'Falhas de Registro', 'Total'],
                y=[custo_paradas, custo_falhas, total_impacto],
                labels={'x': 'Tipo de Custo', 'y': 'Valor (R$)'},
                title="Impacto Financeiro da Falta de Registros",
                color=['Paradas', 'Falhas', 'Total'],
                color_discrete_map={'Paradas':'red', 'Falhas':'orange', 'Total':'darkred'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ Nenhum dia sem registros detectado no período filtrado")

# --- INTERFACE PRINCIPAL ---
def main():
    st.title("📊 Painel de Gestão de Estoque Inteligente")
    
    # Carregar dados
    df = carregar_dados()
    
    # --- BARRA LATERAL COM FILTROS ---
    with st.sidebar:
        st.header("⚙️ Filtros e Configurações")
        
        # Filtro por período
        data_min = df['Data'].min().date()
        data_max = df['Data'].max().date()
        periodo = st.date_input("Período", 
                              value=(data_min, data_max),
                              min_value=data_min,
                              max_value=data_max)
        
        # Filtros adicionais
        unidade = st.multiselect("Unidade", options=df['Local'].unique())
        material = st.multiselect("Material", options=df['Material'].unique())
        
        # Configurações de alerta
        st.header("🔔 Configuração de Alertas")
        limite_desvio = st.slider("Limite de desvio padrão para alerta", 1.0, 5.0, 2.0)
        email_gestor = st.text_input("E-mail do gestor para alertas")
        
        # Testar notificação
        if st.button("Testar Notificação"):
            if enviar_alerta_email(email_gestor, "TESTE - Alerta de Estoque", 
                                 "Este é um teste do sistema de alertas."):
                st.success("E-mail de teste enviado com sucesso!")

    # Aplicar filtros
    if len(periodo) == 2:
        df_filtrado = df[(df['Data'].dt.date >= periodo[0]) & 
                        (df['Data'].dt.date <= periodo[1])]
    else:
        df_filtrado = df.copy()
        
    if unidade:
        df_filtrado = df_filtrado[df_filtrado['Local'].isin(unidade)]
    if material:
        df_filtrado = df_filtrado[df_filtrado['Material'].isin(material)]

    # --- SEÇÃO DE KPIs ---
    st.header("📈 Indicadores-Chave (KPIs)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        total_mov = df_filtrado['Quantidade'].abs().sum()
        st.metric("Total Movimentado", f"{total_mov:,} unidades")
    
    with col2:
        materiais_unicos = df_filtrado['Material'].nunique()
        st.metric("Materiais Únicos", materiais_unicos)
    
    with col3:
        media_diaria = df_filtrado.groupby('Data')['Quantidade'].sum().mean()
        st.metric("Média Diária", f"{media_diaria:,.1f} unidades")

    # --- SIMULADOR DE IMPACTO FINANCEIRO ---
    simular_impacto_financeiro(df_filtrado)

    # Top 10 materiais com maior variação
    st.subheader("📊 Top 10 Materiais com Maior Variação")
    top_var = calcular_kpis(df_filtrado)
    fig_kpi = px.bar(top_var, x='Material', y='CV', 
                    color='CV', color_continuous_scale='RdYlGn_r',
                    title="Coeficiente de Variação por Material")
    st.plotly_chart(fig_kpi, use_container_width=True)

    # --- SEÇÃO DE ALERTAS ---
    st.header("🚨 Alertas Automatizados")
    
    # Alertas baseados em desvio padrão
    alertas = []
    for material in df_filtrado['Material'].unique():
        df_mat = df_filtrado[df_filtrado['Material'] == material]
        media = df_mat['Quantidade'].mean()
        std = df_mat['Quantidade'].std()
        
        ultimo_valor = df_mat.iloc[-1]['Quantidade']
        if abs(ultimo_valor) > (media + limite_desvio * std):
            alertas.append({
                'Material': material,
                'Valor': ultimo_valor,
                'Média': media,
                'Desvio Padrão': std,
                'Tipo': 'Alto' if ultimo_valor > 0 else 'Baixo'
            })

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        
        # Aplicar cores baseadas na urgência
        def colorizar(val):
            color = 'red' if val > 0 else 'orange'
            return f'color: {color}'
        
        st.dataframe(df_alertas.style.applymap(colorizar, subset=['Valor']), 
                    use_container_width=True)
        
        # Botão para enviar alertas por e-mail
        if email_gestor and st.button("Enviar Alertas por E-mail"):
            mensagem = "Alertas de Estoque:\n\n" + \
                      "\n".join([f"{a['Material']}: {a['Valor']} (Média: {a['Média']:.1f} ± {a['Desvio Padrão']:.1f})" 
                               for a in alertas])
            
            if enviar_alerta_email(email_gestor, "ALERTA - Anomalias no Estoque", mensagem):
                st.success("Alertas enviados por e-mail!")
    else:
        st.success("✅ Nenhum alerta crítico detectado")

    # --- ANÁLISE DETALHADA ---
    st.header("🔍 Análise Detalhada")
    
    tab1, tab2 = st.tabs(["Movimentação por Material", "Tendência Temporal"])
    
    with tab1:
        fig_mat = px.bar(df_filtrado.groupby(['Material', 'Tipo'])['Quantidade']
                        .sum().reset_index(),
                        x='Material', y='Quantidade', color='Tipo',
                        barmode='group', title="Movimentação por Material")
        st.plotly_chart(fig_mat, use_container_width=True)
    
    with tab2:
        df_tempo = df_filtrado.groupby(['Data', 'Tipo'])['Quantidade'].sum().reset_index()
        fig_temp = px.line(df_tempo, x='Data', y='Quantidade', color='Tipo',
                          title="Tendência Temporal", markers=True)
        st.plotly_chart(fig_temp, use_container_width=True)

# Executar aplicação
if __name__ == "__main__":
    main()
