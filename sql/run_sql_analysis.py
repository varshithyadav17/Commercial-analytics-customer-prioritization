"""Execute documented SQL analyses against an in-memory SQLite database."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def run_queries(data_dir=None, output_dir=None):
    data_dir = Path(data_dir) if data_dir is not None else ROOT / "data"
    output_dir = Path(output_dir) if output_dir is not None else ROOT / "sql" / "query_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    input_map = {
        "hcps_with_segment": "hcps_with_segment.csv",
        "reps": "reps.csv",
        "calls": "calls.csv",
        "sales": "sales.csv",
        "rep_targets": "rep_targets.csv",
    }
    missing = [name for name in input_map.values() if not (data_dir / name).is_file()]
    if missing:
        raise FileNotFoundError("Generate datasets first; missing: " + ", ".join(missing))
    results = {}
    with sqlite3.connect(":memory:") as connection:
        for table, filename in input_map.items():
            pd.read_csv(data_dir / filename).to_sql(table, connection, index=False, if_exists="replace")
        script = (ROOT / "sql" / "analysis_queries.sql").read_text(encoding="utf-8")
        blocks = script.split("-- Q")[1:]
        if not blocks:
            raise ValueError("No SQL query blocks labelled -- Q1, -- Q2, ... were found")
        for number, block in enumerate(blocks, start=1):
            label, separator, body = block.partition("\n")
            if not separator:
                raise ValueError(f"Query {number} has no SQL body")
            query_lines = [line for line in body.splitlines() if not line.lstrip().startswith("--")]
            query = "\n".join(query_lines).strip().rstrip(";")
            if not query:
                continue
            frame = pd.read_sql_query(query, connection)
            frame.to_csv(output_dir / f"Q{number}_result.csv", index=False)
            results[f"Q{number}"] = frame
            print(f"Q{number} — {label.strip()}: {len(frame)} rows")
    return results


if __name__ == "__main__":
    run_queries()
