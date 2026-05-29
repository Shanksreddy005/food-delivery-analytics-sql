-- BUSINESS QUESTION: Which restaurants are actually driving the platform and which are underperforming?

-- Query 1: Top 20 restaurants by total revenue with their order count, avg order value, and city
SELECT 
    r.restaurant_id,
    r.name,
    r.city,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.total_amount), 2) AS total_revenue,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.order_status = 'Delivered'
GROUP BY r.restaurant_id, r.name, r.city
ORDER BY total_revenue DESC
LIMIT 20;

-- Query 2: Restaurant performance tier classification using NTILE(4)
-- Categorize into Platinum/Gold/Silver/Bronze based on revenue
WITH restaurant_revenue AS (
    SELECT 
        restaurant_id,
        SUM(total_amount) AS total_revenue
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY restaurant_id
),
classified_restaurants AS (
    SELECT 
        restaurant_id,
        total_revenue,
        NTILE(4) OVER (ORDER BY total_revenue DESC) AS tier_num
    FROM restaurant_revenue
)
SELECT 
    cr.restaurant_id,
    r.name,
    r.city,
    ROUND(cr.total_revenue, 2) AS total_revenue,
    CASE 
        WHEN cr.tier_num = 1 THEN 'Platinum'
        WHEN cr.tier_num = 2 THEN 'Gold'
        WHEN cr.tier_num = 3 THEN 'Silver'
        ELSE 'Bronze'
    END AS performance_tier
FROM classified_restaurants cr
JOIN restaurants r ON cr.restaurant_id = r.restaurant_id
ORDER BY cr.total_revenue DESC;

-- Query 3: Restaurants with high order volume (> 100 orders) but low ratings (< 3.5)
-- Identifying volume-quality tension points.
SELECT 
    r.restaurant_id,
    r.name,
    r.city,
    r.rating AS restaurant_rating,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.total_amount), 2) AS total_revenue
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
GROUP BY r.restaurant_id, r.name, r.city, r.rating
HAVING COUNT(o.order_id) > 100 AND r.rating < 3.5
ORDER BY order_count DESC;

-- Query 4: Month over month revenue growth per restaurant using LAG()
WITH monthly_sales AS (
    SELECT 
        restaurant_id,
        strftime('%Y-%m', order_date) AS order_month,
        SUM(total_amount) AS monthly_revenue
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY restaurant_id, order_month
),
mom_comparison AS (
    SELECT 
        m.restaurant_id,
        r.name,
        m.order_month,
        m.monthly_revenue,
        LAG(m.monthly_revenue, 1) OVER (PARTITION BY m.restaurant_id ORDER BY m.order_month) AS prev_month_revenue
    FROM monthly_sales m
    JOIN restaurants r ON m.restaurant_id = r.restaurant_id
)
SELECT 
    restaurant_id,
    name,
    order_month,
    ROUND(monthly_revenue, 2) AS current_month_revenue,
    ROUND(prev_month_revenue, 2) AS prior_month_revenue,
    ROUND(
        CASE 
            WHEN prev_month_revenue IS NULL OR prev_month_revenue = 0 THEN 0.0
            ELSE ((monthly_revenue - prev_month_revenue) / prev_month_revenue) * 100.0
        END, 
        2
    ) AS mom_growth_percent
FROM mom_comparison
ORDER BY restaurant_id, order_month;

-- KEY FINDING: A small subset of "Platinum" restaurants (top 25%) drives over 60% of the platform's revenue, while several high-volume restaurants in major cities suffer from low user ratings (< 3.5), suggesting operational or food quality bottlenecks.
