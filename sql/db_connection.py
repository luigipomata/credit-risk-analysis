"""
Connessione condivisa a SQL Server per gli script in sql/.

Tutti i parametri di connessione vengono letti da .env (mai hardcodati).
Copiare .env.example in .env e impostare i valori per la propria macchina
prima di eseguire import_credit_data.py o export_analysis_results.py.
"""

import os
import urllib.parse
from pathlib import Path

import pyodbc
from dotenv import load_dotenv
from sqlalchemy import create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE", "CreditRiskAnalysis")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "yes")
DB_TRUST_SERVER_CERTIFICATE = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")

if not DB_SERVER:
    raise RuntimeError(
        "DB_SERVER non impostato. Copia .env.example in .env nella root del "
        "progetto e inserisci i parametri di connessione per questa macchina."
    )


def _odbc_connection_string(database: str) -> str:
    return (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={database};"
        f"Trusted_Connection={DB_TRUSTED_CONNECTION};"
        f"TrustServerCertificate={DB_TRUST_SERVER_CERTIFICATE};"
    )


def get_pyodbc_connection(database: str = "master", autocommit: bool = False):
    """Connessione pyodbc diretta (per DDL/comandi amministrativi come CREATE DATABASE)."""
    return pyodbc.connect(_odbc_connection_string(database), autocommit=autocommit)


def get_engine(database: str | None = None):
    """Engine SQLAlchemy (per pandas.read_sql / to_sql), con fast_executemany attivo."""
    database = database or DB_DATABASE
    odbc_str = urllib.parse.quote_plus(_odbc_connection_string(database))
    url = f"mssql+pyodbc:///?odbc_connect={odbc_str}"
    return create_engine(url, fast_executemany=True)
