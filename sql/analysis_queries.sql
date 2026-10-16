-- Commercial analytics questions for synthetic healthcare-commercial data.
-- Every query aggregates one-to-many sources before joining them.

-- Q1. Segment profile and simulated sales volume
WITH sales_by_hcp AS (
    SELECT hcp_id, SUM(rx_volume) AS total_rx_volume FROM sales GROUP BY hcp_id
)
SELECT h.segment, COUNT(DISTINCT h.hcp_id) AS hcp_count,
       ROUND(AVG(h.potential_score), 1) AS avg_potential,
       ROUND(AVG(h.receptivity_score), 1) AS avg_receptivity,
       ROUND(SUM(COALESCE(s.total_rx_volume, 0)), 1) AS total_rx_volume
FROM hcps_with_segment h
LEFT JOIN sales_by_hcp s ON s.hcp_id = h.hcp_id
GROUP BY h.segment
ORDER BY total_rx_volume DESC;

-- Q2. Actual versus target contact frequency by segment
WITH call_counts AS (
    SELECT hcp_id, COUNT(*) AS total_calls FROM calls GROUP BY hcp_id
)
SELECT h.segment, COUNT(DISTINCT h.hcp_id) AS hcp_count,
       ROUND(AVG(COALESCE(c.total_calls, 0) / 12.0), 2) AS avg_actual_calls_per_month,
       CASE h.segment WHEN 'Key Target' THEN 2.0 WHEN 'Growth' THEN 1.5
            WHEN 'Maintain' THEN 1.0 ELSE 0.4 END AS target_calls_per_month
FROM hcps_with_segment h
LEFT JOIN call_counts c ON c.hcp_id = h.hcp_id
GROUP BY h.segment
ORDER BY h.segment;

-- Q3. Representative performance proxy with calls and sales aggregated separately
WITH call_counts AS (
    SELECT rep_id, COUNT(*) AS total_calls FROM calls GROUP BY rep_id
),
sales_by_rep AS (
    SELECT h.rep_id, SUM(s.rx_volume) AS total_rx_volume
    FROM hcps_with_segment h JOIN sales s ON s.hcp_id = h.hcp_id
    GROUP BY h.rep_id
)
SELECT r.rep_id, r.rep_name, COALESCE(c.total_calls, 0) AS total_calls,
       ROUND(COALESCE(s.total_rx_volume, 0), 1) AS total_rx_volume,
       ROUND(COALESCE(s.total_rx_volume, 0) / NULLIF(c.total_calls, 0), 2) AS rx_per_call_proxy
FROM reps r
LEFT JOIN call_counts c ON c.rep_id = r.rep_id
LEFT JOIN sales_by_rep s ON s.rep_id = r.rep_id
ORDER BY rx_per_call_proxy DESC;

-- Q4. Quarterly quota attainment and illustrative incentive tier
SELECT rep_id, quarter, quota_volume, actual_volume,
       ROUND(actual_volume * 100.0 / NULLIF(quota_volume, 0), 1) AS attainment_pct,
       CASE WHEN actual_volume * 1.0 / NULLIF(quota_volume, 0) >= 1.10 THEN 'Accelerator (150%)'
            WHEN actual_volume * 1.0 / NULLIF(quota_volume, 0) >= 1.00 THEN 'Full Payout (100%)'
            WHEN actual_volume * 1.0 / NULLIF(quota_volume, 0) >= 0.80 THEN 'Partial Payout (50%)'
            ELSE 'No Payout (0%)' END AS payout_tier
FROM rep_targets
ORDER BY quarter, attainment_pct DESC;

-- Q5. Specialty-region volume per contact without row multiplication
WITH sales_by_hcp AS (
    SELECT hcp_id, SUM(rx_volume) AS total_rx_volume FROM sales GROUP BY hcp_id
),
calls_by_hcp AS (
    SELECT hcp_id, COUNT(*) AS total_calls FROM calls GROUP BY hcp_id
),
hcp_metrics AS (
    SELECT h.hcp_id, h.specialty, h.region,
           COALESCE(s.total_rx_volume, 0) AS total_rx_volume,
           COALESCE(c.total_calls, 0) AS total_calls
    FROM hcps_with_segment h
    LEFT JOIN sales_by_hcp s ON s.hcp_id = h.hcp_id
    LEFT JOIN calls_by_hcp c ON c.hcp_id = h.hcp_id
)
SELECT specialty, region, ROUND(SUM(total_rx_volume), 1) AS total_rx_volume,
       SUM(total_calls) AS total_calls,
       ROUND(SUM(total_rx_volume) / NULLIF(SUM(total_calls), 0), 2) AS rx_per_call_proxy
FROM hcp_metrics
GROUP BY specialty, region
ORDER BY rx_per_call_proxy DESC;
