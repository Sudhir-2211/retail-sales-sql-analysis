-- ============================================================================
-- Query 5: Customer Retention, Repeat Purchase Rate & Average Order Value (AOV)
-- Evaluates commercial health metrics and customer lifetime metrics
-- ============================================================================

WITH customer_order_counts AS (
    SELECT 
        c.customer_id,
        c.segment,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_pct)), 2) AS total_customer_spend
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status IN ('Completed', 'Shipped')
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.segment
),
segment_metrics AS (
    SELECT 
        segment,
        COUNT(customer_id) AS total_customers,
        SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
        SUM(CASE WHEN order_count = 1 THEN 1 ELSE 0 END) AS single_order_customers,
        SUM(CASE WHEN order_count = 0 THEN 1 ELSE 0 END) AS zero_order_customers,
        ROUND(SUM(total_customer_spend), 2) AS total_segment_revenue,
        ROUND(AVG(total_customer_spend), 2) AS avg_clv_per_customer,
        SUM(order_count) AS total_orders_in_segment
    FROM customer_order_counts
    GROUP BY segment
)
SELECT 
    segment,
    total_customers,
    repeat_customers,
    single_order_customers,
    zero_order_customers,
    -- Repeat Purchase Rate
    ROUND((CAST(repeat_customers AS REAL) / NULLIF(total_customers - zero_order_customers, 0)) * 100.0, 2) AS repeat_purchase_rate_pct,
    total_segment_revenue,
    avg_clv_per_customer,
    -- Average Order Value (AOV)
    ROUND(total_segment_revenue / NULLIF(total_orders_in_segment, 0), 2) AS average_order_value_aov
FROM segment_metrics
ORDER BY total_segment_revenue DESC;
