import pandas as pd
import sidrapy
import numpy as np
from sqlalchemy import create_engine
import os

# Configurações
DB_URL = "sqlite:///projeto_inadimplencia.db"
engine = create_engine(DB_URL)

def coletar_municipios_rj_atualizado():
    """Coleta dados reais e recentes (Censo 2022 e PIB 2021) dos 92 municípios do RJ"""
    print("Coletando dados RECENTES do RJ via IBGE (Censo 2022 e PIB 2021)...")
    
    try:
        # PIB (Tabela 5938 - Dados mais recentes consolidados são de 2021)
        print("Buscando PIB 2021 (mais recente consolidado)...")
        df_pib = sidrapy.get_table(table_code="5938", territorial_level="6", ibge_territorial_code="all", variable="37", period="2021")
        df_pib = df_pib.iloc[1:][['D1C', 'D1N', 'D2N', 'V']]
        df_pib.columns = ['codigo_ibge', 'nome_municipio', 'uf', 'pib_recente']
        df_pib = df_pib[df_pib['codigo_ibge'].str.startswith('33')]
        
        # População (Tabela 9514 - Censo Demográfico 2022)
        print("Buscando População Censo 2022...")
        codigos_rj = ",".join(df_pib['codigo_ibge'].tolist())
        # Tabela 9514: População residente (Censo 2022)
        df_pop = sidrapy.get_table(table_code="9514", territorial_level="6", ibge_territorial_code=codigos_rj, variable="93", period="2022")
        df_pop = df_pop.iloc[1:][['D1C', 'V']]
        df_pop.columns = ['codigo_ibge', 'populacao_2022']
        
        df_final = pd.merge(df_pib, df_pop, on='codigo_ibge')
        df_final['codigo_ibge'] = df_final['codigo_ibge'].astype(int)
        df_final['pib_recente'] = pd.to_numeric(df_final['pib_recente'], errors='coerce')
        df_final['populacao_2022'] = pd.to_numeric(df_final['populacao_2022'], errors='coerce')
        
        # Salvar no banco
        df_db = df_final[['codigo_ibge', 'nome_municipio', 'uf', 'populacao_2022', 'pib_recente']]
        df_db.columns = ['codigo_ibge', 'nome', 'uf', 'populacao_2022', 'pib_2021']
        df_db.to_sql('municipios', engine, if_exists='replace', index=False)
        print(f"Dados RECENTES de {len(df_db)} municípios do RJ salvos.")
        return True
    except Exception as e:
        print(f"Erro ao coletar dados recentes: {e}")
        # Fallback simplificado RJ
        municipios_rj = [
            (3304557, 'Rio de Janeiro', 'RJ', 6211423, 359634752),
            (3304904, 'São Gonçalo', 'RJ', 896744, 15635854),
            (3301702, 'Duque de Caxias', 'RJ', 808152, 25759325),
            (3303500, 'Nova Iguaçu', 'RJ', 785867, 14995388),
            (3303302, 'Niterói', 'RJ', 481749, 23871404)
        ]
        df_fallback = pd.DataFrame(municipios_rj, columns=['codigo_ibge', 'nome', 'uf', 'populacao_2022', 'pib_2021'])
        df_fallback.to_sql('municipios', engine, if_exists='replace', index=False)
        return True

def simular_dados_bancarios_2023_2024():
    """Gera dados de inadimplência simulados para o período de 2023-2024"""
    print("Gerando séries temporais de inadimplência (2023-2024)...")
    try:
        df_mun = pd.read_sql("SELECT codigo_ibge, pib_2021 FROM municipios", engine)
        
        records = []
        # Simular 24 meses (2023 e 2024)
        for _, row in df_mun.iterrows():
            cod = row['codigo_ibge']
            pib = row['pib_2021'] if pd.notnull(row['pib_2021']) else 1000000
            
            for ano in [2023, 2024]:
                for mes in range(1, 13):
                    # Tendência de leve alta nos juros e inadimplência em 2023/24
                    fator_ano = 1.1 if ano == 2024 else 1.0
                    saldo = (pib / 75) * np.random.uniform(0.95, 1.05) * fator_ano
                    # Taxa de inadimplência realista para o período (5% a 11%)
                    taxa_inad = np.random.uniform(0.05, 0.11) * (1 + (mes/30))
                    provisao = saldo * taxa_inad
                    
                    records.append({
                        'codigo_ibge': int(cod),
                        'ano': ano,
                        'mes': mes,
                        'saldo_operacoes_credito': float(saldo),
                        'provisao_devedores_duvidosos': float(provisao)
                    })
        
        df_estban = pd.DataFrame(records)
        df_estban.to_sql('estban_mensal', engine, if_exists='replace', index=False)
        print(f"Séries temporais 2023-2024 geradas com sucesso.")
    except Exception as e:
        print(f"Erro na simulação: {e}")

if __name__ == "__main__":
    if coletar_municipios_rj_atualizado():
        simular_dados_bancarios_2023_2024()
