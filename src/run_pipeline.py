"""Run the commercial analytics pipeline from generated CSV inputs."""
from pathlib import Path
from src.analytics import build_analytics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MODEL = DATA / "model_outputs"


def main():
    outputs = build_analytics(DATA, MODEL)
    from sql.run_sql_analysis import run_queries
    query_outputs = run_queries(DATA, ROOT / "sql" / "query_results")
    print("Commercial analytics pipeline completed.")
    print(f"HCPs analysed: {len(outputs['hcps_segmented'])}")
    print(f"Calls analysed: {sum(1 for _ in open(DATA / 'calls.csv', encoding='utf-8')) - 1}")
    print("Segment summary:")
    print(outputs["segment_summary"][["segment", "hcp_count", "avg_actual_calls_per_month", "avg_planned_calls_per_month"]].to_string(index=False))
    print(f"SQL analyses saved: {len(query_outputs)}")
    print(f"Model outputs: {MODEL}")
    return outputs


if __name__ == "__main__":
    main()
