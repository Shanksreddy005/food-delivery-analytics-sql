import pandas as pd
import numpy as np
import os

np.random.seed(42)

RAW_PATH = "data/raw/swiggy_restaurants.csv"
OUT_PATH = "data/generated/menu.csv"

restaurants = pd.read_csv(RAW_PATH)

cuisine_col = next(
    (col for col in restaurants.columns
     if any(x in col.lower() for x in
            ['cuisine', 'food_type', 'type', 'category'])),
    restaurants.columns[2]
)
print(f"Detected cuisine column: '{cuisine_col}'")

id_col = next(
    (col for col in restaurants.columns
     if any(x in col.lower() for x in
            ['restaurant_id', 'id', 'rest_id'])),
    restaurants.columns[0]
)
print(f"Detected ID column: '{id_col}'")

CUISINE_MENUS = {
    "north indian": [
        "Butter Chicken", "Dal Makhani", "Paneer Tikka",
        "Biryani", "Naan", "Roti", "Rajma Chawal",
        "Chole Bhature", "Palak Paneer", "Lassi"
    ],
    "south indian": [
        "Masala Dosa", "Idli Sambar", "Vada",
        "Uttapam", "Rasam Rice", "Filter Coffee",
        "Pongal", "Appam", "Coconut Chutney", "Medu Vada"
    ],
    "chinese": [
        "Fried Rice", "Hakka Noodles", "Manchurian",
        "Spring Rolls", "Chilli Paneer", "Dim Sum",
        "Hot and Sour Soup", "Schezwan Rice",
        "Chilli Chicken", "Momos"
    ],
    "pizza": [
        "Margherita Pizza", "Pepperoni Pizza",
        "BBQ Chicken Pizza", "Veggie Supreme",
        "Garlic Bread", "Pasta Arrabiata",
        "Caesar Salad", "Tiramisu",
        "Cheesy Dip", "Cold Drink"
    ],
    "biryani": [
        "Chicken Biryani", "Mutton Biryani",
        "Veg Biryani", "Egg Biryani",
        "Raita", "Mirchi Ka Salan",
        "Haleem", "Kebab Platter",
        "Shahi Tukda", "Lassi"
    ],
    "burger": [
        "Classic Burger", "Chicken Zinger",
        "Veggie Burger", "Double Patty Burger",
        "Crispy Chicken Burger", "Fries",
        "Onion Rings", "Coleslaw",
        "Milkshake", "Cold Drink"
    ],
    "fast food": [
        "French Fries", "Burger", "Wrap",
        "Hot Dog", "Nuggets", "Pizza Slice",
        "Sandwich", "Cold Drink", "Ice Cream", "Brownie"
    ],
    "default": [
        "Special Thali", "Veg Platter", "Non-Veg Platter",
        "Starter Combo", "Main Course", "Dessert",
        "Cold Drink", "Soup", "Salad", "Bread Basket"
    ]
}

PRICE_RANGES = {
    "north indian": (120, 450),
    "south indian": (80, 280),
    "chinese": (100, 380),
    "pizza": (150, 550),
    "biryani": (150, 500),
    "burger": (90, 350),
    "fast food": (60, 300),
    "default": (100, 400)
}

menu_rows = []
menu_id = 1
match_counts = {}

for _, restaurant in restaurants.iterrows():
    rest_id = restaurant[id_col]
    food_type = str(restaurant[cuisine_col]).lower().strip()

    matched_cuisine = "default"
    for cuisine_key in CUISINE_MENUS:
        if cuisine_key == "default":
            continue
        if cuisine_key in food_type:
            matched_cuisine = cuisine_key
            break

    match_counts[matched_cuisine] = match_counts.get(
        matched_cuisine, 0
    ) + 1

    items = CUISINE_MENUS[matched_cuisine]
    price_min, price_max = PRICE_RANGES[matched_cuisine]

    num_items = np.random.randint(5, len(items) + 1)
    selected_items = np.random.choice(
        items, size=num_items, replace=False
    )

    for item_name in selected_items:
        price = round(
            np.random.uniform(price_min, price_max), 0
        )
        menu_rows.append({
            "menu_id":       menu_id,
            "restaurant_id": rest_id,
            "item_name":     item_name,
            "price":         price,
            "cuisine_type":  matched_cuisine.title(),
            "is_available":  np.random.choice(
                [1, 0], p=[0.92, 0.08]
            )
        })
        menu_id += 1

menu_df = pd.DataFrame(menu_rows)
os.makedirs("data/generated", exist_ok=True)
menu_df.to_csv(OUT_PATH, index=False)

print(f"\nMenu generated: {len(menu_df):,} items")
print(f"Avg per restaurant: {len(menu_df)/len(restaurants):.1f}")
print(f"\nCuisine breakdown:")
for k, v in sorted(match_counts.items(),
                    key=lambda x: -x[1]):
    pct = v / len(restaurants) * 100
    print(f"  {k.title():20s} {v:5,} restaurants "
          f"({pct:.1f}%)")