import pandas as pd
import json
import os

def calcular_pontuacao_publico(codigo_liga, temporada):
    """
    Calcula a pontuação baseada na média de público.
    1º lugar = 20 pontos, 2º = 19, ..., 20º = 1, outros = 0.
    """

    # Mapeamento de Código para Nome da Pasta e Nome do Arquivo
    mapa_ligas = {
        "BSA": {"pasta": "campeonato brasileiro serie a", "nome_arquivo": "Campeonato Brasileiro Série A"},
        "PL": {"pasta": "premier league", "nome_arquivo": "Premier League"},
        "FL1": {"pasta": "ligue1", "nome_arquivo": "Ligue 1"},
        "BL1": {"pasta": "bundesliga", "nome_arquivo": "Bundesliga"},
        "SA": {"pasta": "serie a", "nome_arquivo": "Serie A"},
        "PD": {"pasta": "laliga", "nome_arquivo": "La Liga"}
    }
    
    info_liga = mapa_ligas.get(codigo_liga)
    if not info_liga:
        print(f"Liga {codigo_liga} não encontrada.")
        return None
        
    pasta = info_liga["pasta"]
    nome_liga_arquivo = info_liga["nome_arquivo"]
    
    # Caminho do arquivo
    caminho_arquivo = f"media de publico por tmeporada/{pasta}/media_{nome_liga_arquivo}_{temporada}.json"
    
    if not os.path.exists(caminho_arquivo):
        print(f"Arquivo não encontrado: {caminho_arquivo}")
        return None
        
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            
        # Ordenar por Media_Publico decrescente
        # Garantir que Media_Publico seja numérico
        for time in dados:
             if isinstance(time['Media_Publico'], str):
                 time['Media_Publico'] = int(str(time['Media_Publico']).replace('.', '').replace(',', ''))
                 
        dados_ordenados = sorted(dados, key=lambda x: x['Media_Publico'], reverse=True)
        
        # Atribuir pontos
        pontos = 20
        for i, time in enumerate(dados_ordenados):
            if pontos > 0:
                time['Pontuacao'] = pontos
                pontos -= 1
            else:
                time['Pontuacao'] = 0
                
        return dados_ordenados
        
    except Exception as e:
        print(f"Erro ao processar pontuação de público: {e}")
        return None
    except Exception as e:
        print(f"Erro ao processar pontuação de público: {e}")
        return None

from funcoes import obter_dados_historicos, obter_dados_ligas

# Mapeamento para normalizar nomes de times (API -> Arquivo de Público)
# Chave: Nome na API (ou nome padronizado)
# Valor: Nome no arquivo de público (se diferente) ou vice-versa.
# Vamos usar o nome da API como padrão principal interna e mapear o do arquivo de público para ele.
# Ou melhor, normalizar ambos par um padrão comum.
# Dado que os dados da API são mais frequentes, vamos mapear PÚBLICO -> API.

NAME_MAPPING = {
    "SC Corinthians": "SC Corinthians Paulista",
    "Atlético Mineiro": "CA Mineiro",
    "Athletico Paranaense": "CA Paranaense",
    "Atlético Goianiense": "AC Goianiense",
    "São Paulo FC": "São Paulo FC", # Igual
    "Botafogo FR": "Botafogo FR", # Igual
    # Adicionar outros conforme necessidade
}

def normalizar_nome(nome):
    return NAME_MAPPING.get(nome, nome)

def calcular_pontuacao_historica(codigo_liga, temporada_atual):
    """
    Calcula a pontuação baseada na média de posição das últimas 3 temporadas.
    1º lugar média = 20 pontos, ...
    """
    historico = obter_dados_historicos(codigo_liga, temporada_atual)
    if not historico:
        return []

    # Agrupar posições por time
    posicoes_times = {}
    
    for ano, dados in historico.items():
        for time_dado in dados:
            nome = time_dado['nome']
            posicao = time_dado['posicao']
            if nome not in posicoes_times:
                posicoes_times[nome] = []
            posicoes_times[nome].append(posicao)
    
    # Calcular média
    media_posicoes = []
    for nome, posicoes in posicoes_times.items():
        media = sum(posicoes) / len(posicoes)
        media_posicoes.append({'nome': nome, 'media_posicao': media})
        
    # Ordenar por média de posição (menor é melhor)
    media_posicoes_ordenada = sorted(media_posicoes, key=lambda x: x['media_posicao'])
    
    # Atribuir pontos
    pontos = 20
    for item in media_posicoes_ordenada:
        item['Pontuacao_Historica'] = max(pontos, 0)
        pontos -= 1
        
    return media_posicoes_ordenada

def calcular_pontuacao_atual(codigo_liga, temporada_atual):
    """
    Calcula a pontuação baseada na posição atual.
    1º lugar = 20 pontos, ...
    """
    dados_atuais = obter_dados_ligas(codigo_liga, temporada_atual)
    if not dados_atuais:
        return []
        
    # Dados já vêm com posição, mas vamos ordenar por pontos/posição para garantir
    # A API retorna ordenado por posição
    # Vamos criar uma lista simplificada
    
    lista_atual = []
    for time_dado in dados_atuais:
        lista_atual.append({
            'nome': time_dado['nome'],
            'posicao': time_dado['posicao']
        })
        
    # Ordenar por posição
    lista_atual = sorted(lista_atual, key=lambda x: x['posicao'])
    
    pontos = 20
    for item in lista_atual:
        item['Pontuacao_Atual'] = max(pontos, 0)
        pontos -= 1
        
    return lista_atual

def calcular_valor_patrocinio(codigo_liga, temporada):
    """
    Calcula o valor final do patrocínio.
    v = (pontos publico * 0.6) + (pontos historico * 0.3) + (pontos atual * 0.1)
    """
    # 1. Pontuação Público
    pontos_publico = calcular_pontuacao_publico(codigo_liga, temporada)
    
    # 2. Pontuação Histórica
    pontos_historico = calcular_pontuacao_historica(codigo_liga, temporada)
    
    # 3. Pontuação Atual
    pontos_atual = calcular_pontuacao_atual(codigo_liga, temporada)
    
    if not pontos_publico or not pontos_historico or not pontos_atual:
        print("Erro: Não foi possível obter todos os dados necessários.")
        return None

    # Consolidar dados usando dicionário para acesso rápido
    tabela_final = {}
    
    # Processar Público (Base)
    for p in pontos_publico:
        # Normalizar nome do arquivo de público para bater com API
        nome_original = p['Time']
        nome_normalizado = normalizar_nome(nome_original)
        
        tabela_final[nome_normalizado] = {
            'Time': nome_original, # Mantém o nome original para exibição se quiser
            'Nome_Normalizado': nome_normalizado,
            'Pontos_Publico': p.get('Pontuacao', 0),
            'Pontos_Historico': 0,
            'Pontos_Atual': 0,
            'Media_Publico': p.get('Media_Publico', 0)
        }
        
    # Processar Histórico
    for h in pontos_historico:
        nome = h['nome']
        # Tenta encontrar direto ou normalizado (se o historico vier da API, ja esta "certo")
        # Mas o nome no dict tabela_final pode ter vindo do arquivo, que foi normalizado.
        # Então 'nome' da API deve bater com 'nome_normalizado'
        
        if nome in tabela_final:
            tabela_final[nome]['Pontos_Historico'] = h['Pontuacao_Historica']
        else:
            # Pode acontecer se o time não tem dados de publico (ex: caiu pra serie B e voltou, arquivo desatualizado)
            # Ou se o mapping falhou.
            pass

    # Processar Atual
    for a in pontos_atual:
        nome = a['nome']
        if nome in tabela_final:
            tabela_final[nome]['Pontos_Atual'] = a['Pontuacao_Atual']
            
    # Calcular Valor Final
    lista_final = []
    for nome, dados in tabela_final.items():
        v = (dados['Pontos_Publico'] * 0.6) + \
            (dados['Pontos_Historico'] * 0.3) + \
            (dados['Pontos_Atual'] * 0.1)
            
        dados['Valor_Patrocinio'] = round(v, 2)
        lista_final.append(dados)
        
    # Ordenar por Valor de Patrocínio
    lista_final = sorted(lista_final, key=lambda x: x['Valor_Patrocinio'], reverse=True)
    
    return lista_final

