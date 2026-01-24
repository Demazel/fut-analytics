import pandas as pd
from funcoes import *

def data_frames(dados):
    df_tabela = pd.DataFrame(dados)
    return df_tabela   
    
def data_frames_artilheiros(escolha_liga, escolha_season):
    df_artilheiros = pd.read_json(f"{escolha_liga}/artilheiros_{escolha_liga}_{escolha_season}.json")
    return df_artilheiros  
