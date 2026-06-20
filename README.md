# Poluição do Ar Mundial e Índice de Qualidade do Ar (AQI) — 2014-2025

Dashboard interativo em Streamlit desenvolvido para a disciplina **EQM2009 –
Tópicos Especiais III** (Doutorado), com base no dataset *World Air
Pollution & AQI Dataset (2014–2025)* (Kaggle).

## Conteúdo do dashboard

Aplicação de página única, com filtros globais na barra lateral (país,
período, poluente em foco) e 4 abas de análise:

1. **Visão Geral Global** — mapa-múndi por AQI médio, distribuição da
   qualidade do ar e ranking de países.
2. **Tendências Temporais** — séries mensais de AQI e do poluente
   selecionado (2014–2025), além da sazonalidade média por mês.
3. **Poluentes & Correlações** — matriz de correlação entre poluentes,
   variáveis meteorológicas e socioeconômicas, dispersão com linha de
   tendência e comparação de poluentes entre países.
4. **Países & Cidades** — ranking de cidades mais/menos poluídas e tabela
   detalhada exportável em CSV.

## Como executar

1. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Rode o app:
   ```bash
   streamlit run app.py
   ```

4. O navegador abrirá automaticamente em `http://localhost:8501`.

## Estrutura do projeto

```
dashboard_project/
├── app.py              # aplicação Streamlit (único arquivo de código)
├── requirements.txt    # dependências
├── README.md
└── data/                # as 24 bases de dados originais (uma por país)
    ├── brazil_air_quality_2014_2025.csv
    ├── india_air_quality_2014_2025.csv
    └── ... (demais 22 países)
```

O `app.py` consolida automaticamente as 24 bases em memória (com cache),
padronizando nomes de colunas e adicionando a coluna `Pais`. **Não é
necessário** rodar nenhum script de preparação separado.

## Nota metodológica importante

A coluna original `AQI_Bucket` usa nomenclaturas distintas por país (ex.:
Índia usa *Satisfactory/Poor*, China usa *Excellent/Lightly Polluted*),
embora todas sigam as mesmas faixas numéricas de AQI (padrão semelhante ao
EPA dos EUA). Para permitir comparação justa entre países, o dashboard
recalcula a categoria **Qualidade do Ar** diretamente a partir do valor
numérico do AQI:

| Categoria | Faixa de AQI |
|---|---|
| Boa | 0–50 |
| Moderada | 51–100 |
| Insalubre (Grupos Sensíveis) | 101–150 |
| Insalubre | 151–200 |
| Muito Insalubre | 201–300 |
| Perigosa | > 300 |

## Possíveis extensões futuras

- Modelagem preditiva do AQI (regressão / aprendizado de máquina), citada
  como objetivo da disciplina mas deixada fora do escopo deste dashboard
  por opção da autora.
- Navegação multi-página (`st.Page` / pasta `pages/`) caso o conteúdo
  cresça além de uma única tela.
- Deploy no Streamlit Community Cloud (basta conectar este repositório).

## Fonte dos dados

Kaggle – *World Air Pollution & AQI Dataset (2014–2025)*.
