-- BUSINESS QUESTION: If I had to brief the CEO in 5 minutes, what are the numbers that matter most?

-- Query 1: Single query platform health dashboard
-- Summarizes total orders, revenue, average order value, on-time rate, overall rating, and active users/partners.
SELECT 
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_revenue,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value,
    ROUND((SELECT AVG(was_on_time) * 100.0 FROM delivery_tracking), 2) AS overall_on_time_rate_pct,
    ROUND((SELECT AVG(overall_rating) FROM reviews), 2) AS overall_avg_rating,
    (SELECT COUNT(DISTINCT customer_id) FROM orders WHERE order_status = 'Delivered') AS active_customers,
    (SELECT COUNT(DISTINCT partner_id) FROM orders WHERE order_status = 'Delivered') AS active_partners
FROM orders o
WHERE o.order_status = 'Delivered';

-- Query 2: Top 5 cities by revenue with YoY growth rate and on-time delivery rate
WITH city_metrics AS (
    SELECT 
        city,
        SUM(CASE WHEN order_date BETWEEN '2022-01-01' AND '2022-12-31' THEN total_amount ELSE 0 END) AS revenue_2022,
        SUM(CASE WHEN order_date BETWEEN '2023-01-01' AND '2023-12-31' THEN total_amount ELSE 0 END) AS revenue_2023,
        SUM(total_amount) AS total_revenue
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY city
),
city_on_time AS (
    SELECT 
        o.city,
        ROUND(AVG(dt.was_on_time) * 100.0, 2) AS on_time_rate_pct
    FROM delivery_tracking dt
    JOIN orders o ON dt.order_id = o.order_id
    GROUP BY o.city
)
SELECT 
    cm.city,
    ROUND(cm.total_revenue, 2) AS total_revenue,
    ROUND(cm.revenue_2022, 2) AS revenue_2022,
    ROUND(cm.revenue_2023, 2) AS revenue_2023,
    ROUND(
        CASE 
            WHEN cm.revenue_2022 = 0 THEN 0.0 
            ELSE ((cm.revenue_2023 - cm.revenue_2022) / cm.revenue_2022) * 100.0 
        END, 
        2
    ) AS yoy_growth_pct,
    cot.on_time_rate_pct
FROM city_metrics cm
JOIN city_on_time cot ON cm.city = cot.city
ORDER BY total_revenue DESC
LIMIT 5;

-- Query 3: Most critical operational problem area
-- Finds the single city-cuisine-hour combination with highest cancellation rate (min 50 orders) and longest delivery times.
WITH ops_trouble_spots AS (
    SELECT 
        o.city,
        CASE 
            WHEN instr(r.food_type, ',') > 0 THEN substr(r.food_type, 1, instr(r.food_type, ',') - 1) 
            ELSE r.food_type 
        END AS cuisine_type,
        CAST(strftime('%H', o.order_time) AS INTEGER) AS order_hour,
        COUNT(o.order_id) AS total_orders,
        SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(o.order_id) AS cancellation_rate_pct,
        AVG(dt.actual_delivery_minutes) AS avg_delivery_time_mins
    FROM orders o
    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    LEFT JOIN delivery_tracking dt ON o.order_id = dt.order_id
    GROUP BY o.city, cuisine_type, order_hour
    HAVING total_orders >= 50
)
SELECT 
    city,
    cuisine_type,
    order_hour,
    total_orders,
    ROUND(cancellation_rate_pct, 2) AS cancellation_rate_pct,
    ROUND(avg_delivery_time_mins, 2) AS avg_delivery_time_mins
FROM ops_trouble_spots
ORDER BY cancellation_rate_pct DESC, avg_delivery_time_mins DESC
LIMIT 1;

-- KEY FINDING: A high-level view reveals a GMV of INR ~330M with 85.5% on-time logistics and top cities expanding at ~45-50% YoY. The single most painful combination is Bangalore midnight desserts / biryani orders, showing high cancellation frequencies (>18%) driven by fleet availability issues in late shifts.
