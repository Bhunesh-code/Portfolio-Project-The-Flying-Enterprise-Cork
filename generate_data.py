"""
generate_data.py - Generates realistic synthetic data for The Flying Enterprise Cork
Run this once to create all CSV datasets used across all 4 projects.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

# ── CONFIG ────────────────────────────────────────────────────────────────────
START_DATE = datetime(2023, 1, 1)
END_DATE   = datetime(2024, 12, 31)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PRODUCTS = {
    "Guinness Pint":        {"category": "Draught Beer",  "price": 6.50, "cost": 1.80},
    "Heineken Pint":        {"category": "Draught Beer",  "price": 6.20, "cost": 1.60},
    "Hop House 13 Pint":    {"category": "Draught Beer",  "price": 6.80, "cost": 1.90},
    "Rockshore Pint":       {"category": "Draught Beer",  "price": 6.20, "cost": 1.60},
    "Smithwicks Pint":      {"category": "Draught Beer",  "price": 5.80, "cost": 1.50},
    "House Red Wine":       {"category": "Wine",          "price": 7.50, "cost": 2.00},
    "House White Wine":     {"category": "Wine",          "price": 7.50, "cost": 2.00},
    "Prosecco Glass":       {"category": "Wine",          "price": 8.00, "cost": 2.50},
    "Jameson & Mixer":      {"category": "Spirits",       "price": 8.00, "cost": 2.20},
    "Vodka & Mixer":        {"category": "Spirits",       "price": 7.50, "cost": 1.80},
    "Gin & Tonic":          {"category": "Spirits",       "price": 9.00, "cost": 2.50},
    "Soft Drink":           {"category": "Non-Alcoholic", "price": 3.50, "cost": 0.60},
    "Coffee":               {"category": "Non-Alcoholic", "price": 3.80, "cost": 0.70},
    "Burger & Chips":       {"category": "Food",          "price": 14.50, "cost": 5.00},
    "Fish & Chips":         {"category": "Food",          "price": 15.50, "cost": 5.50},
    "Chicken Wings":        {"category": "Food",          "price": 12.00, "cost": 4.00},
    "Loaded Fries":         {"category": "Food",          "price": 9.50,  "cost": 3.00},
    "Club Sandwich":        {"category": "Food",          "price": 13.00, "cost": 4.50},
}

STAFF = [
    {"staff_id": f"S{str(i).zfill(3)}", "name": n, "role": r, "hourly_rate": hr}
    for i, (n, r, hr) in enumerate([
        ("Aoife Murphy",    "Bartender",   14.50),
        ("Cian O'Sullivan", "Bartender",   14.50),
        ("Siobhan Kelly",   "Bartender",   14.50),
        ("Declan Byrne",    "Supervisor",  18.00),
        ("Niamh Walsh",     "Bartender",   14.50),
        ("Seamus Connolly", "Floor Staff", 13.50),
        ("Roisin Doyle",    "Floor Staff", 13.50),
        ("Patrick Hennessy","Supervisor",  18.00),
        ("Emma Burke",      "Kitchen",     15.00),
        ("Liam McCarthy",   "Kitchen",     15.00),
    ], start=1)
]

EVENTS = [
    ("2023-03-17", "St. Patrick's Day"),
    ("2023-06-17", "Munster Rugby Final"),
    ("2023-07-15", "Cork Jazz Pre-Event"),
    ("2023-10-27", "Cork Jazz Festival"),
    ("2023-12-25", "Christmas Day"),
    ("2023-12-31", "New Year's Eve"),
    ("2024-02-10", "Six Nations Ireland v France"),
    ("2024-03-17", "St. Patrick's Day"),
    ("2024-06-01", "Cork Beer Festival"),
    ("2024-10-25", "Cork Jazz Festival"),
    ("2024-12-31", "New Year's Eve"),
]
EVENT_DATES = {e[0] for e in EVENTS}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def weather_factor(date):
    month = date.month
    if month in [6, 7, 8]:    return np.random.uniform(1.3, 1.6)  # Summer beer garden boost
    if month in [12, 1, 2]:   return np.random.uniform(0.7, 0.9)  # Winter dip
    return np.random.uniform(0.95, 1.15)

def day_factor(date):
    dow = date.weekday()
    if dow == 4: return 1.4   # Friday
    if dow == 5: return 1.6   # Saturday
    if dow == 6: return 1.2   # Sunday
    if dow == 3: return 1.1   # Thursday
    return 0.85               # Mon-Wed

def is_event(date):
    return date.strftime("%Y-%m-%d") in EVENT_DATES

# ── GENERATE TRANSACTIONS ─────────────────────────────────────────────────────
print("Generating transactions...")
transactions = []
transaction_id = 1
current = START_DATE

while current <= END_DATE:
    base_txns = 180
    multiplier = weather_factor(current) * day_factor(current)
    if is_event(current): multiplier *= 2.2
    n_transactions = int(base_txns * multiplier * np.random.uniform(0.9, 1.1))

    for _ in range(n_transactions):
        hour = np.random.choice(
            list(range(12, 24)),
            p=[0.02,0.03,0.06,0.09,0.11,0.13,0.13,0.12,0.11,0.10,0.07,0.03]
        )
        minute = random.randint(0, 59)
        ts = current.replace(hour=hour, minute=minute)

        product = random.choice(list(PRODUCTS.keys()))
        qty = np.random.choice([1, 2, 3], p=[0.60, 0.30, 0.10])
        info = PRODUCTS[product]
        revenue = round(info["price"] * qty, 2)
        cost    = round(info["cost"]  * qty, 2)
        staff   = random.choice(STAFF)

        transactions.append({
            "transaction_id":  f"TXN{str(transaction_id).zfill(6)}",
            "timestamp":       ts,
            "date":            current.date(),
            "hour":            hour,
            "day_of_week":     current.strftime("%A"),
            "week":            current.isocalendar()[1],
            "month":           current.month,
            "month_name":      current.strftime("%B"),
            "year":            current.year,
            "product":         product,
            "category":        info["category"],
            "quantity":        qty,
            "unit_price":      info["price"],
            "revenue":         revenue,
            "cost":            cost,
            "gross_profit":    round(revenue - cost, 2),
            "staff_id":        staff["staff_id"],
            "staff_name":      staff["name"],
            "is_event_day":    is_event(current),
            "is_weekend":      current.weekday() >= 5,
        })
        transaction_id += 1

    current += timedelta(days=1)

df_txn = pd.DataFrame(transactions)
df_txn.to_csv(f"{OUTPUT_DIR}/transactions.csv", index=False)
print(f"  ✓ transactions.csv — {len(df_txn):,} rows")

# ── GENERATE CUSTOMERS ────────────────────────────────────────────────────────
print("Generating customers...")
n_customers = 1200
first_names = ["Liam","Aoife","Cian","Siobhan","Declan","Niamh","Sean","Roisin",
                "Patrick","Emma","Conor","Ciara","Brendan","Sinead","Eoin","Grainne",
                "Darragh","Aisling","Fionn","Orla","Jack","Caoimhe","Oisin","Maeve"]
last_names  = ["Murphy","O'Sullivan","Walsh","Byrne","O'Brien","Kelly","McCarthy",
               "Doyle","Connolly","Burke","Hennessy","Ryan","Brennan","Kavanagh"]
emails_used = set()
customers   = []

for i in range(1, n_customers + 1):
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    base_email = f"{fn.lower()}.{ln.lower().replace(chr(39),'')}@gmail.com"
    email = base_email if base_email not in emails_used else f"{fn.lower()}{i}@gmail.com"
    emails_used.add(email)

    join_date   = START_DATE + timedelta(days=random.randint(0, 600))
    visits      = random.randint(1, 120)
    avg_spend   = round(random.uniform(15, 85), 2)
    loyalty_pts = visits * random.randint(5, 15)

    if visits >= 50:   segment = "VIP"
    elif visits >= 20: segment = "Regular"
    elif visits >= 5:  segment = "Occasional"
    else:              segment = "New"

    customers.append({
        "customer_id":     f"C{str(i).zfill(4)}",
        "first_name":      fn,
        "last_name":       ln,
        "email":           email,
        "join_date":       join_date.date(),
        "total_visits":    visits,
        "avg_spend_eur":   avg_spend,
        "total_spend_eur": round(visits * avg_spend, 2),
        "loyalty_points":  loyalty_pts,
        "segment":         segment,
        "preferred_category": random.choice(list({v["category"] for v in PRODUCTS.values()})),
        "is_active":       visits > 3,
    })

df_cust = pd.DataFrame(customers)
df_cust.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)
print(f"  ✓ customers.csv — {len(df_cust):,} rows")

# ── GENERATE INVENTORY ────────────────────────────────────────────────────────
print("Generating inventory...")
inventory_items = [
    ("Guinness Keg 50L",    "Draught Beer", 280, 50,  15, 120),
    ("Heineken Keg 50L",    "Draught Beer", 200, 40,  15, 100),
    ("Hop House 13 Keg",    "Draught Beer", 160, 30,  10, 80),
    ("Rockshore Keg 50L",   "Draught Beer", 140, 25,  10, 70),
    ("Red Wine Cases",      "Wine",         80,  15,  5,  40),
    ("White Wine Cases",    "Wine",         75,  15,  5,  40),
    ("Prosecco Cases",      "Wine",         40,  10,  3,  20),
    ("Jameson 70cl",        "Spirits",      60,  12,  5,  30),
    ("Vodka 70cl",          "Spirits",      50,  10,  5,  25),
    ("Gin 70cl",            "Spirits",      45,  10,  5,  25),
    ("Soft Drinks Cases",   "Non-Alcoholic",120, 20,  8,  50),
    ("Coffee Beans kg",     "Non-Alcoholic",30,  8,   3,  15),
    ("Beef Patties (box)",  "Food",         90,  15,  5,  40),
    ("Cod Portions (box)",  "Food",         70,  12,  4,  30),
    ("Chicken Wings (kg)",  "Food",         80,  15,  5,  35),
    ("Frozen Chips (bag)",  "Food",         100, 20,  8,  50),
]

inv_records = []
current = START_DATE
item_stocks = {item[0]: item[2] for item in inventory_items}

while current <= END_DATE:
    for (name, cat, base_stock, reorder_pt, min_order, max_stock) in inventory_items:
        daily_usage = random.randint(3, 18) * (1.5 if is_event(current) else 1.0)
        stock = max(0, item_stocks[name] - daily_usage)
        reorder = stock <= reorder_pt
        if reorder:
            stock = min(stock + random.randint(min_order, max_stock), max_stock)
        item_stocks[name] = stock

        inv_records.append({
            "date":           current.date(),
            "item_name":      name,
            "category":       cat,
            "stock_level":    round(stock, 1),
            "reorder_point":  reorder_pt,
            "reorder_triggered": reorder,
            "daily_usage":    round(daily_usage, 1),
            "waste_units":    round(random.uniform(0, 0.5) * daily_usage * 0.1, 2),
        })
    current += timedelta(days=1)

df_inv = pd.DataFrame(inv_records)
df_inv.to_csv(f"{OUTPUT_DIR}/inventory.csv", index=False)
print(f"  ✓ inventory.csv — {len(df_inv):,} rows")

# ── GENERATE STAFF SCHEDULES ──────────────────────────────────────────────────
print("Generating staff schedules...")
shifts = []
current = START_DATE

while current <= END_DATE:
    dow     = current.weekday()
    is_busy = dow >= 4 or is_event(current)
    n_staff = random.randint(5, 8) if is_busy else random.randint(2, 4)
    selected = random.sample(STAFF, min(n_staff, len(STAFF)))

    for s in selected:
        start_h = random.choice([11, 12, 13, 17])
        hours   = random.choice([8, 7, 6]) if is_busy else random.choice([6, 5])
        labour  = round(hours * s["hourly_rate"], 2)
        shifts.append({
            "shift_id":    f"SH{current.strftime('%Y%m%d')}{s['staff_id']}",
            "date":        current.date(),
            "staff_id":    s["staff_id"],
            "staff_name":  s["name"],
            "role":        s["role"],
            "shift_start": start_h,
            "hours_worked": hours,
            "hourly_rate": s["hourly_rate"],
            "labour_cost": labour,
            "is_weekend":  dow >= 5,
            "is_event_day": is_event(current),
        })
    current += timedelta(days=1)

df_staff = pd.DataFrame(shifts)
df_staff.to_csv(f"{OUTPUT_DIR}/staff_schedules.csv", index=False)
print(f"  ✓ staff_schedules.csv — {len(df_staff):,} rows")

# ── EVENTS REFERENCE ──────────────────────────────────────────────────────────
df_events = pd.DataFrame(EVENTS, columns=["date", "event_name"])
df_events.to_csv(f"{OUTPUT_DIR}/events.csv", index=False)
print(f"  ✓ events.csv — {len(df_events)} rows")

print("\n✅ All datasets generated successfully!")
print(f"   Total transaction records: {len(df_txn):,}")
print(f"   Date range: {START_DATE.date()} → {END_DATE.date()}")
