import json
import os
from funcoes import *
from data_frames import *   

def main():
    print("Bem-vindo ao app Fut.Analytica")
    print("Escolha uma opção:")
    print("1. Imprimir tabela de liga especificada")
    print("2. Sair")
    opcao = input("Opção: ")
    
    if opcao == "1":
        escolha_liga = input("Escolha uma liga entre: Campeonato Brasileiro Série A, Championship, Premier League, Ligue 1, Bundesliga, Serie A, Eredivisie, Primeira Liga, Primera Division: ")

        escolha_seasons_input = input("Escolha as temporadas a partir de 2023 (separadas por vírgula, ex: 2023, 2024): ")
        
        try:
            seasons = [int(s.strip()) for s in escolha_seasons_input.split(',')]
        except ValueError:
            print("Entrada inválida. Certifique-se de digitar anos válidos separados por vírgula.")
            return

        codigo_liga = obter_codigo_liga(escolha_liga)
        
        if codigo_liga:
            for escolha_season in seasons:
                print(f"\n--- Processando Temporada {escolha_season} ---")
                print(f"Buscando dados para {escolha_liga} ({codigo_liga})...")
                dados = obter_dados_ligas(codigo_liga, escolha_season)
                
                if not os.path.exists(escolha_liga):
                    os.makedirs(escolha_liga)
                
                nome_arquivo = f"{escolha_liga}/tabela_{escolha_liga}_{escolha_season}.json"
                with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
                    json.dump(dados, arquivo, indent=4, ensure_ascii=False)
                
                print(f"Dados salvos com sucesso em {nome_arquivo}")

                print("\n")
                try:
                    df_tabela = data_frames(escolha_liga, escolha_season)
                except Exception as e:
                    print(f"Erro ao exibir dataframe para {escolha_season}: {e}")
                
                print("\n")
                
                ataque = melhor_ataque(df_tabela)
                defesa = melhor_defesa(df_tabela)
                
                if ataque is not None:
                    print(f"{ataque['nome']} teve o melhor ataque com {ataque['gols_pro']} gols")
                if defesa is not None:
                    print(f"{defesa['nome']} teve a melhor defesa, tomando apenas {defesa['gols_contra']} gols")
            
        else:
            print("Liga não encontrada. Verifique o nome digitado.")
    elif opcao == "2":
        print("Obrigado por usar o app Fut.Analytica")
    else:
        print("Opção inválida")


if __name__ == "__main__":
    main()     