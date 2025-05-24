import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. LISTA AMPLIADA DE MATERIAIS (30 tipos diferentes)
materiais = [
    "Reagente Glicose HK", "Tubo Vácuo EDTA 4mL", "Kit PCR COVID-19",
    "Seringa 10mL", "Agulha 25x7", "Luvas Latex M", "Luvas Latex G",
    "Máscara N95", "Álcool Gel 70%", "Swab Nasal", "Tubo Coleta 5mL",
    "Bandagem Estéril", "Gaze Estéril", "Tala Articulada", "Solução Salina",
    "Cateter Intravenoso", "Frasco Soro 500mL", "Bisturi Desc. #15",
    "Compressor Cirúrgico", "Touca Desc.", "Máscara Cirúrgica", "Avental Desc.",
    "Torneira 3 Vias", "Sonda Vesical", "Óxido Nitroso", "Anestésico Local",
    "Antisséptico Clorexidina", "Fio de Sutura", "Curativo Adesivo", "Termômetro Digital"
]

# 2. UNIDADES E RESPONSÁVEIS (ampliados)
unidades = ["Lab SP", "Lab RJ", "Lab BH", "Lab POA", "Lab Salvador", "Lab Recife", "Lab Brasília"]
responsaveis = ["Maria Souza", "João Silva", "Ana Costa", "Carlos Oliveira", "Fernanda Lima", 
               "Ricardo Santos", "Patrícia Mendes", "Lucas Pereira", "Juliana Almeida"]
tipos_operacao = ["Compra", "Consumo", "Transferência", "Ajuste", "Doação"]

# 3. GERAR DATAS (ÚLTIMOS 6 MESES para mais variação)
hoje = datetime.now()
datas = [hoje - timedelta(days=x) for x in range(180)]  # 180 dias = ~6 meses

# 4. CRIAR 500 REGISTROS COM SALDO SIMULADO
dados = []
saldo_atual = {material: np.random.randint(50, 200) for material in materiais}  # Estoque inicial variado

for i in range(1, 501):  # 500 registros
    material = np.random.choice(materiais)
    tipo = np.random.choice(tipos_operacao)
    
    # Quantidade varia conforme o tipo
    if tipo == "Compra":
        quantidade = np.random.randint(10, 100)
    elif tipo == "Consumo":
        quantidade = -np.random.randint(1, 30)
    else:  # Transferência/Ajuste/Doação
        quantidade = np.random.randint(-20, 20)
    
    # Atualiza saldo (não permite negativo)
    saldo_atual[material] = max(0, saldo_atual[material] + quantidade)
    
    # Define unidade de medida automaticamente
    if any(x in material for x in ["Reagente", "Solução", "Álcool", "Antisséptico"]):
        unidade_medida = "frascos"
    elif any(x in material for x in ["Tubo", "Seringa", "Swab", "Cateter"]):
        unidade_medida = "unidades"
    else:
        unidade_medida = np.random.choice(["unidades", "caixas", "pacotes"])
    
    dados.append({
        "ID": i,
        "Data": np.random.choice(datas).strftime("%d/%m/%Y"),
        "Material": material,
        "Quantidade": quantidade,
        "Saldo": saldo_atual[material],
        "Tipo": tipo,
        "Unidade": unidade_medida,
        "Responsável": np.random.choice(responsaveis),
        "Local": np.random.choice(unidades),
        "Lote": f"LOTE-{np.random.randint(202300, 202400)}"  # Novo campo!
    })

# 5. SALVAR CSV COM MAIS DETALHES
df = pd.DataFrame(dados)
df.to_csv("controle_estoque.csv", index=False, encoding="utf-8-sig")

# Verificação
print(f"✅ CSV gerado com {len(df)} registros!")
print(f"📦 Materiais distintos: {len(materiais)}")
print(f"🏢 Unidades: {len(unidades)}")
print(f"👤 Responsáveis: {len(responsaveis)}")
print("📅 Período coberto:", df['Data'].min(), "a", df['Data'].max())
