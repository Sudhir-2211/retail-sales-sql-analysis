-- ============================================================================
-- Query 1: Monthly Revenue, Profitability, and MoM Growth Analysis
-- Uses Window Functions (LAG, SUM OVER) to track performance trends
-- ============================================================================

WITH monthly_sales AS (
    SELECT 
        order_month,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(quantity) AS total_units_sold,
        ROUND(SUM(net_revenue), 2) AS monthly_revenue,
        ROUND(SUM(total_cost), 2) AS monthly_cost,
        ROUND(SUM(gross_profit), 2) AS monthly_profit,
        ROUND((SUM(gross_profit) / NULLIF(SUM(net_revenue), 0)) * 100.0, 2) AS profit_margin_pct
    FROM v_sales_detailed
    WHERE order_status IN ('Completed', 'Shipped')
    GROUP BY order_month
)
SELECT 
    order_month,
    total_orders,
    total_units_sold,
    monthly_revenue,
    monthly_profit,
    profit_margin_pct,
    -- Previous Month Revenue via LAG window function
    LAG(monthly_revenue, 1) OVER (ORDER BY order_month) AS prev_month_revenue,
    -- Month-over-Month (MoM) Growth Percentage
    ROUND(
        ((monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY order_month)) 
        / NULLIF(LAG(monthly_revenue, 1) OVER (ORDER BY order_month), 0)) * 100.0, 
        2
    ) AS mom_growth_pct,
    -- Cumulative Running Revenue
    ROUND(SUM(monthly_revenue) OVER (ORDER BY order_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total_revenue
FROM monthly_sales
ORDER BY order_month ASC;
