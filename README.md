# Commercial Analytics & Customer Prioritization

A reproducible analytics case study for allocating limited customer-facing capacity across a synthetic healthcare-commercial portfolio. It joins transparent customer segmentation, contact planning, performance summaries, SQL analysis, an Excel workbook, and an interactive dashboard.

**Stack:** Python · pandas · NumPy · SQL · SQLite · Excel/openpyxl · Streamlit · Plotly · pytest · GitHub Actions

> **Synthetic-data boundary:** All HCP, representative, call, quota, and volume records are generated for this portfolio. They do not represent real people, patients, prescriptions, or company performance. The relationship between calls and simulated volume is deliberately constructed for demonstration, so correlations are not causal evidence.

## Business question

Given limited monthly call capacity, how can an analyst prioritise accounts transparently, track contact coverage against a target, and compare commercial performance without overstating what the data proves?

## What the pipeline produces

- **Explainable segmentation:** four groups from potential and receptivity thresholds.
- **Capacity-constrained call plan:** a minimum coverage floor plus a priority-weighted allocation of remaining capacity. This is a decision aid, not a proof of global optimality.
- **Contact compliance:** actual calls per HCP per month compared with the segment-level target.
- **Incentive compensation preview:** quarterly quota attainment with illustrative payout tiers.
- **Commercial summaries:** segment and territory tables, a monthly trend, and SQL output tables.
- **Reporting:** interactive Streamlit dashboard and Excel workbook.
- **Quality guardrails:** deterministic data generation, input-key checks, a controlled SQLite analysis, automated tests, and GitHub Actions.

## Architecture

~~~mermaid
flowchart TD
    A[Seeded synthetic generator] --> B[HCP, rep, calls, sales, quota CSVs]
    B --> C[Python segmentation and planning]
    B --> D[(In-memory SQLite)]
    C --> E[Model outputs]
    D --> F[Five SQL analyses]
    E --> G[Dashboard and Excel]
    F --> G
~~~

## Run locally (Windows PowerShell)

~~~powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

python data/generate_data.py
python -m src.run_pipeline
python -m pytest -q
python dashboard/build_excel.py
streamlit run dashboard/app.py
~~~

If activation is blocked, use .\.venv\Scripts\python.exe instead of python in each command. The generator uses a fixed seed, so the same configuration produces the same synthetic sample.

## Key files

| Path | Purpose |
|---|---|
| data/generate_data.py | Synthetic input-data generator |
| src/analytics.py | Segment rules, contact-plan heuristic, quota calculations, summaries |
| src/run_pipeline.py | One-command orchestration |
| sql/analysis_queries.sql | Five documented, grain-safe SQL questions |
| sql/run_sql_analysis.py | Loads CSV inputs into SQLite and writes query-result CSVs |
| data/model_outputs/ | Generated segment, call-plan, territory, trend, and compensation tables |
| dashboard/app.py | Interactive dashboard |
| dashboard/build_excel.py | Workbook generator |
| tests/ | Unit and integration tests |
| docs/data_dictionary.md | Dataset definitions and grains |
| docs/interview_walkthrough.md | Interview narrative, assumptions, and limitations |

Outputs are generated locally and are rebuildable; they are not the source-of-truth. The SQL scripts aggregate call and sales tables before joining where both are one-to-many, avoiding row multiplication that inflates performance metrics.

## Five SQL questions

1. How do customer segments compare on count, potential, receptivity, and simulated volume?
2. How does actual monthly contact frequency compare with the target by segment?
3. What is each representative’s volume-per-call proxy when calls and sales are aggregated separately?
4. How do representatives compare on quarterly quota attainment and the illustrative payout tier?
5. Which specialty-region combinations have the highest simulated volume-per-call proxy?

## Business Analyst case-study artifacts

The links below document the hypothetical business problem, scope, requirements, stakeholder communication, process-improvement hypothesis, user stories, acceptance criteria, and KPI measurement approach. These are portfolio artifacts—not evidence of real stakeholder interviews, company adoption, or achieved operational impact.

- [Business requirements brief](docs/business_requirements.md)
- [Stakeholder and communication plan](docs/stakeholder_and_communication_plan.md)
- [As-is / to-be process improvement case](docs/process_improvement_case.md)
- [User stories and acceptance criteria](docs/user_stories_acceptance_criteria.md)
- [KPI and measurement plan](docs/kpi_measurement_plan.md)

## Interpretation and limitations

- **Descriptive, not causal:** the synthetic generator encodes an association between contacts and volume. These data cannot establish that calls cause volume changes.
- **Heuristic, not optimal:** the contact plan maintains a floor and allocates remaining capacity by a transparent priority score. Real planning requires travel time, availability, preferences, costs, and field constraints.
- **Payouts are illustrative:** the thresholds and incentive amount are teaching assumptions, not payroll logic.
- **Metrics need correct grain:** totals must be aggregated at HCP, call, sales, or rep grain before one-to-many joins.
- **No real healthcare data:** do not interpret synthetic values as evidence about providers or clinical outcomes.
- **No license is granted by this README.** Review repository ownership and licensing requirements before others reuse the code.

See docs/interview_walkthrough.md for a concise explanation, methodology, likely questions, and honest limitations.
