-- ============================================================================
-- Query 4: Customer RFM (Recency, Frequency, Monetary) Segmentation
-- Segments client base into Champions, Loyal, At Risk, and Hibernating tiers
-- ============================================================================

WITH max_date_cte AS (
    SELECT MAX(order_date) AS max_order_date FROM orders WHERE order_status IN ('Completed', 'Shipped')
),
customer_rfm_raw AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.segment AS account_tier,
        c.city,
        c.state,
        -- Recency: Days since most recent purchase
        CAST(julianday((SELECT max_order_date FROM max_date_cte)) - julianday(MAX(o.order_date)) AS INTEGER) AS recency_days,
        -- Frequency: Count of distinct completed orders
        COUNT(DISTINCT o.order_id) AS frequency,
        -- Monetary: Total spend
        ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_pct)), 2) AS monetary_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status IN ('Completed', 'Shipped')
    GROUP BY c.customer_id, c.customer_name, c.segment, c.city, c.state
),
rfm_scored AS (
    SELECT 
        customer_id,
        customer_name,
        account_tier,
        city,
        state,
        recency_days,
        frequency,
        monetary_value,
        -- Recency Score: lower days is better (rank 4 is most recent, 1 is least recent)
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
        -- Frequency Score: higher frequency is better (rank 4 is most frequent)
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        -- Monetary Score: higher spend is better
        NTILE(4) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM customer_rfm_raw
)
SELECT 
    customer_id,
    customer_name,
    account_tier,
    city,
    recency_days,
    frequency,
    monetary_value,
    (r_score || '-' || f_score || '-' || m_score) AS rfm_cell,
    CASE 
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champion / VIP'
        WHEN r_score >= 3 AND f_score >= 2 THEN 'Loyal Customer'
        WHEN r_score >= 3 AND f_score = 1 THEN 'Recent New Buyer'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk (High Value / Inactive)'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'Need Attention'
        ELSE 'Hibernating / Churned'
    END AS customer_rfm_segment
FROM rfm_scored
ORDER BY monetary_value DESC;
