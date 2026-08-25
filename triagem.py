import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import os
import platform
from email.message import EmailMessage 

# teste de rede (infraestrutura)
def testar_conexao(host):
    print(f"Testando conexão com o servidor central ({host})...")
    parametro = '-n' if platform.system().lower() == 'windows' else '-c'
    comando = f"ping {parametro} 1 {host} > nul 2>&1" if platform.system().lower() == 'windows' else f"ping {parametro} 1 {host} > /dev/null 2>&1"
    
    if os.system(comando) == 0:
        print("✅ Servidor ONLINE. Iniciando processamento...\n")
        return True
    else:
        print("❌ ALERTA CRÍTICO: Servidor OFFLINE. Processamento abortado.\n")
        return False

# notificação por e-mail
def enviar_alerta_email(total_chamados):
    """
    Constrói a estrutura do e-mail e simula o envio SMTP para
    garantir a segurança das credenciais no repositório público.
    """
    msg = EmailMessage()
    msg['Subject'] = f"⚠️ Alerta de Operação: {total_chamados} incidentes registrados"
    msg['From'] = 'automacao.ti@dundermifflin.com'
    msg['To'] = 'michael.scott@dundermifflin.com' 
    
    corpo_email = f"""
    Olá equipe de gestão,
    
    O sistema automatizado concluiu a triagem diária e detectou {total_chamados} chamados logísticos.
    Os dados já foram salvos no banco de dados SQLite e o dashboard atualizado foi gerado no servidor.
    
    Atenciosamente,
    Sistema de Automação - Infraestrutura TI
    """
    msg.set_content(corpo_email)
    
    # simulação do terminal 
    print("\n--- SIMULAÇÃO DE ENVIO DE E-MAIL (SMTP) ---")
    print(f"De: {msg['From']}")
    print(f"Para: {msg['To']}")
    print(f"Assunto: {msg['Subject']}")
    print("Status: 📧 E-mail enviado com sucesso para a gestão!")
    print("-------------------------------------------\n")

def principal():
    if not testar_conexao("8.8.8.8"):
        return 
    
    try:
        df = pd.read_csv('chamados.csv')
    except FileNotFoundError:
        print("Erro: Arquivo 'chamados.csv' não encontrado.")
        return

    def categorizar_chamado(descricao):
        texto = str(descricao).lower()
        if any(p in texto for p in ['sinal', 'gps', 'rastreador', 'posição', 'rota']):
            return 'Telemetria/GPS'
        elif any(p in texto for p in ['login', 'senha', 'acesso', 'intranet']):
            return 'Autenticação'
        elif any(p in texto for p in ['quebrou', 'tela', 'hardware', 'bateria', 'empilhadeira']):
            return 'Hardware'
        else:
            return 'Dúvidas Gerais'

    df['Categoria'] = df['Descricao'].apply(categorizar_chamado)
    
    conexao = sqlite3.connect('logistica_suporte.db')
    df.to_sql('historico_chamados', conexao, if_exists='replace', index=False)
    conexao.close()
    
    contagem = df['Categoria'].value_counts()
    plt.figure(figsize=(10, 6))
    
    # cores do sistema
    contagem.plot(kind='bar', color=['#5C4033', '#8B5A2B', '#6B8E23', '#CD853F'])
    
    plt.title('Triagem Automatizada de Chamados - Logística', fontsize=14, fontweight='bold')
    plt.xlabel('Categoria do Incidente', fontsize=12)
    plt.ylabel('Quantidade de Chamados', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig('resumo_triagem.png', bbox_inches='tight')
    
    # chama a função de e-mail passando a quantidade total de linhas (chamados) lidas
    enviar_alerta_email(len(df))
    print("Processo 100% finalizado!")

if __name__ == "__main__":
    principal()