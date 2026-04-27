import pandas as pd
import plotly.express as px
import streamlit as st

from config import LIGAS_MAP, TEMPORADAS_DISPONIVEIS
from data_frames import data_frames, data_frames_artilheiros
from funcoes import (
    melhor_ataque,
    melhor_defesa,
    obter_codigo_liga,
    obter_dados_artilheiros,
    obter_dados_historicos,
    obter_dados_ligas,
)
from patrocinio import calcular_valor_patrocinio


COLUNAS_TABELA = {
    "posicao": "Posição",
    "escudo": "Escudo",
    "nome": "Time",
    "pontos": "Pontos",
    "jogos": "J",
    "gols_pro": "GP",
    "gols_contra": "GC",
    "saldo_gols": "SG",
}


def configurar_pagina():
    st.set_page_config(page_title="Fut.Analytica", layout="wide")
    st.title("Fut.Analytica ⚽")
    st.write("Bem-vindo ao app Fut.Analytica")

    st.markdown(
        """
        <style>
        div[data-testid="stDataFrame"] {
            font-size: 0.8rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def obter_filtros_sidebar():
    st.sidebar.header("Configurações")
    escolha_liga = st.sidebar.selectbox("Escolha um campeonato:", list(LIGAS_MAP.keys()))
    escolha_season = st.sidebar.selectbox(
        "Escolha a temporada:",
        options=TEMPORADAS_DISPONIVEIS,
        index=0,
    )
    processar = st.sidebar.button("Processar Dados")
    return escolha_liga, escolha_season, processar


def montar_dataframe_tabela(dados):
    return data_frames(dados).rename(columns=COLUNAS_TABELA)


def renderizar_classificacao(df_tabela):
    st.subheader("Classificação")
    st.dataframe(
        df_tabela[["Posição", "Escudo", "Time", "Pontos", "GP", "GC"]],
        column_config={
            "Escudo": st.column_config.ImageColumn("Escudo"),
            "Time": st.column_config.TextColumn("Time", width="medium"),
        },
        hide_index=True,
        width="stretch",
    )


def renderizar_artilharia(dados_artilheiros):
    st.subheader("Artilharia")
    if not dados_artilheiros:
        st.info("Artilharia não disponível.")
        return

    df_art = data_frames_artilheiros(dados_artilheiros)
    st.dataframe(
        df_art[["nome", "gols", "time", "escudo"]].head(20),
        column_config={
            "nome": "Jogador",
            "gols": "Gols",
            "time": "Time",
            "escudo": st.column_config.ImageColumn("Escudo"),
        },
        hide_index=True,
        width="stretch",
    )


def renderizar_resumo(df_tabela):
    ataque = melhor_ataque(df_tabela)
    defesa = melhor_defesa(df_tabela)
    col1, col2 = st.columns(2)

    with col1:
        if ataque is not None:
            st.metric(label="Melhor Ataque", value=ataque["Time"], delta=f"{ataque['GP']} Gols")

    with col2:
        if defesa is not None:
            st.metric(
                label="Melhor Defesa",
                value=defesa["Time"],
                delta=f"{defesa['GC']} Gols Sofridos",
                delta_color="inverse",
            )


def categorizar_ataques(df_tabela):
    df_ordenado = df_tabela.sort_values(by="GP", ascending=False).copy()
    top_5 = set(df_ordenado.head(5).index)
    bottom_5 = set(df_ordenado.tail(5).index)

    def get_color_category(idx):
        if idx in top_5:
            return "Melhores Ataques"
        if idx in bottom_5:
            return "Piores Ataques"
        return "Outros"

    df_ordenado["categoria"] = df_ordenado.index.map(get_color_category)
    return df_ordenado


def renderizar_grafico_dispersao(df_tabela, liga, temporada):
    st.subheader(f"Gráfico de Dispersão: {liga} ({temporada})")
    df_plot = categorizar_ataques(df_tabela)

    fig = px.scatter(
        df_plot,
        x="GP",
        y="GC",
        hover_data=["Time"],
        text="Time",
        color="categoria",
        color_discrete_map={
            "Melhores Ataques": "lightgreen",
            "Piores Ataques": "lightcoral",
            "Outros": "lightblue",
        },
        title=f"Dispersão de Gols - {liga} ({temporada})",
        labels={"GP": "Gols Pró", "GC": "Gols Sofridos", "categoria": "Legenda"},
    )
    fig.update_traces(textposition="top center", marker=dict(size=12))
    st.plotly_chart(fig, key=f"scatter_{liga}_{temporada}")


def renderizar_mandante_visitante(df_tabela, liga, temporada):
    st.divider()
    st.subheader("🏠 Desempenho: Gols Mandante x Visitante")

    if "gols_casa" not in df_tabela.columns or "gols_fora" not in df_tabela.columns:
        st.info("Dados de Gols Mandante/Visitante não disponíveis para esta temporada.")
        return

    df_ha = df_tabela.sort_values(by="GP", ascending=False).head(12)
    df_melted_ha = df_ha.melt(
        id_vars=["Time"],
        value_vars=["gols_casa", "gols_fora"],
        var_name="Local",
        value_name="Gols",
    )

    fig_ha = px.bar(
        df_melted_ha,
        x="Time",
        y="Gols",
        color="Local",
        title="Top 12 Ataques: Onde eles marcam mais?",
        barmode="group",
        labels={"Local": "Mando", "Gols": "Gols Marcados", "Time": "Time"},
        color_discrete_map={"gols_casa": "#3498db", "gols_fora": "#e74c3c"},
    )
    nomes_legenda = {"gols_casa": "Em Casa 🏠", "gols_fora": "Fora de Casa ✈️"}
    fig_ha.for_each_trace(lambda trace: trace.update(name=nomes_legenda.get(trace.name, trace.name)))
    st.plotly_chart(fig_ha, key=f"ha_{liga}_{temporada}")


def renderizar_patrocinio(codigo_liga, temporada):
    st.divider()
    st.subheader("💰 Valuation de Patrocínio")
    st.markdown("##### Top 3 patrocínios mais caros")

    with st.spinner("Calculando valor de patrocínio..."):
        dados_patrocinio = calcular_valor_patrocinio(codigo_liga, temporada)

    if not dados_patrocinio:
        st.warning("Não foi possível calcular o valuation de patrocínio (falta de dados de público ou histórico).")
        return None

    medals = ["🥇", "🥈", "🥉"]
    for index, (coluna, time) in enumerate(zip(st.columns(3), dados_patrocinio[:3])):
        with coluna:
            st.metric(
                label=f"{medals[index]} {time['Time']}",
                value=f"{time['Valor_Patrocinio']}",
                delta=f"Público: {time['Pontos_Publico']} | Hist: {time['Pontos_Historico']}",
            )

    df_patrocinio = pd.DataFrame(dados_patrocinio)
    st.markdown("### Ranking Completo")
    st.dataframe(
        df_patrocinio[
            ["Escudo", "Time", "Valor_Patrocinio", "Pontos_Publico", "Pontos_Historico", "Pontos_Atual", "Media_Publico"]
        ],
        column_config={
            "Escudo": st.column_config.ImageColumn("Escudo", width="small"),
            "Time": "Time",
            "Valor_Patrocinio": st.column_config.NumberColumn("Score Final", format="%.2f"),
            "Pontos_Publico": "Pts Público (60%)",
            "Pontos_Historico": "Pts Histórico (30%)",
            "Pontos_Atual": "Pts Atual (10%)",
            "Media_Publico": "Média Público",
        },
        hide_index=True,
        width="stretch",
    )

    renderizar_composicao_patrocinio(df_patrocinio)
    return dados_patrocinio


def renderizar_composicao_patrocinio(df_patrocinio):
    st.markdown("### Composição do Score (Top 10)")
    top10 = df_patrocinio.head(10).copy()
    top10["Contrib. Público"] = top10["Pontos_Publico"] * 0.6
    top10["Contrib. Histórico"] = top10["Pontos_Historico"] * 0.3
    top10["Contrib. Atual"] = top10["Pontos_Atual"] * 0.1

    df_melted_pat = top10.melt(
        id_vars=["Time"],
        value_vars=["Contrib. Público", "Contrib. Histórico", "Contrib. Atual"],
        var_name="Componente",
        value_name="Pontos Ponderados",
    )

    fig_val = px.bar(
        df_melted_pat,
        x="Time",
        y="Pontos Ponderados",
        color="Componente",
        title="Composição do Valor de Patrocínio",
        labels={"Pontos Ponderados": "Score Contribuído"},
    )
    st.plotly_chart(fig_val, key="val_patrocinio")


def escolher_melhor_oportunidade(df_merged):
    median_val = df_merged["Valor_Patrocinio"].median()
    median_gp = df_merged["GP"].median()
    opportunities = df_merged[(df_merged["GP"] >= median_gp) & (df_merged["Valor_Patrocinio"] <= median_val)]

    if not opportunities.empty:
        escolha = opportunities.sort_values(by=["GP", "Valor_Patrocinio"], ascending=[False, True]).iloc[0]
        return escolha, "Este time está no quadrante de 'Oportunidade': Entrega acima da média por um custo abaixo da média."

    top_scorers = df_merged[df_merged["GP"] >= median_gp]
    if not top_scorers.empty:
        escolha = top_scorers.sort_values(by="ROI_Score", ascending=False).iloc[0]
        return escolha, "Não há times de baixo custo com alta entrega. Esta é a opção mais eficiente entre os líderes de gols."

    escolha = df_merged.sort_values(by="ROI_Score", ascending=False).iloc[0]
    return escolha, "Melhor retorno por ponto investido."


def renderizar_scouting_curto_prazo(df_tabela, dados_patrocinio, liga):
    if not dados_patrocinio:
        st.warning("Valuation de patrocínio não disponível para realizar a análise cruzada.")
        return

    df_val = pd.DataFrame(dados_patrocinio)
    df_merged = pd.merge(df_tabela, df_val[["Time", "Valor_Patrocinio"]], on="Time", how="inner")
    if df_merged.empty:
        st.warning("Não há times compatíveis entre classificação e valuation para análise cruzada.")
        return

    df_merged["ROI_Score"] = df_merged["GP"] / df_merged["Valor_Patrocinio"]
    best_choice, label_veredicto = escolher_melhor_oportunidade(df_merged)
    median_val = df_merged["Valor_Patrocinio"].median()
    median_gp = df_merged["GP"].median()
    team_rec = best_choice["Time"]

    df_merged["Veredito"] = df_merged.apply(lambda row: classificar_time(row, median_gp, median_val), axis=1)

    st.success(f"🚀 **Oportunidade Inteligente: {team_rec}**")
    st.markdown(
        f"""
        **Análise Estratégica:**
        - **Alta Visibilidade:** {best_choice['GP']} gols marcados.
        - **Baixo Custo:** Score de valuation {best_choice['Valor_Patrocinio']:.1f} (Abaixo da média de mercado).
        - **Veredito:** {label_veredicto}
        """
    )

    st.markdown("#### Análise Estratégica Completa (Todos os Times)")
    st.dataframe(
        df_merged[["Escudo", "Time", "Veredito", "GP", "Valor_Patrocinio", "ROI_Score"]].sort_values(
            by="ROI_Score",
            ascending=False,
        ),
        column_config={
            "Escudo": st.column_config.ImageColumn("Escudo", width="small"),
            "Time": "Time",
            "Veredito": "Classificação",
            "GP": "Gols (Retorno)",
            "Valor_Patrocinio": st.column_config.NumberColumn("Custo (Score)", format="%.2f"),
            "ROI_Score": st.column_config.NumberColumn("ROI", format="%.4f"),
        },
        hide_index=True,
        width="stretch",
    )

    renderizar_matriz_roi(df_merged, team_rec, median_gp, median_val, liga)


def classificar_time(row, median_gp, median_val):
    if row["GP"] >= median_gp and row["Valor_Patrocinio"] <= median_val:
        return "💎 Oportunidade"
    if row["GP"] >= median_gp and row["Valor_Patrocinio"] > median_val:
        return "🏆 Premium"
    if row["GP"] < median_gp and row["Valor_Patrocinio"] > median_val:
        return "⚠️ Ineficiente"
    return "🛡️ Baixo Impacto"


def obter_categoria_roi(row, team_rec, median_gp, median_val):
    if row["Time"] == team_rec:
        return "⭐ Smart Choice"
    if row["GP"] >= median_gp and row["Valor_Patrocinio"] <= median_val:
        return "💎 Oportunidade (Alta Entrega / Baixo Custo)"
    if row["GP"] >= median_gp and row["Valor_Patrocinio"] > median_val:
        return "🏆 Premium (Líderes / Caro)"
    if row["GP"] < median_gp and row["Valor_Patrocinio"] > median_val:
        return "⚠️ Baixo Retorno / Custo Alto"
    return "📉 Baixa Visibilidade"


def renderizar_matriz_roi(df_merged, team_rec, median_gp, median_val, liga):
    df_merged["Categoria ROI"] = df_merged.apply(
        lambda row: obter_categoria_roi(row, team_rec, median_gp, median_val),
        axis=1,
    )
    df_merged["Text_Label"] = df_merged["Time"].where(df_merged["Time"] == team_rec, "")

    col_scout1, col_scout2 = st.columns([1, 1.5])

    with col_scout1:
        st.write("📊 Top Eficiência (Gols / Custo)")
        st.dataframe(
            df_merged[["Time", "GP", "Valor_Patrocinio"]].sort_values(by="GP", ascending=False),
            column_config={
                "Valor_Patrocinio": st.column_config.NumberColumn("Score Valor", format="%.1f"),
                "GP": "Gols",
            },
            hide_index=True,
        )

    with col_scout2:
        st.write("📈 Matriz de Decisão: Visibilidade x Custo")
        fig_roi = px.scatter(
            df_merged,
            x="Valor_Patrocinio",
            y="GP",
            color="Categoria ROI",
            text="Text_Label",
            hover_name="Time",
            color_discrete_map={
                "⭐ Smart Choice": "#FFD700",
                "💎 Oportunidade (Alta Entrega / Baixo Custo)": "#00CC96",
                "🏆 Premium (Líderes / Caro)": "#636EFA",
                "⚠️ Baixo Retorno / Custo Alto": "#EF553B",
                "📉 Baixa Visibilidade": "#AB63FA",
            },
            title="Onde investir meu dinheiro?",
            labels={"Valor_Patrocinio": "Custo (Valuation Score)", "GP": "Retorno (Gols)"},
        )
        fig_roi.add_vline(x=median_val, line_dash="dash", line_color="grey", annotation_text="Custo Médio")
        fig_roi.add_hline(y=median_gp, line_dash="dash", line_color="grey", annotation_text="Entrega Média")
        fig_roi.update_traces(textposition="top center", marker=dict(size=10))
        st.plotly_chart(fig_roi, key=f"roi_{liga}")


def renderizar_scouting_longo_prazo(codigo_liga, temporada):
    st.markdown("### Análise de Consistência Histórica")
    with st.spinner("Analisando histórico de temporadas..."):
        historico = obter_dados_historicos(codigo_liga, temporada)

    if len(historico) < 2:
        st.warning("Dados históricos insuficientes para análise de longo prazo.")
        return

    teams_per_year = [set(pd.DataFrame(dados_ano)["nome"]) for dados_ano in historico.values()]
    common_teams = set.intersection(*teams_per_year)
    if not common_teams:
        st.warning("Não há times que jogaram todas as temporadas selecionadas (possível alta rotatividade na liga).")
        return

    team_stats = []
    for team in common_teams:
        stats = {"Time": team, "Total Gols": 0}
        for ano, dados_ano in historico.items():
            df_ano = pd.DataFrame(dados_ano)
            goals = df_ano[df_ano["nome"] == team].iloc[0]["gols_pro"]
            stats["Total Gols"] += goals
            stats[ano] = goals
        team_stats.append(stats)

    df_historic = pd.DataFrame(team_stats).sort_values(by="Total Gols", ascending=False)
    top_5_historic = df_historic.head(5)
    best_long_term = top_5_historic.iloc[0]
    num_seasons = len(historico)

    st.success(f"💎 **Investimento Seguro (Longo Prazo): {best_long_term['Time']}**")
    st.markdown(
        f"""
        **Análise de Consistência:**
        - **Domínio Histórico**: O **{best_long_term['Time']}** é o time mais ofensivo acumulado no período analisado (**{best_long_term['Total Gols']/num_seasons:.1f} média de gols por temporada**).
        - **Estabilidade**: Presença garantida na elite e entrega constante de "tempo de tela" (gols).
        - **Veredito:** A "Blue Chip" do campeonato. Ideal para contratos longos (2+ anos).
        """
    )

    anos_cols = [col for col in df_historic.columns if col not in ["Time", "Total Gols"]]
    df_melted = top_5_historic.melt(id_vars=["Time"], value_vars=anos_cols, var_name="Temporada", value_name="Gols")
    df_melted = df_melted.sort_values(by="Temporada")

    fig_hist = px.bar(
        df_melted,
        x="Time",
        y="Gols",
        color="Temporada",
        barmode="group",
        title="Evolução dos Top 5 Ataques (Times Consistentes)",
        text="Gols",
    )
    fig_hist.update_traces(textposition="outside")
    st.plotly_chart(fig_hist, key=f"hist_{codigo_liga}_{temporada}")


def renderizar_scouting(df_tabela, dados_patrocinio, codigo_liga, liga, temporada):
    st.divider()
    st.subheader("🤖 Scouting Intelligence - Gol de Placa")

    tab_curto, tab_longo = st.tabs(["Curto Prazo (Temporada Atual)", "Longo Prazo (Consistência)"])
    with tab_curto:
        renderizar_scouting_curto_prazo(df_tabela, dados_patrocinio, liga)
    with tab_longo:
        renderizar_scouting_longo_prazo(codigo_liga, temporada)


def renderizar_dashboard(liga, temporada, codigo_liga):
    st.divider()
    st.subheader(f"{liga} - Temporada {temporada}")

    with st.spinner(f"Buscando dados para {liga} ({temporada})..."):
        dados, fonte = obter_dados_ligas(codigo_liga, temporada)
        dados_artilheiros = obter_dados_artilheiros(codigo_liga, temporada)

    if fonte == "Arquivo Local":
        st.warning("⚠️ API Indisponível no momento (Limite de Requisições ou Conexão). Exibindo dados locais (Backup).")

    if not dados:
        st.warning(f"Não foi possível obter dados para {liga} ({temporada}).")
        return

    try:
        df_tabela = montar_dataframe_tabela(dados)
        col_tab, col_art = st.columns([1.8, 1.2])

        with col_tab:
            renderizar_classificacao(df_tabela)
        with col_art:
            renderizar_artilharia(dados_artilheiros)

        renderizar_resumo(df_tabela)
        renderizar_grafico_dispersao(df_tabela, liga, temporada)
        renderizar_mandante_visitante(df_tabela, liga, temporada)
        dados_patrocinio = renderizar_patrocinio(codigo_liga, temporada)
        renderizar_scouting(df_tabela, dados_patrocinio, codigo_liga, liga, temporada)

    except Exception as erro:
        st.error(f"Erro ao exibir dados para {liga} ({temporada}): {erro}")


def main():
    configurar_pagina()
    escolha_liga, escolha_season, processar = obter_filtros_sidebar()

    if not processar:
        return

    codigo_liga = obter_codigo_liga(escolha_liga)
    if not codigo_liga:
        st.error(f"Liga não encontrada: {escolha_liga}")
        return

    renderizar_dashboard(escolha_liga, escolha_season, codigo_liga)


if __name__ == "__main__":
    main()
