from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

# Usar backend sem interface gráfica no Matplotlib
matplotlib.use("Agg")

app = Flask(__name__)

# Carregar os dados
df_animais = pd.read_csv("pesquisa_animais.csv")
df_saude = pd.read_csv("pesquisas_saude.csv")

# Ajustar nomes de colunas removendo espaços extras
df_animais.columns = df_animais.columns.str.strip()
df_saude.columns = df_saude.columns.str.strip()

# Renomear colunas para evitar problemas
df_animais.rename(columns={"adoção de animais: (Distrito Federal)": "Adocoes"}, inplace=True)

# Converter a coluna de ansiedade para numérico corretamente
df_saude["Indice_Ansiedade"] = pd.to_numeric(df_saude["0"], errors="coerce")

# Converter a coluna "Adocoes" para numérico, caso tenha valores errados
df_animais["Adocoes"] = pd.to_numeric(df_animais["Adocoes"], errors="coerce")

# Remover valores NaN após a conversão
df_saude.dropna(subset=["Indice_Ansiedade"], inplace=True)
df_animais.dropna(subset=["Adocoes"], inplace=True)

def gerar_grafico_adocao():
    """Gera um gráfico do interesse na adoção de animais ao longo do tempo."""
    plt.figure(figsize=(10, 5))  # Aumenta o tamanho do gráfico
    sns.lineplot(data=df_animais, x="Semana", y="Adocoes", marker="o")
    
    plt.xticks(rotation=45)  # Rotaciona os rótulos do eixo X
    plt.xlabel("Semana")
    plt.ylabel("Adoções")
    plt.title("Interesse na Adoção ao Longo do Tempo")
    
    plt.tight_layout()  # Ajusta para evitar cortes nos rótulos
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

def gerar_grafico_ansiedade():
    """Gera um gráfico do índice de ansiedade ao longo do tempo."""
    plt.figure(figsize=(10, 5))  # Aumenta o tamanho do gráfico
    sns.lineplot(data=df_saude, x="TOP", y="0", marker="o", color="red")

    plt.xticks(rotation=45)  # Rotaciona os rótulos do eixo X
    plt.xlabel("Semana")
    plt.ylabel("Índice de Ansiedade")
    plt.title("Evolução da Ansiedade ao Longo do Tempo")
    
    plt.tight_layout()  # Ajusta para evitar cortes nos rótulos
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

def calcular_estatisticas():
    """Calcula estatísticas gerais e a correlação entre adoção de pets e ansiedade."""
    
    # Converter a coluna para numérica, tratando valores inválidos
    df_saude["0"] = pd.to_numeric(df_saude["0"], errors="coerce")
    df_animais["Adocoes"] = pd.to_numeric(df_animais["Adocoes"], errors="coerce")

    # Média da ansiedade
    media_ansiedade = df_saude["0"].mean()
    if pd.isna(media_ansiedade):
        media_ansiedade = 0  # Se não houver valores válidos, definir como 0

    # Total de adoções
    total_adocoes = df_animais["Adocoes"].sum()
    if pd.isna(total_adocoes):
        total_adocoes = 0

    # Unindo os dados para calcular correlação
    df_combinado = pd.merge(df_animais, df_saude, left_on="Semana", right_on="TOP", how="inner")

    if not df_combinado.empty:
        correlacao = df_combinado["Adocoes"].corr(df_combinado["0"])
        if pd.isna(correlacao):
            correlacao = 0
    else:
        correlacao = 0  # Se não houver dados combinados, correlação = 0

    return {
        "Média da Ansiedade": round(media_ansiedade, 2),
        "Total de Adoções": int(total_adocoes),  # Garantir que seja int
        "Correlação Pets-Ansiedade": round(correlacao, 2)
    }


@app.route("/", methods=["GET"])
def index():
    grafico = gerar_grafico_adocao()
    grafico_ansiedade = gerar_grafico_ansiedade()
    estatisticas = calcular_estatisticas()

    return render_template("index.html",
                           grafico=grafico,
                           grafico_ansiedade=grafico_ansiedade,
                           estatisticas=estatisticas)

if __name__ == "__main__":
    app.run(debug=True)
