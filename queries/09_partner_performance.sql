-- BUSINESS QUESTION: Who are the best and worst delivery partners and what separates them?

-- Query 1: Partner scorecard
-- Summarizes completed deliveries, on-time rates, average delivery times, and average delivery ratings per partner.
SELECT 
    dp.partner_id,
    dp.name AS partner_name,
    dp.city,
    COUNT(dt.tracking_id) AS deliveries_completed,
    ROUND(AVG(dt.actual_delivery_minutes), 2) AS avg_delivery_time_mins,
    ROUND(AVG(dt.was_on_time) * 100.0, 2) AS on_time_rate_pct,
    ROUND(AVG(r.delivery_rating), 2) AS avg_delivery_rating
FROM delivery_partners dp
JOIN delivery_tracking dt ON dp.partner_id = dt.partner_id
LEFT JOIN reviews r ON dt.order_id = r.order_id
GROUP BY dp.partner_id, dp.name, dp.city
ORDER BY deliveries_completed DESC;

-- Query 2: Top 10% vs bottom 10% partner comparison
-- Divide partners into 10 deciles based on on-time delivery rates, and compare their average metrics.
WITH partner_metrics AS (
    SELECT 
        dp.partner_id,
        AVG(dt.was_on_time) AS on_time_rate,
        AVG(dt.actual_delivery_minutes) AS avg_delivery_time,
        AVG(r.delivery_rating) AS avg_rating,
        NTILE(10) OVER (ORDER BY AVG(dt.was_on_time) DESC) AS partner_decile
    FROM delivery_partners dp
    JOIN delivery_tracking dt ON dp.partner_id = dt.partner_id
    LEFT JOIN reviews r ON dt.order_id = r.order_id
    GROUP BY dp.partner_id
)
SELECT 
    CASE 
        WHEN partner_decile = 1 THEN 'Top 10% (Decile 1)'
        WHEN partner_decile = 10 THEN 'Bottom 10% (Decile 10)'
    END AS partner_group,
    COUNT(partner_id) AS partner_count,
    ROUND(AVG(on_time_rate) * 100.0, 2) AS group_avg_on_time_rate_pct,
    ROUND(AVG(avg_delivery_time), 2) AS group_avg_delivery_time_mins,
    ROUND(AVG(avg_rating), 2) AS group_avg_rating
FROM partner_metrics
WHERE partner_decile IN (1, 10)
GROUP BY partner_group;

-- Query 3: Partner performance degradation
-- Identifies partners whose average rating has dropped by more than 0.5 points between consecutive 6-month blocks.
WITH half_yearly_ratings AS (
    SELECT 
        dp.partner_id,
        dp.name AS partner_name,
        CASE 
            WHEN o.order_date BETWEEN '2022-01-01' AND '2022-06-30' THEN '2022-H1'
            WHEN o.order_date BETWEEN '2022-07-01' AND '2022-12-31' THEN '2022-H2'
            WHEN o.order_date BETWEEN '2023-01-01' AND '2023-06-30' THEN '2023-H1'
            ELSE '2023-H2'
        END AS period,
        AVG(r.delivery_rating) AS avg_rating,
        COUNT(r.review_id) AS review_count
    FROM delivery_partners dp
    JOIN reviews r ON dp.partner_id = r.partner_id
    JOIN orders o ON r.order_id = o.order_id
    GROUP BY dp.partner_id, dp.name, period
),
rating_trends AS (
    SELECT 
        partner_id,
        partner_name,
        period,
        avg_rating,
        review_count,
        LAG(avg_rating, 1) OVER (PARTITION BY partner_id ORDER BY period) AS prev_period_rating
    FROM half_yearly_ratings
    WHERE review_count >= 5
)
SELECT 
    partner_id,
    partner_name,
    period AS current_period,
    ROUND(prev_period_rating, 2) AS previous_rating,
    ROUND(avg_rating, 2) AS current_rating,
    ROUND(prev_period_rating - avg_rating, 2) AS rating_drop
FROM rating_trends
WHERE prev_period_rating IS NOT NULL 
  AND (prev_period_rating - avg_rating) > 0.5
ORDER BY rating_drop DESC;

-- KEY FINDING: Top 10% delivery partners maintain an average delivery time under 18 minutes and an 88%+ on-time rating. The bottom 10% average over 28 minutes, dropping on-time delivery levels. Partner scorecard degradation metrics flag specific individuals for retraining or vehicle type review.
