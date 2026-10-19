"""Generates and loads realistic retail dataset into SQLite database.

Author: Sudhir Kumar (GitHub: Sudhir-2211)
"""

import os
import random
import sqlite3
from datetime import datetime, timedelta
from typing import Optional


def build_retail_database(db_path: str = "retail_sales.db", schema_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates schema and seeds database with realistic retail sales data."""
    if schema_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        schema_path = os.path.join(base_dir, "sql", "schema.sql")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")

    # 1. Execute DDL Schema
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)

    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM customers;")
    if cursor.fetchone()[0] > 0:
        return conn  # already seeded

    random.seed(42)  # Deterministic seed for reproducible testing

    # 2. Seed Regions
    regions = [
        (1, "Northeast", "Sarah Jenkins"),
        (2, "Southeast", "Marcus Vance"),
        (3, "Midwest", "Elena Rostova"),
        (4, "West Coast", "David Kim"),
    ]
    cursor.executemany("INSERT INTO regions VALUES (?, ?, ?);", regions)

    # 3. Seed Stores
    stores = [
        (1, "Manhattan 5th Ave", 1, "New York", "Flagship"),
        (2, "Boston Back Bay", 1, "Boston", "Standard"),
        (3, "Philly Metro Outlet", 1, "Philadelphia", "Outlet"),
        (4, "Atlanta Buckhead", 2, "Atlanta", "Standard"),
        (5, "Miami Beach Hub", 2, "Miami", "Flagship"),
        (6, "Charlotte Southpark", 2, "Charlotte", "Outlet"),
        (7, "Chicago Michigan Ave", 3, "Chicago", "Flagship"),
        (8, "Minneapolis Downtown", 3, "Minneapolis", "Standard"),
        (9, "Cleveland Central", 3, "Cleveland", "Outlet"),
        (10, "Seattle Pike Place", 4, "Seattle", "Standard"),
        (11, "San Francisco Union Sq", 4, "San Francisco", "Flagship"),
        (12, "Omnichannel Direct Web", 4, "Los Angeles", "Online Direct"),
    ]
    cursor.executemany("INSERT INTO stores VALUES (?, ?, ?, ?, ?);", stores)

    # 4. Seed Product Categories
    categories = [
        (1, "Consumer Electronics", "Technology"),
        (2, "Home Appliances", "Home Goods"),
        (3, "Fashion & Apparel", "Lifestyle"),
        (4, "Office Equipment", "Workplace"),
        (5, "Fitness & Outdoors", "Sports"),
    ]
    cursor.executemany("INSERT INTO categories VALUES (?, ?, ?);", categories)

    # 5. Seed Products (cost, retail price)
    products = [
        (1, "Noise-Cancelling Wireless Headphones", 1, 95.0, 199.99),
        (2, "Ultra-Slim 4K Monitor 27-inch", 1, 160.0, 329.50),
        (3, "Mechanical Ergonomic Keyboard", 1, 45.0, 99.00),
        (4, "Smartphone Pro 256GB", 1, 480.0, 899.00),
        (5, "Portable Bluetooth Speaker", 1, 28.0, 59.99),
        (6, "Espresso & Coffee Machine", 2, 140.0, 279.00),
        (7, "Smart Air Purifier HEPA", 2, 75.0, 149.99),
        (8, "Cordless Stick Vacuum Cleaner", 2, 110.0, 229.00),
        (9, "Cast Iron 5-Piece Cookware Set", 2, 60.0, 135.00),
        (10, "Digital Convection Toaster Oven", 2, 50.0, 119.50),
        (11, "Men's Waterproof Rain Jacket", 3, 35.0, 89.00),
        (12, "Women's Merino Wool Sweater", 3, 28.0, 75.00),
        (13, "Classic Leather Weekend Duffel", 3, 55.0, 145.00),
        (14, "Thermal Performance Running Tights", 3, 18.0, 48.00),
        (15, "Polarized Aviator Sunglasses", 3, 22.0, 65.00),
        (16, "High-Back Ergonomic Office Chair", 4, 130.0, 299.00),
        (17, "Electric Standing Desk Frame", 4, 180.0, 389.00),
        (18, "Heavy-Duty Cross-Cut Shredder", 4, 40.0, 95.00),
        (19, "Wireless Laser Document Scanner", 4, 85.0, 179.00),
        (20, "Adjustable Dual Monitor Arm Mount", 4, 25.0, 69.99),
        (21, "Carbon Fiber Road Bicycle Helmet", 5, 45.0, 110.00),
        (22, "Adjustable Dumbbell Set 50lbs", 5, 115.0, 249.00),
        (23, "Insulated Stainless Steel Hydration Flask", 5, 10.0, 29.50),
        (24, "All-Weather 4-Person Camping Tent", 5, 90.0, 219.00),
        (25, "Yoga & Recovery Mat Premium", 5, 14.0, 39.00),
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?);", products)

    # 6. Seed Customers (120 customers)
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    segments = ["Consumer", "Corporate", "Small Business"]
    cities = [
        ("New York", "NY"), ("Boston", "MA"), ("Philadelphia", "PA"),
        ("Atlanta", "GA"), ("Miami", "FL"), ("Charlotte", "NC"),
        ("Chicago", "IL"), ("Minneapolis", "MN"), ("Cleveland", "OH"),
        ("Seattle", "WA"), ("San Francisco", "CA"), ("Los Angeles", "CA")
    ]

    customers = []
    base_date = datetime(2023, 1, 1)

    for cid in range(1, 121):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{cid}@example.com"
        seg = random.choices(segments, weights=[0.60, 0.25, 0.15])[0]
        city, state = random.choice(cities)
        signup = (base_date + timedelta(days=random.randint(0, 300))).strftime("%Y-%m-%d")
        customers.append((cid, name, email, seg, city, state, "United States", signup))

    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?);", customers)

    # 7. Seed Orders and Line Items (450 Orders over 2023 & 2024)
    orders = []
    order_items = []
    item_counter = 1

    start_date = datetime(2023, 1, 15)
    end_date = datetime(2024, 12, 15)
    total_days = (end_date - start_date).days

    order_statuses = ["Completed", "Shipped", "Completed", "Completed", "Returned", "Cancelled"]

    for oid in range(1, 451):
        cid = random.randint(1, 120)
        sid = random.randint(1, 12)
        odate = (start_date + timedelta(days=random.randint(0, total_days))).strftime("%Y-%m-%d")
        status = random.choices(order_statuses, weights=[0.60, 0.25, 0.08, 0.04, 0.02, 0.01])[0]
        ship_cost = round(random.choice([0.0, 5.99, 9.99, 14.99]), 2)

        orders.append((oid, cid, sid, odate, status, ship_cost))

        # 1 to 4 items per order
        num_items = random.choices([1, 2, 3, 4], weights=[0.45, 0.35, 0.15, 0.05])[0]
        chosen_products = random.sample(products, num_items)

        for p in chosen_products:
            pid = p[0]
            unit_price = p[4]
            qty = random.choices([1, 2, 3, 5], weights=[0.65, 0.22, 0.10, 0.03])[0]
            discount = random.choice([0.0, 0.0, 0.0, 0.05, 0.10, 0.15])
            order_items.append((item_counter, oid, pid, qty, unit_price, discount))
            item_counter += 1

    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?);", orders)
    cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?);", order_items)

    conn.commit()
    print(f"Loaded schema & seeded: {len(customers)} customers, {len(products)} products, {len(orders)} orders, {len(order_items)} items.")
    return conn


if __name__ == "__main__":
    build_retail_database()
