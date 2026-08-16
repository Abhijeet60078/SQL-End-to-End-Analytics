-- ============================================================
-- SQL BUSINESS ANALYSIS PROJECT
-- 12 real-world business questions answered with SQL
-- Database: ecommerce.db (SQLite)
-- ============================================================


-- Q1. MONTHLY REVENUE TREND
-- Business need: track how revenue is trending month over month
-- (only counting completed orders)
-- ------------------------------------------------------------
SELECT
    strftime('%Y-%m', o.order_date)           AS month,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
    COUNT(DISTINCT o.order_id)                 AS orders_count
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY month
ORDER BY month;


-- Q2. TOP 10 CUSTOMERS BY LIFETIME REVENUE
-- Business need: identify highest-value customers for retention/loyalty programs
-- ------------------------------------------------------------
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS lifetime_revenue,
    COUNT(DISTINCT o.order_id)                 AS total_orders
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY c.customer_id, c.customer_name, c.segment
ORDER BY lifetime_revenue DESC
LIMIT 10;


-- Q3. TOP 10 BEST-SELLING PRODUCTS (BY REVENUE AND BY QUANTITY)
-- Business need: identify which products to promote / restock
-- ------------------------------------------------------------
SELECT
    p.product_id,
    p.product_name,
    cat.category_name,
    SUM(oi.quantity)                           AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
JOIN categories cat ON cat.category_id = p.category_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_id, p.product_name, cat.category_name
ORDER BY revenue DESC
LIMIT 10;


-- Q4. REVENUE AND PROFIT MARGIN BY CATEGORY
-- Business need: which categories actually drive profit, not just revenue
-- ------------------------------------------------------------
SELECT
    cat.category_name,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)                          AS revenue,
    ROUND(SUM(oi.quantity * p.unit_cost), 2)                            AS total_cost,
    ROUND(SUM(oi.quantity * (oi.unit_price - p.unit_cost)), 2)          AS gross_profit,
    ROUND(100.0 * SUM(oi.quantity * (oi.unit_price - p.unit_cost))
          / NULLIF(SUM(oi.quantity * oi.unit_price), 0), 2)             AS margin_pct
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
JOIN categories cat ON cat.category_id = p.category_id
WHERE o.order_status = 'Completed'
GROUP BY cat.category_name
ORDER BY gross_profit DESC;


-- Q5. CUSTOMER REPEAT PURCHASE RATE
-- Business need: what % of customers order more than once (a core loyalty metric)
-- ------------------------------------------------------------
WITH order_counts AS (
    SELECT customer_id, COUNT(*) AS orders_placed
    FROM orders
    WHERE order_status = 'Completed'
    GROUP BY customer_id
)
SELECT
    COUNT(*)                                              AS total_customers_with_orders,
    SUM(CASE WHEN orders_placed > 1 THEN 1 ELSE 0 END)     AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN orders_placed > 1 THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                   AS repeat_purchase_rate_pct
FROM order_counts;


-- Q6. AVERAGE ORDER VALUE (AOV) TREND BY QUARTER
-- Business need: is the average customer spending more or less per order over time
-- ------------------------------------------------------------
SELECT
    (strftime('%Y', o.order_date) || '-Q' ||
        ((CAST(strftime('%m', o.order_date) AS INTEGER) - 1) / 3 + 1)) AS quarter,
    ROUND(SUM(oi.quantity * oi.unit_price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY quarter
ORDER BY quarter;


-- Q7. NEW CUSTOMER ACQUISITION BY MONTH
-- Business need: track growth in customer base
-- ------------------------------------------------------------
SELECT
    strftime('%Y-%m', signup_date) AS signup_month,
    COUNT(*)                        AS new_customers
FROM customers
GROUP BY signup_month
ORDER BY signup_month;


-- Q8. CHURN RISK — CUSTOMERS WITH NO ORDER IN THE LAST 90 DAYS
-- Business need: flag customers for a win-back marketing campaign
-- (uses the latest order date in the dataset as "today" for reproducibility)
-- ------------------------------------------------------------
WITH last_order AS (
    SELECT customer_id, MAX(order_date) AS last_order_date
    FROM orders
    WHERE order_status = 'Completed'
    GROUP BY customer_id
),
reference_date AS (
    SELECT MAX(order_date) AS today FROM orders
)
SELECT
    c.customer_id,
    c.customer_name,
    lo.last_order_date,
    CAST(julianday((SELECT today FROM reference_date)) - julianday(lo.last_order_date) AS INTEGER) AS days_since_last_order
FROM last_order lo
JOIN customers c ON c.customer_id = lo.customer_id
WHERE julianday((SELECT today FROM reference_date)) - julianday(lo.last_order_date) > 90
ORDER BY days_since_last_order DESC;


-- Q9. REVENUE BY STATE / REGION
-- Business need: which regions to prioritize for marketing spend or new warehouses
-- ------------------------------------------------------------
SELECT
    o.ship_state,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
    COUNT(DISTINCT o.order_id)                 AS orders_count
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY o.ship_state
ORDER BY revenue DESC;


-- Q10. ORDER STATUS BREAKDOWN (CANCELLATION / RETURN RATE)
-- Business need: monitor operational health — high cancel/return rates signal problems
-- ------------------------------------------------------------
SELECT
    order_status,
    COUNT(*)                                              AS order_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 2) AS pct_of_total
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;


-- Q11. RFM-LITE: RECENCY, FREQUENCY, MONETARY PER CUSTOMER
-- Business need: foundational table for customer segmentation / targeted marketing
-- ------------------------------------------------------------
WITH reference_date AS (
    SELECT MAX(order_date) AS today FROM orders
),
customer_orders AS (
    SELECT
        o.customer_id,
        MAX(o.order_date)                          AS last_order_date,
        COUNT(DISTINCT o.order_id)                  AS frequency,
        SUM(oi.quantity * oi.unit_price)            AS monetary
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY o.customer_id
)
SELECT
    c.customer_id,
    c.customer_name,
    CAST(julianday((SELECT today FROM reference_date)) - julianday(co.last_order_date) AS INTEGER) AS recency_days,
    co.frequency,
    ROUND(co.monetary, 2) AS monetary
FROM customer_orders co
JOIN customers c ON c.customer_id = co.customer_id
ORDER BY monetary DESC;


-- Q12. YEAR-OVER-YEAR REVENUE GROWTH
-- Business need: single headline number for leadership — is the business growing
-- ------------------------------------------------------------
WITH yearly AS (
    SELECT
        strftime('%Y', o.order_date)               AS year,
        SUM(oi.quantity * oi.unit_price)            AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY year
)
SELECT
    year,
    ROUND(revenue, 2) AS revenue,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year))
          / LAG(revenue) OVER (ORDER BY year), 2) AS yoy_growth_pct
FROM yearly
ORDER BY year;
