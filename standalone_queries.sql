-- ============================================================
-- Flying Enterprise Cork — Standalone SQL Analytics Queries
-- Compatible with: MySQL 8.0+, PostgreSQL, SQLite
-- Author: Bhunesh Dadheech
-- ============================================================
-- HOW TO USE: Import transactions, customers, inventory, and
-- staff_schedules CSVs into your MySQL database, then run
-- each query block below.
-- ============================================================


-- ── Q1: Revenue & Gross Profit by Category ──────────────────
SELECT
    category,
    COUNT(*)                                                AS transactions,
    ROUND(SUM(revenue), 2)                                  AS total_revenue,
    ROUND(SUM(gross_profit), 2)                             AS gross_profit,
    ROUND(AVG(unit_price), 2)                               AS avg_unit_price,
    ROUND(SUM(gross_profit) * 100.0 / SUM(revenue), 1)     AS gp_margin_pct,
    ROUND(SUM(revenue) * 100.0 /
          (SELECT SUM(revenue) FROM transactions), 1)       AS revenue_share_pct
FROM transactions
GROUP BY category
ORDER BY total_revenue DESC;


-- ── Q2: Customer Segmentation (RFM-style) ───────────────────
SELECT
    segment,
    COUNT(*)                                                AS customer_count,
    ROUND(AVG(total_visits), 1)                             AS avg_visits,
    ROUND(AVG(avg_spend_eur), 2)                            AS avg_spend_eur,
    ROUND(AVG(total_spend_eur), 2)                          AS avg_lifetime_value,
    ROUND(SUM(total_spend_eur), 2)                          AS segment_total_revenue,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 1) AS pct_of_customers
FROM customers
GROUP BY segment
ORDER BY avg_lifetime_value DESC;


-- ── Q3: Top 10 Products with Window Function RANK() ─────────
SELECT
    product,
    category,
    SUM(quantity)                                           AS units_sold,
    ROUND(SUM(revenue), 2)                                  AS total_revenue,
    ROUND(SUM(gross_profit), 2)                             AS gross_profit,
    ROUND(SUM(gross_profit) * 100.0 / SUM(revenue), 1)     AS gp_margin_pct,
    ROUND(AVG(revenue / quantity), 2)                       AS avg_unit_price,
    RANK() OVER (ORDER BY SUM(revenue) DESC)                AS revenue_rank
FROM transactions
GROUP BY product, category
ORDER BY total_revenue DESC
LIMIT 10;


-- ── Q4: Peak Trading Windows (Hour × Day of Week) ───────────
SELECT
    day_of_week,
    hour,
    COUNT(*)                        AS transactions,
    ROUND(SUM(revenue), 2)          AS total_revenue,
    ROUND(AVG(revenue), 2)          AS avg_revenue_per_txn
FROM transactions
GROUP BY day_of_week, hour
ORDER BY total_revenue DESC
LIMIT 20;


-- ── Q5: Event Day vs Normal Day Revenue Impact ───────────────
SELECT
    CASE WHEN is_event_day = 1 THEN 'Event Day' ELSE 'Normal Day' END AS day_type,
    COUNT(DISTINCT date)                            AS trading_days,
    COUNT(*)                                        AS total_transactions,
    ROUND(SUM(revenue), 2)                          AS total_revenue,
    ROUND(AVG(revenue), 2)                          AS avg_per_transaction,
    ROUND(SUM(revenue) / COUNT(DISTINCT date), 2)   AS avg_daily_revenue
FROM transactions
GROUP BY is_event_day;


-- ── Q6: Staff Performance — Revenue per Hour ────────────────
SELECT
    t.staff_name,
    COUNT(*)                                                AS transactions_served,
    ROUND(SUM(t.revenue), 2)                                AS revenue_generated,
    ROUND(AVG(t.revenue), 2)                                AS avg_transaction_value,
    s.total_hours,
    ROUND(SUM(t.revenue) / NULLIF(s.total_hours, 0), 2)    AS revenue_per_hour
FROM transactions t
LEFT JOIN (
    SELECT staff_name, SUM(hours_worked) AS total_hours
    FROM staff_schedules
    GROUP BY staff_name
) s ON t.staff_name = s.staff_name
GROUP BY t.staff_name, s.total_hours
ORDER BY revenue_generated DESC
LIMIT 10;


-- ── Q7: Inventory Wastage & Stockout Risk ───────────────────
SELECT
    item_name,
    category,
    ROUND(AVG(stock_level), 1)                      AS avg_stock,
    ROUND(AVG(daily_usage), 1)                      AS avg_daily_usage,
    ROUND(SUM(waste_units), 1)                      AS total_wastage_units,
    COUNT(CASE WHEN reorder_triggered = 1 THEN 1 END) AS reorder_events,
    ROUND(SUM(waste_units) * 2.5, 2)               AS estimated_wastage_eur
FROM inventory
GROUP BY item_name, category
ORDER BY estimated_wastage_eur DESC
LIMIT 10;


-- ── Q8: Monthly YoY Revenue Comparison ──────────────────────
SELECT
    month_name,
    month,
    ROUND(SUM(CASE WHEN year = 2023 THEN revenue ELSE 0 END), 2) AS rev_2023,
    ROUND(SUM(CASE WHEN year = 2024 THEN revenue ELSE 0 END), 2) AS rev_2024,
    ROUND(
        (SUM(CASE WHEN year = 2024 THEN revenue ELSE 0 END) -
         SUM(CASE WHEN year = 2023 THEN revenue ELSE 0 END)) * 100.0 /
        NULLIF(SUM(CASE WHEN year = 2023 THEN revenue ELSE 0 END), 0)
    , 1) AS yoy_growth_pct
FROM transactions
GROUP BY month_name, month
ORDER BY month;
