"""Interactive commercial analytics dashboard. Run: streamlit run dashboard/app.py"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MODEL = DATA / "model_outputs"
SQL_OUT = ROOT / "sql" / "query_results"
st.set_page_config(page_title="Commercial Analytics & Prioritization", page_icon="📈", layout="wide")


@st.cache_data
def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path.relative_to(ROOT)}. Run data/generate_data.py and python -m src.run_pipeline first.")
    return pd.read_csv(path)


try:
    segments = read_csv(MODEL / "segment_summary.csv")
    plan = read_csv(MODEL / "optimized_call_plan.csv")
    icm = read_csv(MODEL / "icm_payouts.csv")
    territories = read_csv(MODEL / "territory_summary.csv")
    trend = read_csv(MODEL / "monthly_trend.csv")
    sql_mix = read_csv(SQL_OUT / "Q5_result.csv")
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

st.title("Commercial Analytics & Customer Prioritization")
st.caption("Synthetic data • decision support, not a causal or production planning system")
n_hcps = int(segments["hcp_count"].sum())
total_rx = float(segments["total_rx_volume"].sum())
total_calls = int(segments["total_calls"].sum())
planned_calls = float(plan["optimized_calls_per_month"].sum())
k1, k2, k3, k4 = st.columns(4)
k1.metric("HCPs in sample", f"{n_hcps:,}")
k2.metric("Simulated annual volume", f"{total_rx:,.0f}")
k3.metric("Observed calls", f"{total_calls:,}")
k4.metric("Planned calls / month", f"{planned_calls:,.0f}")

tab1, tab2, tab3, tab4 = st.tabs(["Segmentation", "Contact plan", "Quota & incentives", "Territory & mix"])
with tab1:
    st.subheader("Segment size and contact frequency")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(segments, x="segment", y="hcp_count", title="HCP count by segment"), use_container_width=True)
    with right:
        cols = ["avg_actual_calls_per_month", "avg_target_calls_per_month", "avg_planned_calls_per_month"]
        chart = segments.melt(id_vars="segment", value_vars=cols, var_name="measure", value_name="calls_per_month")
        st.plotly_chart(px.bar(chart, x="segment", y="calls_per_month", color="measure", barmode="group",
                               title="Average monthly calls: observed, target, plan"), use_container_width=True)
    st.dataframe(segments, use_container_width=True, hide_index=True)
    st.caption("Volume differences are descriptive. Synthetic data does not demonstrate call effectiveness.")
with tab2:
    st.subheader("Capacity-constrained contact planning")
    region = st.selectbox("Region", ["All regions"] + sorted(plan["region"].dropna().unique().tolist()))
    view = plan if region == "All regions" else plan[plan["region"] == region]
    st.write(f"{len(view):,} HCPs in selected view.")
    st.plotly_chart(px.scatter(view, x="potential_score", y="receptivity_score", color="segment",
                               size="optimized_calls_per_month", hover_data=["hcp_id", "region"],
                               title="Priority map and planned call allocation"), use_container_width=True)
    st.dataframe(view.sort_values("optimized_calls_per_month", ascending=False).head(100),
                 use_container_width=True, hide_index=True)
    st.download_button("Download selected contact plan", view.to_csv(index=False).encode("utf-8"),
                       file_name="contact_plan.csv", mime="text/csv")
    st.caption("The plan is a heuristic: a coverage floor plus priority-weighted capacity for the top half of HCPs.")
with tab3:
    st.subheader("Illustrative quota attainment and incentive tiers")
    quarter = st.selectbox("Quarter", sorted(icm["quarter"].unique()))
    q = icm[icm["quarter"] == quarter].copy()
    c1, c2, c3 = st.columns(3)
    c1.metric("Average attainment", f"{q['attainment'].mean():.1%}")
    c2.metric("Accelerator tier", int((q["payout_pct"] >= 1.5).sum()))
    c3.metric("Illustrative payout", "$" + f"{q['incentive_payout_usd'].sum():,.0f}")
    st.plotly_chart(px.histogram(q, x="attainment", nbins=20, title=f"Attainment distribution — {quarter}"),
                    use_container_width=True)
    st.dataframe(q.sort_values("attainment", ascending=False), use_container_width=True, hide_index=True)
    st.caption("Payout assumptions are illustrative only and are not suitable for real compensation decisions.")
with tab4:
    st.subheader("Regional performance and monthly trend")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(territories, x="region", y="rx_per_call_proxy",
                               title="Simulated volume-per-call proxy by region"), use_container_width=True)
        st.dataframe(territories, use_container_width=True, hide_index=True)
    with right:
        st.plotly_chart(px.line(trend, x="month", y="rx_volume", markers=True,
                                title="Simulated monthly volume"), use_container_width=True)
    st.subheader("Specialty × region")
    st.dataframe(sql_mix, use_container_width=True, hide_index=True)

st.divider()
st.caption("All records are synthetic. Ratios are descriptive and do not establish causal effects or real-world commercial performance.")
