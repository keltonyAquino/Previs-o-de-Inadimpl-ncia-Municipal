# Previsão de Inadimplência Municipal 🏦📉

Este projeto foi desenvolvido para demonstrar habilidades em **Data Science**, abrangendo desde a coleta de dados públicos até o deploy de um dashboard interativo. O objetivo é prever a taxa de inadimplência em municípios brasileiros utilizando indicadores econômicos e sociais.

## 🚀 Funcionalidades

- **ETL Automatizado**: Coleta de dados do IBGE (PIB e População) via API SIDRA.
- **Integração SQL**: Armazenamento e manipulação de dados em banco de dados SQL (PostgreSQL/SQLite).
- **Machine Learning**: Modelo preditivo utilizando **XGBoost** para estimar o risco de crédito.
- **Dashboard Interativo**: Visualização de resultados e simulações via **Streamlit**.

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.11
- **Banco de Dados**: PostgreSQL (via SQLAlchemy)
- **Manipulação de Dados**: Pandas, NumPy
- **Machine Learning**: XGBoost, Scikit-learn
- **Visualização**: Plotly, Streamlit
- **APIs**: IBGE (sidrapy), Banco Central (python-bcb)

## 📁 Estrutura do Projeto

```text
projeto_inadimplencia/
├── app/                # Código do Dashboard Streamlit
├── data/               # Dados brutos e processados
├── models/             # Modelos de ML treinados
├── notebooks/          # Análise Exploratória (EDA)
├── scripts/            # Scripts de ETL e Treinamento
├── requirements.txt    # Dependências do projeto
└── README.md           # Documentação
```

## 📊 Como Executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/projeto-inadimplencia.git
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o pipeline de dados:
   ```bash
   python scripts/etl_completo.py
   ```
4. Treine o modelo:
   ```bash
   python scripts/train_model.py
   ```
5. Inicie o dashboard:
   ```bash
   streamlit run app/main.py
   ```

---
Desenvolvido como parte de um portfólio de Ciência de Dados.
