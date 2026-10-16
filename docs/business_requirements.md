# Business Requirements Brief — Commercial Analytics & Customer Prioritization

> **Case-study boundary:** This project uses deterministic synthetic commercial data. The stakeholder needs and requirements below are illustrative; no pharma company, healthcare professional, field representative, or commercial team was consulted.

## Problem statement and objective
A hypothetical field organisation has limited customer-facing capacity and wants to prioritise accounts transparently, compare actual and planned contact frequency, and review results by segment and territory. The prototype demonstrates a repeatable decision-support workflow—segmentation, a capacity-constrained planning heuristic, SQL analyses, dashboard and Excel output. It does not prove actual commercial improvement or causal effectiveness.

## Illustrative stakeholders
| Role | Need / decision |
|---|---|
| Commercial / field excellence manager | Review allocation logic and planning assumptions |
| Regional / territory manager | Understand account coverage and workload feasibility |
| Field representative | Understand why an account is prioritised |
| Commercial analytics / BI analyst | Maintain metric definitions, joins and validation |
| Finance / incentive-compensation partner | Review quota calculations and illustrative payout tiers |
| Data governance / compliance reviewer | Confirm appropriate data use and boundaries |

These are hypothetical roles, not interview participants. The sample contains no real HCP or prescription data.

## Scope
**In scope:** synthetic data generation; explainable four-group segmentation; monthly contact activity; a minimum coverage floor plus priority-weighted call-plan heuristic; illustrative representative-capacity assumptions; descriptive territory / segment / monthly summaries; quarterly quota and payout preview; five SQL questions; Streamlit dashboard; Excel workbook; tests and documentation.

**Out of scope:** real HCP targeting, clinical or prescribing recommendations, production territory optimisation, route scheduling, compliance determinations, payroll processing, causal estimates of contact effectiveness, or deployment to a field team.

## Business requirements
| ID | Requirement | Priority | Acceptance evidence |
|---|---|---|---|
| BR-01 | Make segment rules and thresholds explainable | Must | Rules documented and tested at boundaries |
| BR-02 | Compare actual contact activity with a segment-level target | Must | Actual/target comparison at documented grain |
| BR-03 | Allocate assumed monthly capacity transparently | Must | Floor, weighting rule and capacity checks documented |
| BR-04 | Preserve correct aggregation grain when joining calls and sales | Must | One-to-many inputs aggregated before join; integration checks pass |
| BR-05 | Summarise descriptive performance by segment, territory and month | Must | Reproducible SQL outputs and dashboard views |
| BR-06 | Make quota attainment / payout assumptions visible | Should | Thresholds documented and boundary-tested |
| BR-07 | Provide stakeholder-readable Excel and interactive reporting | Should | Workbook and dashboard regenerate |
| BR-08 | Communicate limitations before decisions | Must | Synthetic and non-causal boundaries visible in reports |

## Business rules and assumptions
- A capacity assumption of 60 calls per representative per month is illustrative, not a validated operating standard.
- The planner is a heuristic, not an optimally solved scheduling problem. Travel time, availability, customer preferences, field policies and other real constraints are excluded.
- Fractional contact frequency describes an average over the planning horizon, not a fractional appointment.
- The synthetic volume formula includes contact-related effects; correlations do not estimate real causal lift.
- Illustrative payout tiers are not production payroll rules.
- Calls, account-month sales and rep-quarter quota figures have different grains; aggregate correctly before joining.

## Definition of done
The pipeline is reproducible; segment and call-plan rules are traceable; plan capacity arithmetic holds; SQL results avoid join multiplication; tests pass; dashboard and workbook can be regenerated; and limitations are visible to reviewers.

## Risks and dependencies
| Risk | Mitigation |
|---|---|
| Rules may not reflect business priorities | Validate thresholds with accountable stakeholders |
| Capacity may vary by territory | Model availability, travel and route constraints before real use |
| One-to-many joins inflate metrics | Preserve grain and test aggregate reconciliation |
| Synthetic contact-volume relationship appears causal | Do not claim ROI or lift; use a valid evaluation design with real data |
| Incentive policy is more complex than the example | Obtain finance / policy owner approval before operational use |
