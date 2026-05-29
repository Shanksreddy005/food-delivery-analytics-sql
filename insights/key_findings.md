# Key Business Findings — Food Delivery Platform SQL Analysis

This document contains plain-English interpretations of the most important findings derived from the 10 SQL analysis modules run on the `food_delivery.db` SQLite database.

---

## 1. Restaurant Performance

**Finding:** The platform follows a heavy power-law distribution in restaurant performance. The top 25% of restaurants (classified as "Platinum" tier) generate over 60% of total GMV. However, 10–15 high-volume restaurants maintain average ratings below 3.5, creating a tension between volume and quality that risks long-term customer trust.

**Implication:** The platform should prioritize quality intervention programmes for high-volume, low-rated restaurants before they erode the customer base that drives the platform's core revenue.

---

## 2. Customer Behaviour & RFM Segmentation

**Finding:** Over 70% of active customers fall into the "Champions" or "Loyal" RFM tiers based on their recency, order frequency, and spending. Early cohorts (customers who registered in Q1–Q2 2021) show the highest customer lifetime value (LTV) of INR 4,000+ per customer over the 2-year analysis window.

**Implication:** Retaining the existing loyal base is significantly more cost-effective than new acquisition. Cohort analysis confirms that customers who order more than 3 times in their first 90 days become high-value lifetime users.

---

## 3. Delivery Analytics

**Finding:** The platform's overall on-time delivery rate is 85.52%, comfortably above the 75% industry benchmark. However, the average delivery time rises by 30–40% during peak dinner hours (7–10 PM), specifically on Fridays and Saturdays. Bicycles average 26 mins vs 20 mins for bikes and scooters.

**Implication:** Targeted surge capacity management — especially for weekends and peak hours — combined with phasing out bicycle assignments for longer-distance deliveries, could close the on-time gap further towards 90%+.

---

## 4. Revenue Analysis

**Finding:** Monthly GMV has grown consistently at 4–6% MoM across the 24-month dataset, reaching a cumulative GMV of INR 333.2M. Kolkata is the highest-revenue city (INR 52.8M), followed by Mumbai (INR 47.6M) and Chennai (INR 45.2M). These three cities alone account for ~44% of total platform GMV.

**Implication:** Revenue concentration in a handful of cities is a strategic risk. The platform should prioritise restaurant supply growth and marketing investment in Tier-2 cities like Ahmedabad and Surat to reduce concentration risk.

---

## 5. Promotion Effectiveness

**Finding:** Promotional orders (30% of all orders) generate an average subtotal 7% higher than non-promotional orders, suggesting users actively inflate cart sizes to hit the minimum order threshold for discounts. The 90-day repeat rate for customers whose first order was promotional is 57.5%, vs 41% for non-promotional first-timers.

**Implication:** Promotions are not just discount spend — they are a high-ROI customer acquisition channel that generates sticky long-term users. The platform should invest more in first-order promo campaigns in cities with low organic acquisition.

---

## 6. Cuisine & Zone Analysis

**Finding:** North Indian and Biryani collectively account for 50%+ market share in every top-5 city. South Indian food dominates morning/breakfast orders while Biryani peaks at lunch and dinner. Multiple cities including Kolkata and Mumbai have top-cuisine market shares below 40%, indicating fragmented markets.

**Implication:** Cities with fragmented cuisine markets are high-opportunity zones for regional cuisine restaurant onboarding. A focused supply-side campaign to bring Bengali or Mughlai restaurants onto the platform in Kolkata could capture an underserved demand segment.

---

## 7. Time Pattern Analysis

**Finding:** Order volumes show twin daily peaks: 12–2 PM (lunch) and 7–10 PM (dinner). Weekend daily order volume is ~38% higher than the weekday baseline. Cancellation rates on weekends increase by ~1.5 percentage points, suggesting delivery fleet constraints during high-volume periods.

**Implication:** Fleet incentive programmes during predicted peak hours and pre-positioning delivery partners in high-density zones before the demand spike can significantly reduce weekend cancellations and improve capacity utilisation.

---

## 8. Churn Analysis

**Finding:** Customers who ordered in the first 90 days of joining but have been inactive for 60+ days show two consistent precursors: their last order delivery time was ~30% longer than the platform average, and their last order rating was 3.2 vs 4.1 for retained customers. Low promo usage also correlates with higher churn probability.

**Implication:** A predictive churn model using these three features (delivery time, last rating, promo usage rate) can be built to identify at-risk customers 2–4 weeks before they reach the 60-day inactive threshold, enabling proactive re-engagement campaigns.

---

## 9. Delivery Partner Performance

**Finding:** Top decile (10%) delivery partners deliver 88%+ on time and average 18-minute delivery windows. Bottom decile partners average 28+ minutes with on-time rates below 65%. This performance gap directly correlates with customer delivery ratings — partners in the bottom decile receive average ratings of 3.1 vs 4.4 for the top decile.

**Implication:** Structured partner coaching programmes, targeted at the bottom 20%, with a focus on route efficiency and peak-hour preparation, could raise the platform's average on-time rate from 85.5% to above 88% within 2 quarters.

---

## 10. Executive Summary

**Finding (Platform Health Dashboard):**
- Total Delivered Orders: 425,644
- Total Platform GMV: INR 333.2M
- Average Order Value: INR 783
- Platform On-Time Rate: 85.52%
- Average Overall Rating: ~4.1
- Active Customers: 48,000+
- Active Delivery Partners: 1,800+

The single most critical operational bottleneck identified is late-night (10 PM–12 AM) orders in high-density cities for popular cuisines — these show the highest cancellation rates (18%+) and the longest average delivery times, driven by fleet shortage in the late shift window.
