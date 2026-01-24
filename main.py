import json
import os
import streamlit as st
from funcoes import *
from data_frames import *

def main():
    st.title("Fut.Analytica ⚽")
    st.write("Bem-vindo ao app Fut.Analytica")

    # Options in the sidebar
    st.sidebar.header("Configurações")
    
    ligas_disponiveis = [
        "Campeonato Brasileiro Série A", "Championship", "Premier League", 
        "Ligue 1", "Bundesliga", "Serie A", "Eredivisie", 
        "Primeira Liga", "Primera Division"
    ]
    
    escolha_liga = st.sidebar.selectbox("Escolha uma liga:", ligas_disponiveis)
    
    escolha_seasons_input = st.sidebar.text_input(
        "Escolha as temporadas (separadas por vírgula):", 
        value="2023"
    )

    if st.sidebar.button("Processar Dados"):
        try:
            seasons = [int(s.strip()) for s in escolha_seasons_input.split(',')]
        except ValueError:
            st.error("Entrada inválida. Certifique-se de digitar anos válidos separados por vírgula.")
            return

        codigo_liga = obter_codigo_liga(escolha_liga)

        if codigo_liga:
            for escolha_season in seasons:
                st.subheader(f"Temporada {escolha_season} - {escolha_liga}")
                
                with st.spinner(f"Buscando dados para {escolha_liga} ({escolha_season})..."):
                    dados = obter_dados_ligas(codigo_liga, escolha_season)
                
                if dados:
                    if not os.path.exists(escolha_liga):
                        os.makedirs(escolha_liga)
                    
                    nome_arquivo = f"{escolha_liga}/tabela_{escolha_liga}_{escolha_season}.json"
                    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
                        json.dump(dados, arquivo, indent=4, ensure_ascii=False)
                    
                    st.success(f"Dados salvos em {nome_arquivo}")

                    try:
                        df_tabela = data_frames(escolha_liga, escolha_season)
                        st.dataframe(df_tabela)
                        
                        ataque = melhor_ataque(df_tabela)
                        defesa = melhor_defesa(df_tabela)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if ataque is not None:
                                st.metric(label="Melhor Ataque", value=ataque['nome'], delta=f"{ataque['gols_pro']} Gols")
                        
                        with col2:
                            if defesa is not None:
                                st.metric(label="Melhor Defesa", value=defesa['nome'], delta=f"{defesa['gols_contra']} Gols Sofridos", delta_color="inverse")
                                
                    except Exception as e:
                        st.error(f"Erro ao exibir dataframe para {escolha_season}: {e}")
                else:
                    st.warning(f"Não foi possível obter dados para {escolha_season}.")
        else:
            st.error("Liga não encontrada.")

if __name__ == "__main__":
    main()