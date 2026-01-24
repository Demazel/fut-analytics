import requests
import json
import pandas as pd
from data_frames import *

def obter_codigo_liga(nome_liga):
    ligas = {
        "Campeonato Brasileiro Série A": "BSA",
        "Championship": "ELC",
        "Premier League": "PL",
        "Ligue 1": "FL1",
        "Bundesliga": "BL1",
        "Serie A": "SA",
        "Eredivisie": "DED",
        "Primeira Liga": "PPL",
        "Primera Division": "PD",
    }
    return ligas.get(nome_liga)

def obter_dados_ligas(codigo_liga, escolha_season):
    try:
        url = f"https://api.football-data.org/v4/competitions/{codigo_liga}/standings"
        headers = {
            "X-Auth-Token": "93029a6429024c46abe457d02cdc19ff" 
        }
        params = {
            "season": escolha_season
        }
        
        response = requests.get(url, headers=headers, params=params)
        dados = response.json()
        
        tabela_formatada = []
        
        if 'standings' in dados:
            for item in dados['standings'][0]['table']:
                dados_time = {
                    "nome": item['team']['name'],
                    "gols_pro": item['goalsFor'],
                    "gols_contra": item['goalsAgainst'],
                    "pontos": item['points']
                }
                tabela_formatada.append(dados_time)
                
        return tabela_formatada 
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return None 

def melhor_ataque(df_tabela):
    try:
        melhor_ataque = df_tabela.loc[df_tabela['gols_pro'].idxmax()]
        return melhor_ataque
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return None

def melhor_defesa(df_tabela):
    try:
        melhor_defesa = df_tabela.loc[df_tabela['gols_contra'].idxmin()]
        return melhor_defesa
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return None