import pandas as pd

# Carregar os dados
df_animais = pd.read_csv("pesquisa_animais.csv")
df_saude = pd.read_csv("pesquisas_saude.csv")

# Remover espaços extras nos nomes das colunas
df_animais.columns = df_animais.columns.str.strip()
df_saude.columns = df_saude.columns.str.strip()

# Exibir os nomes das colunas para verificar se estão corretos
print("Colunas de df_animais:", df_animais.columns)
print("Colunas de df_saude:", df_saude.columns)
