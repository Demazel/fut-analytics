import html

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

CORES_GRAFICOS = {
    "principal": "#1f4e5f",
    "secundaria": "#d9822b",
    "positivo": "#2f855a",
    "negativo": "#c53030",
    "neutro": "#718096",
    "apoio": "#6b46c1",
}

PALETA_COMPONENTES = ["#1f4e5f", "#d9822b", "#2f855a"]

TEMA_ESCURO = {
    "bg": "#0f141b",
    "surface": "#172026",
    "surface_soft": "#202b33",
    "text": "#f6f7f3",
    "muted": "#b7c0c7",
    "line": "#2b3740",
    "accent": "#53a2be",
    "accent_2": "#f0a340",
    "sidebar_bg": "#090d12",
    "sidebar_text": "#f6f7f3",
    "input_bg": "#121923",
    "plot_bg": "#121923",
    "grid": "#2b3740",
}


def configurar_pagina():
    st.set_page_config(page_title="Fut.Analytica", layout="wide")


def aplicar_visual():
    cores = TEMA_ESCURO

    st.markdown(
        f"""
        <style>
        :root {{
            --bg: {cores["bg"]};
            --surface: {cores["surface"]};
            --surface-soft: {cores["surface_soft"]};
            --text: {cores["text"]};
            --muted: {cores["muted"]};
            --line: {cores["line"]};
            --accent: {cores["accent"]};
            --accent-2: {cores["accent_2"]};
            --sidebar-bg: {cores["sidebar_bg"]};
            --sidebar-text: {cores["sidebar_text"]};
            --input-bg: {cores["input_bg"]};
        }}

        .stApp {{
            background: var(--bg);
            color: var(--text);
        }}

        [data-testid="stHeader"] {{
            background: var(--bg);
        }}

        [data-testid="stToolbar"] {{
            color: var(--text);
        }}

        [data-testid="stSidebar"] {{
            background: var(--sidebar-bg);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}

        [data-testid="stSidebar"] * {{
            color: var(--sidebar-text);
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background: var(--input-bg);
            border-color: rgba(255, 255, 255, 0.12);
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] span,
        [data-testid="stSidebar"] [data-baseweb="select"] input {{
            color: var(--sidebar-text) !important;
        }}

        [data-testid="stSidebar"] button {{
            background: var(--accent-2);
            border: 0;
            color: #172026;
            font-weight: 700;
        }}

        [data-testid="stSidebar"] button:focus {{
            border-color: var(--accent-2);
            box-shadow: 0 0 0 2px rgba(217, 130, 43, 0.28);
            outline: none;
        }}

        .block-container {{
            padding-top: 2.4rem;
            padding-bottom: 3rem;
            max-width: 1240px;
        }}

        .hero {{
            border-bottom: 1px solid var(--line);
            margin-bottom: 1.4rem;
            padding-bottom: 1.1rem;
        }}

        .hero h1 {{
            color: var(--text);
            font-size: 2.35rem;
            font-weight: 800;
            letter-spacing: 0;
            line-height: 1.05;
            margin: 0 0 .35rem 0;
        }}

        .hero p {{
            color: var(--muted);
            font-size: 1rem;
            margin: 0;
            max-width: 780px;
        }}

        .data-strip {{
            display: grid;
            gap: .85rem;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            margin: .9rem 0 1.1rem 0;
        }}

        .data-strip div {{
            background: var(--surface);
            border: 1px solid var(--line);
            border-left: 4px solid var(--accent);
            border-radius: 6px;
            padding: .75rem .85rem;
        }}

        .data-strip span {{
            color: var(--muted);
            display: block;
            font-size: .75rem;
            letter-spacing: .04em;
            text-transform: uppercase;
        }}

        .data-strip strong {{
            color: var(--text);
            display: block;
            font-size: 1rem;
            margin-top: .18rem;
        }}

        .callout {{
            background: var(--surface-soft);
            border: 1px solid var(--line);
            border-left: 4px solid var(--accent-2);
            border-radius: 6px;
            color: var(--text);
            margin-top: .95rem;
            padding: .85rem 1rem;
        }}

        .notice {{
            background: var(--surface-soft);
            border: 1px solid var(--line);
            border-left: 4px solid var(--accent);
            border-radius: 6px;
            color: var(--text);
            font-weight: 600;
            margin: .65rem 0 1rem 0;
            padding: .85rem 1rem;
        }}

        .notice.warning {{
            border-left-color: var(--accent-2);
        }}

        h2, h3, h4, p, label {{
            color: var(--text);
            letter-spacing: 0;
        }}

        [data-testid="stMetric"] {{
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 6px;
            padding: .75rem .85rem;
        }}

        [data-testid="stMetricLabel"],
        [data-testid="stMetricDelta"] {{
            color: var(--muted);
        }}

        [data-testid="stMetricValue"] {{
            color: var(--text);
            font-size: 1.55rem;
            letter-spacing: 0;
            line-height: 1.15;
        }}

        div[data-testid="stDataFrame"] {{
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 6px;
            font-size: 0.8rem !important;
        }}

        div[data-testid="stDataFrame"] * {{
            border-color: var(--line) !important;
        }}

        div[data-testid="stDataFrame"] [role="grid"],
        div[data-testid="stDataFrame"] [role="row"],
        div[data-testid="stDataFrame"] [role="gridcell"],
        div[data-testid="stDataFrame"] [role="columnheader"] {{
            background-color: var(--surface) !important;
            color: var(--text) !important;
        }}

        [data-testid="stAlert"] {{
            background: var(--surface-soft);
            border: 1px solid var(--line);
            border-left: 4px solid var(--accent-2);
            border-radius: 6px;
        }}

        [data-testid="stAlert"] * {{
            color: var(--text) !important;
        }}

        @media (max-width: 820px) {{
            .block-container {{
                padding-top: 1.4rem;
            }}

            .hero h1 {{
                font-size: 1.85rem;
            }}

            .data-strip {{
                grid-template-columns: 1fr;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <section class="hero">
            <h1>Fut.Analytica</h1>
            <p>Dashboard de dados de futebol para comparar desempenho esportivo, público médio e atratividade comercial por liga e temporada.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def obter_filtros_sidebar():
    st.sidebar.header("Filtros da análise")
    escolha_liga = st.sidebar.selectbox("Campeonato", list(LIGAS_MAP.keys()))
    escolha_season = st.sidebar.selectbox(
        "Temporada",
        options=TEMPORADAS_DISPONIVEIS,
        index=0,
    )
    processar = st.sidebar.button("Atualizar dashboard")
    st.sidebar.caption("Fonte: API Football Data com fallback para arquivos locais do projeto.")
    return escolha_liga, escolha_season, processar


def montar_dataframe_tabela(dados):
    return data_frames(dados).rename(columns=COLUNAS_TABELA)


def renderizar_aviso(mensagem, tipo="info"):
    classe = "warning" if tipo == "warning" else "info"
    st.markdown(
        f'<div class="notice {classe}">{html.escape(mensagem)}</div>',
        unsafe_allow_html=True,
    )


def aplicar_layout_grafico(fig, altura=500):
    cores = TEMA_ESCURO

    fig.update_layout(
        template="plotly_dark",
        height=altura,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=cores["plot_bg"],
        font=dict(family="Arial, sans-serif", color=cores["text"], size=12),
        title_text="",
        legend=dict(
            title_text="",
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11, color=cores["muted"]),
        ),
        margin=dict(l=42, r=24, t=58, b=58),
    )
    fig.update_xaxes(showgrid=True, gridcolor=cores["grid"], zeroline=False, title_standoff=12)
    fig.update_yaxes(showgrid=True, gridcolor=cores["grid"], zeroline=False, title_standoff=12)
    return fig


def renderizar_estado_inicial():
    st.markdown(
        """
        <div class="data-strip">
            <div><span>Escopo</span><strong>6 ligas europeias e brasileira</strong></div>
            <div><span>Análise</span><strong>classificação, gols e artilharia</strong></div>
            <div><span>Mercado</span><strong>score de patrocínio e público</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="callout">Escolha campeonato e temporada na lateral e atualize o dashboard para carregar a análise.</div>',
        unsafe_allow_html=True,
    )


def renderizar_contexto_dataset(df_tabela, fonte, temporada):
    total_times = len(df_tabela)
    media_gols = df_tabela["GP"].mean() if "GP" in df_tabela.columns and not df_tabela.empty else 0
    lider = df_tabela.iloc[0]["Time"] if not df_tabela.empty else "-"

    st.markdown(
        f"""
        <div class="data-strip">
            <div><span>Fonte dos dados</span><strong>{fonte}</strong></div>
            <div><span>Temporada {temporada}</span><strong>{total_times} clubes analisados</strong></div>
            <div><span>Líder da tabela</span><strong>{lider} · {media_gols:.1f} GP médios</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_classificacao(df_tabela):
    st.subheader("Tabela da liga")
    st.dataframe(
        df_tabela[["Posição", "Escudo", "Time", "Pontos", "GP", "GC"]],
        column_config={
            "Escudo": st.column_config.ImageColumn("Escudo"),
            "Time": st.column_config.TextColumn("Time", width="medium"),
        },
        hide_index=True,
        width="stretch",
    )


def renderizar_artilharia(dados_artilheiros, fonte):
    st.subheader("Artilharia")
    if not dados_artilheiros:
        if fonte == "Arquivo Local":
            renderizar_aviso("Artilharia indisponível no backup local. Esse bloco depende da API.")
        else:
            renderizar_aviso("Artilharia não disponível para a temporada selecionada.")
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
    st.subheader("Eficiência ofensiva x defensiva")
    df_plot = categorizar_ataques(df_tabela)

    fig = px.scatter(
        df_plot,
        x="GP",
        y="GC",
        hover_data=["Time"],
        text="Time",
        color="categoria",
        color_discrete_map={
            "Melhores Ataques": CORES_GRAFICOS["positivo"],
            "Piores Ataques": CORES_GRAFICOS["negativo"],
            "Outros": CORES_GRAFICOS["neutro"],
        },
        title=f"Gols marcados e sofridos · {liga} {temporada}",
        labels={"GP": "Gols Pró", "GC": "Gols Sofridos", "categoria": "Legenda"},
    )
    fig.update_traces(textposition="top center", marker=dict(size=11, line=dict(width=1, color="#ffffff")))
    st.plotly_chart(aplicar_layout_grafico(fig), key=f"scatter_{liga}_{temporada}", width="stretch")


def renderizar_mandante_visitante(df_tabela, liga, temporada):
    st.divider()
    st.subheader("Produção ofensiva por mando")

    if "gols_casa" not in df_tabela.columns or "gols_fora" not in df_tabela.columns:
        renderizar_aviso("Dados de Gols Mandante/Visitante não disponíveis para esta temporada.")
        return

    if df_tabela[["gols_casa", "gols_fora"]].fillna(0).sum().sum() == 0:
        renderizar_aviso("Dados de mando não disponíveis no backup local. Quando a API responde, este gráfico usa a divisão casa/fora.")
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
        color_discrete_map={"gols_casa": CORES_GRAFICOS["principal"], "gols_fora": CORES_GRAFICOS["secundaria"]},
    )
    nomes_legenda = {"gols_casa": "Casa", "gols_fora": "Fora"}
    fig_ha.for_each_trace(lambda trace: trace.update(name=nomes_legenda.get(trace.name, trace.name)))
    st.plotly_chart(aplicar_layout_grafico(fig_ha), key=f"ha_{liga}_{temporada}", width="stretch")


def renderizar_patrocinio(codigo_liga, temporada):
    st.divider()
    st.subheader("Score de patrocínio")
    st.markdown("##### Top 3 por atratividade comercial")

    with st.spinner("Calculando valor de patrocínio..."):
        dados_patrocinio = calcular_valor_patrocinio(codigo_liga, temporada)

    if not dados_patrocinio:
        renderizar_aviso("Não foi possível calcular o valuation de patrocínio (falta de dados de público ou histórico).", "warning")
        return None

    for index, (coluna, time) in enumerate(zip(st.columns(3), dados_patrocinio[:3])):
        with coluna:
            st.metric(
                label=f"{index + 1}º · {time['Time']}",
                value=f"{time['Valor_Patrocinio']}",
                delta=f"Público: {time['Pontos_Publico']} | Hist: {time['Pontos_Historico']}",
            )

    df_patrocinio = pd.DataFrame(dados_patrocinio)
    st.markdown("### Ranking de valuation")
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
        color_discrete_sequence=PALETA_COMPONENTES,
        title="Composição do Valor de Patrocínio",
        labels={"Pontos Ponderados": "Score Contribuído"},
    )
    st.plotly_chart(aplicar_layout_grafico(fig_val), key="val_patrocinio", width="stretch")


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
        renderizar_aviso("Valuation de patrocínio não disponível para realizar a análise cruzada.", "warning")
        return

    df_val = pd.DataFrame(dados_patrocinio)
    df_merged = pd.merge(df_tabela, df_val[["Time", "Valor_Patrocinio"]], on="Time", how="inner")
    if df_merged.empty:
        renderizar_aviso("Não há times compatíveis entre classificação e valuation para análise cruzada.", "warning")
        return

    df_merged["ROI_Score"] = df_merged["GP"] / df_merged["Valor_Patrocinio"]
    best_choice, label_veredicto = escolher_melhor_oportunidade(df_merged)
    median_val = df_merged["Valor_Patrocinio"].median()
    median_gp = df_merged["GP"].median()
    team_rec = best_choice["Time"]

    df_merged["Veredito"] = df_merged.apply(lambda row: classificar_time(row, median_gp, median_val), axis=1)

    st.success(f"Melhor relação entrega/custo: **{team_rec}**")
    st.markdown(
        f"""
        **Leitura do dado:**
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
        return "Oportunidade"
    if row["GP"] >= median_gp and row["Valor_Patrocinio"] > median_val:
        return "Premium"
    if row["GP"] < median_gp and row["Valor_Patrocinio"] > median_val:
        return "Ineficiente"
    return "Baixo impacto"


def obter_categoria_roi(row, team_rec, median_gp, median_val):
    if row["Time"] == team_rec:
        return "Melhor custo-benefício"
    if row["GP"] >= median_gp and row["Valor_Patrocinio"] <= median_val:
        return "Oportunidade"
    if row["GP"] >= median_gp and row["Valor_Patrocinio"] > median_val:
        return "Premium"
    if row["GP"] < median_gp and row["Valor_Patrocinio"] > median_val:
        return "Custo alto"
    return "Baixa visibilidade"


def renderizar_matriz_roi(df_merged, team_rec, median_gp, median_val, liga):
    df_merged["Categoria ROI"] = df_merged.apply(
        lambda row: obter_categoria_roi(row, team_rec, median_gp, median_val),
        axis=1,
    )
    df_merged["Text_Label"] = df_merged["Time"].where(df_merged["Time"] == team_rec, "")

    col_scout1, col_scout2 = st.columns([1, 1.8])

    with col_scout1:
        st.write("Top eficiência: gols por custo")
        st.dataframe(
            df_merged[["Time", "GP", "Valor_Patrocinio"]].sort_values(by="GP", ascending=False),
            column_config={
                "Valor_Patrocinio": st.column_config.NumberColumn("Score Valor", format="%.1f"),
                "GP": "Gols",
            },
            hide_index=True,
        )

    with col_scout2:
        st.write("Matriz de decisão: visibilidade x custo")
        fig_roi = px.scatter(
            df_merged,
            x="Valor_Patrocinio",
            y="GP",
            color="Categoria ROI",
            text="Text_Label",
            hover_name="Time",
            color_discrete_map={
                "Melhor custo-benefício": CORES_GRAFICOS["secundaria"],
                "Oportunidade": CORES_GRAFICOS["positivo"],
                "Premium": CORES_GRAFICOS["principal"],
                "Custo alto": CORES_GRAFICOS["negativo"],
                "Baixa visibilidade": CORES_GRAFICOS["neutro"],
            },
            title=None,
            labels={"Valor_Patrocinio": "Custo (Valuation Score)", "GP": "Retorno (Gols)"},
        )
        st.caption("Linhas tracejadas indicam as medianas de custo e gols.")
        fig_roi.add_vline(x=median_val, line_dash="dash", line_color="grey")
        fig_roi.add_hline(y=median_gp, line_dash="dash", line_color="grey")
        fig_roi.update_traces(textposition="top center", marker=dict(size=10, line=dict(width=1, color="#ffffff")))
        st.plotly_chart(aplicar_layout_grafico(fig_roi), key=f"roi_{liga}", width="stretch")


def renderizar_scouting_longo_prazo(codigo_liga, temporada):
    st.markdown("### Análise de Consistência Histórica")
    with st.spinner("Analisando histórico de temporadas..."):
        historico = obter_dados_historicos(codigo_liga, temporada)

    if len(historico) < 2:
        renderizar_aviso("Dados históricos insuficientes para análise de longo prazo.", "warning")
        return

    teams_per_year = [set(pd.DataFrame(dados_ano)["nome"]) for dados_ano in historico.values()]
    common_teams = set.intersection(*teams_per_year)
    if not common_teams:
        renderizar_aviso("Não há times que jogaram todas as temporadas selecionadas (possível alta rotatividade na liga).", "warning")
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

    st.success(f"Opção mais consistente no histórico: **{best_long_term['Time']}**")
    st.markdown(
        f"""
        **Análise de Consistência:**
        - **Domínio Histórico**: O **{best_long_term['Time']}** é o time mais ofensivo acumulado no período analisado (**{best_long_term['Total Gols']/num_seasons:.1f} média de gols por temporada**).
        - **Estabilidade**: Presença garantida na elite e entrega constante de "tempo de tela" (gols).
        - **Veredito:** Perfil mais previsível para contratos longos.
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
        color_discrete_sequence=["#1f4e5f", "#d9822b", "#2f855a"],
        barmode="group",
        title="Evolução dos Top 5 Ataques (Times Consistentes)",
        text="Gols",
    )
    fig_hist.update_traces(textposition="outside")
    st.plotly_chart(aplicar_layout_grafico(fig_hist), key=f"hist_{codigo_liga}_{temporada}", width="stretch")


def renderizar_scouting(df_tabela, dados_patrocinio, codigo_liga, liga, temporada):
    st.divider()
    st.subheader("Análise de oportunidade de patrocínio")

    tab_curto, tab_longo = st.tabs(["Temporada atual", "Consistência histórica"])
    with tab_curto:
        renderizar_scouting_curto_prazo(df_tabela, dados_patrocinio, liga)
    with tab_longo:
        renderizar_scouting_longo_prazo(codigo_liga, temporada)


def renderizar_dashboard(liga, temporada, codigo_liga):
    st.divider()
    st.subheader(f"{liga} · temporada {temporada}")

    with st.spinner(f"Buscando dados para {liga} ({temporada})..."):
        dados, fonte = obter_dados_ligas(codigo_liga, temporada)
        dados_artilheiros = obter_dados_artilheiros(codigo_liga, temporada)

    if fonte == "Arquivo Local":
        renderizar_aviso(
            "API indisponível ou sem token configurado. Exibindo backup local; artilharia e mando podem ficar indisponíveis.",
            "warning",
        )

    if not dados:
        renderizar_aviso(f"Não foi possível obter dados para {liga} ({temporada}).", "warning")
        return

    try:
        df_tabela = montar_dataframe_tabela(dados)
        renderizar_contexto_dataset(df_tabela, fonte, temporada)
        col_tab, col_art = st.columns([1.8, 1.2])

        with col_tab:
            renderizar_classificacao(df_tabela)
        with col_art:
            renderizar_artilharia(dados_artilheiros, fonte)

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
    aplicar_visual()

    if not processar:
        renderizar_estado_inicial()
        return

    codigo_liga = obter_codigo_liga(escolha_liga)
    if not codigo_liga:
        st.error(f"Liga não encontrada: {escolha_liga}")
        return

    renderizar_dashboard(escolha_liga, escolha_season, codigo_liga)


if __name__ == "__main__":
    main()
