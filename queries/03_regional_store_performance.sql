-- ============================================================================
-- Query 3: Regional & Store Sales Performance
-- Ranks stores within each geographic sales territory
-- ============================================================================

WITH store_summary AS (
    SELECT 
        r.region_id,
        r.region_name,
        r.manager_name,
        s.store_id,
        s.store_name,
        s.city AS store_city,
        s.store_type,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_pct)), 2) AS total_revenue,
        ROUND(SUM((oi.quantity * oi.unit_price * (1.0 - oi.discount_pct)) - (oi.quantity * p.unit_cost)), 2) AS total_profit
    FROM regions r
    JOIN stores s ON r.region_id = s.region_id
    JOIN orders o ON s.store_id = o.store_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status IN ('Completed', 'Shipped')
    GROUP BY r.region_id, r.region_name, r.manager_name, s.store_id, s.store_name, s.city, s.store_type
)
SELECT 
    region_name,
    manager_name,
    store_name,
    store_city,
    store_type,
    total_orders,
    total_revenue,
    total_profit,
    ROUND((total_profit / NULLIF(total_revenue, 0)) * 100.0, 2) AS profit_margin_pct,
    -- Store Rank within territory
    DENSE_RANK() OVER (PARTITION BY region_name ORDER BY total_revenue DESC) AS regional_store_rank,
    -- Regional Revenue Contribution Share %
    ROUND(
        (total_revenue / SUM(total_revenue) OVER (PARTITION BY region_name)) * 100.0, 
        2
    ) AS pct_of_regional_sales
FROM store_summary
ORDER BY region_name ASC, regional_store_rank ASC;
