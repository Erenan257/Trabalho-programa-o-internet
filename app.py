from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

matplotlib.use("Agg")

app = Flask(__name__)

df_animais = pd.read_csv("pesquisa_animais.csv")
df_saude = pd.read_csv("pesquisas_saude.csv")

df_animais.columns = df_animais.columns.str.strip()
df_saude.columns = df_saude.columns.str.strip()

df_animais.rename(columns={"adoção de animais: (Distrito Federal)": "Adocoes"}, inplace=True)

df_saude["Indice_Ansiedade"] = pd.to_numeric(df_saude["0"], errors="coerce")

df_animais["Adocoes"] = pd.to_numeric(df_animais["Adocoes"], errors="coerce")

df_saude.dropna(subset=["Indice_Ansiedade"], inplace=True)
df_animais.dropna(subset=["Adocoes"], inplace=True)

def gerar_grafico_adocao():
    """Gera um gráfico do interesse na adoção de animais ao longo do tempo."""
    plt.figure(figsize=(10, 5))  
    sns.lineplot(data=df_animais, x="Semana", y="Adocoes", marker="o")
    
    plt.xticks(rotation=45)  
    plt.xlabel("Semana")
    plt.ylabel("Adoções")
    plt.title("Interesse na Adoção ao Longo do Tempo")
    
    plt.tight_layout()  
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

def gerar_grafico_ansiedade():
    """Gera um gráfico do índice de ansiedade ao longo do tempo."""
    plt.figure(figsize=(10, 5))  
    sns.lineplot(data=df_saude, x="TOP", y="0", marker="o", color="red")

    plt.xticks(rotation=45)  
    plt.xlabel("Semana")
    plt.ylabel("Índice de Ansiedade")
    plt.title("Evolução da Ansiedade ao Longo do Tempo")
    
    plt.tight_layout()  
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

def calcular_estatisticas():
    """Calcula estatísticas gerais e a correlação entre adoção de pets e ansiedade."""
    

    df_saude["0"] = pd.to_numeric(df_saude["0"], errors="coerce")
    df_animais["Adocoes"] = pd.to_numeric(df_animais["Adocoes"], errors="coerce")

    media_ansiedade = df_saude["0"].mean()
    if pd.isna(media_ansiedade):
        media_ansiedade = 0  

   
    total_adocoes = df_animais["Adocoes"].sum()
    if pd.isna(total_adocoes):
        total_adocoes = 0


    df_combinado = pd.merge(df_animais, df_saude, left_on="Semana", right_on="TOP", how="inner")

    if not df_combinado.empty:
        correlacao = df_combinado["Adocoes"].corr(df_combinado["0"])
        if pd.isna(correlacao):
            correlacao = 0
    else:
        correlacao = 0  

    return {
        "Média da Ansiedade": round(media_ansiedade, 2),
        "Total de Adoções": int(total_adocoes),  
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
