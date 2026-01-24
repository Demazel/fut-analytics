import streamlit as st
import plotly.express as px
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
    
    escolha_seasons_input = st.sidebar.selectbox(
        "Escolha a temporada:", 
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
                    
                    # File saving removed
                    
                    try:
                        df_tabela = data_frames(dados)
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
                        
                        st.subheader("Gráfico de Dispersão: Gols Pró x Gols Contra")
                        fig = px.scatter(
                            df_tabela, 
                            x='gols_pro', 
                            y='gols_contra', 
                            hover_data=['nome'], 
                            title='Dispersão de Gols',
                            labels={'gols_pro': 'Gols Pró', 'gols_contra': 'Gols Sofridos'}
                        )
                        st.plotly_chart(fig)
                                
                    except Exception as e:
                        st.error(f"Erro ao exibir dataframe para {escolha_season}: {e}")

                else:
                    st.warning(f"Não foi possível obter dados para {escolha_season}.")
        else:
            st.error("Liga não encontrada.")

if __name__ == "__main__":
    main()