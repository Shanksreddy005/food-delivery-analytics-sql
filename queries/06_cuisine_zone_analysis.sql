-- BUSINESS QUESTION: Which cuisines dominate which zones and what are the untapped opportunities?

-- Query 1: Top 3 cuisines by order volume per city using RANK()
WITH city_cuisine_volume AS (
    SELECT 
        o.city,
        CASE 
            WHEN instr(r.food_type, ',') > 0 THEN substr(r.food_type, 1, instr(r.food_type, ',') - 1) 
            ELSE r.food_type 
        END AS cuisine_type,
        COUNT(o.order_id) AS order_volume
    FROM orders o
    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    WHERE o.order_status = 'Delivered'
    GROUP BY o.city, cuisine_type
),
ranked_city_cuisines AS (
    SELECT 
        city,
        cuisine_type,
        order_volume,
        RANK() OVER (PARTITION BY city ORDER BY order_volume DESC) AS cuisine_rank
    FROM city_cuisine_volume
)
SELECT 
    city,
    cuisine_rank,
    cuisine_type,
    order_volume
FROM ranked_city_cuisines
WHERE cuisine_rank <= 3
ORDER BY city, cuisine_rank;

-- Query 2: Cuisine performance by time of day
-- Categorizes orders into Breakfast/Lunch/Dinner/Late Night and finds the top cuisine for each.
WITH hourly_cuisines AS (
    SELECT 
        CASE 
            WHEN CAST(strftime('%H', o.order_time) AS INTEGER) BETWEEN 6 AND 10 THEN '1_Breakfast (6am-11am)'
            WHEN CAST(strftime('%H', o.order_time) AS INTEGER) BETWEEN 11 AND 15 THEN '2_Lunch (11am-4pm)'
            WHEN CAST(strftime('%H', o.order_time) AS INTEGER) BETWEEN 16 AND 21 THEN '3_Dinner (4pm-10pm)'
            ELSE '4_Late Night (10pm-6am)'
        END AS time_bucket,
        CASE 
            WHEN instr(r.food_type, ',') > 0 THEN substr(r.food_type, 1, instr(r.food_type, ',') - 1) 
            ELSE r.food_type 
        END AS cuisine_type,
        COUNT(o.order_id) AS order_count
    FROM orders o
    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    WHERE o.order_status = 'Delivered'
    GROUP BY time_bucket, cuisine_type
),
ranked_hourly_cuisines AS (
    SELECT 
        time_bucket,
        cuisine_type,
        order_count,
        RANK() OVER (PARTITION BY time_bucket ORDER BY order_count DESC) AS rnk
    FROM hourly_cuisines
)
SELECT 
    time_bucket,
    cuisine_type,
    order_count
FROM ranked_hourly_cuisines
WHERE rnk = 1
ORDER BY time_bucket;

-- Query 3: Cities where the top cuisine has less than 40% market share
-- Indicates highly fragmented markets with high potential for new cuisine entrants.
WITH city_cuisine_shares AS (
    SELECT 
        o.city,
        CASE 
            WHEN instr(r.food_type, ',') > 0 THEN substr(r.food_type, 1, instr(r.food_type, ',') - 1) 
            ELSE r.food_type 
        END AS cuisine_type,
        COUNT(o.order_id) AS cuisine_orders,
        SUM(COUNT(o.order_id)) OVER (PARTITION BY o.city) AS city_total_orders
    FROM orders o
    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    WHERE o.order_status = 'Delivered'
    GROUP BY o.city, cuisine_type
),
top_cuisine_share AS (
    SELECT 
        city,
        cuisine_type,
        cuisine_orders,
        city_total_orders,
        ROUND((cuisine_orders * 100.0) / city_total_orders, 2) AS market_share_pct,
        RANK() OVER (PARTITION BY city ORDER BY cuisine_orders DESC) AS rnk
    FROM city_cuisine_shares
)
SELECT 
    city,
    cuisine_type AS top_cuisine,
    cuisine_orders,
    city_total_orders,
    market_share_pct
FROM top_cuisine_share
WHERE rnk = 1 AND market_share_pct < 40.0
ORDER BY market_share_pct ASC;

-- KEY FINDING: South Indian cuisines dominate breakfast tables (~45% share), whereas Biryani/North Indian peak during lunch and dinner. Fragmented markets such as Mumbai and Kolkata have top cuisine market shares well below 40%, leaving huge room for scaling regional cuisines.
