-- E-commerce Analytics Query
-- This query analyzes product sales performance by category
-- Company: eXonware.com
-- Date: 07-Oct-2025

WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', o.order_date) AS month,
        c.category_name,
        p.product_name,
        SUM(oi.quantity * oi.unit_price) AS total_revenue,
        COUNT(DISTINCT o.customer_id) AS unique_customers,
        AVG(oi.quantity * oi.unit_price) AS avg_order_value
    FROM orders o
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    INNER JOIN categories c ON p.category_id = c.category_id
    WHERE o.order_date >= '2024-01-01'
        AND o.status = 'completed'
        AND c.category_name IN ('Electronics', 'Clothing', 'Books')
    GROUP BY DATE_TRUNC('month', o.order_date), c.category_name, p.product_name
    HAVING SUM(oi.quantity * oi.unit_price) > 1000
),
top_products AS (
    SELECT 
        category_name,
        product_name,
        total_revenue,
        ROW_NUMBER() OVER (PARTITION BY category_name ORDER BY total_revenue DESC) AS revenue_rank
    FROM monthly_sales
)
SELECT 
    tp.category_name,
    tp.product_name,
    tp.total_revenue,
    tp.revenue_rank,
    ms.unique_customers,
    ms.avg_order_value,
    CASE 
        WHEN tp.revenue_rank = 1 THEN 'Top Performer'
        WHEN tp.revenue_rank <= 3 THEN 'High Performer'
        ELSE 'Standard'
    END AS performance_tier
FROM top_products tp
INNER JOIN monthly_sales ms ON tp.category_name = ms.category_name 
    AND tp.product_name = ms.product_name
WHERE tp.revenue_rank <= 5
ORDER BY tp.category_name, tp.revenue_rank;

