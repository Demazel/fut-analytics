# Fut.Analytica ⚽

Este projeto é uma aplicação web de analytics de futebol construída com **Streamlit**, projetada para fornecer insights sobre ligas de futebol, desempenho de times e análise de valuation para patrocínios.

## 📋 Funcionalidades

- **Seleção de Ligas e Temporadas**: Acompanhe o Campeonato Brasileiro, Premier League, La Liga, Bundesliga, Serie A e Ligue 1 nas temporadas recentes (2023-2025).
- **Tabela de Classificação**: Visualização completa da classificação com pontos, vitórias, saldo de gols e mais.
- **Artilharia**: Lista dos principais goleadores da competição.
- **Análise de Desempenho**:
  - **Melhor Ataque e Defesa**: Destaques automáticos dos melhores e piores setores.
  - **Gráfico de Dispersão**: Visualização de "Gols Pró vs. Gols Sofridos" para identificar o perfil dos times.
  - **Desempenho Mandante x Visitante**: Comparativo de onde os times marcam mais gols.
- **💰 Valuation de Patrocínio**:
  - Cálculo de "Score de Patrocínio" baseado em Público (60%), Histórico (30%) e Desempenho Atual (10%).
  - Ranking dos patrocínios mais valiosos.
- **🤖 Scouting Intelligence**:
  - **Curto Prazo (Smart Choice)**: Identificação de oportunidades de investimento (times com alta visibilidade/gols e baixo custo de patrocínio).
  - **Longo Prazo**: Análise de consistência histórica para identificar times sólidos para contratos longos.

## 🛠️ Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/)**: Framework para construção da interface web interativa.
- **[Pandas](https://pandas.pydata.org/)**: Manipulação e análise de dados.
- **[Plotly](https://plotly.com/python/)**: Criação de gráficos interativos (dispersão, barras, etc.).
- **Python**: Linguagem principal do projeto.

## 🚀 Como Executar o Projeto

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/fut-analytics.git
   cd fut-analytics
   ```

2. **Instale as dependências**
   Certifique-se de ter o Python instalado. Em seguida, instale as bibliotecas necessárias:
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação**
   ```bash
   streamlit run main.py
   ```
   O navegador abrirá automaticamente com a aplicação rodando (geralmente em `http://localhost:8501`).

## 📂 Estrutura do Projeto

- `main.py`: Arquivo principal da aplicação Streamlit.
- `funcoes.py`: Funções auxiliares para busca e processamento de dados.
- `patrocinio.py`: Lógica para cálculo de valuation e score de patrocínio.
- `data_frames.py`: Manipulação e limpeza de DataFrames.
- `requirements.txt`: Lista de dependências do Python.

## 📊 Fontes de Dados

O projeto consome dados de APIs de futebol (como API-Football) ou utiliza arquivos locais em JSON como backup caso a API esteja indisponível.

---
Desenvolvido com ❤️ para fãs de futebol e dados.
