import requests
import json
import pandas as pd
import streamlit as st
from data_frames import *

LIGAS_MAP = {
    "Campeonato Brasileiro Série A": "BSA",
    "Premier League": "PL",
    "Ligue 1": "FL1",
    "Bundesliga": "BL1",
    "Serie A": "SA",
    "Primera Division": "PD",
}

def obter_codigo_liga(nome_liga):
    return LIGAS_MAP.get(nome_liga)

def obter_dados_ligas(codigo_liga, escolha_season):
    dados = None
    # 1. Tentativa via API
    try:
        url = f"https://api.football-data.org/v4/competitions/{codigo_liga}/standings"
        headers = {
            "X-Auth-Token": st.secrets["API_TOKEN"]
        }
        params = {
            "season": escolha_season
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
             dados = response.json()
    except Exception as e:
        print(f"Erro API: {e}")

    # 2. Tentativa via Arquivo Local (Fallback)
    if not dados or 'standings' not in dados:
        try:
            # Encontrar nome da liga pelo codigo
            nome_liga = next((nome for nome, code in LIGAS_MAP.items() if code == codigo_liga), None)
            if nome_liga:
                # Tenta formatacao padrao dos arquivos salvos
                # O arquivo está dentro de uma pasta com o nome da liga
                nome_arquivo = f"{nome_liga}/tabela_{nome_liga}_{escolha_season}.json"
                
                # Verifica se arquivo existe antes de abrir? Ou try/except
                with open(nome_arquivo, "r", encoding="utf-8") as f:
                    # O arquivo local ja estaria formatado no padrao da API ou padrao processado?
                    # Pelos logs anteriores, 'tabela_xxx.json' existe. 
                    # Vamos assumir que ele contem o JSON puro da API ou o processado?
                    # O usuario queria "salvar o json".
                    # Se for o JSON processado (lista), o parsing abaixo vai falhar pois espera {'standings': ...}
                    # Vamos verificar o CONTEUDO do arquivo.
                    conteudo = json.load(f)
                    
                    # Se for lista, retorna direto. Se for dict com 'standings', processa.
                    if isinstance(conteudo, list):
                        # Fix: Ensure 'posicao' exists
                        for i, item in enumerate(conteudo):
                            if 'posicao' not in item:
                                item['posicao'] = i + 1
                        return conteudo
                    else:
                        dados = conteudo
        except Exception as e:
            print(f"Erro Arquivo Local: {e}")

    try:
        tabela_formatada = []
        
        if dados and 'standings' in dados:
            # Find specific tables ensuring we get TOTAL, HOME, and AWAY
            tabela_total = next((s['table'] for s in dados['standings'] if s['type'] == 'TOTAL'), [])
            tabela_home = next((s['table'] for s in dados['standings'] if s['type'] == 'HOME'), [])
            tabela_away = next((s['table'] for s in dados['standings'] if s['type'] == 'AWAY'), [])
            
            # Map Home/Away goals by team name for easy lookup
            dict_home = {t['team']['name']: t['goalsFor'] for t in tabela_home}
            dict_away = {t['team']['name']: t['goalsFor'] for t in tabela_away}

            for item in tabela_total:
                nome_time = item['team']['name']
                dados_time = {
                    "posicao": item['position'],
                    "escudo": item['team']['crest'],
                    "nome": nome_time,
                    "pontos": item['points'],
                    "jogos": item['playedGames'],
                    "vitorias": item['won'],
                    "derrotas": item['lost'],
                    "gols_pro": item['goalsFor'],
                    "gols_contra": item['goalsAgainst'],
                    "saldo_gols": item['goalDifference'],
                    # New helper columns for Home/Away analysis
                    "gols_casa": dict_home.get(nome_time, 0),
                    "gols_fora": dict_away.get(nome_time, 0)
                }
                tabela_formatada.append(dados_time)
                
        return tabela_formatada 
    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        return None 

def melhor_ataque(df_tabela):
    try:
        melhor_ataque = df_tabela.loc[df_tabela['GP'].idxmax()]
        return melhor_ataque
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return None

def melhor_defesa(df_tabela):
    try:
        melhor_defesa = df_tabela.loc[df_tabela['GC'].idxmin()]
        return melhor_defesa
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return None

def obter_dados_artilheiros(codigo_liga, escolha_season):
    try:
        url = f"https://api.football-data.org/v4/competitions/{codigo_liga}/scorers"
        headers = {
            "X-Auth-Token": st.secrets["API_TOKEN"]
        }
        params = {
            "season": escolha_season
        }
        
        response = requests.get(url, headers=headers, params=params)
        dados = response.json()
        
        tabela_formatada = []
        
        if 'scorers' in dados:
            for item in dados['scorers']:
                dados_time = {
                    "nome": item['player']['name'],
                    "gols": item['goals'],
                    "time": item['team']['name'],
                    "escudo": item['team']['crest']
                }
                tabela_formatada.append(dados_time)
                
        return tabela_formatada 
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return None 

def obter_dados_historicos(codigo_liga, temporada_atual):
    """
    Busca dados da temporada atual e das 2 anteriores.
    Retorna um dicionario: { '2025': [dados], '2024': [dados], ... }
    """
    historico = {}
    try:
        ano_atual = int(temporada_atual)
        # 3 years including current
        anos = range(ano_atual, ano_atual - 3, -1) 
        
        for ano in anos:
            dados_ano = obter_dados_ligas(codigo_liga, str(ano))
            if dados_ano:
                historico[str(ano)] = dados_ano
            
        return historico
    except Exception as e:
        print(f"Erro ao obter historico: {e}")
        return historico

