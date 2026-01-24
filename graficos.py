import matplotlib.pyplot as plt
import pandas as pd
import os
import glob

def gerar_grafico_liga(nome_liga, anos):
    dados_times = {}

    for ano in anos:
        caminho_arquivo = f"{nome_liga}/tabela_{nome_liga}_{ano}.json"
        
        # Check if file exists to process
        if os.path.exists(caminho_arquivo):
            try:
                df = pd.read_json(caminho_arquivo)
                
                # Check for required columns
                if 'nome' in df.columns and 'gols_pro' in df.columns:
                    for index, row in df.iterrows():
                        nome_time = row['nome']
                        gols = row['gols_pro']
                        
                        if nome_time not in dados_times:
                            dados_times[nome_time] = {'total_goals': 0, 'seasons': 0}
                        
                        dados_times[nome_time]['total_goals'] += gols
                        dados_times[nome_time]['seasons'] += 1
            except Exception as e:
                print(f"Erro ao ler {caminho_arquivo}: {e}")

    if not dados_times:
        print(f"Nenhum dado encontrado para {nome_liga}.")
        return

    # Calculate averages
    media_times = []
    for time, dados in dados_times.items():
        media = dados['total_goals'] / dados['seasons']
        media_times.append({'time': time, 'media_gols': media})
    
    # Create DataFrame
    df_media = pd.DataFrame(media_times)
    
    # Sort and take Top 5
    top_5 = df_media.sort_values(by='media_gols', ascending=False).head(5)
    
    # Start Plotting
    plt.figure(figsize=(10, 6))
    bars = plt.bar(top_5['time'], top_5['media_gols'], color='teal')
    
    plt.title(f'Top 5 Ataques (Média) - {nome_liga}', fontsize=14)
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Média de Gols por Temporada', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    plt.bar_label(bars, fmt='%.1f')
    plt.tight_layout()
    
    filename = f"grafico_media_{nome_liga}.png"
    plt.savefig(filename)
    print(f"Gráfico salvo para {nome_liga} como: {filename}")
    plt.close()

def processar_todas_ligas():
    anos = [2023, 2024, 2025]
    
    # Discover leagues
    ligas_encontradas = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and item not in ['__pycache__', '.git', '.gemini']:
            # Check if it has at least one matching JSON file
            if glob.glob(f"{item}/tabela_{item}_*.json"):
                ligas_encontradas.append(item)
    
    print(f"Encontradas {len(ligas_encontradas)} ligas: {ligas_encontradas}")
    
    for liga in ligas_encontradas:
        print(f"Gerando gráfico para: {liga}...")
        gerar_grafico_liga(liga, anos)

if __name__ == "__main__":
    processar_todas_ligas()
