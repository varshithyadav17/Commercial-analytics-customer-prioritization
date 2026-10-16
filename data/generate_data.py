"""Generate deterministic synthetic commercial datasets from first principles."""
from pathlib import Path
from datetime import date, timedelta
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data"
SPECIALTIES = ["Cardiology", "Endocrinology", "Oncology", "Neurology", "Primary Care"]
REGIONS = ["Northeast", "Midwest", "South", "West"]


def generate(out_dir=None, seed=42, n_hcps=600, n_reps=40):
    if n_hcps < 4 or n_reps < 4:
        raise ValueError("Generate at least four HCPs and four representatives")
    out = Path(out_dir) if out_dir is not None else DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    reps = pd.DataFrame({
        "rep_id": [f"REP{i:03d}" for i in range(1, n_reps + 1)],
        "rep_name": [f"Rep {i:03d}" for i in range(1, n_reps + 1)],
        "region": [REGIONS[(i - 1) % len(REGIONS)] for i in range(1, n_reps + 1)],
        "tenure_years": rng.integers(0, 16, n_reps),
    })
    hcps = pd.DataFrame({
        "hcp_id": [f"HCP{i:04d}" for i in range(1, n_hcps + 1)],
        "specialty": rng.choice(SPECIALTIES, n_hcps, p=[0.15, 0.15, 0.15, 0.15, 0.40]),
        "region": rng.choice(REGIONS, n_hcps),
        "decile": rng.integers(1, 11, n_hcps),
        "patient_volume": rng.integers(50, 2001, n_hcps),
    })
    hcps["potential_score"] = (
        hcps["decile"] * 7.2 + hcps["patient_volume"] / 48 + rng.normal(0, 8, n_hcps)
    ).clip(0, 100).round(2)
    hcps["receptivity_score"] = rng.normal(55, 19, n_hcps).clip(0, 100).round(2)
    segment_mask = [
        (hcps["potential_score"] >= 60) & (hcps["receptivity_score"] >= 55),
        hcps["potential_score"] >= 60,
        hcps["receptivity_score"] >= 55,
    ]
    hcps["segment"] = np.select(segment_mask, ["Key Target", "Growth", "Maintain"], default="Low Priority")
    target_frequency = {"Key Target": 2.0, "Growth": 1.5, "Maintain": 1.0, "Low Priority": 0.4}
    hcps["rep_id"] = [
        rng.choice(reps.loc[reps["region"] == region, "rep_id"].to_numpy())
        for region in hcps["region"]
    ]

    weeks = [date(2025, 1, 6) + timedelta(weeks=w) for w in range(52)]
    call_rows = []
    for hcp in hcps.itertuples(index=False):
        probability = min(target_frequency[hcp.segment] / 4.33, 0.9)
        for week in weeks:
            if rng.random() < probability * rng.uniform(0.65, 1.15):
                call_rows.append({
                    "hcp_id": hcp.hcp_id,
                    "rep_id": hcp.rep_id,
                    "call_date": week.isoformat(),
                    "call_type": rng.choice(["In-person", "Virtual", "Education event"], p=[0.62, 0.33, 0.05]),
                    "duration_min": int(rng.integers(8, 31)),
                })
    calls = pd.DataFrame(call_rows, columns=["hcp_id", "rep_id", "call_date", "call_type", "duration_min"])
    calls["month"] = pd.to_datetime(calls["call_date"]).dt.to_period("M").astype(str)
    monthly_calls = calls.groupby(["hcp_id", "month"]).size().to_dict()

    sales_rows = []
    months = pd.date_range("2025-01-01", periods=12, freq="MS")
    hcp_lookup = hcps.set_index("hcp_id")
    for hcp in hcps.itertuples(index=False):
        baseline = hcp.patient_volume * (hcp.decile / 10) * 0.38
        for month in months:
            n_calls = monthly_calls.get((hcp.hcp_id, month.strftime("%Y-%m")), 0)
            lift_proxy = 1 + 0.045 * n_calls * (hcp.receptivity_score / 100)
            seasonal = 1 + 0.04 * np.sin(2 * np.pi * month.month / 12)
            noise = max(0.60, rng.normal(1.0, 0.08))
            sales_rows.append({
                "hcp_id": hcp.hcp_id,
                "month": month.strftime("%Y-%m-%d"),
                "rx_volume": round(max(0, baseline * lift_proxy * seasonal * noise), 1),
            })
    sales = pd.DataFrame(sales_rows)

    sales_q = sales.copy()
    sales_q["quarter"] = pd.to_datetime(sales_q["month"]).dt.quarter
    sales_q = sales_q.merge(hcps[["hcp_id", "rep_id"]], on="hcp_id", validate="many_to_one")
    actuals = sales_q.groupby(["rep_id", "quarter"], as_index=False)["rx_volume"].sum()
    actuals = actuals.rename(columns={"rx_volume": "actual_volume"})
    targets = actuals.copy()
    targets["quarter"] = targets["quarter"].map(lambda q: f"2025-Q{q}")
    targets["quota_volume"] = (
        targets["actual_volume"] / rng.uniform(0.82, 1.18, len(targets))
    ).round(1)
    targets["actual_volume"] = targets["actual_volume"].round(1)
    targets = targets[["rep_id", "quarter", "quota_volume", "actual_volume"]]

    hcps.drop(columns=["segment"]).to_csv(out / "hcps.csv", index=False)
    hcps.to_csv(out / "hcps_with_segment.csv", index=False)
    reps.to_csv(out / "reps.csv", index=False)
    calls.drop(columns=["month"]).to_csv(out / "calls.csv", index=False)
    sales.to_csv(out / "sales.csv", index=False)
    targets.to_csv(out / "rep_targets.csv", index=False)
    print(f"Generated {len(hcps):,} HCPs, {len(reps):,} reps, {len(calls):,} calls, {len(sales):,} monthly sales rows.")
    return {"hcps": hcps, "reps": reps, "calls": calls, "sales": sales, "rep_targets": targets}


if __name__ == "__main__":
    generate()
