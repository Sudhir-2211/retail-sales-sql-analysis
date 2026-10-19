"""Automated SQL Query Execution and Visual Reporting Script.

Executes all analytical queries against retail_sales.db and produces publication-grade charts.
Author: Sudhir Kumar (GitHub: Sudhir-2211)
"""

import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.load_data import build_retail_database

# Configure styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 0.8


def run_query_from_file(conn: sqlite3.Connection, filepath: str) -> pd.DataFrame:
    """Reads a SQL script and executes it via pandas."""
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()
    return pd.read_sql_query(sql, conn)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "retail_sales.db")
    reports_dir = os.path.join(base_dir, "reports", "visualizations")
    os.makedirs(reports_dir, exist_ok=True)

    print("==================================================================")
    print("      RETAIL SALES SQL ANALYTICS & COMMERCIAL INTELLIGENCE        ")
    print("      Author: Sudhir Kumar (GitHub: Sudhir-2211)                  ")
    print("==================================================================")

    # 1. Ensure database exists
    conn = build_retail_database(db_path=db_path)

    # 2. Query 1: Monthly Growth & Revenue
    q1_path = os.path.join(base_dir, "queries", "01_monthly_revenue_and_growth.sql")
    df_monthly = run_query_from_file(conn, q1_path)
    print("\n--- 1. Monthly Revenue & MoM Growth (First 5 Months) ---")
    print(df_monthly[["order_month", "total_orders", "monthly_revenue", "monthly_profit", "mom_growth_pct"]].head())

    # Plot 1: Monthly Revenue & Profit Trajectory
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    x = range(len(df_monthly))
    ax1.bar([i - 0.2 for i in x], df_monthly["monthly_revenue"], width=0.4, label="Monthly Revenue ($)", color="#1E3A8A")
    ax1.bar([i + 0.2 for i in x], df_monthly["monthly_profit"], width=0.4, label="Gross Profit ($)", color="#0D9488")
    ax2.plot(x, df_monthly["profit_margin_pct"], color="#E11D48", marker="o", linewidth=2.2, label="Profit Margin %")

    ax1.set_xticks(x)
    ax1.set_xticklabels(df_monthly["order_month"], rotation=45, ha="right", fontsize=9)
    ax1.set_ylabel("Revenue & Profit ($)", fontsize=11, fontweight="bold", color="#1E3A8A")
    ax2.set_ylabel("Margin %", fontsize=11, fontweight="bold", color="#E11D48")
    ax1.set_title("Monthly Revenue, Gross Profit & Profit Margin Trends", fontsize=14, fontweight="bold", pad=15)
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "monthly_revenue_and_profit.png"), dpi=200)
    plt.close()

    # 3. Query 2: Product Performance & Margins
    q2_path = os.path.join(base_dir, "queries", "02_product_profitability_and_margins.sql")
    df_products = run_query_from_file(conn, q2_path)
    print("\n--- 2. Top 5 Most Profitable Products ---")
    print(df_products[["product_name", "category_name", "total_units_sold", "total_revenue", "total_profit", "realized_margin_pct"]].head())

    # Plot 2: Top 10 Products by Profit
    plt.figure(figsize=(10, 6))
    top10 = df_products.head(10).sort_values(by="total_profit", ascending=True)
    bars = plt.barh(top10["product_name"], top10["total_profit"], color="#0284C7")
    plt.xlabel("Total Gross Profit ($)", fontweight="bold")
    plt.title("Top 10 Most Profitable Retail Products", fontsize=13, fontweight="bold")
    for bar in bars:
        w = bar.get_width()
        plt.text(w + 100, bar.get_y() + bar.get_height() / 2, f"${w:,.0f}", va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "top_profitable_products.png"), dpi=200)
    plt.close()

    # 4. Query 3: Regional & Store Performance
    q3_path = os.path.join(base_dir, "queries", "03_regional_store_performance.sql")
    df_regional = run_query_from_file(conn, q3_path)
    print("\n--- 3. Regional Store Rankings ---")
    print(df_regional[["region_name", "store_name", "store_type", "total_revenue", "profit_margin_pct", "pct_of_regional_sales"]].head(6))

    # Plot 3: Revenue by Store and Region
    plt.figure(figsize=(11, 6))
    sns.barplot(data=df_regional, x="total_revenue", y="store_name", hue="region_name", dodge=False, palette="Set2")
    plt.xlabel("Total Sales Revenue ($)", fontweight="bold")
    plt.ylabel("Retail Store Location", fontweight="bold")
    plt.title("Retail Store Performance Across Geographic Sales Territories", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "regional_store_performance.png"), dpi=200)
    plt.close()

    # 5. Query 4: RFM Customer Segmentation
    q4_path = os.path.join(base_dir, "queries", "04_customer_rfm_segmentation.sql")
    df_rfm = run_query_from_file(conn, q4_path)
    print("\n--- 4. Customer RFM Distribution ---")
    rfm_summary = df_rfm["customer_rfm_segment"].value_counts().reset_index()
    rfm_summary.columns = ["Segment", "Customer Count"]
    print(rfm_summary)

    # Plot 4: Customer RFM Breakdown
    plt.figure(figsize=(8, 6))
    plt.pie(
        rfm_summary["Customer Count"],
        labels=rfm_summary["Segment"],
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette("pastel"),
        explode=[0.05 if s == "Champion / VIP" else 0 for s in rfm_summary["Segment"]],
    )
    plt.title("Customer RFM Segmentation Portfolio Share", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "rfm_customer_segments.png"), dpi=200)
    plt.close()

    # 6. Query 5: Retention & CLV
    q5_path = os.path.join(base_dir, "queries", "05_repeat_purchase_and_clv.sql")
    df_clv = run_query_from_file(conn, q5_path)
    print("\n--- 5. Customer Lifetime Value & Repeat Purchase Rates ---")
    print(df_clv)

    conn.close()
    print("\n[SUCCESS] All 5 SQL queries executed. Visualizations saved to reports/visualizations/.")


if __name__ == "__main__":
    main()
