import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. LISTAS PARA SIMULAÇÃO
materiais = ["Reagente Glicose HK", "Tubo Vácuo EDTA 4mL", "Kit PCR COVID-19"]
unidades = ["Lab SP", "Lab RJ", "Lab BH"]
responsaveis = ["Maria Souza", "João Silva", "Ana Costa"]
tipos_operacao = ["Compra", "Consumo", "Transferência"]

# 2. GERAR DATAS (ÚLTIMOS 3 MESES)
hoje = datetime.now()
datas = [hoje - timedelta(days=x) for x in range(90)]  # 90 dias = ~3 meses

# 3. CRIAR REGISTROS ALEATÓRIOS
dados = []
for i in range(1, 101):  # 100 registros (para exemplo rápido)
    material = np.random.choice(materiais)
    quantidade = np.random.randint(1, 50)
    tipo = np.random.choice(tipos_operacao)
    
    if tipo == "Consumo":
        quantidade = -quantidade  # Saídas são negativas
    
    dados.append({
        "ID": i,
        "Data": np.random.choice(datas).strftime("%d/%m/%Y"),
        "Material": material,
        "Quantidade": quantidade,
        "Tipo": tipo,
        "Unidade": "frascos" if "Reagente" in material else "unidades",
        "Responsável": np.random.choice(responsaveis),
        "Local": np.random.choice(unidades)
    })

# 4. CRIAR DATAFRAME E MOSTRAR TABELA
df = pd.DataFrame(dados)
print("\n📊 TABELA DE DADOS SIMULADOS (10 PRIMEIRAS LINHAS):")
print(df.head(10))  # Mostra apenas as primeiras linhas para não poluir o terminal

# 5. SALVAR EM CSV (OPCIONAL)
df.to_csv("controle_estoque.csv", index=False, encoding="utf-8-sig")
print("\n✅ Arquivo 'dados_dasa.csv' salvo!")
