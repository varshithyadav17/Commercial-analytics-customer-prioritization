# Interview Walkthrough: Commercial Analytics & Customer Prioritization

## 60-second explanation

“I built a reproducible commercial analytics case study on seeded synthetic data. It segments accounts using two transparent signals—potential and receptivity—then compares actual contact frequency with segment targets and builds a monthly plan under an assumed rep capacity. Python produces segment, territory, trend, and illustrative incentive outputs; SQL loads the tables into SQLite and answers five business questions; Streamlit and Excel expose the results to a non-technical reviewer. I also added checks to prevent row-multiplication errors when calls and monthly sales are joined. The data is synthetic, so I discuss operational trade-offs and data-grain correctness rather than claiming that calls caused volume.”

## Business decision

The decision is how to distribute limited representative capacity across accounts while maintaining a coverage floor and making the assumptions auditable.

## Methodology

1. **Segmentation:** potential score >= 60 and receptivity >= 55 produces Key Target; high potential only produces Growth; high receptivity only produces Maintain; otherwise Low Priority.
2. **Baseline activity:** count contact events by HCP and divide by 12 to estimate an average monthly frequency.
3. **Planning heuristic:** reserve 0.5 planned calls per HCP per month, then allocate remaining assumed capacity (60 calls per representative per month) to the top half of accounts, weighted by potential × receptivity.
4. **Commercial measures:** aggregate monthly simulated volume by HCP before joining with calls; calculate volume-per-call only as a descriptive proxy.
5. **Quota preview:** compare synthetic quarterly actual volume with synthetic quota and apply explicitly documented payout tiers.
6. **Reporting:** make the segment and territory summaries available through SQL CSV outputs, an interactive dashboard, and a workbook.

## Data-grain issue and why it matters

Calls are one-to-many per HCP, and sales are also one-to-many per HCP because each HCP has multiple months. Joining raw calls directly to raw sales creates a calls × months row multiplication. A sum over the joined table can then overstate sales. The SQL script aggregates calls by HCP/rep and sales by HCP/rep first, and only then joins the aggregates. Integration tests assert that rep and specialty-region totals reconcile to the input populations.

## How to interpret results

All records are generated. The simulated sales formula incorporates a contact-related term, so a positive relationship is built into the scenario. It does not establish a real causal lift, a return on investment, or a recommendation to increase contacts in a particular region.

The call plan is also a transparent heuristic—not a solver for a fully specified operations-research problem. Real planning would require route/travel cost, field time availability, contact preferences, customer limits, diminishing returns, and uncertainty.

## Likely interview questions

**Why use rule-based segmentation rather than clustering?**  
The threshold logic is explainable to a stakeholder and easy to challenge. A later experiment could compare it with clustering or outcome-based segmentation using validation criteria and stability analysis.

**Why are planned calls fractional?**  
The allocation represents an expected or averaged monthly frequency across a planning horizon, not a literal fraction of one appointment on a calendar. A scheduling stage would convert it into integer activities and validate capacity.

**What does volume per call mean?**  
It is a descriptive ratio. It is influenced by account mix, baseline volume, timing, and generated data assumptions. It is not an estimate of causal effectiveness.

**How is the capacity constraint checked?**  
The planned call totals are asserted to sum to assumed monthly capacity (number of representatives × calls per representative) and each HCP receives the minimum coverage floor.

**What are the limitations?**  
Synthetic inputs, simplified four-bucket labels, a heuristic planner, illustrative payout tiers, no causal identification, and no route scheduling. The purpose is to demonstrate reliable analyst workflow, not production readiness.

**What would you do next with real data?**  
Define the grain and metric contract, audit data completeness, align segment and territory targets with business owners, evaluate plan feasibility, measure outcomes with a suitable experiment or quasi-experiment, and track adoption and coverage changes.
