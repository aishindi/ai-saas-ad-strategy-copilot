import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = "ad_strategy.db"
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def load_csv_to_table(csv_name, table_name):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_csv(DATA_DIR / csv_name)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()


if __name__ == "__main__":
    create_tables()
    load_csv_to_table("campaigns.csv", "campaigns")
    load_csv_to_table("audience_segments.csv", "audience_segments")
    load_csv_to_table("platform_metrics.csv", "platform_metrics")
    load_csv_to_table("messaging_themes.csv", "messaging_themes")
    load_csv_to_table("keywords.csv", "keywords")
    print("Database seeded successfully.")