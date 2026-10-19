-- ============================================================================
-- Query 2: Product Performance, Profitability & Margin Ranking
-- Identifies top margin drivers, volume leaders, and low-performing inventory
-- ============================================================================

WITH product_metrics AS (
    SELECT 
        p.product_id,
        p.product_name,
        cat.category_name,
        cat.department,
        p.unit_cost,
        p.unit_price,
        COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
        COALESCE(ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_pct)), 2), 0.0) AS total_revenue,
        COALESCE(ROUND(SUM(oi.quantity * p.unit_cost), 2), 0.0) AS total_cogs,
        COALESCE(ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_pct)) - SUM(oi.quantity * p.unit_cost), 2), 0.0) AS total_profit
    FROM products p
    JOIN categories cat ON p.category_id = cat.category_id
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status IN ('Completed', 'Shipped')
    GROUP BY p.product_id, p.product_name, cat.category_name, cat.department, p.unit_cost, p.unit_price
)
SELECT 
    product_id,
    product_name,
    category_name,
    department,
    unit_price,
    total_units_sold,
    total_revenue,
    total_profit,
    ROUND((total_profit / NULLIF(total_revenue, 0)) * 100.0, 2) AS realized_margin_pct,
    -- Rank products by profit within their category
    DENSE_RANK() OVER (PARTITION BY category_name ORDER BY total_profit DESC) AS rank_in_category,
    -- Stock status classification
    CASE 
        WHEN total_units_sold = 0 THEN 'Dead Stock (0 Sales)'
        WHEN total_units_sold < 10 THEN 'Slow Moving'
        WHEN total_units_sold >= 40 THEN 'Top Velocity'
        ELSE 'Regular Performer'
    END AS inventory_velocity_status
FROM product_metrics
ORDER BY total_profit DESC;
