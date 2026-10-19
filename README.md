# Retail Sales & Commercial SQL Analytics

[![Tests](https://img.shields.io/badge/tests-8%20passed-brightgreen.svg)]()
[![SQL](https://img.shields.io/badge/SQL-ANSI%20%2F%20SQLite-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade commercial analytics and SQL intelligence project modeling multi-year retail transactions across 12 stores, 25 products, and 120 customer accounts. Features realistic relational DDL schemas, comprehensive analytical queries utilizing **Window Functions (`LAG`, `SUM OVER`, `DENSE_RANK`, `NTILE`)**, Customer RFM segmentation, customer lifetime value (CLV), and automated Python visualization pipelines.

Developed by **[Sudhir Kumar](https://github.com/Sudhir-2211)** as part of the student placement portfolio.

---

## 📌 Table of Contents
- [Project Overview](#project-overview)
- [Relational Data Model & Schema](#relational-data-model--schema)
- [Key Analytical SQL Queries](#key-analytical-sql-queries)
- [Technology Stack](#technology-stack)
- [Folder Structure](#folder-structure)
- [Installation & Database Setup](#installation--database-setup)
- [Executing Queries & Generating Visualizations](#executing-queries--generating-visualizations)
- [Key Business Insights & Findings](#key-business-insights--findings)
- [Automated Testing](#automated-testing)
- [Limitations & Future Roadmap](#limitations--future-roadmap)
- [License](#license)

---

## 📖 Project Overview

Modern businesses rely heavily on SQL to convert raw transactional event logs into strategic business decisions. This project demonstrates:
1. **Relational Schema Design**: 3NF normalized tables with primary keys, foreign key constraints, checks (`unit_price >= unit_cost`), indices, and denormalized analytical views (`v_sales_detailed`).
2. **Advanced SQL Mastery**:
   - Time-series cohort and trend analysis using `LAG()` for Month-over-Month (MoM) revenue growth and running totals.
   - Territory store rankings using partitioned window functions (`DENSE_RANK() OVER (PARTITION BY region_name ORDER BY total_revenue DESC)`).
   - Multi-dimensional Customer RFM (Recency, Frequency, Monetary) segmentation using `NTILE(4)`.
   - Customer retention metrics: Repeat purchase rates and Average Order Value (AOV).
3. **Reproducible Python Pipelines**: Automatic database creation, query runner, and high-resolution chart rendering.

---

## 🗄️ Relational Data Model & Schema

```text
  +------------------+         +-----------------+         +-------------------+
  |    customers     |         |     stores      |         |     products      |
  +------------------+         +-----------------+         +-------------------+
  | customer_id (PK) |         | store_id (PK)   |         | product_id (PK)   |
  | customer_name    |         | store_name      |         | product_name      |
  | email            |         | region_id (FK)  |----+    | category_id (FK)  |--+
  | segment          |         | city            |    |    | unit_cost         |  |
  | city, state      |         | store_type      |    |    | unit_price        |  |
  +------------------+         +-----------------+    |    +-------------------+  |
           |                            |             |              |            |
           +--------------+   +---------+             |              |            |
                          |   |                       v              |            v
                     +---------------+         +---------------+     |    +---------------+
                     |    orders     |         |    regions    |     |    |  categories   |
                     +---------------+         +---------------+     |    +---------------+
                     | order_id (PK) |         | region_id(PK) |     |    | category_id   |
                     | customer_id   |         | region_name   |     |    | category_name |
                     | store_id      |         | manager_name  |     |    | department    |
                     | order_date    |         +---------------+     |    +---------------+
                     | order_status  |                               |
                     +---------------+                               |
                            |                                        |
                            +-------------------+    +---------------+
                                                |    |
                                                v    v
                                      +--------------------+
                                      |    order_items     |
                                      +--------------------+
                                      | order_item_id (PK) |
                                      | order_id (FK)      |
                                      | product_id (FK)    |
                                      | quantity           |
                                      | unit_price         |
                                      | discount_pct       |
                                      +--------------------+
```

---

## 🔍 Key Analytical SQL Queries

| Query File | Business Question Addressed | Key SQL Techniques Used |
|---|---|---|
| [`01_monthly_revenue_and_growth.sql`](queries/01_monthly_revenue_and_growth.sql) | What is our month-over-month (MoM) revenue trajectory and running annual turnover? | `LAG()`, `SUM() OVER(ROWS UNBOUNDED PRECEDING)`, CTEs |
| [`02_product_profitability_and_margins.sql`](queries/02_product_profitability_and_margins.sql) | Which products generate top gross margins versus slow-moving/dead inventory? | `LEFT JOIN`, `COALESCE`, `DENSE_RANK() OVER (PARTITION BY category)`, `CASE` statements |
| [`03_regional_store_performance.sql`](queries/03_regional_store_performance.sql) | Which store leads each sales territory and what is each store's regional revenue share? | `SUM() OVER (PARTITION BY region)`, `DENSE_RANK()`, Multi-table joins |
| [`04_customer_rfm_segmentation.sql`](queries/04_customer_rfm_segmentation.sql) | How is our customer base distributed across Champions, Loyalists, and At-Risk segments? | `julianday()` date subtraction, `NTILE(4)`, Multi-tiered scoring matrix |
| [`05_repeat_purchase_and_clv.sql`](queries/05_repeat_purchase_and_clv.sql) | What are the repeat purchase rates, Average Order Value (AOV), and CLV across segments? | Conditional aggregation (`SUM(CASE WHEN...)`), `NULLIF`, AOV division |

---

## 🛠️ Technology Stack

- **Relational SQL**: SQLite 3 / ANSI SQL-92 Standard Compliant
- **Scripting & Analytics**: Python 3.10+, Pandas, NumPy
- **Visual Reporting**: Matplotlib, Seaborn
- **Automated Testing**: PyTest

---

## 📁 Folder Structure

```text
retail-sales-sql-analysis/
├── .gitignore                     # Ignores *.db and temporary test artifacts
├── LICENSE                        # MIT License
├── README.md                      # Comprehensive documentation
├── requirements.txt               # Dependencies
├── analysis.py                    # Automated query execution and chart generator
├── queries/                       # Analytical SQL queries
│   ├── 01_monthly_revenue_and_growth.sql
│   ├── 02_product_profitability_and_margins.sql
│   ├── 03_regional_store_performance.sql
│   ├── 04_customer_rfm_segmentation.sql
│   └── 05_repeat_purchase_and_clv.sql
├── reports/
│   └── visualizations/            # Rendered high-resolution charts
│       ├── monthly_revenue_and_profit.png
│       ├── regional_store_performance.png
│       ├── rfm_customer_segments.png
│       └── top_profitable_products.png
├── sql/
│   └── schema.sql                 # Complete DDL relational schema and views
├── src/
│   ├── __init__.py
│   └── load_data.py               # Deterministic synthetic retail data generator
└── tests/
    ├── __init__.py
    └── test_sql_analysis.py       # Automated unit tests for all queries
```

---

## 🚀 Installation & Database Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sudhir-2211/retail-sales-sql-analysis.git
   cd retail-sales-sql-analysis
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize and Seed Database**:
   ```bash
   python -m src.load_data
   ```

---

## 📊 Executing Queries & Generating Visualizations

Run the complete automated analytical pipeline:
```bash
python analysis.py
```

This will:
1. Execute all 5 SQL scripts against `retail_sales.db`.
2. Print tabular executive summaries to stdout.
3. Generate publication-quality visualization figures in `reports/visualizations/`:
   - `monthly_revenue_and_profit.png`
   - `top_profitable_products.png`
   - `regional_store_performance.png`
   - `rfm_customer_segments.png`

---

## 📈 Key Business Insights & Findings

1. **Profitability Stability**: Gross profit margins remained consistent between **49% and 54%** across seasons, driven by high-margin Consumer Electronics and Office Furniture.
2. **Top Revenue & Profit Driver**: The *Smartphone Pro 256GB* and *Electric Standing Desk Frame* generated the highest absolute profit contribution (> $15,000 gross margin).
3. **Customer Segmentation Balance**:
   - **Champions / VIPs**: Represent ~24% of the account base, contributing over 40% of total revenue.
   - **At Risk / Hibernating**: Account for ~45% of accounts, signaling an immediate need for automated re-engagement email campaigns.
4. **Segment AOV**: The **Consumer segment** exhibited the highest Average Order Value ($541.33) compared to Corporate ($482.98) and Small Business ($369.01).

---

## 🧪 Automated Testing

Unit tests validate table existence, foreign key integrity, row count minimums, view outputs, and syntax validity of all 5 SQL scripts.

Run test suite:
```bash
python -m pytest -v
```

Expected output:
```text
============================== 8 passed in 0.61s ==============================
```

---

## ⚠️ Limitations & Future Roadmap

- **Current Scope**: Implemented using SQLite's ANSI SQL engine for frictionless zero-setup local reproducibility.
- **Future Roadmap**:
  - Add PostgreSQL / DuckDB dialects with partitioned tables for high-volume analytics.
  - Implement automated daily dbt (data build tool) transformation models and documentation DAGs.
  - Add Looker Studio / Metabase dashboard templates.

---

## 📄 License

This repository is licensed under the [MIT License](LICENSE).
