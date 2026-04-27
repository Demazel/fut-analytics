import json

import requests
import streamlit as st

from config import BASE_DIR, LIGAS_MAP, PASTAS_TABELAS


API_BASE_URL = "https://api.football-data.org/v4"
TIMEOUT_SECONDS = 15


def obter_codigo_liga(nome_liga):
    return LIGAS_MAP.get(nome_liga)


def _obter_nome_liga(codigo_liga):
    return next((nome for nome, code in LIGAS_MAP.items() if code == codigo_liga), None)


def _obter_headers_api():
    try:
        token = st.secrets.get("API_TOKEN")
    except Exception:
        token = None

    if not token:
        return None
    return {"X-Auth-Token": token}


def _buscar_api(endpoint, codigo_liga, temporada):
    headers = _obter_headers_api()
    if not headers:
        return None

    url = f"{API_BASE_URL}/competitions/{codigo_liga}/{endpoint}"
    response = requests.get(
        url,
        headers=headers,
        params={"season": temporada},
        timeout=TIMEOUT_SECONDS,
    )
    if response.status_code != 200:
        return None
    return response.json()


def _caminho_tabela_local(codigo_liga, temporada):
    nome_liga = _obter_nome_liga(codigo_liga)
    if not nome_liga:
        return None

    nome_pasta = PASTAS_TABELAS.get(nome_liga, nome_liga)
    return BASE_DIR / nome_pasta / f"tabela_{nome_pasta}_{temporada}.json"


def _normalizar_linha_tabela(item, posicao):
    gols_pro = item.get("gols_pro", 0)
    gols_contra = item.get("gols_contra", 0)

    return {
        **item,
        "posicao": item.get("posicao", posicao),
        "escudo": item.get("escudo", ""),
        "pontos": item.get("pontos", 0),
        "jogos": item.get("jogos", 0),
        "vitorias": item.get("vitorias", 0),
        "derrotas": item.get("derrotas", 0),
        "gols_pro": gols_pro,
        "gols_contra": gols_contra,
        "saldo_gols": item.get("saldo_gols", gols_pro - gols_contra),
        "gols_casa": item.get("gols_casa", 0),
        "gols_fora": item.get("gols_fora", 0),
    }


def _carregar_tabela_local(codigo_liga, temporada):
    caminho_arquivo = _caminho_tabela_local(codigo_liga, temporada)
    if not caminho_arquivo or not caminho_arquivo.exists():
        return None

    with caminho_arquivo.open("r", encoding="utf-8") as arquivo:
        conteudo = json.load(arquivo)

    if isinstance(conteudo, list):
        return [_normalizar_linha_tabela(item, index + 1) for index, item in enumerate(conteudo)]

    return conteudo


def _formatar_tabela_api(dados):
    if not dados or "standings" not in dados:
        return []

    tabela_total = next((s["table"] for s in dados["standings"] if s["type"] == "TOTAL"), [])
    tabela_home = next((s["table"] for s in dados["standings"] if s["type"] == "HOME"), [])
    tabela_away = next((s["table"] for s in dados["standings"] if s["type"] == "AWAY"), [])

    gols_casa_por_time = {item["team"]["name"]: item["goalsFor"] for item in tabela_home}
    gols_fora_por_time = {item["team"]["name"]: item["goalsFor"] for item in tabela_away}

    tabela_formatada = []
    for item in tabela_total:
        nome_time = item["team"]["name"]
        tabela_formatada.append(
            {
                "posicao": item["position"],
                "escudo": item["team"]["crest"],
                "nome": nome_time,
                "pontos": item["points"],
                "jogos": item["playedGames"],
                "vitorias": item["won"],
                "derrotas": item["lost"],
                "gols_pro": item["goalsFor"],
                "gols_contra": item["goalsAgainst"],
                "saldo_gols": item["goalDifference"],
                "gols_casa": gols_casa_por_time.get(nome_time, 0),
                "gols_fora": gols_fora_por_time.get(nome_time, 0),
            }
        )

    return tabela_formatada


def obter_dados_ligas(codigo_liga, escolha_season):
    try:
        dados_api = _buscar_api("standings", codigo_liga, escolha_season)
        tabela_api = _formatar_tabela_api(dados_api)
        if tabela_api:
            return tabela_api, "API"
    except Exception as erro:
        print(f"Erro API: {erro}")

    try:
        dados_locais = _carregar_tabela_local(codigo_liga, escolha_season)
        if isinstance(dados_locais, list):
            return dados_locais, "Arquivo Local"
        return _formatar_tabela_api(dados_locais), "Arquivo Local"
    except Exception as erro:
        print(f"Erro Arquivo Local: {erro}")

    return None, None


def melhor_ataque(df_tabela):
    try:
        return df_tabela.loc[df_tabela["GP"].idxmax()]
    except Exception as erro:
        print(f"Erro ao obter melhor ataque: {erro}")
        return None


def melhor_defesa(df_tabela):
    try:
        return df_tabela.loc[df_tabela["GC"].idxmin()]
    except Exception as erro:
        print(f"Erro ao obter melhor defesa: {erro}")
        return None


def obter_dados_artilheiros(codigo_liga, escolha_season):
    try:
        dados = _buscar_api("scorers", codigo_liga, escolha_season)
        if not dados or "scorers" not in dados:
            return None

        return [
            {
                "nome": item["player"]["name"],
                "gols": item["goals"],
                "time": item["team"]["name"],
                "escudo": item["team"]["crest"],
            }
            for item in dados["scorers"]
        ]
    except Exception as erro:
        print(f"Erro ao obter artilheiros: {erro}")
        return None


def obter_dados_historicos(codigo_liga, temporada_atual):
    historico = {}

    try:
        ano_atual = int(temporada_atual)
    except (TypeError, ValueError):
        return historico

    for ano in range(ano_atual, ano_atual - 3, -1):
        dados_ano, _ = obter_dados_ligas(codigo_liga, str(ano))
        if dados_ano:
            historico[str(ano)] = dados_ano

    return historico
