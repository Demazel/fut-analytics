import streamlit as st
import plotly.express as px
from funcoes import *
from data_frames import *


def main():
    st.set_page_config(page_title="Fut.Analytica", layout="wide")
    st.title("Fut.Analytica ⚽")
    st.write("Bem-vindo ao app Fut.Analytica")

    # Options in the sidebar
    st.sidebar.header("Configurações")
    
    ligas_disponiveis = [
        "Campeonato Brasileiro Série A", "Championship", "Premier League", 
        "Ligue 1", "Bundesliga", "Serie A", "Eredivisie", 
        "Primeira Liga", "Primera Division"
    ]
    escolha_liga = st.sidebar.selectbox("Escolha um campeonato:", ligas_disponiveis)
    
    available_seasons = [str(year) for year in range(2025, 2022, -1)] # Years 2025, 2024, 2023
    escolha_season = st.sidebar.selectbox(
        "Escolha a temporada:", 
        options=available_seasons,
        index=0
    )

    if st.sidebar.button("Processar Dados"):
        
        codigo_liga = obter_codigo_liga(escolha_liga)

        if codigo_liga:
            st.divider()
            st.subheader(f"{escolha_liga} - Temporada {escolha_season}")
            
            with st.spinner(f"Buscando dados para {escolha_liga} ({escolha_season})..."):
                dados = obter_dados_ligas(codigo_liga, escolha_season)
                dados_artilheiros = obter_dados_artilheiros(codigo_liga, escolha_season)
            
            if dados:
                
                # File saving removed
                
                try:
                    df_tabela = data_frames(dados)
                    
                    df_tabela = df_tabela.rename(columns={
                        'posicao': 'Posição',
                        'escudo': 'Escudo',
                        'nome': 'Time',
                        'pontos': 'Pontos',
                        'jogos': 'J',
                        'gols_pro': 'GP',
                        'gols_contra': 'GC',
                        'saldo_gols': 'SG'
                    })
                    
                    # CSS to reduce font size for better fit
                    st.markdown("""
                        <style>
                        div[data-testid="stDataFrame"] {
                            font-size: 0.8rem !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    col_tab, col_art = st.columns([1.8, 1.2])
                    
                    with col_tab:
                        st.subheader("Classificação")
                        st.dataframe(
                            df_tabela[['Posição', 'Escudo', 'Time', 'Pontos', 'GP', 'GC']],
                            column_config={
                                "Escudo": st.column_config.ImageColumn("Escudo"),
                                "Time": st.column_config.TextColumn("Time", width="medium")
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                        
                    with col_art:
                        st.subheader("Artilharia")
                        if dados_artilheiros:
                            df_art = data_frames_artilheiros(dados_artilheiros)
                            st.dataframe(
                                df_art[['nome', 'gols', 'time']].head(20), # Show top 20
                                column_config={
                                    "nome": "Jogador",
                                    "gols": "Gols",
                                    "time": "Time"
                                },
                                hide_index=True,
                                use_container_width=True
                            )
                        else:
                            st.info("Artilharia não disponível.")
                    
                    ataque = melhor_ataque(df_tabela)
                    defesa = melhor_defesa(df_tabela)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if ataque is not None:
                            st.metric(label="Melhor Ataque", value=ataque['Time'], delta=f"{ataque['GP']} Gols")
                    
                    with col2:
                        if defesa is not None:
                            st.metric(label="Melhor Defesa", value=defesa['Time'], delta=f"{defesa['GC']} Gols Sofridos", delta_color="inverse")
                    
                    st.subheader(f"Gráfico de Dispersão: {escolha_liga} ({escolha_season})")
                    
                    # Categorize teams for coloring
                    # Using GP (Gols Pró) since we renamed it
                    df_tabela = df_tabela.sort_values(by='GP', ascending=False)
                    top_5 = df_tabela.head(5).index
                    bottom_5 = df_tabela.tail(5).index
                    
                    def get_color_category(idx):
                        if idx in top_5:
                            return 'Melhores Ataques'
                        elif idx in bottom_5:
                            return 'Piores Ataques'
                        else:
                            return 'Outros'
                    
                    df_tabela['categoria'] = df_tabela.index.map(get_color_category)

                    color_map = {
                        'Melhores Ataques': 'lightgreen',
                        'Piores Ataques': 'lightcoral',
                        'Outros': 'lightblue'
                    }
                    
                    fig = px.scatter(
                        df_tabela, 
                        x='GP', 
                        y='GC', 
                        hover_data=['Time'], 
                        text='Time',
                        color='categoria',
                        color_discrete_map=color_map,
                        title=f'Dispersão de Gols - {escolha_liga} ({escolha_season})',
                        labels={'GP': 'Gols Pró', 'GC': 'Gols Sofridos', 'categoria': 'Legenda'}
                    )
                    
                    fig.update_traces(textposition='top center', marker=dict(size=12))

                    st.plotly_chart(fig, key=f"scatter_{escolha_liga}_{escolha_season}")



                    # --- Desempenho Mandante vs Visitante ---
                    st.divider()
                    st.subheader("🏠 Desempenho: Gols Mandante x Visitante")
                    
                    # Prepare dataframe: Top 12 Offensive Teams
                    df_ha = df_tabela.sort_values(by='GP', ascending=False).head(12)
                    
                    # Melt dataframe for Plotly
                    df_melted_ha = df_ha.melt(id_vars=['Time'], value_vars=['gols_casa', 'gols_fora'], var_name='Local', value_name='Gols')
                    
                    fig_ha = px.bar(
                        df_melted_ha, 
                        x='Time', 
                        y='Gols', 
                        color='Local', 
                        title="Top 12 Ataques: Onde eles marcam mais?",
                        barmode='group',
                        labels={'Local': 'Mando', 'Gols': 'Gols Marcados', 'Time': 'Time'},
                        color_discrete_map={'gols_casa': '#3498db', 'gols_fora': '#e74c3c'}
                    )
                    
                    # Rename Legend Items
                    new_names = {'gols_casa': 'Em Casa 🏠', 'gols_fora': 'Fora de Casa ✈️'}
                    fig_ha.for_each_trace(lambda t: t.update(name = new_names.get(t.name, t.name)))
                    
                    st.plotly_chart(fig_ha, key=f"ha_{escolha_liga}_{escolha_season}")

                    st.divider()
                    st.subheader("🤖 Scouting Intelligence - Gol de Placa")

                    tab_curto, tab_longo = st.tabs(["Curto Prazo (Temporada Atual)", "Longo Prazo (Consistência)"])

                    with tab_curto:
                        # Calculate Efficiency (Goals per Game)
                        df_tabela['Eficiência (Gols/Jogo)'] = (df_tabela['GP'] / df_tabela['J']).round(2)

                        # Investment Logic: Find "Undervalued" Teams
                        # Criteria: Teams ranked 5th or lower but with high Goal Count
                        df_targets = df_tabela[df_tabela['Posição'] > 4]
                        
                        if not df_targets.empty:
                            # Find the max Goals For in this subset
                            max_gp_target = df_targets['GP'].max()
                            # Get the team(s) with this max GP
                            recommendations = df_targets[df_targets['GP'] == max_gp_target]
                            
                            team_rec = recommendations.iloc[0]['Time']
                            pos_rec = recommendations.iloc[0]['Posição']
                            gp_rec = recommendations.iloc[0]['GP']
                            
                            st.success(f"🌟 **Recomendação de Investimento: {team_rec}**")
                            st.markdown(f"""
                            **Análise do Algoritmo:**
                            - O **{team_rec}** ocupa a **{pos_rec}ª posição**, o que reduz o custo do patrocínio comparado aos líderes.
                            - Porém, o time marcou **{gp_rec} gols**, garantindo alta visibilidade na TV.
                            - **Veredito:** Melhor custo-benefício para curto prazo.
                            """)
                        else:
                            st.info("Todos os times com ataques fortes já estão no Top 4. Considere investir nos líderes para cobertura máxima.")

                        col_scout1, col_scout2 = st.columns(2)
                        
                        with col_scout1:
                            st.write("📊 Eficiência Ofensiva (Gols / Jogo)")
                            st.dataframe(
                                df_tabela[['Posição', 'Time', 'GP', 'J', 'Eficiência (Gols/Jogo)']].sort_values(by='Eficiência (Gols/Jogo)', ascending=False),
                                hide_index=True
                            )
                            
                        with col_scout2:
                            st.write("📈 Mapa de Oportunidade")
                            # Scatter focusing on Position vs Goals (Marketing View)
                            
                            # Define helper to determine category based on 'team_rec' (calculated above)
                            # We assume 'team_rec' might exist if df_targets was not empty.
                            # Initialize safe fallback if no rec found
                            target_team_name = team_rec if 'team_rec' in locals() else None

                            def get_scout_category(row):
                                if target_team_name and row['Time'] == target_team_name:
                                    return 'Recomendação' # Gold
                                elif row['Posição'] <= 4:
                                    return 'Elite (Top 4)' # LightGreen
                                else:
                                    return 'Outros' # LightBlue

                            df_tabela['scout_color'] = df_tabela.apply(get_scout_category, axis=1)
                            
                            # Label logic: Show name ONLY for Recommendation
                            def get_scout_label(row):
                                if target_team_name and row['Time'] == target_team_name:
                                    return row['Time']
                                else:
                                    return ''
                            
                            df_tabela['scout_label'] = df_tabela.apply(get_scout_label, axis=1)
                            
                            color_map_scout = {
                                'Recomendação': '#FFD700', # Gold
                                'Elite (Top 4)': 'lightgreen', 
                                'Outros': 'lightblue'
                            }

                            fig_opp = px.scatter(
                                df_tabela,
                                x='Posição',
                                y='GP',
                                text='scout_label', 
                                hover_data=['Time', 'Eficiência (Gols/Jogo)'],
                                color='scout_color',
                                color_discrete_map=color_map_scout,
                                title="Posição x Gols (Busca por Oportunidades)",
                                labels={'Posição': 'Posição na Tabela (Direita = Menor Custo)', 'GP': 'Gols Marcados (TV Time)', 'scout_color': 'Legenda'}
                            )
                            # Add vertical line separating Top 4
                            fig_opp.add_vline(x=4.5, line_width=1, line_dash="dash", line_color="grey")
                            fig_opp.add_annotation(x=15, y=df_tabela['GP'].max(), text="Zona de Oportunidade (Investimento)", showarrow=False, font=dict(color="green"))
                            
                            fig_opp.update_traces(textposition='top center', marker=dict(size=10))
                            st.plotly_chart(fig_opp, key=f"opp_{escolha_liga}_{escolha_season}")

                    with tab_longo:
                        st.markdown("### Análise de Consistência Histórica")
                        with st.spinner("Analisando histórico de temporadas..."):
                            historico = obter_dados_historicos(codigo_liga, escolha_season)
                        
                        if len(historico) >= 2:
                            # 1. Identify teams present in ALL fetched seasons
                            # Get sets of team names for each year
                            teams_per_year = []
                            for ano, dados_ano in historico.items():
                                df_ano = pd.DataFrame(dados_ano)
                                teams_per_year.append(set(df_ano['nome']))
                            
                            # Intersection of all sets
                            common_teams = set.intersection(*teams_per_year)
                            
                            if common_teams:
                                # 2. Aggregate Goals for these teams
                                team_stats = []
                                for team in common_teams:
                                    total_goals = 0
                                    yearly_data = {}
                                    
                                    for ano, dados_ano in historico.items():
                                        df_ano = pd.DataFrame(dados_ano)
                                        row = df_ano[df_ano['nome'] == team].iloc[0]
                                        goals = row['gols_pro'] # funcoes.py uses 'gols_pro', not 'GP' in raw data
                                        total_goals += goals
                                        yearly_data[ano] = goals
                                    
                                    stats = {'Time': team, 'Total Gols': total_goals}
                                    stats.update(yearly_data)
                                    team_stats.append(stats)
                                
                                df_historic = pd.DataFrame(team_stats)
                                df_historic = df_historic.sort_values(by='Total Gols', ascending=False)
                                
                                # 3. Top 5 Best Attacks
                                top_5_historic = df_historic.head(5)
                                
                                # Long Term Recommendation
                                best_long_term = top_5_historic.iloc[0]
                                team_lt = best_long_term['Time']
                                total_lt = best_long_term['Total Gols']
                                num_seasons = len(historico)
                                
                                st.success(f"💎 **Investimento Seguro (Longo Prazo): {team_lt}**")
                                st.markdown(f"""
                                **Análise de Consistência:**
                                - **Domínio Histórico**: O **{team_lt}** é o time mais ofensivo acumulado no período analisado (**{total_lt/num_seasons:.1f} média de gols por temporada**).
                                - **Estabilidade**: Presença garantida na elite e entrega constante de "tempo de tela" (gols).
                                - **Veredito:** A "Blue Chip" do campeonato. Ideal para contratos longos (2+ anos).
                                """)
                                
                                # Reshape for chart
                                # We need columns: [Time, Ano, Gols]
                                # The current df_historic has: [Time, Total, 2025, 2024, 2023]
                                # Melt it
                                years_cols = [col for col in df_historic.columns if col not in ['Time', 'Total Gols']]
                                df_melted = top_5_historic.melt(id_vars=['Time'], value_vars=years_cols, var_name='Temporada', value_name='Gols')
                                df_melted = df_melted.sort_values(by='Temporada')

                                fig_hist = px.bar(
                                    df_melted,
                                    x='Time',
                                    y='Gols',
                                    color='Temporada',
                                    barmode='group',
                                    title="Evolução dos Top 5 Ataques (Times Consistentes)",
                                    text='Gols'
                                )
                                fig_hist.update_traces(textposition='outside')
                                st.plotly_chart(fig_hist, key=f"hist_{escolha_liga}")
                                
                            else:
                                st.warning("Não há times que jogaram todas as temporadas selecionadas (possível alta rotatividade na liga).")
                        else:
                            st.warning("Dados históricos insuficientes para análise de longo prazo.")
                                
                except Exception as e:
                    st.error(f"Erro ao exibir dados para {escolha_liga} ({escolha_season}): {e}")

            else:
                st.warning(f"Não foi possível obter dados para {escolha_liga} ({escolha_season}).")
        else:
            st.error(f"Liga não encontrada: {escolha_liga}")

if __name__ == "__main__":
    main()