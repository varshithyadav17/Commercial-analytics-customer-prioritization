import pandas as pd
import pytest

from data.generate_data import generate
from src.analytics import assign_segments, build_analytics, payout_rate
from sql.run_sql_analysis import run_queries


def test_segment_thresholds_are_explainable():
    hcps = pd.DataFrame({
        "hcp_id": ["A", "B", "C", "D"],
        "potential_score": [60, 60, 59.9, 59.9],
        "receptivity_score": [55, 54.9, 55, 54.9],
    })
    result = assign_segments(hcps).set_index("hcp_id")["segment"].to_dict()
    assert result == {
        "A": "Key Target",
        "B": "Growth",
        "C": "Maintain",
        "D": "Low Priority",
    }


@pytest.mark.parametrize(
    ("attainment", "expected"),
    [(0.79, 0.0), (0.80, 0.5), (0.999, 0.5), (1.00, 1.0), (1.099, 1.0), (1.10, 1.5), (1.50, 1.5)],
)
def test_payout_tiers(attainment, expected):
    assert payout_rate(attainment) == expected


def test_generator_is_seeded_and_creates_expected_schemas(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    generate(first, seed=7, n_hcps=40, n_reps=4)
    generate(second, seed=7, n_hcps=40, n_reps=4)
    for name in ["hcps.csv", "calls.csv", "sales.csv", "reps.csv", "rep_targets.csv"]:
        a = pd.read_csv(first / name)
        b = pd.read_csv(second / name)
        pd.testing.assert_frame_equal(a, b)
    assert len(pd.read_csv(first / "hcps.csv")) == 40
    assert len(pd.read_csv(first / "sales.csv")) == 40 * 12
    assert set(pd.read_csv(first / "hcps_with_segment.csv")["segment"]) <= {
        "Key Target", "Growth", "Maintain", "Low Priority"
    }


def test_pipeline_respects_capacity_and_sql_grain(tmp_path):
    data_dir = tmp_path / "data"
    generate(data_dir, seed=11, n_hcps=40, n_reps=4)
    output_dir = tmp_path / "model_outputs"
    outputs = build_analytics(data_dir, output_dir, monthly_calls_per_rep=60)

    plan = outputs["optimized_call_plan"]
    assert len(plan) == 40
    assert plan["optimized_calls_per_month"].sum() == pytest.approx(4 * 60)
    assert (plan["optimized_calls_per_month"] >= 0.5).all()
    assert outputs["segment_summary"]["hcp_count"].sum() == 40

    sql_results = run_queries(data_dir, tmp_path / "query_results")
    calls = pd.read_csv(data_dir / "calls.csv")
    sales = pd.read_csv(data_dir / "sales.csv")
    assert sql_results["Q1"]["hcp_count"].sum() == 40
    assert sql_results["Q2"]["hcp_count"].sum() == 40
    assert sql_results["Q3"]["total_calls"].sum() == len(calls)
    assert sql_results["Q3"]["total_rx_volume"].sum() == pytest.approx(sales["rx_volume"].sum(), abs=2.1)
    assert sql_results["Q5"]["total_calls"].sum() == len(calls)
    assert sql_results["Q5"]["total_rx_volume"].sum() == pytest.approx(sales["rx_volume"].sum(), abs=1.1)
    for name in ["segment_summary.csv", "optimized_call_plan.csv", "icm_payouts.csv",
                 "territory_summary.csv", "monthly_trend.csv", "excel_raw_data.csv"]:
        assert (output_dir / name).is_file()


def test_pipeline_rejects_unknown_hcp_in_activity(tmp_path):
    data_dir = tmp_path / "data"
    generate(data_dir, seed=13, n_hcps=40, n_reps=4)
    calls = pd.read_csv(data_dir / "calls.csv")
    calls.loc[0, "hcp_id"] = "MISSING-HCP"
    calls.to_csv(data_dir / "calls.csv", index=False)
    with pytest.raises(ValueError, match="unknown HCP"):
        build_analytics(data_dir, tmp_path / "outputs")
