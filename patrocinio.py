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
             if 'Media_Publico' not in time:
                 time['Media_Publico'] = 0
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
    # Brasileirao
    "SC Corinthians": "SC Corinthians Paulista",
    "Atlético Mineiro": "CA Mineiro",
    "Athletico Paranaense": "CA Paranaense",
    "Atlético Goianiense": "AC Goianiense",
    "São Paulo FC": "São Paulo FC",
    "Botafogo FR": "Botafogo FR", 
    "Vasco da Gama": "CR Vasco da Gama",
    "Grêmio FBPA": "Grêmio FBPA",
    "Santos FC": "Santos FC",
    "EC Bahia": "EC Bahia",
    "Cuiabá EC": "Cuiabá EC",

    # Ligue 1
    "FC Paris Saint-Germain": "Paris Saint-Germain FC",
    "Olympique Marselha": "Olympique de Marseille",
    "Olympique Lyon": "Olympique Lyonnais",
    "RC Lens": "Racing Club de Lens",
    "Stade Rennais FC": "Stade Rennais FC 1901",
    "FC Nantes": "FC Nantes",
    "AC Le Havre": "Le Havre AC", 
    "AS Monaco": "AS Monaco FC",
    "Stade Brestois 29": "Stade Brestois 29",
    "Stade Reims": "Stade de Reims",
    "RC Strasbourg Alsace": "RC Strasbourg Alsace",
    "FC Lorient": "FC Lorient",
    "FC Toulouse": "Toulouse FC",
    "OGC Nice": "OGC Nice",
    "Montpellier HSC": "Montpellier HSC",
    
    # Premier League
    "Manchester City": "Manchester City FC",
    "Arsenal FC": "Arsenal FC",
    "Liverpool FC": "Liverpool FC",
    "Aston Villa": "Aston Villa FC",
    "Tottenham Hotspur": "Tottenham Hotspur FC",
    "Chelsea FC": "Chelsea FC",
    "Newcastle United": "Newcastle United FC",
    "Manchester United": "Manchester United FC",
    "West Ham United": "West Ham United FC",
    "Brighton & Hove Albion": "Brighton & Hove Albion FC",
    "Wolverhampton Wanderers": "Wolverhampton Wanderers FC",
    "Fulham FC": "Fulham FC",
    "Bournemouth": "AFC Bournemouth",
    "Crystal Palace": "Crystal Palace FC",
    "Brentford FC": "Brentford FC",
    "Everton FC": "Everton FC",
    "Nottingham Forest": "Nottingham Forest FC",
    "Luton Town": "Luton Town FC", # Relegated but might appear
    "Burnley FC": "Burnley FC", # Relegated but might appear
    "Sheffield United": "Sheffield United FC", # Relegated but might appear
    
    # La Liga
    "Real Madrid": "Real Madrid CF",
    "FC Barcelona": "FC Barcelona",
    "Girona FC": "Girona FC",
    "Atlético de Madrid": "Club Atlético de Madrid",
    "Athletic Bilbao": "Athletic Club",
    "Real Sociedad": "Real Sociedad de Fútbol",
    "Real Betis": "Real Betis Balompié",
    "Villarreal CF": "Villarreal CF",
    "Valencia CF": "Valencia CF",
    "Sevilla FC": "Sevilla FC",
    
    # Serie A (Italia)
    "Inter de Milão": "FC Internazionale Milano",
    "Genoa": "Genoa CFC",
    "Hellas Verona": "Hellas Verona FC",
    "Salernitana Calcio 1919": "US Salernitana 1919",
    "US Sassuolo": "US Sassuolo Calcio",
    "FC Empoli": "Empoli FC",
    "Bologna": "Bologna FC 1909",
    # Mismatches usually are partials, but let's be safe
    "AC Milan": "AC Milan", 
    "AS Roma": "AS Roma",

    # Bundesliga
    "FC Bayern Munique": "FC Bayern München",
    "SG Eintracht Frankfurt": "Eintracht Frankfurt",
    "1.FC Colônia": "1. FC Köln",
    "Werder Bremen": "SV Werder Bremen",
    "1.FSV Mainz 05": "1. FSV Mainz 05",
    "1.FC Union Berlim": "1. FC Union Berlin",
    "1.FC Heidenheim 1846": "1. FC Heidenheim 1846",
    "VfL Bochum": "VfL Bochum 1848",

    # Premier League
    "FC Arsenal": "Arsenal FC",
    "FC Liverpool": "Liverpool FC",
    "FC Everton": "Everton FC",
    "FC Fulham": "Fulham FC",
    "FC Burnley": "Burnley FC", # Relegated
    "Brighton & Hove Albion": "Brighton & Hove Albion FC",
    "Luton Town": "Luton Town FC", # Relegated
    "Newcastle United": "Newcastle United FC",
    "Nottingham Forest": "Nottingham Forest FC",
    "Sheffield United": "Sheffield United FC", # Relegated
    "Tottenham Hotspur": "Tottenham Hotspur FC",
    "West Ham United": "West Ham United FC",
    "Wolverhampton Wanderers": "Wolverhampton Wanderers FC",
    "Manchester City": "Manchester City FC",
    "Manchester United": "Manchester United FC",
    "Aston Villa": "Aston Villa FC",
    "Chelsea FC": "Chelsea FC",
    "Crystal Palace": "Crystal Palace FC",
    "Brentford FC": "Brentford FC",
    "Bournemouth": "AFC Bournemouth",

    # Ligue 1
    "FC Paris Saint-Germain": "Paris Saint-Germain FC",
    "Olympique Marselha": "Olympique de Marseille",
    "Olympique Lyon": "Olympique Lyonnais",
    "LOSC Lille": "Lille OSC",
    "RC Lens": "Racing Club de Lens",
    "Stade Rennais FC": "Stade Rennais FC 1901",
    "Stade Reims": "Stade de Reims",
    "FC Toulouse": "Toulouse FC",
    "AS Monaco": "AS Monaco FC",
    "OGC Nice": "OGC Nice",
    "FC Nantes": "FC Nantes",
    "AC Le Havre": "Le Havre AC", 
    "Stade Brestois 29": "Stade Brestois 29",
    "RC Strasbourg Alsace": "RC Strasbourg Alsace",
    "FC Lorient": "FC Lorient",
    "Montpellier HSC": "Montpellier HSC",

    # La Liga
    "FC Villarreal": "Villarreal CF",
    "Athletic Bilbao": "Athletic Club",
    "Atlético de Madrid": "Club Atlético de Madrid",
    "Celta de Vigo": "RC Celta de Vigo",
    "Rayo Vallecano": "Rayo Vallecano de Madrid",
    "Real Sociedad": "Real Sociedad de Fútbol",
    "Real Madrid": "Real Madrid CF",
    "FC Barcelona": "FC Barcelona",
    "Girona FC": "Girona FC",
    "Real Betis": "Real Betis Balompié",
    "Valencia CF": "Valencia CF",
    "Sevilla FC": "Sevilla FC",
    "Osasuna": "CA Osasuna", # Potential missing
    "Mallorca": "RCD Mallorca", # Potential missing
    "Las Palmas": "UD Las Palmas", # Potential missing
    "Alaves": "Deportivo Alavés", # Potential missing
    "Granada": "Granada CF",
    "Almería": "UD Almería",
    "Cadiz": "Cádiz CF",
    "RCD Espanyol": "RCD Espanyol de Barcelona", 

    # Additional Historical/Variations found in check_all_names
    "Napoli": "SSC Napoli",
    "América Mineiro": "América FC (Minas Gerais)",
    "Coritiba FC": "Coritiba FBC",
    "Sport Recife": "SC Recife",
    "AFC Sunderland": "Sunderland AFC",
    "FC Southampton": "Southampton FC",
    "AC Ajaccio": "AC Ajaccio", # Check verification if needed
    "ESTAC Troyes": "ES Troyes AC",
    "Hertha Berlim": "Hertha BSC",
    "Schalke 04": "FC Schalke 04",
    "FC St. Pauli": "FC St. Pauli 1910",
    "Pisa Sporting Club": "Pisa Sporting Club", # Serie B?
    "Spezia Calcio": "Spezia Calcio", 
    "UC Sampdoria": "UC Sampdoria",
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
            'posicao': time_dado['posicao'],
            'escudo': time_dado.get('escudo', '')
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
            'Time': nome_normalizado, # Alterado para bater com API no merge do main.py
            'Nome_Original': nome_original, 
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
            # Add Crest if available
            if 'escudo' in a:
                tabela_final[nome]['Escudo'] = a['escudo']
            
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

