import requests
import pandas as pd
import io

def get_sgs_series(serie_id):
    """Coleta séries temporais do SGS (Sistema Gerenciador de Séries Temporais)"""
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie_id}/dados?formato=json"
    response = requests.get(url)
    return pd.DataFrame(response.json())

def get_estban_data(ano, mes):
    """
    Coleta dados da ESTBAN. 
    Nota: O BCB fornece arquivos CSV mensais. 
    A URL padrão costuma seguir um padrão de data.
    """
    # Exemplo de URL: https://www.bcb.gov.br/content/estatisticas/estban/202312ESTBAN.zip
    url = f"https://www.bcb.gov.br/content/estatisticas/estban/{ano}{mes:02d}ESTBAN.zip"
    # Devido a possíveis bloqueios de bot, pode ser necessário tratar headers
    return url

if __name__ == "__main__":
    # Inadimplência total PF - 21084
    # Inadimplência total PJ - 21086
    df_pf = get_sgs_series(21084)
    print("Série de inadimplência PF coletada.")
