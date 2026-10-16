# Stakeholder & Communication Plan — Commercial Prioritization

> A proposed stakeholder model for a synthetic case study. This is not a record of actual requirements interviews or field feedback.

## Stakeholder map
| Role | Key question | Evidence to communicate |
|---|---|---|
| Commercial / field excellence lead | What rules drive priority and capacity use? | Segment logic, weights, assumptions and sensitivity |
| Territory manager | Is the plan feasible locally? | Account-level plan, coverage gap, workload and capacity |
| Field representative | Why is this account prioritised? | Explainable score components and expected frequency |
| Commercial analytics / BI | Are the metrics correct and reproducible? | Data dictionary, grain definitions, SQL and tests |
| Finance / incentive partner | How is attainment and payout calculated? | Actual, quota, threshold and example payout |
| Data governance / compliance | Is the data suitable and bounded? | Provenance, permitted use and explicit exclusions |

## Proposed touchpoints
| Touchpoint | Audience | Agenda | Intended output |
|---|---|---|---|
| Metric / data-grain workshop | Analytics + BI | Definitions, keys, missingness, period, table grain | Approved metric dictionary |
| Planning-rule review | Field excellence + territory managers | Segment thresholds, coverage floor, capacity assumptions | Rule feedback and feasibility constraints |
| Territory review | Manager + representative | Account-level conflicts, coverage gaps and overrides | Documented exception / adjustment |
| Quota-rule review | Finance + commercial owner | Actual and quota definitions, quarter boundaries, payout tiers | Approved policy before any real use |
| Pilot readout | Process owner + analytics | Adoption, feasibility, outcomes and guardrails | Continue / adjust / stop decision |

## Communication standards
- Explain why each account receives a segment and planned frequency.
- Show planned activity beside the assumed capacity.
- Separate actual historical contact from planned frequency.
- Display metric grain, period and denominator.
- Do not claim calls caused simulated volume.
- Label payout outputs illustrative, not payroll logic.

## Draft RACI
| Activity | Analytics | Field excellence | Territory manager | Finance | Data governance |
|---|---|---|---|---|---|
| Define data and metrics | R | A | C | C | C |
| Approve segment rules | R | A | C | I | C |
| Validate plan feasibility | C | A | R | I | I |
| Validate quota / payout policy | C | C | I | A/R | C |
| Approve real-data use | C | C | I | I | A/R |

R = Responsible, A = Accountable, C = Consulted, I = Informed. This draft must be replaced or approved by actual stakeholders before deployment.
