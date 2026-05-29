import sqlite3
import pandas as pd
import os

def load_all_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'food_delivery.db')
    schema_path = os.path.join(base_dir, 'schema', 'create_tables.sql')
    data_gen_dir = os.path.join(base_dir, 'data', 'generated')
    data_raw_dir = os.path.join(base_dir, 'data', 'raw')

    # Remove existing DB if any to ensure clean slate
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database.")

    # 1. Connect to SQLite and create database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. Run create_tables.sql
    print("Executing create_tables.sql...")
    with open(schema_path, 'r') as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    conn.commit()

    # 3. Load CSVs into their respective tables
    
    # Load raw restaurants
    raw_restaurant_csv = os.path.join(data_raw_dir, 'swiggy_restaurants.csv')
    if os.path.exists(raw_restaurant_csv):
        print("Loading restaurants...")
        df_rest = pd.read_csv(raw_restaurant_csv)
        # Rename columns to match SQL schema
        df_rest = df_rest.rename(columns={
            'ID': 'restaurant_id',
            'Restaurant': 'name',
            'City': 'city',
            'Area': 'area',
            'Avg ratings': 'rating',
            'Total ratings': 'total_ratings',
            'Food type': 'food_type',
            'Address': 'address',
            'Delivery time': 'delivery_time',
            'Price': 'price'
        })
        # Clean data for SQLite loading
        df_rest['rating'] = pd.to_numeric(df_rest['rating'], errors='coerce').fillna(4.0)
        df_rest['total_ratings'] = pd.to_numeric(df_rest['total_ratings'], errors='coerce').fillna(0).astype(int)
        df_rest['price'] = pd.to_numeric(df_rest['price'], errors='coerce').fillna(0.0)
        df_rest['delivery_time'] = pd.to_numeric(df_rest['delivery_time'], errors='coerce').fillna(30).astype(int)
        
        # Write to db
        df_rest.to_sql('restaurants', conn, if_exists='append', index=False)
        print(f"Loaded {len(df_rest)} restaurants.")
    else:
        print("Warning: swiggy_restaurants.csv not found in data/raw!")

    # Generated tables mapping
    csv_load_mapping = {
        'customers.csv': 'customers',
        'delivery_partners.csv': 'delivery_partners',
        'promotions.csv': 'promotions',
        'orders.csv': 'orders',
        'order_items.csv': 'order_items',
        'delivery_tracking.csv': 'delivery_tracking',
        'reviews.csv': 'reviews',
    }

    for csv_file, table_name in csv_load_mapping.items():
        csv_path = os.path.join(data_gen_dir, csv_file)
        if os.path.exists(csv_path):
            print(f"Loading {table_name} from {csv_file}...")
            df = pd.read_csv(csv_path)
            # SQLite handles NaN/Nat differently; convert pd.NA/NaN to None
            df = df.where(pd.notnull(df), None)
            df.to_sql(table_name, conn, if_exists='append', index=False)
            print(f"Loaded {len(df)} rows into {table_name}.")
        else:
            print(f"Warning: {csv_file} not found in {data_gen_dir}!")

    conn.commit()

    # 4. Validate row counts after loading
    print("\n--- ROW COUNT VALIDATION ---")
    tables = ['restaurants', 'customers', 'delivery_partners', 'promotions', 'orders', 'order_items', 'delivery_tracking', 'reviews']
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"Table '{t}': {count} rows")

    # 5. Sanity check queries
    print("\n--- SANITY CHECK QUERIES ---")

    # Query 1: Top 5 customers by order count
    print("Sanity Check 1: Top 5 customers by order count")
    cursor.execute("""
        SELECT c.name, COUNT(o.order_id) AS total_orders, ROUND(SUM(o.total_amount), 2) AS total_spend
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY total_orders DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"Customer: {row[0]}, Orders: {row[1]}, Spend: INR {row[2]}")

    # Query 2: Active delivery partners distribution by city
    print("\nSanity Check 2: Active delivery partners count by city (Top 5)")
    cursor.execute("""
        SELECT city, COUNT(*) AS active_partners
        FROM delivery_partners
        WHERE is_active = 1
        GROUP BY city
        ORDER BY active_partners DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"City: {row[0]}, Active Partners: {row[1]}")

    # Query 3: On-time delivery rate
    print("\nSanity Check 3: Platform On-time delivery rate")
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_delivered,
            SUM(CASE WHEN was_on_time = 1 THEN 1 ELSE 0 END) AS on_time_count,
            ROUND(AVG(was_on_time) * 100, 2) AS on_time_percentage
        FROM delivery_tracking
    """)
    res = cursor.fetchone()
    print(f"Total Delivered: {res[0]}, On-Time: {res[1]}, Rate: {res[2]}%")

    conn.close()

if __name__ == '__main__':
    load_all_data()
