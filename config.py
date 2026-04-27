from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

LIGAS_MAP = {
    "Campeonato Brasileiro Série A": "BSA",
    "Premier League": "PL",
    "Ligue 1": "FL1",
    "Bundesliga": "BL1",
    "Serie A": "SA",
    "La Liga": "PD",
}

PASTAS_TABELAS = {
    "La Liga": "Primera Division",
}

PUBLICO_LIGAS = {
    "BSA": {"pasta": "campeonato brasileiro serie a", "nome_arquivo": "Campeonato Brasileiro Série A"},
    "PL": {"pasta": "premier league", "nome_arquivo": "Premier League"},
    "FL1": {"pasta": "ligue1", "nome_arquivo": "Ligue 1"},
    "BL1": {"pasta": "bundesliga", "nome_arquivo": "Bundesliga"},
    "SA": {"pasta": "serie a", "nome_arquivo": "Serie A"},
    "PD": {"pasta": "laliga", "nome_arquivo": "La Liga"},
}

TEMPORADAS_DISPONIVEIS = [str(year) for year in range(2025, 2022, -1)]
