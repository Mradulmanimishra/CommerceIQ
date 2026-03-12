"""
CommerceIQ — Synthetic E-Commerce Data Generator
=================================================
Generates five interlinked CSV datasets that model a realistic Indian
e-commerce business operating throughout calendar year 2024.

Tables produced:
    customers.csv   – 500 customer profiles (B2C / B2B / Enterprise)
    products.csv    – 50 SKUs across 5 categories
    orders.csv      – 5 000 orders with festive-season uplift
    order_items.csv – line items (1-4 per order)
    operations.csv  – fulfilment & return records

Usage:
    pip install faker pandas numpy
    python generate_data.py
"""

import os
import warnings
from datetime import timedelta

import numpy as np
import pandas as pd
from faker import Faker

# ── reproducibility ──────────────────────────────────────────────────
SEED = 42
np.random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Indian geography ─────────────────────────────────────────────────
CITY_STATE_MAP = {
    "Mumbai": "Maharashtra",
    "Delhi": "Delhi",
    "Bangalore": "Karnataka",
    "Hyderabad": "Telangana",
    "Chennai": "Tamil Nadu",
    "Kolkata": "West Bengal",
    "Pune": "Maharashtra",
    "Ahmedabad": "Gujarat",
    "Jaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh",
    "Surat": "Gujarat",
    "Nagpur": "Maharashtra",
}
CITIES = list(CITY_STATE_MAP.keys())

# ── helper: sprinkle ~2 % nulls in non-key columns ──────────────────
def add_nulls(df: pd.DataFrame, key_cols: list[str], pct: float = 0.02):
    """Replace ~pct of values with NaN in non-key columns."""
    rng = np.random.default_rng(SEED)
    for col in df.columns:
        if col in key_cols:
            continue
        mask = rng.random(len(df)) < pct
        df.loc[mask, col] = np.nan
    return df


# ═══════════════════════════════════════════════════════════════════════
# 1. CUSTOMERS
# ═══════════════════════════════════════════════════════════════════════
def generate_customers(n: int = 500) -> pd.DataFrame:
    """Generate n customer records with Indian locale data."""
    segments = np.random.choice(
        ["B2C", "B2B", "Enterprise"], size=n, p=[0.60, 0.30, 0.10]
    )
    cities = np.random.choice(CITIES, size=n)
    states = [CITY_STATE_MAP[c] for c in cities]

    rows = []
    for i in range(n):
        rows.append(
            {
                "CustomerID": f"CUST-{i+1:04d}",
                "Name": fake.name(),
                "City": cities[i],
                "State": states[i],
                "Email": fake.email(),
                "Segment": segments[i],
                "JoinDate": fake.date_between_dates(
                    date_start=pd.Timestamp("2020-01-01"),
                    date_end=pd.Timestamp("2024-12-31"),
                ).isoformat(),
            }
        )

    df = pd.DataFrame(rows)
    df = add_nulls(df, key_cols=["CustomerID"])
    return df


# ═══════════════════════════════════════════════════════════════════════
# 2. PRODUCTS
# ═══════════════════════════════════════════════════════════════════════
PRODUCT_CATALOG = {
    "Electronics": [
        "Wireless Earbuds", "Smartphone Case", "USB-C Hub", "Bluetooth Speaker",
        "Power Bank 20000mAh", "LED Desk Lamp", "Webcam HD", "Mechanical Keyboard",
        "Portable SSD 1TB", "Smart Watch Band",
    ],
    "Apparel": [
        "Cotton Kurta", "Denim Jeans", "Polo T-Shirt", "Running Shorts",
        "Formal Blazer", "Silk Saree", "Winter Jacket", "Linen Shirt",
        "Track Pants", "Cotton Dupatta",
    ],
    "Home": [
        "Stainless Steel Bottle", "Ceramic Mug Set", "Bedsheet 300TC",
        "Wall Clock Wooden", "Scented Candle Set", "Cushion Cover Pack",
        "Kitchen Organizer", "Door Mat Coir", "Table Lamp Brass", "Photo Frame Set",
    ],
    "Sports": [
        "Yoga Mat 6mm", "Resistance Bands Set", "Cricket Bat Kashmir",
        "Badminton Racquet", "Dumbbell 5kg Pair", "Skipping Rope",
        "Football Size 5", "Cycling Gloves", "Gym Bag 40L", "Swim Goggles",
    ],
    "Beauty": [
        "Face Serum Vitamin C", "Sunscreen SPF50", "Hair Oil Argan",
        "Lipstick Matte Set", "Face Wash Neem", "Body Lotion 400ml",
        "Nail Polish Kit", "Eye Cream Anti-Age", "Sheet Mask Pack", "Perfume 100ml",
    ],
}


def generate_products() -> pd.DataFrame:
    """50 products; Electronics priced ~3× the average of other categories."""
    rows = []
    pid = 1
    for category, names in PRODUCT_CATALOG.items():
        for name in names:
            if category == "Electronics":
                price = round(np.random.uniform(2000, 8000), 2)
            else:
                price = round(np.random.uniform(300, 2500), 2)
            rows.append(
                {
                    "ProductID": f"PROD-{pid:03d}",
                    "Name": name,
                    "Category": category,
                    "Price": price,
                    "Cost": round(price * 0.6, 2),
                    "Stock": int(np.random.randint(0, 501)),
                    "ReorderLevel": 50,
                }
            )
            pid += 1

    df = pd.DataFrame(rows)
    df = add_nulls(df, key_cols=["ProductID"])
    return df


# ═══════════════════════════════════════════════════════════════════════
# 3. ORDERS  (5 000 rows — Oct-Dec volume +40 %)
# ═══════════════════════════════════════════════════════════════════════
def _weighted_order_dates(n: int) -> pd.Series:
    """Distribute order dates across 2024 with Q4 festive spike."""
    # Monthly weights: Jan-Sep normal, Oct-Dec +40 %
    month_weights = np.array([1.0] * 9 + [1.4] * 3)
    month_weights /= month_weights.sum()

    months = np.random.choice(range(1, 13), size=n, p=month_weights)
    dates = []
    for m in months:
        max_day = pd.Timestamp(2024, m, 1).days_in_month
        day = np.random.randint(1, max_day + 1)
        dates.append(pd.Timestamp(2024, m, day))
    return pd.Series(dates)


def generate_orders(n: int = 5000, customer_ids: list[str] = None) -> pd.DataFrame:
    """Generate n orders linked to existing customers."""
    order_dates = _weighted_order_dates(n)
    channels = np.random.choice(
        ["Online", "Marketplace", "InStore"], size=n, p=[0.50, 0.35, 0.15]
    )
    statuses = np.random.choice(
        ["Delivered", "Returned", "Pending"], size=n, p=[0.80, 0.12, 0.08]
    )

    df = pd.DataFrame(
        {
            "OrderID": [f"ORD-{i+1:05d}" for i in range(n)],
            "CustomerID": np.random.choice(customer_ids, size=n),
            "OrderDate": order_dates,
            "Channel": channels,
            "Status": statuses,
        }
    )
    df = add_nulls(df, key_cols=["OrderID", "CustomerID", "OrderDate"])
    return df


# ═══════════════════════════════════════════════════════════════════════
# 4. ORDER ITEMS  (1-4 items per order)
# ═══════════════════════════════════════════════════════════════════════
def generate_order_items(
    orders_df: pd.DataFrame, products_df: pd.DataFrame
) -> pd.DataFrame:
    """Create line items with category-aware return rates."""
    product_ids = products_df["ProductID"].tolist()
    product_prices = dict(zip(products_df["ProductID"], products_df["Price"]))

    rows = []
    for oid in orders_df["OrderID"]:
        n_items = np.random.randint(1, 5)  # 1 to 4 items
        chosen = np.random.choice(product_ids, size=n_items, replace=False)
        for pid in chosen:
            qty = int(np.random.randint(1, 6))
            base_price = product_prices.get(pid, 999)
            # handle potential NaN from null injection
            if pd.isna(base_price):
                base_price = 999.0
            discount = round(np.random.uniform(0, 0.20), 2)
            rows.append(
                {
                    "OrderID": oid,
                    "ProductID": pid,
                    "Quantity": qty,
                    "UnitPrice": base_price,
                    "Discount": discount,
                }
            )

    df = pd.DataFrame(rows)
    df = add_nulls(df, key_cols=["OrderID", "ProductID"])
    return df


# ═══════════════════════════════════════════════════════════════════════
# 5. OPERATIONS  (fulfilment + returns)
# ═══════════════════════════════════════════════════════════════════════
RETURN_REASONS = ["Defective", "Wrong Size", "Changed Mind", "Damaged", "Not as Expected"]
WAREHOUSES = ["WH-North", "WH-South", "WH-East", "WH-West"]

# Category-level return probability
CATEGORY_RETURN_RATE = {
    "Electronics": 0.15,
    "Apparel": 0.10,
    "Home": 0.05,
    "Sports": 0.05,
    "Beauty": 0.05,
}


def generate_operations(
    orders_df: pd.DataFrame,
    order_items_df: pd.DataFrame,
    products_df: pd.DataFrame,
) -> pd.DataFrame:
    """One operations row per order with delivery & return info."""
    # Build a lookup: OrderID → dominant category (most items)
    item_cat = order_items_df.merge(
        products_df[["ProductID", "Category"]], on="ProductID", how="left"
    )
    dominant = (
        item_cat.groupby("OrderID")["Category"]
        .agg(lambda x: x.mode().iloc[0] if len(x.mode()) else "Home")
    )

    rows = []
    for _, order in orders_df.iterrows():
        oid = order["OrderID"]
        order_date = pd.Timestamp(order["OrderDate"])
        wh = np.random.choice(WAREHOUSES)
        ship_delay = int(np.random.randint(1, 4))  # 1-3 days
        delivery_transit = int(np.random.randint(1, 8))  # 1-7 days
        ship_date = order_date + timedelta(days=ship_delay)
        delivery_date = ship_date + timedelta(days=delivery_transit)
        delivery_days = ship_delay + delivery_transit
        on_time = 1 if delivery_days <= 5 else 0

        cat = dominant.get(oid, "Home")
        ret_prob = CATEGORY_RETURN_RATE.get(cat, 0.05)
        return_flag = int(np.random.random() < ret_prob)
        reason = np.random.choice(RETURN_REASONS) if return_flag else ""

        rows.append(
            {
                "OrderID": oid,
                "WarehouseID": wh,
                "ShipDate": ship_date.strftime("%Y-%m-%d"),
                "DeliveryDate": delivery_date.strftime("%Y-%m-%d"),
                "DeliveryDays": delivery_days,
                "OnTimeFlag": on_time,
                "ReturnFlag": return_flag,
                "ReturnReason": reason,
            }
        )

    df = pd.DataFrame(rows)
    df = add_nulls(df, key_cols=["OrderID"])
    return df


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════
def main():
    print("🔧 CommerceIQ — Data Generation Started")
    print("=" * 50)

    # 1. Customers
    customers = generate_customers(500)
    customers.to_csv(os.path.join(OUTPUT_DIR, "customers.csv"), index=False)
    print(f"✅ customers.csv  → {len(customers):>5} rows")

    # 2. Products
    products = generate_products()
    products.to_csv(os.path.join(OUTPUT_DIR, "products.csv"), index=False)
    print(f"✅ products.csv   → {len(products):>5} rows")

    # 3. Orders
    orders = generate_orders(5000, customers["CustomerID"].tolist())
    orders.to_csv(os.path.join(OUTPUT_DIR, "orders.csv"), index=False)
    print(f"✅ orders.csv     → {len(orders):>5} rows")

    # 4. Order Items
    order_items = generate_order_items(orders, products)
    order_items.to_csv(os.path.join(OUTPUT_DIR, "order_items.csv"), index=False)
    print(f"✅ order_items.csv→ {len(order_items):>5} rows")

    # 5. Operations
    operations = generate_operations(orders, order_items, products)
    operations.to_csv(os.path.join(OUTPUT_DIR, "operations.csv"), index=False)
    print(f"✅ operations.csv → {len(operations):>5} rows")

    print("=" * 50)
    print("🎉 All datasets saved to ./data/")

    # Quick sanity checks
    print("\n── Sanity Checks ──")
    rev = (order_items["UnitPrice"] * order_items["Quantity"] * (1 - order_items["Discount"])).sum()
    print(f"   Total Revenue (approx): ₹{rev:,.0f}")
    print(f"   Unique customers in orders: {orders['CustomerID'].nunique()}")
    print(f"   Order status distribution:\n{orders['Status'].value_counts().to_string()}")
    print(f"   Avg items per order: {len(order_items) / len(orders):.2f}")
    ret_rate = operations["ReturnFlag"].mean() * 100
    print(f"   Overall return rate: {ret_rate:.1f}%")
    on_time_rate = operations["OnTimeFlag"].mean() * 100
    print(f"   On-time delivery rate: {on_time_rate:.1f}%")


if __name__ == "__main__":
    main()
