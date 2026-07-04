import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

# Configurações
DB_URL = "sqlite:///projeto_inadimplencia.db"
engine = create_engine(DB_URL)

def load_data():
    query = """
    SELECT 
        m.codigo_ibge, m.uf, m.populacao_2022, m.pib_2021,
        e.ano, e.mes, e.saldo_operacoes_credito, e.provisao_devedores_duvidosos
    FROM municipios m
    JOIN estban_mensal e ON m.codigo_ibge = e.codigo_ibge
    """
    df = pd.read_sql(query, engine)
    return df

def feature_engineering(df):
    # Alvo: Taxa de Inadimplência
    df['taxa_inadimplencia'] = df['provisao_devedores_duvidosos'] / df['saldo_operacoes_credito']
    
    # Lag features
    df = df.sort_values(['codigo_ibge', 'ano', 'mes'])
    df['taxa_in_lag1'] = df.groupby('codigo_ibge')['taxa_inadimplencia'].shift(1)
    
    # PIB per capita
    df['pib_per_capita'] = df['pib_2021'] / df['populacao_2022']
    
    df = df.dropna()
    df = pd.get_dummies(df, columns=['uf'], drop_first=True)
    return df

def train():
    print("Treinando modelo XGBoost com dados do RJ (Ciclo 2023-2024)...")
    df = load_data()
    if df.empty:
        print("Erro: Sem dados.")
        return

    df = feature_engineering(df)
    
    X = df.drop(['codigo_ibge', 'taxa_inadimplencia', 'provisao_devedores_duvidosos', 'ano'], axis=1)
    y = df['taxa_inadimplencia']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = XGBRegressor(n_estimators=300, learning_rate=0.03, max_depth=7)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    print(f"Métricas do Modelo RJ Atualizado:")
    print(f"- MAE: {mean_absolute_error(y_test, preds):.6f}")
    print(f"- R2 Score: {r2_score(y_test, preds):.4f}")
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/xgb_model.pkl')
    joblib.dump(X.columns.tolist(), 'models/model_columns.pkl')
    print("Modelo salvo com sucesso.")

if __name__ == "__main__":
    train()
