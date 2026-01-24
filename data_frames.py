import pandas as pd
from funcoes import *

def data_frames(escolha_liga, escolha_season):
    df_tabela = pd.read_json(f"{escolha_liga}/tabela_{escolha_liga}_{escolha_season}.json")
    print(df_tabela)
    return df_tabela   
    