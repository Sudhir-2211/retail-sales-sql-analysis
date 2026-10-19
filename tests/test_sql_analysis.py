"""Automated unit tests for Retail Sales SQL Analysis."""

import pytest
import sqlite3
import os
import tempfile
import pandas as pd
from src.load_data import build_retail_database


@pytest.fixture(scope="module")
def retail_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = build_retail_database(db_path=path)
    yield conn, path
    conn.close()
    if os.path.exists(path):
        os.remove(path)


def test_schema_and_tables_exist(retail_db):
    conn, _ = retail_db
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {r[0] for r in cursor.fetchall()}

    expected_tables = {"customers", "categories", "products", "regions", "stores", "orders", "order_items"}
    assert expected_tables.issubset(tables)


def test_table_row_counts(retail_db):
    conn, _ = retail_db
    cursor = conn.cursor()

    counts = {}
    for tbl in ["customers", "categories", "products", "regions", "stores", "orders", "order_items"]:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        counts[tbl] = cursor.fetchone()[0]

    assert counts["customers"] == 120
    assert counts["categories"] == 5
    assert counts["products"] == 25
    assert counts["regions"] == 4
    assert counts["stores"] == 12
    assert counts["orders"] == 450
    assert counts["order_items"] > 450


def test_view_sales_detailed(retail_db):
    conn, _ = retail_db
    df = pd.read_sql_query("SELECT * FROM v_sales_detailed LIMIT 10;", conn)
    assert not df.empty
    assert "net_revenue" in df.columns
    assert "gross_profit" in df.columns
    assert (df["net_revenue"] >= 0).all()


def test_query_01_monthly_revenue(retail_db):
    conn, _ = retail_db
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    q_path = os.path.join(base_dir, "queries", "01_monthly_revenue_and_growth.sql")
    with open(q_path, "r", encoding="utf-8") as f:
        sql = f.read()

    df = pd.read_sql_query(sql, conn)
    assert not df.empty
    assert "monthly_revenue" in df.columns
    assert "mom_growth_pct" in df.columns
    assert "running_total_revenue" in df.columns
    assert len(df) > 10


def test_query_02_product_profitability(retail_db):
    conn, _ = retail_db
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    q_path = os.path.join(base_dir, "queries", "02_product_profitability_and_margins.sql")
    with open(q_path, "r", encoding="utf-8") as f:
        sql = f.read()

    df = pd.read_sql_query(sql, conn)
    assert not df.empty
    assert len(df) == 25  # All 25 products represented
    assert "realized_margin_pct" in df.columns
    assert "inventory_velocity_status" in df.columns


def test_query_03_regional_store_performance(retail_db):
    conn, _ = retail_db
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    q_path = os.path.join(base_dir, "queries", "03_regional_store_performance.sql")
    with open(q_path, "r", encoding="utf-8") as f:
        sql = f.read()

    df = pd.read_sql_query(sql, conn)
    assert not df.empty
    assert "regional_store_rank" in df.columns
    assert "pct_of_regional_sales" in df.columns
    assert len(df) == 12  # All 12 stores represented


def test_query_04_customer_rfm_segmentation(retail_db):
    conn, _ = retail_db
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    q_path = os.path.join(base_dir, "queries", "04_customer_rfm_segmentation.sql")
    with open(q_path, "r", encoding="utf-8") as f:
        sql = f.read()

    df = pd.read_sql_query(sql, conn)
    assert not df.empty
    assert "customer_rfm_segment" in df.columns
    assert "recency_days" in df.columns
    assert "frequency" in df.columns
    assert "monetary_value" in df.columns
    assert df["recency_days"].min() >= 0


def test_query_05_repeat_purchase_and_clv(retail_db):
    conn, _ = retail_db
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    q_path = os.path.join(base_dir, "queries", "05_repeat_purchase_and_clv.sql")
    with open(q_path, "r", encoding="utf-8") as f:
        sql = f.read()

    df = pd.read_sql_query(sql, conn)
    assert not df.empty
    assert len(df) == 3  # Consumer, Corporate, Small Business
    assert "repeat_purchase_rate_pct" in df.columns
    assert "average_order_value_aov" in df.columns
    assert (df["repeat_purchase_rate_pct"] > 0).all()
