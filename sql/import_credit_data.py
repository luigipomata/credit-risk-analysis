"""
Crea (se non esiste) il database CreditRiskAnalysis su SQL Server, crea la
tabella credit_applications dalla DDL in create_table_credit_applications.sql
e importa il dataset pulito da data/processed/cs-training-clean.csv.

Idempotente: rieseguibile senza errori. Se il database/tabella esistono già
non vengono ricreati; se la tabella contiene già righe l'import viene saltato
per evitare duplicati (id è chiave primaria).

Uso:
    python sql/import_credit_data.py
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_connection import DB_DATABASE, DB_SERVER, get_engine, get_pyodbc_connection

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DDL_PATH = SCRIPT_DIR / "create_table_credit_applications.sql"
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "cs-training-clean.csv"

TABLE_NAME = "credit_applications"

# Mappa colonna CSV -> colonna SQL (i trattini originali diventano underscore).
COLUMN_MAP = {
    "id": "id",
    "SeriousDlqin2yrs": "SeriousDlqin2yrs",
    "RevolvingUtilizationOfUnsecuredLines": "RevolvingUtilizationOfUnsecuredLines",
    "age": "age",
    "NumberOfTime30-59DaysPastDueNotWorse": "NumberOfTime30_59DaysPastDueNotWorse",
    "DebtRatio": "DebtRatio",
    "MonthlyIncome": "MonthlyIncome",
    "NumberOfOpenCreditLinesAndLoans": "NumberOfOpenCreditLinesAndLoans",
    "NumberOfTimes90DaysLate": "NumberOfTimes90DaysLate",
    "NumberRealEstateLoansOrLines": "NumberRealEstateLoansOrLines",
    "NumberOfTime60-89DaysPastDueNotWorse": "NumberOfTime60_89DaysPastDueNotWorse",
    "NumberOfDependents": "NumberOfDependents",
}


def create_database_if_missing() -> None:
    conn = get_pyodbc_connection(database="master", autocommit=True)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sys.databases WHERE name = ?", (DB_DATABASE,))
        if cur.fetchone():
            print(f"Database '{DB_DATABASE}' già esistente.")
        else:
            cur.execute(f"CREATE DATABASE [{DB_DATABASE}]")
            print(f"Database '{DB_DATABASE}' creato.")
    finally:
        conn.close()


def create_table_if_missing() -> None:
    conn = get_pyodbc_connection(database=DB_DATABASE, autocommit=True)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?",
            (TABLE_NAME,),
        )
        if cur.fetchone():
            print(f"Tabella '{TABLE_NAME}' già esistente.")
            return
        ddl = DDL_PATH.read_text(encoding="utf-8")
        cur.execute(ddl)
        print(f"Tabella '{TABLE_NAME}' creata da {DDL_PATH.name}.")
    finally:
        conn.close()


def load_clean_csv() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Non trovo {CSV_PATH}. Esegui prima il notebook notebooks/01_eda "
            "per generare il dataset pulito."
        )
    df = pd.read_csv(CSV_PATH)
    missing_cols = [c for c in COLUMN_MAP if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Colonne attese ma non trovate nel CSV pulito: {missing_cols}")

    df = df[list(COLUMN_MAP.keys())].rename(columns=COLUMN_MAP)
    # NumberOfDependents resta float64 nel CSV (colonna con NaN imputati a 0 nel notebook 01_eda);
    # la tabella SQL la definisce INT, quindi va convertita esplicitamente prima dell'insert.
    df["NumberOfDependents"] = df["NumberOfDependents"].astype(int)
    return df


def import_data() -> None:
    engine = get_engine(DB_DATABASE)
    with engine.connect() as conn:
        existing = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}")).scalar()

    if existing:
        print(f"'{TABLE_NAME}' contiene già {existing:,} righe: import saltato (già eseguito).")
        return

    df = load_clean_csv()
    df.to_sql(TABLE_NAME, engine, if_exists="append", index=False, chunksize=1000)
    print(f"Importate {len(df):,} righe in '{TABLE_NAME}'.")


def main() -> None:
    print(f"Server: {DB_SERVER}  |  Database: {DB_DATABASE}")
    create_database_if_missing()
    create_table_if_missing()
    import_data()


if __name__ == "__main__":
    main()
