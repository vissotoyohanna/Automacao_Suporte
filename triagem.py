import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import os
import platform

# function to test network connectivity
def testar_conexao(host):
    print(f"Testando conexão com o servidor central ({host})...")
    
    # fefine the ping parameter (-n for Windows, -c for Linux/Mac)
    parametro = '-n' if platform.system().lower() == 'windows' else '-c'
    comando = f"ping {parametro} 1 {host} > nul 2>&1" if platform.system().lower() == 'windows' else f"ping {parametro} 1 {host} > /dev/null 2>&1"
    
    # executes the command in the OS
    resposta = os.system(comando)
    
    if resposta == 0:
        print("✅ Servidor ONLINE. Iniciando processamento de dados...\n")
        return True
    else:
        print("❌ ALERTA CRÍTICO: Servidor OFFLINE. Processamento abortado para evitar perda de dados.\n")
        return False

def principal():
    # verifica a infraestrutura antes de qualquer coisa
    servidor_operacao = "8.8.8.8" # simulando o servidor de banco de dados/GPS
    
    if not testar_conexao(servidor_operacao):
        return # para a execução do código aqui se não houver rede
    
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
    
    # database Integration
    conexao = sqlite3.connect('logistica_suporte.db')
    df.to_sql('historico_chamados', conexao, if_exists='replace', index=False)
    conexao.close()
    print("Dados armazenados no banco de dados SQLite.")
    
    # visual dashboard
    contagem = df['Categoria'].value_counts()
    plt.figure(figsize=(10, 6))
    contagem.plot(kind='bar', color=['#5C4033', '#8B5A2B', '#6B8E23', '#CD853F'])
    
    plt.title('Triagem Automatizada de Chamados - Logística', fontsize=14, fontweight='bold')
    plt.xlabel('Categoria do Incidente', fontsize=12)
    plt.ylabel('Quantidade de Chamados', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig('resumo_triagem.png', bbox_inches='tight')
    print("Processo finalizado! Imagem 'resumo_triagem.png' atualizada.")

if __name__ == "__main__":
    principal()