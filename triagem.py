import pandas as pd
import matplotlib.pyplot as plt
import sqlite3 

def principal():
    print("Iniciando processamento de chamados de telemetria e frota...")
    
    try:
        df = pd.read_csv('chamados.csv')
    except FileNotFoundError:
        print("Erro: Arquivo 'chamados.csv' não encontrado.")
        return

    def categorizar_chamado(descricao):
        texto = str(descricao).lower()
        if any(p in texto for p in ['sinal', 'gps', 'rastreador', 'posição']):
            return 'Telemetria/GPS'
        elif any(p in texto for p in ['login', 'senha', 'acesso']):
            return 'Autenticação'
        elif any(p in texto for p in ['quebrou', 'tela', 'hardware', 'bateria']):
            return 'Hardware'
        else:
            return 'Dúvidas Gerais'

    df['Categoria'] = df['Descricao'].apply(categorizar_chamado)
    
    # INTEGRAÇÃO COM BANCO DE DADOS (SQL)
    print("Conectando ao banco de dados SQLite...")
    conexao = sqlite3.connect('logistica_suporte.db')
    
    df.to_sql('historico_chamados', conexao, if_exists='replace', index=False)
    
    print("\n--- Validação via Consulta SQL ---")
    resultado_sql = pd.read_sql("SELECT Categoria, COUNT(*) as Total FROM historico_chamados GROUP BY Categoria", conexao)
    print(resultado_sql)
    
    conexao.close() 
    print("Dados armazenados no banco de dados com sucesso.")
    
# gera o gráfico visual
    contagem = df['Categoria'].value_counts()
    plt.figure(figsize=(10, 6))
    contagem.plot(kind='bar', color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    
    plt.title('Triagem Automatizada de Chamados - Logística', fontsize=14, fontweight='bold')
    plt.xlabel('Categoria do Incidente', fontsize=12)
    plt.ylabel('Quantidade de Chamados', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig('resumo_triagem.png', bbox_inches='tight')
    print("\nProcesso finalizado! Imagem 'resumo_triagem.png' atualizada.")

if __name__ == "__main__":
    principal()