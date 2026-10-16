"""Original, reproducible commercial analytics calculations for synthetic data."""
from pathlib import Path
import numpy as np
import pandas as pd

TARGET_CALLS = {"Key Target": 2.0, "Growth": 1.5, "Maintain": 1.0, "Low Priority": 0.4}


def assign_segments(hcps: pd.DataFrame) -> pd.DataFrame:
    """Apply a transparent potential × receptivity framework to each HCP."""
    required = {"hcp_id", "potential_score", "receptivity_score"}
    missing = required - set(hcps.columns)
    if missing:
        raise ValueError(f"Missing HCP columns: {sorted(missing)}")
    out = hcps.copy()
    potential = pd.to_numeric(out["potential_score"], errors="coerce")
    receptivity = pd.to_numeric(out["receptivity_score"], errors="coerce")
    if potential.isna().any() or receptivity.isna().any():
        raise ValueError("Potential and receptivity scores must be numeric and non-missing")
    out["segment"] = np.select(
        [(potential >= 60) & (receptivity >= 55), potential >= 60, receptivity >= 55],
        ["Key Target", "Growth", "Maintain"],
        default="Low Priority",
    )
    return out


def payout_rate(attainment: float) -> float:
    """Return the illustrative payout multiplier for quota attainment."""
    if attainment >= 1.10:
        return 1.50
    if attainment >= 1.00:
        return 1.00
    if attainment >= 0.80:
        return 0.50
    return 0.0


def build_analytics(data_dir: str | Path, output_dir: str | Path,
                    monthly_calls_per_rep: float = 60.0) -> dict[str, pd.DataFrame]:
    """Build prioritisation, segment, territory, and compensation tables."""
    data_dir, output_dir = Path(data_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    required_files = ["hcps.csv", "calls.csv", "sales.csv", "reps.csv", "rep_targets.csv"]
    missing = [name for name in required_files if not (data_dir / name).is_file()]
    if missing:
        raise FileNotFoundError("Generate datasets first; missing: " + ", ".join(missing))

    hcps = pd.read_csv(data_dir / "hcps.csv")
    calls = pd.read_csv(data_dir / "calls.csv")
    sales = pd.read_csv(data_dir / "sales.csv")
    reps = pd.read_csv(data_dir / "reps.csv")
    targets = pd.read_csv(data_dir / "rep_targets.csv")
    hcps = assign_segments(hcps)
    if hcps["hcp_id"].isna().any() or hcps["hcp_id"].duplicated().any():
        raise ValueError("HCP master must contain unique, non-missing hcp_id values")
    if reps["rep_id"].isna().any() or reps["rep_id"].duplicated().any():
        raise ValueError("Rep master must contain unique, non-missing rep_id values")

    for frame, label, key in [(calls, "calls", "hcp_id"), (sales, "sales", "hcp_id")]:
        if key not in frame.columns:
            raise ValueError(f"{label} data is missing {key}")
        unknown = set(frame[key].dropna()) - set(hcps["hcp_id"])
        if unknown:
            raise ValueError(f"{label} data contains unknown HCP identifiers")

    call_counts = calls.groupby("hcp_id").size().rename("total_calls")
    sales_by_hcp = sales.groupby("hcp_id", as_index=False)["rx_volume"].sum().rename(
        columns={"rx_volume": "total_rx_volume"}
    )
    metrics = hcps.merge(sales_by_hcp, on="hcp_id", how="left")
    metrics = metrics.join(call_counts, on="hcp_id")
    metrics[["total_rx_volume", "total_calls"]] = metrics[["total_rx_volume", "total_calls"]].fillna(0)
    metrics["actual_calls_per_month"] = metrics["total_calls"] / 12.0
    metrics["target_calls_per_month"] = metrics["segment"].map(TARGET_CALLS)
    metrics["expected_lift_per_call"] = (
        metrics["potential_score"].clip(lower=0) * metrics["receptivity_score"].clip(lower=0) / 100.0
    )

    total_capacity = float(monthly_calls_per_rep) * int(reps["rep_id"].nunique())
    floor_calls = min(0.5, total_capacity / max(len(metrics), 1))
    minimum_total = floor_calls * len(metrics)
    if total_capacity + 1e-9 < minimum_total:
        raise ValueError("Representative capacity is lower than the minimum coverage floor")
    remaining = max(0.0, total_capacity - minimum_total)
    metrics["optimized_calls_per_month"] = floor_calls
    top_count = max(1, len(metrics) // 2) if len(metrics) else 0
    selected = metrics.sort_values(
        ["expected_lift_per_call", "potential_score", "hcp_id"],
        ascending=[False, False, True],
    ).head(top_count)
    if len(selected):
        weights = selected["expected_lift_per_call"].clip(lower=0)
        if float(weights.sum()) <= 0:
            weights = pd.Series(1.0, index=selected.index)
        metrics.loc[selected.index, "optimized_calls_per_month"] += weights / weights.sum() * remaining
    call_plan = metrics[[
        "hcp_id", "rep_id", "specialty", "region", "segment", "potential_score",
        "receptivity_score", "expected_lift_per_call", "actual_calls_per_month",
        "target_calls_per_month", "optimized_calls_per_month",
    ]].sort_values(["optimized_calls_per_month", "expected_lift_per_call"], ascending=False)

    segment_summary = metrics.groupby("segment", as_index=False).agg(
        hcp_count=("hcp_id", "nunique"),
        avg_potential=("potential_score", "mean"),
        avg_receptivity=("receptivity_score", "mean"),
        total_rx_volume=("total_rx_volume", "sum"),
        total_calls=("total_calls", "sum"),
        avg_actual_calls_per_month=("actual_calls_per_month", "mean"),
        avg_target_calls_per_month=("target_calls_per_month", "mean"),
        avg_planned_calls_per_month=("optimized_calls_per_month", "mean"),
    )
    segment_summary["rx_per_call_proxy"] = np.where(
        segment_summary["total_calls"] > 0,
        segment_summary["total_rx_volume"] / segment_summary["total_calls"],
        np.nan,
    )
    territory_summary = metrics.groupby("region", as_index=False).agg(
        hcp_count=("hcp_id", "nunique"),
        total_rx_volume=("total_rx_volume", "sum"),
        total_calls=("total_calls", "sum"),
        avg_potential=("potential_score", "mean"),
        avg_actual_calls_per_month=("actual_calls_per_month", "mean"),
    )
    territory_summary["rx_per_call_proxy"] = np.where(
        territory_summary["total_calls"] > 0,
        territory_summary["total_rx_volume"] / territory_summary["total_calls"],
        np.nan,
    )
    monthly_trend = sales.copy()
    monthly_trend["month"] = pd.to_datetime(monthly_trend["month"], errors="coerce")
    monthly_trend = monthly_trend.groupby("month", as_index=False)["rx_volume"].sum()
    monthly_trend["month"] = monthly_trend["month"].dt.strftime("%Y-%m")

    icm = targets.copy()
    icm["attainment"] = np.divide(
        pd.to_numeric(icm["actual_volume"], errors="coerce").fillna(0),
        pd.to_numeric(icm["quota_volume"], errors="coerce").replace(0, np.nan),
    )
    icm["attainment"] = icm["attainment"].fillna(0)
    icm["payout_pct"] = icm["attainment"].map(payout_rate)
    icm["incentive_payout_usd"] = (5000 * icm["payout_pct"]).round(0)

    outputs = {
        "hcps_segmented.csv": metrics,
        "optimized_call_plan.csv": call_plan,
        "icm_payouts.csv": icm,
        "segment_summary.csv": segment_summary,
        "territory_summary.csv": territory_summary,
        "monthly_trend.csv": monthly_trend,
        "excel_raw_data.csv": metrics,
    }
    for name, frame in outputs.items():
        frame.to_csv(output_dir / name, index=False)
    return {Path(name).stem: frame for name, frame in outputs.items()}
