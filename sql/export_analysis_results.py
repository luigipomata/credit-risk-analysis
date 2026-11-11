"""
Esegue le query esplorative in exploratory_queries.sql sul database
CreditRiskAnalysis ed esporta ciascun risultato come CSV separato in
data/processed/, pronto per essere usato dalla dashboard.

Uso:
    python sql/export_analysis_results.py
"""

import re
from pathlib import Path

import pandas as pd

from db_connection import get_engine

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SQL_FILE = SCRIPT_DIR / "exploratory_queries.sql"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

# nome query (marcatore nel .sql) -> file CSV di output
OUTPUT_FILES = {
    "tasso_default_per_fascia_reddito": "tasso_default_per_fascia_reddito.csv",
    "tasso_default_per_fascia_eta": "tasso_default_per_fascia_eta.csv",
    "tasso_default_per_prestiti_aperti": "tasso_default_per_prestiti_aperti.csv",
}

QUERY_MARKER = re.compile(r"--\s*QUERY:\s*(\w+)\s*\n")


def load_queries(sql_path: Path) -> dict[str, str]:
    text = sql_path.read_text(encoding="utf-8")
    parts = QUERY_MARKER.split(text)
    # parts = [preambolo, nome1, corpo1, nome2, corpo2, ...]
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def main() -> None:
    queries = load_queries(SQL_FILE)
    engine = get_engine()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with engine.connect() as conn:
        for query_name, filename in OUTPUT_FILES.items():
            if query_name not in queries:
                raise KeyError(f"Query '{query_name}' non trovata in {SQL_FILE.name}")
            df = pd.read_sql(queries[query_name], conn)
            out_path = OUTPUT_DIR / filename
            df.to_csv(out_path, index=False)
            print(f"{query_name}: {len(df)} righe -> {out_path}")


if __name__ == "__main__":
    main()
