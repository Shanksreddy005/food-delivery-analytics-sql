-- 1. RESTAURANTS TABLE
-- Represents the restaurants onboarded on the Swiggy platform.
CREATE TABLE restaurants (
    restaurant_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    area TEXT,
    rating REAL,
    total_ratings INTEGER,
    food_type TEXT,
    address TEXT,
    delivery_time INTEGER,
    price REAL
);

-- 2. MENU TABLE
-- Represents the menu items offered by the restaurants.
CREATE TABLE menu (
    menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    price REAL NOT NULL,
    veg_or_nonveg TEXT,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

-- 3. CUSTOMERS TABLE
-- Represents the customers registered on the platform.
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    area TEXT,
    phone TEXT NOT NULL,
    email TEXT,
    registration_date DATE NOT NULL,
    age INTEGER,
    gender TEXT,
    loyalty_tier TEXT NOT NULL
);

-- 4. DELIVERY_PARTNERS TABLE
-- Represents the delivery fleet partners.
CREATE TABLE delivery_partners (
    partner_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    vehicle_type TEXT NOT NULL,
    rating REAL,
    joined_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL,
    total_deliveries INTEGER NOT NULL
);

-- 5. PROMOTIONS TABLE
-- Represents promotional codes and discounts.
CREATE TABLE promotions (
    promo_id INTEGER PRIMARY KEY,
    promo_code TEXT NOT NULL UNIQUE,
    discount_type TEXT NOT NULL,
    discount_value REAL NOT NULL,
    min_order_value REAL NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL,
    max_uses INTEGER NOT NULL
);

-- 6. ORDERS TABLE
-- Represents transactions placed by customers.
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    restaurant_id INTEGER NOT NULL,
    partner_id INTEGER NOT NULL,
    promo_id INTEGER,
    order_date DATE NOT NULL,
    order_time TEXT NOT NULL,
    order_status TEXT NOT NULL,
    subtotal REAL NOT NULL,
    discount_amount REAL NOT NULL,
    delivery_fee REAL NOT NULL,
    total_amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    city TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
    FOREIGN KEY (partner_id) REFERENCES delivery_partners(partner_id),
    FOREIGN KEY (promo_id) REFERENCES promotions(promo_id)
);

-- 7. ORDER_ITEMS TABLE
-- Represents the individual items within each order.
CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    menu_item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 8. DELIVERY_TRACKING TABLE
-- Tracks delivery details for delivered orders.
CREATE TABLE delivery_tracking (
    tracking_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    partner_id INTEGER NOT NULL,
    pickup_time TEXT NOT NULL,
    delivery_time TEXT NOT NULL,
    distance_km REAL NOT NULL,
    actual_delivery_minutes INTEGER NOT NULL,
    promised_delivery_minutes INTEGER NOT NULL,
    was_on_time BOOLEAN NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (partner_id) REFERENCES delivery_partners(partner_id)
);

-- 9. REVIEWS TABLE
-- Customer reviews for their orders.
CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    restaurant_id INTEGER NOT NULL,
    partner_id INTEGER NOT NULL,
    food_rating INTEGER NOT NULL,
    delivery_rating INTEGER NOT NULL,
    overall_rating REAL NOT NULL,
    review_date DATE NOT NULL,
    has_text_review BOOLEAN NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
    FOREIGN KEY (partner_id) REFERENCES delivery_partners(partner_id)
);

-- INDEXES FOR OPTIMIZED PERFORMANCE
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_restaurant_id ON orders(restaurant_id);
CREATE INDEX idx_orders_partner_id ON orders(partner_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_city ON orders(city);
CREATE INDEX idx_orders_order_status ON orders(order_status);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);

CREATE INDEX idx_reviews_restaurant_id ON reviews(restaurant_id);
CREATE INDEX idx_reviews_partner_id ON reviews(partner_id);
CREATE INDEX idx_reviews_customer_id ON reviews(customer_id);

CREATE INDEX idx_delivery_tracking_partner_id ON delivery_tracking(partner_id);
CREATE INDEX idx_delivery_tracking_order_id ON delivery_tracking(order_id);
