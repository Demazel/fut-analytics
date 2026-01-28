import streamlit as st
import plotly.express as px
from funcoes import *
from data_frames import *
from patrocinio import calcular_valor_patrocinio


def main():
    st.set_page_config(page_title="Fut.Analytica", layout="wide")
    st.title("Fut.Analytica ⚽")
    st.write("Bem-vindo ao app Fut.Analytica")

    # Options in the sidebar
    st.sidebar.header("Configurações")
    
    ligas_disponiveis = [
        "Campeonato Brasileiro Série A", "Premier League", 
        "Ligue 1", "Bundesliga", "Serie A", 
        "Primera Division"
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
                                df_art[['nome', 'gols', 'time', 'escudo']].head(20), # Show top 20
                                column_config={
                                    "nome": "Jogador",
                                    "gols": "Gols",
                                    "time": "Time",
                                    "escudo": st.column_config.ImageColumn("Escudo")
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

                    # --- Valuation de Patrocínio ---
                    st.divider()
                    st.subheader("💰 Valuation de Patrocínio")
                    st.markdown("##### Top 3 patrocínios mais caros")
                
                    with st.spinner("Calculando valor de patrocínio..."):
                         dados_patrocinio = calcular_valor_patrocinio(codigo_liga, escolha_season)
                     
                    if dados_patrocinio:
                        # Metrics for Top 3
                        top3 = dados_patrocinio[:3]
                        cols_metrics = st.columns(3)
                    
                        medals = ["🥇", "🥈", "🥉"]
                    
                        for i, time in enumerate(top3):
                            with cols_metrics[i]:
                                st.metric(
                                    label=f"{medals[i]} {time['Time']}",
                                    value=f"{time['Valor_Patrocinio']}",
                                    delta=f"Público: {time['Pontos_Publico']} | Hist: {time['Pontos_Historico']}"
                                )
                            
                        # Table
                        df_patrocinio = pd.DataFrame(dados_patrocinio)
                    
                        st.markdown("### Ranking Completo")
                        st.dataframe(
                            df_patrocinio[['Escudo', 'Time', 'Valor_Patrocinio', 'Pontos_Publico', 'Pontos_Historico', 'Pontos_Atual', 'Media_Publico']],
                            column_config={
                                "Escudo": st.column_config.ImageColumn("Escudo", width="small"),
                                "Time": "Time",
                                "Valor_Patrocinio": st.column_config.NumberColumn("Score Final", format="%.2f"),
                                "Pontos_Publico": "Pts Público (60%)",
                                "Pontos_Historico": "Pts Histórico (30%)",
                                "Pontos_Atual": "Pts Atual (10%)",
                                "Media_Publico": "Média Público"
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                    
                        # Chart Breakdown for Top 10
                        st.markdown("### Composição do Score (Top 10)")
                        top10 = df_patrocinio.head(10).copy()
                    
                        # We need to reverse calculate the weighted values to show stacked bar correctly,
                        # OR just show the raw points. Stacked bar of weighted contribution is better for "Valuation".
                    
                        top10['Contrib. Público'] = top10['Pontos_Publico'] * 0.6
                        top10['Contrib. Histórico'] = top10['Pontos_Historico'] * 0.3
                        top10['Contrib. Atual'] = top10['Pontos_Atual'] * 0.1
                    
                        df_melted_pat = top10.melt(
                            id_vars=['Time'], 
                            value_vars=['Contrib. Público', 'Contrib. Histórico', 'Contrib. Atual'],
                            var_name='Componente',
                            value_name='Pontos Ponderados'
                        )
                    
                        fig_val = px.bar(
                            df_melted_pat,
                            x='Time',
                            y='Pontos Ponderados',
                            color='Componente',
                            title="Composição do Valor de Patrocínio",
                            labels={'Pontos Ponderados': 'Score Contribuído'}
                        )
                        st.plotly_chart(fig_val, key=f"val_{escolha_liga}")
                    
                    else:
                        st.warning("Não foi possível calcular o valuation de patrocínio (falta de dados de público ou histórico).")

                    st.divider()
                    st.subheader("🤖 Scouting Intelligence - Gol de Placa")

                    tab_curto, tab_longo = st.tabs(["Curto Prazo (Temporada Atual)", "Longo Prazo (Consistência)"])

                    with tab_curto:
                        # 1. Merge Valuation Data (Cost Proxy) with Table Data (Performance)
                        # We need 'Valor_Patrocinio' from df_patrocinio
                        if dados_patrocinio:
                             df_val = pd.DataFrame(dados_patrocinio)
                             # Merge on 'Time'
                             # Note: df_tabela has 'Time', df_val has 'Time'. 
                             df_merged = pd.merge(df_tabela, df_val[['Time', 'Valor_Patrocinio']], on='Time', how='inner')
                             
                             # 2. ROI Calculation: GP / Valor_Patrocinio
                             # Higher is better: More goals per unit of sponsorship cost
                             df_merged['ROI_Score'] = (df_merged['GP'] / df_merged['Valor_Patrocinio'])
                             
                             # Normalizing for chart sizing or coloring if needed
                             
                             # 3. Find Best Opportunity
                             # User Request: "Time com mais gols que tem alta entrega com baixo custo"
                             
                             median_val = df_merged['Valor_Patrocinio'].median()
                             median_gp = df_merged['GP'].median()
                             
                             # Filter: High Delivery (GP >= Median) AND Low Cost (Val <= Median)
                             opportunities = df_merged[
                                 (df_merged['GP'] >= median_gp) & 
                                 (df_merged['Valor_Patrocinio'] <= median_val)
                             ]
                             
                             if not opportunities.empty:
                                 # Priority: Max Goals
                                 # Tie-breaker: Low Cost (Ascending), then High ROI (Descending) just in case
                                 best_choice = opportunities.sort_values(by=['GP', 'Valor_Patrocinio'], ascending=[False, True]).iloc[0]
                                 label_veredicto = "Este time está no quadrante de 'Oportunidade': Entrega acima da média por um custo abaixo da média."
                             else:
                                 # Fallback: If no team is in the "Gold Mine" quadrant
                                 # Pick the best ROI among the Top 50% of Goal Scorers (guarantees visibility)
                                 top_scorers = df_merged[df_merged['GP'] >= median_gp]
                                 if not top_scorers.empty:
                                      best_choice = top_scorers.sort_values(by='ROI_Score', ascending=False).iloc[0]
                                      label_veredicto = "Não há times de baixo custo com alta entrega. Esta é a opção mais eficiente entre os líderes de gols."
                                 else:
                                      # Fallback total
                                      best_choice = df_merged.sort_values(by='ROI_Score', ascending=False).iloc[0]
                                      label_veredicto = "Melhor retorno por ponto investido."
                             
                             team_rec = best_choice['Time']
                             gp_rec = best_choice['GP']
                             val_rec = best_choice['Valor_Patrocinio']
                             pos_rec = best_choice['Posição']
                             
                             # Classify ALL teams into Quadrants
                             def classify_team(row):
                                 if row['GP'] >= median_gp and row['Valor_Patrocinio'] <= median_val:
                                     return "💎 Oportunidade"
                                 elif row['GP'] >= median_gp and row['Valor_Patrocinio'] > median_val:
                                     return "🏆 Premium"
                                 elif row['GP'] < median_gp and row['Valor_Patrocinio'] > median_val:
                                     return "⚠️ Ineficiente"
                                 else:
                                     return "🛡️ Baixo Impacto"

                             df_merged['Veredito'] = df_merged.apply(classify_team, axis=1)

                             st.success(f"🚀 **Oportunidade Inteligente: {team_rec}**")
                             st.markdown(f"""
                             **Análise Estratégica:**
                             - **Alta Visibilidade:** {gp_rec} gols marcados.
                             - **Baixo Custo:** Score de valuation {val_rec:.1f} (Abaixo da média de mercado).
                             - **Veredito:** {label_veredicto}
                             """)
                             
                             st.markdown("#### Análise Estratégica Completa (Todos os Times)")
                             st.dataframe(
                                 df_merged[['escudo', 'Time', 'Veredito', 'GP', 'Valor_Patrocinio', 'ROI_Score']].sort_values(by='ROI_Score', ascending=False),
                                 column_config={
                                     "escudo": st.column_config.ImageColumn("Escudo", width="small"),
                                     "Time": "Time",
                                     "Veredito": "Classificação",
                                     "GP": "Gols (Retorno)",
                                     "Valor_Patrocinio": st.column_config.NumberColumn("Custo (Score)", format="%.2f"),
                                     "ROI_Score": st.column_config.NumberColumn("ROI", format="%.4f")
                                 },
                                 hide_index=True,
                                 use_container_width=True
                             )

                             # 4. Scatter Plot: Valuation vs Goals
                             
                             # Define Quadrants
                             median_val = df_merged['Valor_Patrocinio'].median()
                             median_gp = df_merged['GP'].median()
                             
                             def get_quadrant(row):
                                 if row['Time'] == team_rec:
                                     return '⭐ Smart Choice'
                                 elif row['GP'] >= median_gp and row['Valor_Patrocinio'] <= median_val:
                                     return '💎 Oportunidade (Alta Entrega / Baixo Custo)'
                                 elif row['GP'] >= median_gp and row['Valor_Patrocinio'] > median_val:
                                     return '🏆 Premium (Líderes / Caro)'
                                 elif row['GP'] < median_gp and row['Valor_Patrocinio'] > median_val:
                                     return '⚠️ Baixo Retorno / Custo Alto'
                                 else:
                                     return '📉 Baixa Visibilidade'

                             df_merged['Categoria ROI'] = df_merged.apply(get_quadrant, axis=1)
                             
                             color_map_roi = {
                                 '⭐ Smart Choice': '#FFD700',      # Gold
                                 '💎 Oportunidade (Alta Entrega / Baixo Custo)': '#00CC96', # Greenish
                                 '🏆 Premium (Líderes / Caro)': '#636EFA', # Blue
                                 '⚠️ Baixo Retorno / Custo Alto': '#EF553B', # Red
                                 '📉 Baixa Visibilidade': '#AB63FA' # Purple
                             }

                             col_scout1, col_scout2 = st.columns([1, 1.5])
                             
                             with col_scout1:
                                 st.write("📊 Top Eficiência (Gols / Custo)")
                                 st.dataframe(
                                     df_merged[['Time', 'GP', 'Valor_Patrocinio']].sort_values(by='GP', ascending=False), # Show raw data sorted by Goals but context is ROI
                                     column_config={
                                         "Valor_Patrocinio": st.column_config.NumberColumn("Score Valor", format="%.1f"),
                                         "GP": "Gols"
                                     },
                                     hide_index=True
                                 )

                             with col_scout2:
                                 st.write("📈 Matriz de Decisão: Visibilidade x Custo")
                                 fig_roi = px.scatter(
                                     df_merged,
                                     x='Valor_Patrocinio',
                                     y='GP',
                                     color='Categoria ROI',
                                     text='Time',
                                     color_discrete_map=color_map_roi,
                                     title="Onde investir meu dinheiro?",
                                     labels={'Valor_Patrocinio': 'Custo (Valuation Score)', 'GP': 'Retorno (Gols)'}
                                 )
                                 # Add reference lines (medians)
                                 fig_roi.add_vline(x=median_val, line_dash="dash", line_color="grey", annotation_text="Custo Médio")
                                 fig_roi.add_hline(y=median_gp, line_dash="dash", line_color="grey", annotation_text="Entrega Média")
                                 
                                 fig_roi.update_traces(textposition='top center', marker=dict(size=10))
                                 st.plotly_chart(fig_roi, key=f"roi_{escolha_liga}")
                        
                        else:
                            st.warning("Valuation de patrocínio não disponível para realizar a análise cruzada.")

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