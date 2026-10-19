-- ============================================================================
-- Retail Sales & Commercial Analytics Database Schema
-- Dialect: SQLite / ANSI SQL-92 Standard Compliant
-- Author: Sudhir Kumar (GitHub: Sudhir-2211)
-- ============================================================================

PRAGMA foreign_keys = ON;

-- 1. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    segment TEXT NOT NULL CHECK (segment IN ('Consumer', 'Corporate', 'Small Business')),
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'United States',
    signup_date DATE NOT NULL
);

-- 2. Product Categories
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE,
    department TEXT NOT NULL
);

-- 3. Products
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    unit_cost REAL NOT NULL CHECK (unit_cost > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= unit_cost),
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT
);

-- 4. Regions
CREATE TABLE IF NOT EXISTS regions (
    region_id INTEGER PRIMARY KEY,
    region_name TEXT NOT NULL UNIQUE,
    manager_name TEXT NOT NULL
);

-- 5. Physical & Online Stores
CREATE TABLE IF NOT EXISTS stores (
    store_id INTEGER PRIMARY KEY,
    store_name TEXT NOT NULL,
    region_id INTEGER NOT NULL,
    city TEXT NOT NULL,
    store_type TEXT NOT NULL CHECK (store_type IN ('Flagship', 'Outlet', 'Online Direct', 'Standard')),
    FOREIGN KEY (region_id) REFERENCES regions(region_id) ON DELETE RESTRICT
);

-- 6. Orders
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    order_status TEXT NOT NULL CHECK (order_status IN ('Completed', 'Shipped', 'Returned', 'Cancelled')),
    shipping_cost REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE RESTRICT
);

-- 7. Order Items (Line Items)
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price > 0),
    discount_pct REAL NOT NULL DEFAULT 0.0 CHECK (discount_pct >= 0.0 AND discount_pct <= 0.50),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

-- Indices for analytical speed
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_store ON orders(store_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);

-- Helpful View for Analytical Queries
CREATE VIEW IF NOT EXISTS v_sales_detailed AS
SELECT 
    o.order_id,
    o.order_date,
    strftime('%Y', o.order_date) AS order_year,
    strftime('%Y-%m', o.order_date) AS order_month,
    o.order_status,
    c.customer_id,
    c.customer_name,
    c.segment AS customer_segment,
    c.city AS customer_city,
    s.store_id,
    s.store_name,
    s.store_type,
    r.region_id,
    r.region_name,
    p.product_id,
    p.product_name,
    cat.category_name,
    cat.department,
    oi.quantity,
    oi.unit_price,
    oi.discount_pct,
    p.unit_cost,
    -- Net Sales Calculation
    ROUND(oi.quantity * oi.unit_price * (1.0 - oi.discount_pct), 2) AS net_revenue,
    -- Total Cost
    ROUND(oi.quantity * p.unit_cost, 2) AS total_cost,
    -- Gross Profit
    ROUND((oi.quantity * oi.unit_price * (1.0 - oi.discount_pct)) - (oi.quantity * p.unit_cost), 2) AS gross_profit
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN stores s ON o.store_id = s.store_id
JOIN regions r ON s.region_id = r.region_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id;
