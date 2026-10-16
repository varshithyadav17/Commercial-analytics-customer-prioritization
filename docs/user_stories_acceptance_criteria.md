# User Stories & Acceptance Criteria — Commercial Planning

> Draft backlog for a hypothetical planning workflow; not reviewed by actual commercial stakeholders.

## US-01 — Explain a segment assignment
**As a territory manager**, I want an account's segment tied to documented thresholds so that I can explain its classification.

- Given potential and receptivity scores, segmentation applies the documented threshold rules.
- Tests cover boundary values.
- Output describes the segment as a heuristic label, not a validated prediction of future performance.

## US-02 — Compare actual contact with target
**As a field excellence lead**, I want actual contact frequency compared with target so that coverage gaps can be inspected.

- Actual and planned contacts have a documented period and grain.
- Outputs show denominator / target definition and surface missing activity data.
- Targets are labelled assumptions until a business owner validates them.

## US-03 — Generate a constrained plan
**As a territory manager**, I want allocation logic and assumed capacity visible so that I can assess feasibility.

- The plan explains the minimum coverage floor and weighting rule.
- Planned activity reconciles to the stated assumed capacity.
- Real constraints such as travel and availability are explicitly excluded, not silently treated as solved.

## US-04 — Prevent inflated SQL totals
**As an analytics reviewer**, I want calls and sales aggregated at the correct grain so that joins do not multiply totals.

- Calls and HCP-month sales are aggregated to intended keys before joining.
- Integration tests verify output consistency.
- Each query output has a documented grain.

## US-05 — Interpret quota / payout previews
**As a finance partner**, I want attainment and illustrative payout thresholds visible so that example calculations can be reviewed.

- Actual, quota, attainment and tier are shown.
- Tests cover payout threshold boundaries.
- Outputs are clearly marked as illustrative, not production payroll.

## US-06 — Review the plan
**As a reviewer**, I want dashboard and workbook views of segments, plan and territory trends.

- Dashboard filters expose the relevant detail.
- Excel is regenerated from current pipeline outputs.
- Definitions and synthetic-data limitations are visible.

## Traceability
| Story | Requirement | Evidence |
|---|---|---|
| US-01 | BR-01 | Segment code + boundary tests |
| US-02 | BR-02 | Actual / target summary |
| US-03 | BR-03 | Capacity checks and heuristic documentation |
| US-04 | BR-04 | Grain-safe SQL and integration tests |
| US-05 | BR-06 | Formula and payout-tier tests |
| US-06 | BR-05, BR-07, BR-08 | Dashboard, workbook and caveats |

## Release checklist
- [ ] Definitions and table grains are documented.
- [ ] Plan totals reconcile to stated capacity assumptions.
- [ ] SQL avoids one-to-many row multiplication.
- [ ] Reporting limitations are visible.
- [ ] Feasibility feedback is collected before a pilot.
- [ ] No causal lift or revenue impact is claimed from simulated data.
