# Executive Case Study – Food Delivery Platform Analytics

## Page 1

### Executive Summary
The platform generated **GMV of INR 333.2 M** across **425,644 delivered orders** in the 24‑month period (2022‑2024). Growth was steady at **4‑6 % MoM**, driven primarily by high‑volume cities (Kolkata, Mumbai, Chennai). Key performance metrics and insights are distilled for senior leadership.

### Business Problem
Deliver a data‑driven assessment of platform health, identify operational bottlenecks, and surface high‑impact growth opportunities for a leading Indian food‑delivery player.

### Business Context
- Marketplace with 9‑table relational schema covering customers, restaurants, orders, deliveries, promotions, and reviews.
- Synthetic dataset of ~2.5 M records augmented with real‑world Swiggy restaurant data.
- Analytic stack: **Python (Pandas, NumPy), SQLite, SQL (CTEs, window functions), Tableau/Matplotlib visualisations**.

### Objectives
1. Quantify core KPIs (GMV, Revenue, AOV, Retention, Churn, CLV, etc.).
2. Diagnose drivers of revenue concentration and delivery performance.
3. Evaluate promotion effectiveness and customer lifecycle.
4. Produce actionable recommendations for the product and operations teams.

### Dataset Overview
- **Orders**: 500 k rows; **Order Items**: ~1.25 M rows.
- **Restaurants**: 8.7 k entries (Kaggle).
- **Customers**: 50 k synthetic profiles.
- **Delivery Partners**: 2 k synthetic fleet.
- **Promotions**: 50 codes.
- **Menu**: 65 k items.

### KPI Definitions
- **GMV (Gross Merchandise Value)** – Total value of all goods sold on the platform (subtotal + delivery fee + taxes). 
- **Revenue** – Platform‑earned amount after commissions, fees, and promotion discounts. 
- **Average Order Value (AOV)** – Mean subtotal per order (GMV ÷ number of orders). 
- **Repeat Purchase Rate** – Percentage of customers who place a second order within 90 days of their first purchase. 
- **Customer Retention** – Share of customers who remain active (at least one order) in a subsequent period. 
- **Customer Churn** – Proportion of customers who become inactive for >60 days. 
- **Customer Lifetime Value (CLV)** – Cumulative net profit attributed to a customer over the analysis horizon. 
- **Promotion ROI** – Incremental revenue generated per rupee spent on promotions. 
- **Delivery Time** – Elapsed minutes from order placement to successful delivery. 
- **Cancellation Rate** – Fraction of placed orders that are cancelled before fulfilment.

### Key Findings
1. **Revenue Concentration** – Kolkata, Mumbai, Chennai contribute ~44 % of GMV. 
2. **Volume‑Quality Tension** – Top 25 % restaurants generate > 60 % GMV, yet 10‑15 high‑volume venues have ratings < 3.5. 
3. **Promotion Effectiveness** – Promo‑origin customers enjoy a **57.5 % repeat rate** vs 41 % for non‑promo customers. 
4. **Delivery Peaks** – Dinner peak (7‑10 PM) inflates average delivery time by **30‑40 %** and raises cancellation risk. 
5. **Partner Performance Gap** – Bottom decile partners deliver **28 + min** with on‑time < 65 % versus top decile **18 min** & 88 % on‑time.

### ONE Business Recommendation
**Implement a Volume‑Quality Recovery Programme** for high‑volume, low‑rated restaurants (rating < 3.5). 
- **Observation**: These restaurants drive > 60 % of GMV while jeopardising brand trust. 
- **Evidence**: Findings 1 & 2 show the rating‑volume mismatch and its potential to erode repeat purchase. 
- **Business Impact**: Safeguarding GMV from quality‑related churn could preserve up to **5‑7 %** of revenue annually.
- **Recommendation**: Mandate quarterly quality audits, introduce rating‑triggered support tickets, and provide targeted incentives for rating improvement.

---

## Page 2

### Data Quality Summary
- **Completeness**: > 99 % of mandatory fields populated; < 0.5 % nulls in key columns (order_id, customer_id, restaurant_id).
- **Validity**: All foreign‑key constraints satisfied; timestamps parsed with `strftime()`; monetary fields stored as INTEGER (cents).
- **Consistency**: Promotion flags align with discount_amount; delivery timestamps correlate with partner assignments.

### Analysis Methodology
- **SQL**: 10 analytical modules leveraging CTEs, window functions, ROLLUP emulation, and cohort analyses.
- **Python**: Data generation, loading, and visualisation pipelines (`pandas`, `matplotlib`, `seaborn`).
- **Tableau**: Dashboard prototypes (executive summary, city‑wise revenue, delivery heatmaps). 

### Supporting Visualisations
![Executive Summary](file:///c:/Users/ShaShank/OneDrive/Desktop/food-delivery-sql-analysis/case_study/executive_summary.png)

*Chart 1 – Monthly GMV Trend* (visualizations/chart1_monthly_revenue.png) 
*Chart 2 – On‑time Delivery Heatmap* (visualizations/chart3_delivery_heatmap.png)

### Limitations
- Synthetic customer/partner data may not capture real‑world behavioural nuances.
- Promotion impact measured on short‑term repeat rate; long‑term CLV effects require longer observation.
- No real‑time streaming data – analysis based on static snapshots.

### Next Steps
1. **Deploy real‑time KPI monitors** in Tableau for delivery latency and cancellation spikes.
2. **Pilot the Quality Recovery Programme** on a subset of Platinum restaurants and measure rating uplift.
3. **Extend churn model** with additional behavioural signals (app usage, push notifications).
4. **Scale restaurant onboarding** in emerging Tier‑2 markets (Ahmedabad, Surat) to diversify revenue.

---

*Prepared by the Data Analytics Team – Swiggy (internal case study)*
