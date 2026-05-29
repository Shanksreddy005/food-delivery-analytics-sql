import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

def generate_data():
    # Setup directories
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    gen_dir = os.path.join(base_dir, 'data', 'generated')
    os.makedirs(gen_dir, exist_ok=True)
    
    # 1. Load real Swiggy CSV data
    try:
        restaurants_df = pd.read_csv(os.path.join(raw_dir, 'swiggy_restaurants.csv'))
        # Using ID as restaurant_id and City
        if 'ID' in restaurants_df.columns:
            restaurants_df['restaurant_id'] = restaurants_df['ID']
        else:
            restaurants_df['restaurant_id'] = range(1, len(restaurants_df) + 1)
        
        if 'City' not in restaurants_df.columns:
            restaurants_df['City'] = 'Bangalore'
            
        real_cities = restaurants_df['City'].unique().tolist()
        restaurant_ids = restaurants_df['restaurant_id'].tolist()
        
        # We also need rating for generating correlation
        if 'Avg ratings' in restaurants_df.columns:
            restaurants_df['rating'] = pd.to_numeric(restaurants_df['Avg ratings'], errors='coerce').fillna(4.0)
        else:
            restaurants_df['rating'] = 4.0
            
    except FileNotFoundError:
        print("swiggy_restaurants.csv not found in data/raw/. Using dummy data.")
        real_cities = ['Bangalore', 'Mumbai', 'Delhi', 'Chennai', 'Hyderabad']
        restaurant_ids = list(range(1, 1001))
        restaurants_df = pd.DataFrame({'restaurant_id': restaurant_ids, 'City': np.random.choice(real_cities, 1000), 'rating': np.random.uniform(3.0, 5.0, 1000)})

    try:
        menu_df = pd.read_csv(os.path.join(raw_dir, 'swiggy_menu.csv'))
        menu_items = menu_df['menu_item'].dropna().unique().tolist() if 'menu_item' in menu_df.columns else ['Biryani', 'Pizza', 'Burger', 'Dosa', 'Noodles', 'Paneer Butter Masala', 'Cold Coffee', 'Fries']
    except FileNotFoundError:
        print("swiggy_menu.csv not found in data/raw/. Using dummy data.")
        menu_items = ['Biryani', 'Pizza', 'Burger', 'Dosa', 'Noodles', 'Paneer Butter Masala', 'Cold Coffee', 'Fries', 'Tandoori Chicken', 'Naan', 'Pasta', 'Salad']

    # 3. Generate tables
    
    # --- CUSTOMERS TABLE (50,000 rows) ---
    print("Generating Customers...")
    num_customers = 50000
    first_names = ['Rahul', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Neha', 'Rohan', 'Pooja', 'Karan', 'Anjali', 'Arjun', 'Riya', 'Aditya', 'Shruti', 'Sanjay', 'Kavita']
    last_names = ['Sharma', 'Verma', 'Gupta', 'Patel', 'Singh', 'Kumar', 'Jain', 'Shah', 'Reddy', 'Rao', 'Nair', 'Menon']
    areas = ['Koramangala', 'Indiranagar', 'Andheri', 'Bandra', 'Connaught Place', 'Hauz Khas', 'T Nagar', 'Adyar', 'Banjara Hills', 'Jubilee Hills']
    
    customer_ids = range(1, num_customers + 1)
    c_names = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(num_customers)]
    c_cities = np.random.choice(real_cities, num_customers)
    c_areas = np.random.choice(areas, num_customers)
    c_phones = [f"{random.choice(['6','7','8','9'])}{''.join([str(random.randint(0,9)) for _ in range(9)])}" for _ in range(num_customers)]
    c_emails = [f"{n.replace(' ','').lower()}{random.randint(1,999)}@gmail.com" for n in c_names]
    
    # Registration dates between 2021-01-01 and 2024-01-01
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 1, 1)
    days_between = (end_date - start_date).days
    c_reg_dates = [start_date + timedelta(days=random.randint(0, days_between)) for _ in range(num_customers)]
    
    c_ages = np.random.randint(18, 56, num_customers)
    c_genders = np.random.choice(['M', 'F', 'Other'], num_customers, p=[0.55, 0.40, 0.05])
    
    def get_loyalty_tier(reg_date):
        age_days = (end_date - reg_date).days
        if age_days < 180: return 'Bronze'
        elif age_days < 365: return 'Silver'
        elif age_days < 730: return 'Gold'
        else: return 'Platinum'
        
    c_loyalty = [get_loyalty_tier(d) for d in c_reg_dates]
    
    customers = pd.DataFrame({
        'customer_id': customer_ids,
        'name': c_names,
        'city': c_cities,
        'area': c_areas,
        'phone': c_phones,
        'email': c_emails,
        'registration_date': [d.strftime('%Y-%m-%d') for d in c_reg_dates],
        'age': c_ages,
        'gender': c_genders,
        'loyalty_tier': c_loyalty
    })
    customers.to_csv(os.path.join(gen_dir, 'customers.csv'), index=False)
    
    # --- DELIVERY PARTNERS TABLE (2,000 rows) ---
    print("Generating Delivery Partners...")
    num_partners = 2000
    p_names = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(num_partners)]
    p_cities = np.random.choice(real_cities, num_partners)
    p_vehicles = np.random.choice(['Bike', 'Scooter', 'Bicycle'], num_partners, p=[0.7, 0.2, 0.1])
    
    p_ratings = np.clip(np.random.normal(4.2, 0.4, num_partners), 3.0, 5.0).round(1)
    
    p_start = datetime(2020, 1, 1)
    p_end = datetime(2024, 1, 1)
    p_days = (p_end - p_start).days
    p_joined = [p_start + timedelta(days=random.randint(0, p_days)) for _ in range(num_partners)]
    
    p_active = np.random.choice([True, False], num_partners, p=[0.9, 0.1])
    
    p_deliveries = []
    for d in p_joined:
        days_active = (datetime(2024,1,1) - d).days
        p_deliveries.append(int(days_active * random.uniform(1.5, 3.5)))
        
    partners = pd.DataFrame({
        'partner_id': range(1, num_partners + 1),
        'name': p_names,
        'city': p_cities,
        'vehicle_type': p_vehicles,
        'rating': p_ratings,
        'joined_date': [d.strftime('%Y-%m-%d') for d in p_joined],
        'is_active': p_active,
        'total_deliveries': p_deliveries
    })
    partners.to_csv(os.path.join(gen_dir, 'delivery_partners.csv'), index=False)
    
    # --- PROMOTIONS TABLE (50 rows) ---
    print("Generating Promotions...")
    num_promos = 50
    promo_types = np.random.choice(['percentage', 'flat'], num_promos)
    promo_values = [random.randint(10, 50) if t == 'percentage' else random.randint(30, 100) for t in promo_types]
    
    promo_start = datetime(2022, 1, 1)
    promo_end = datetime(2023, 1, 1)
    pr_days = (promo_end - promo_start).days
    
    valid_froms = [promo_start + timedelta(days=random.randint(0, pr_days)) for _ in range(num_promos)]
    valid_tos = [d + timedelta(days=180) for d in valid_froms]
    
    promotions = pd.DataFrame({
        'promo_id': range(1, num_promos + 1),
        'promo_code': [f"PROMO{i:02d}{chr(random.randint(65,90))}" for i in range(1, num_promos + 1)],
        'discount_type': promo_types,
        'discount_value': promo_values,
        'min_order_value': np.random.randint(0, 301, num_promos),
        'valid_from': [d.strftime('%Y-%m-%d') for d in valid_froms],
        'valid_to': [d.strftime('%Y-%m-%d') for d in valid_tos],
        'max_uses': np.random.randint(500, 5001, num_promos)
    })
    promotions.to_csv(os.path.join(gen_dir, 'promotions.csv'), index=False)
    
    # --- ORDERS TABLE (500,000 rows) ---
    print("Generating Orders...")
    num_orders = 500000
    
    rest_probs = restaurants_df['rating'].values ** 2
    rest_probs = rest_probs / rest_probs.sum()
    
    o_customer_ids = np.random.choice(customers['customer_id'], num_orders)
    
    o_rest_idx = np.random.choice(len(restaurants_df), num_orders, p=rest_probs)
    o_restaurant_ids = restaurants_df.iloc[o_rest_idx]['restaurant_id'].values
    o_cities = restaurants_df.iloc[o_rest_idx]['City'].values
    
    o_partner_ids = np.random.choice(partners['partner_id'], num_orders)
    
    o_promos = np.random.choice([None] + list(promotions['promo_id']), num_orders, p=[0.7] + [0.3/num_promos]*num_promos)
    
    o_start = datetime(2022, 1, 1)
    o_end = datetime(2024, 1, 1)
    o_days = (o_end - o_start).days
    
    o_dates_obj = [o_start + timedelta(days=random.randint(0, o_days)) for _ in range(num_orders)]
    o_dates = [d.strftime('%Y-%m-%d') for d in o_dates_obj]
    
    def get_time():
        hour = np.random.choice([
            *range(0, 11), *range(11, 15), *range(15, 18), *range(18, 23), 23
        ], p=[
            *(0.01 for _ in range(11)), *(0.1 for _ in range(4)), *(0.02 for _ in range(3)), *(0.08 for _ in range(5)), 0.03
        ])
        minute = random.randint(0, 59)
        return f"{hour:02d}:{minute:02d}:00", hour
        
    o_times_and_hours = [get_time() for _ in range(num_orders)]
    o_times = [t[0] for t in o_times_and_hours]
    o_hours = [t[1] for t in o_times_and_hours]
    
    o_status = np.random.choice(['Delivered', 'Cancelled', 'Returned', 'Failed'], num_orders, p=[0.85, 0.08, 0.04, 0.03])
    o_subtotals = np.random.randint(150, 1501, num_orders)
    
    o_discounts = np.zeros(num_orders)
    for i in range(num_orders):
        if pd.notna(o_promos[i]):
            pid = o_promos[i]
            promo_row = promotions[promotions['promo_id'] == pid].iloc[0]
            if o_subtotals[i] >= promo_row['min_order_value']:
                if promo_row['discount_type'] == 'percentage':
                    o_discounts[i] = round(o_subtotals[i] * (promo_row['discount_value'] / 100), 2)
                else:
                    o_discounts[i] = promo_row['discount_value']
    
    o_delivery_fees = np.where(o_subtotals > 500, 0, np.random.randint(20, 81, num_orders))
    o_total_amounts = o_subtotals - o_discounts + o_delivery_fees
    o_total_amounts = np.maximum(0, o_total_amounts)
    
    o_payments = np.random.choice(['UPI', 'Card', 'COD', 'Wallet'], num_orders, p=[0.45, 0.25, 0.20, 0.10])
    
    orders = pd.DataFrame({
        'order_id': range(1, num_orders + 1),
        'customer_id': o_customer_ids,
        'restaurant_id': o_restaurant_ids,
        'partner_id': o_partner_ids,
        'promo_id': o_promos,
        'order_date': o_dates,
        'order_time': o_times,
        'order_status': o_status,
        'subtotal': o_subtotals,
        'discount_amount': o_discounts,
        'delivery_fee': o_delivery_fees,
        'total_amount': o_total_amounts,
        'payment_method': o_payments,
        'city': o_cities
    })
    orders.to_csv(os.path.join(gen_dir, 'orders.csv'), index=False)
    
    # --- ORDER_ITEMS TABLE (approx 1.5M rows) ---
    print("Generating Order Items...")
    items_per_order = np.random.randint(1, 5, num_orders)
    total_items = items_per_order.sum()
    
    oi_order_ids = np.repeat(orders['order_id'].values, items_per_order)
    oi_menu_names = np.random.choice(menu_items, total_items)
    oi_quantities = np.random.randint(1, 5, total_items)
    oi_unit_prices = np.random.randint(50, 401, total_items)
    
    order_items = pd.DataFrame({
        'item_id': range(1, total_items + 1),
        'order_id': oi_order_ids,
        'menu_item_name': oi_menu_names,
        'quantity': oi_quantities,
        'unit_price': oi_unit_prices,
        'total_price': oi_quantities * oi_unit_prices
    })
    order_items.to_csv(os.path.join(gen_dir, 'order_items.csv'), index=False)
    
    # --- DELIVERY_TRACKING TABLE (delivered orders only) ---
    print("Generating Delivery Tracking...")
    delivered_mask = orders['order_status'] == 'Delivered'
    delivered_orders = orders[delivered_mask]
    num_delivered = len(delivered_orders)
    
    dt_order_ids = delivered_orders['order_id'].values
    dt_partner_ids = delivered_orders['partner_id'].values
    
    pickup_delays = np.random.randint(3, 10, num_delivered)
    delivery_durations = np.random.randint(12, 35, num_delivered)
    
    delivered_hours = np.array([int(t.split(':')[0]) for t in delivered_orders['order_time'].values])
    peak_mask = (delivered_hours >= 12) & (delivered_hours <= 14) | (delivered_hours >= 19) & (delivered_hours <= 21)
    delivery_durations[peak_mask] += np.random.randint(5, 12, peak_mask.sum())
    
    dt_distances = np.round(np.random.uniform(1.0, 8.0, num_delivered), 1)
    dt_promised = np.random.choice([30, 35, 40, 45], num_delivered)
    dt_was_on_time = delivery_durations <= dt_promised
    
    dt_pickup_times = []
    dt_delivery_times = []
    
    for i, t_str in enumerate(delivered_orders['order_time'].values):
        base_time = datetime.strptime(t_str, "%H:%M:%S")
        pickup = base_time + timedelta(minutes=int(pickup_delays[i]))
        delivery = pickup + timedelta(minutes=int(delivery_durations[i]))
        dt_pickup_times.append(pickup.strftime("%H:%M:%S"))
        dt_delivery_times.append(delivery.strftime("%H:%M:%S"))
        
    delivery_tracking = pd.DataFrame({
        'tracking_id': range(1, num_delivered + 1),
        'order_id': dt_order_ids,
        'partner_id': dt_partner_ids,
        'pickup_time': dt_pickup_times,
        'delivery_time': dt_delivery_times,
        'distance_km': dt_distances,
        'actual_delivery_minutes': delivery_durations,
        'promised_delivery_minutes': dt_promised,
        'was_on_time': dt_was_on_time
    })
    delivery_tracking.to_csv(os.path.join(gen_dir, 'delivery_tracking.csv'), index=False)
    
    # --- REVIEWS TABLE (60% of delivered orders) ---
    print("Generating Reviews...")
    num_reviews = int(num_delivered * 0.6)
    review_indices = np.random.choice(num_delivered, num_reviews, replace=False)
    
    rev_orders = delivered_orders.iloc[review_indices]
    
    r_food_ratings = np.clip(np.random.normal(4.2, 0.8, num_reviews), 1, 5).astype(int)
    r_delivery_ratings = np.clip(np.random.normal(4.0, 1.0, num_reviews), 1, 5).astype(int)
    
    r_review_dates = []
    for d_str in rev_orders['order_date'].values:
        d = datetime.strptime(d_str, "%Y-%m-%d") + timedelta(days=random.randint(1,3))
        r_review_dates.append(d.strftime("%Y-%m-%d"))
        
    reviews = pd.DataFrame({
        'review_id': range(1, num_reviews + 1),
        'order_id': rev_orders['order_id'].values,
        'customer_id': rev_orders['customer_id'].values,
        'restaurant_id': rev_orders['restaurant_id'].values,
        'partner_id': rev_orders['partner_id'].values,
        'food_rating': r_food_ratings,
        'delivery_rating': r_delivery_ratings,
        'overall_rating': (r_food_ratings + r_delivery_ratings) / 2.0,
        'review_date': r_review_dates,
        'has_text_review': np.random.choice([True, False], num_reviews, p=[0.3, 0.7])
    })
    reviews.to_csv(os.path.join(gen_dir, 'reviews.csv'), index=False)
    
    print("\n--- DATA GENERATION SUMMARY ---")
    print(f"Customers: {len(customers)} rows")
    print(f"Delivery Partners: {len(partners)} rows")
    print(f"Promotions: {len(promotions)} rows")
    print(f"Orders: {len(orders)} rows")
    print(f"Order Items: {len(order_items)} rows")
    print(f"Delivery Tracking: {len(delivery_tracking)} rows")
    print(f"Reviews: {len(reviews)} rows")
    print(f"Order Dates: {orders['order_date'].min()} to {orders['order_date'].max()}")
    print(f"Cities: {orders['city'].nunique()} distinct cities")
    print(f"Avg Order Value: {orders['total_amount'].mean():.2f}")
    
if __name__ == '__main__':
    generate_data()
