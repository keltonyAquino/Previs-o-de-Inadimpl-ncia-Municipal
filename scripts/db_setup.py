import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Priorizar PostgreSQL se configurado, caso contrário usar SQLite para portabilidade do projeto
DB_URL = os.getenv("DATABASE_URL", "sqlite:///projeto_inadimplencia.db")

def setup_database():
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        # No SQLite não usamos SCHEMA, então vamos ajustar
        if "sqlite" in DB_URL:
            prefix = ""
        else:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS inadimplencia_municipal;"))
            prefix = "inadimplencia_municipal."
            conn.commit()
        
        # Tabela de municípios (IBGE)
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {prefix}municipios (
                codigo_ibge INTEGER PRIMARY KEY,
                nome TEXT,
                uf TEXT,
                populacao_2021 INTEGER,
                pib_2021 REAL
            );
        """))
        
        # Tabela de dados bancários (ESTBAN)
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {prefix}estban_mensal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_ibge INTEGER,
                ano INTEGER,
                mes INTEGER,
                saldo_operacoes_credito REAL,
                provisao_devedores_duvidosos REAL,
                FOREIGN KEY (codigo_ibge) REFERENCES {prefix}municipios(codigo_ibge)
            );
        """))
        
        conn.commit()
    print(f"Banco de dados ({DB_URL}) configurado com sucesso.")

if __name__ == "__main__":
    setup_database()
