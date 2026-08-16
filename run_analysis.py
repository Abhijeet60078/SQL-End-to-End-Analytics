"""
run_analysis.py
-----------------
Connects to ecommerce.db, runs every business question in
queries/business_questions.sql, prints a preview of each result,
and exports each to a CSV file in outputs/ for use in Excel/Power BI/Tableau.

Run: python run_analysis.py
"""

import sqlite3
import csv
import re
import os

DB_PATH = "ecommerce.db"
QUERY_FILE = "queries/business_questions.sql"
OUTPUT_DIR = "outputs"


def split_queries(sql_text: str):
    """
    Splits the .sql file into (question_number, title, query) tuples
    using the '-- Q<n>. TITLE' comment markers as delimiters.
    """
    blocks = re.split(r"\n-- (Q\d+\.[^\n]+)\n", sql_text)
    # blocks[0] is the file header/comments before Q1; skip it
    results = []
    for i in range(1, len(blocks), 2):
        title = blocks[i].strip()
        query_body = blocks[i + 1]
        # strip trailing comment lines and blank lines, keep the SQL statement
        query = query_body.strip()
        # remove leading comment lines (business need explanation)
        query_lines = [ln for ln in query.split("\n") if not ln.strip().startswith("--")]
        query = "\n".join(query_lines).strip()
        results.append((title, query))
    return results


def safe_filename(title: str) -> str:
    name = title.split(".", 1)[0]  # "Q1"
    return name.lower() + ".csv"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    with open(QUERY_FILE, "r") as f:
        sql_text = f.read()

    queries = split_queries(sql_text)
    print(f"Found {len(queries)} business questions.\n")

    for title, query in queries:
        print("=" * 70)
        print(title)
        print("=" * 70)
        try:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            # print preview (first 5 rows)
            print(" | ".join(columns))
            for row in rows[:5]:
                print(" | ".join(str(v) for v in row))
            if len(rows) > 5:
                print(f"... ({len(rows)} rows total)")
            print()

            # export full result to CSV
            out_path = os.path.join(OUTPUT_DIR, safe_filename(title))
            with open(out_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)
                writer.writerows(rows)

        except sqlite3.Error as e:
            print(f"ERROR running query: {e}\n")

    conn.close()
    print(f"\nAll results exported to /{OUTPUT_DIR}/ as CSV files.")


if __name__ == "__main__":
    main()
