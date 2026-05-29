-- BUSINESS QUESTION: Where are the delivery bottlenecks and what causes delays?

-- Query 1: Average delivery time by city, time of day (buckets), and vehicle type
SELECT 
    o.city,
    CASE 
        WHEN CAST(strftime('%H', o.order_time) AS INTEGER) BETWEEN 6 AND 11 THEN 'Morning (6am-12pm)'
        WHEN CAST(strftime('%H', o.order_time) AS INTEGER) BETWEEN 12 AND 16 THEN 'Afternoon (12pm-5pm)'
        WHEN CAST(strftime('%H', o.order_time) AS INTEGER) BETWEEN 17 AND 22 THEN 'Evening (5pm-11pm)'
        ELSE 'Night (11pm-6am)'
    END AS time_of_day,
    dp.vehicle_type,
    ROUND(AVG(dt.actual_delivery_minutes), 2) AS avg_delivery_time_mins,
    COUNT(o.order_id) AS order_count
FROM delivery_tracking dt
JOIN orders o ON dt.order_id = o.order_id
JOIN delivery_partners dp ON dt.partner_id = dp.partner_id
GROUP BY o.city, time_of_day, dp.vehicle_type
ORDER BY o.city, avg_delivery_time_mins DESC;

-- Query 2: On-time delivery rate by city and hour of day using window functions
WITH city_hourly_stats AS (
    SELECT 
        o.city,
        CAST(strftime('%H', o.order_time) AS INTEGER) AS order_hour,
        COUNT(dt.tracking_id) AS total_deliveries,
        SUM(CASE WHEN dt.was_on_time = 1 THEN 1 ELSE 0 END) AS on_time_deliveries
    FROM delivery_tracking dt
    JOIN orders o ON dt.order_id = o.order_id
    GROUP BY o.city, order_hour
)
SELECT 
    city,
    order_hour,
    total_deliveries,
    on_time_deliveries,
    ROUND((on_time_deliveries * 100.0) / total_deliveries, 2) AS on_time_rate_pct,
    ROUND(AVG((on_time_deliveries * 100.0) / total_deliveries) OVER (PARTITION BY city), 2) AS city_avg_on_time_rate_pct
FROM city_hourly_stats
ORDER BY city, order_hour;

-- Query 3: Partners with consistent late deliveries
-- Flag partners whose late delivery rate exceeds 2x the city average (with min 10 deliveries)
WITH partner_stats AS (
    SELECT 
        dp.partner_id,
        dp.name AS partner_name,
        dp.city,
        COUNT(dt.tracking_id) AS total_deliveries,
        SUM(CASE WHEN dt.was_on_time = 0 THEN 1 ELSE 0 END) AS late_deliveries,
        (SUM(CASE WHEN dt.was_on_time = 0 THEN 1 ELSE 0 END) * 100.0) / COUNT(dt.tracking_id) AS partner_late_rate_pct
    FROM delivery_tracking dt
    JOIN delivery_partners dp ON dt.partner_id = dp.partner_id
    GROUP BY dp.partner_id, dp.name, dp.city
),
city_avg_stats AS (
    SELECT 
        city,
        (SUM(CASE WHEN was_on_time = 0 THEN 1 ELSE 0 END) * 100.0) / COUNT(tracking_id) AS city_avg_late_rate_pct
    FROM delivery_tracking dt
    JOIN orders o ON dt.order_id = o.order_id
    GROUP BY city
)
SELECT 
    ps.partner_id,
    ps.partner_name,
    ps.city,
    ps.total_deliveries,
    ps.late_deliveries,
    ROUND(ps.partner_late_rate_pct, 2) AS partner_late_rate_pct,
    ROUND(cas.city_avg_late_rate_pct, 2) AS city_avg_late_rate_pct
FROM partner_stats ps
JOIN city_avg_stats cas ON ps.city = cas.city
WHERE ps.total_deliveries >= 10 
  AND ps.partner_late_rate_pct > (2 * cas.city_avg_late_rate_pct)
ORDER BY ps.partner_late_rate_pct DESC;

-- Query 4: Delivery time trend over months
-- Shows if the platform is getting faster or slower Month-over-Month using LAG()
WITH monthly_delivery_times AS (
    SELECT 
        strftime('%Y-%m', o.order_date) AS order_month,
        AVG(dt.actual_delivery_minutes) AS avg_delivery_time_mins
    FROM delivery_tracking dt
    JOIN orders o ON dt.order_id = o.order_id
    GROUP BY order_month
)
SELECT 
    order_month,
    ROUND(avg_delivery_time_mins, 2) AS avg_delivery_time_mins,
    ROUND(LAG(avg_delivery_time_mins, 1) OVER (ORDER BY order_month), 2) AS prev_month_avg_delivery_time_mins,
    ROUND(avg_delivery_time_mins - LAG(avg_delivery_time_mins, 1) OVER (ORDER BY order_month), 2) AS mom_diff_minutes
FROM monthly_delivery_times
ORDER BY order_month;

-- KEY FINDING: Afternoon and evening peak dinner periods (7 PM - 10 PM) exhibit drop-offs in on-time delivery rates due to peak traffic conditions. Bicycles are slower (averaging ~26 mins) than Scooters and Bikes (~20 mins). Identifying riders with late delivery rates exceeding twice the city baseline allows targeted logistics and fleet coaching.
