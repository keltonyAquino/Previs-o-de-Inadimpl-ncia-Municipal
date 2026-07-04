import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sqlalchemy import create_engine
import plotly.express as px

# Configurações
st.set_page_config(page_title="Monitor de Crédito RJ (2023-2024)", layout="wide", page_icon="🏙️")
DB_URL = "sqlite:///projeto_inadimplencia.db"
engine = create_engine(DB_URL)

@st.cache_resource
def load_model():
    try:
        model = joblib.load('models/xgb_model.pkl')
        columns = joblib.load('models/model_columns.pkl')
        return model, columns
    except:
        return None, None

@st.cache_data
def load_data():
    query = """
    SELECT 
        m.nome, m.populacao_2022, m.pib_2021,
        AVG(e.provisao_devedores_duvidosos / e.saldo_operacoes_credito) as taxa_media,
        MAX(e.ano) as ultimo_ano
    FROM municipios m
    JOIN estban_mensal e ON m.codigo_ibge = e.codigo_ibge
    GROUP BY m.codigo_ibge
    """
    return pd.read_sql(query, engine)

def main():
    st.title("🏙️ Monitor de Inadimplência Municipal: Rio de Janeiro")
    st.subheader("Análise Atualizada (Censo 2022 | Ciclo 2023-2024)")
    
    df_rj = load_data()
    model, model_cols = load_model()
    
    if df_rj.empty:
        st.error("Dados não encontrados. Por favor, execute o pipeline de dados.")
        return

    # Sidebar para Filtros
    st.sidebar.header("Configurações da Análise")
    top_n = st.sidebar.slider("Mostrar top municípios por PIB", 5, 20, 10)

    # Métricas de Destaque
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Municípios Analisados", len(df_rj))
    m2.metric("População (Censo 2022)", f"{df_rj['populacao_2022'].sum():,}")
    m3.metric("PIB Médio (2021)", f"R$ {df_rj['pib_2021'].mean():,.0f}")
    m4.metric("Inadimplência Média", f"{df_rj['taxa_media'].mean()*100:.2f}%")

    st.divider()

    # Layout Principal
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 🏆 Top Municípios por PIB")
        fig_bar = px.bar(df_rj.sort_values('pib_2021', ascending=False).head(top_n), 
                        x='nome', y='pib_2021', color='taxa_media',
                        labels={'pib_2021': 'PIB (R$)', 'taxa_media': 'Risco'},
                        color_continuous_scale='Reds')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown("### 📊 Relação População vs Inadimplência")
        fig_scatter = px.scatter(df_rj, x='populacao_2022', y='taxa_media', 
                                size='pib_2021', hover_name='nome',
                                title="Censo 2022: Tamanho Populacional vs Taxa de Risco",
                                labels={'populacao_2022': 'Habitantes', 'taxa_media': 'Taxa de Inadimplência'})
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    # Simulador de Previsão 2024
    st.markdown("### 🔮 Simulador Preditor de Inadimplência (XGBoost)")
    st.info("Este simulador utiliza o modelo treinado para prever o comportamento do crédito em 2024.")
    
    if model:
        c1, c2, c3 = st.columns(3)
        with c1:
            mun_selecionado = st.selectbox("Escolha o Município", df_rj['nome'].sort_values())
            dados_m = df_rj[df_rj['nome'] == mun_selecionado].iloc[0]
        with c2:
            saldo_proj = st.number_input("Volume de Crédito Projetado (R$)", value=1000000, step=100000)
        with c3:
            mes_proj = st.slider("Mês de Referência (2024)", 1, 12, 6)

        # Preparação do Input
        input_data = pd.DataFrame([{
            'populacao_2022': dados_m['populacao_2022'],
            'pib_2021': dados_m['pib_2021'],
            'mes': mes_proj,
            'saldo_operacoes_credito': saldo_proj,
            'taxa_in_lag1': 0.07, # Valor base simulado
            'pib_per_capita': dados_m['pib_2021'] / dados_m['populacao_2022']
        }])

        # Ajuste de colunas para o modelo
        for col in model_cols:
            if col not in input_data.columns:
                input_data[col] = 0
        input_data = input_data[model_cols]

        pred = model.predict(input_data)[0]
        
        st.write(f"#### Resultado da Análise para **{mun_selecionado}**")
        if pred > 0.09:
            st.error(f"⚠️ **Risco Elevado**: Taxa prevista de **{pred*100:.2f}%**. Recomenda-se cautela na concessão de novos créditos.")
        else:
            st.success(f"✅ **Risco Controlado**: Taxa prevista de **{pred*100:.2f}%**. Cenário favorável para o período.")
    else:
        st.warning("Modelo não carregado. Treine o modelo para habilitar a previsão.")

if __name__ == "__main__":
    main()
