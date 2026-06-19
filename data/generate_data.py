"""Generate synthetic data for the ucode Vibe Coding workshop.

Writes 8 tables to a target Databricks catalog/schema via Databricks Connect.
The item catalog, store locations, and review/reply language are driven by a
COMPANY_CONFIGS dict so you can swap in a different brand without editing
the schema or the row counts.

Pass --company <key> to pick a config (default: lce).

Usage:
    pip install databricks-connect faker
    python generate_data.py --profile DEFAULT --catalog ioc_sandbox --schema vibe_workshop --company lce
"""
from __future__ import annotations

import argparse
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from faker import Faker


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


# Region rollup: state -> region (used by gen_stores). Anything else falls
# back to "Central".
STATE_TO_REGION = {
    # West
    "CA": "West", "WA": "West", "OR": "West", "NV": "West", "AZ": "West",
    "UT": "West", "ID": "West", "MT": "West", "WY": "West", "CO": "West",
    "NM": "West", "AK": "West", "HI": "West",
    # East
    "ME": "East", "NH": "East", "VT": "East", "MA": "East", "RI": "East",
    "CT": "East", "NY": "East", "NJ": "East", "PA": "East", "DE": "East",
    "MD": "East", "DC": "East", "VA": "East", "WV": "East", "NC": "East",
    "SC": "East", "GA": "East", "FL": "East",
    # Central (everything else)
}


# =============================================================================
# Company configs
#
# Each entry defines: store roster, item catalog, review/reply language.
# Schema columns, row counts, role mixes, and the daypart/labor model are
# brand-agnostic and live in the generators below.
# =============================================================================

COMPANY_CONFIGS = {
    "lce": {
        "brand": "Little Caesars",
        # 20 real LCE-presence locations (city, state, neighborhood)
        "store_locations": [
            ("Detroit", "MI", "Greenfield Rd"),
            ("Detroit", "MI", "8 Mile"),
            ("Warren", "MI", "Van Dyke"),
            ("Chicago", "IL", "Cicero Ave"),
            ("Chicago", "IL", "Western Ave"),
            ("Houston", "TX", "Bellaire"),
            ("Houston", "TX", "Pasadena"),
            ("Phoenix", "AZ", "Glendale"),
            ("Las Vegas", "NV", "Sahara"),
            ("Atlanta", "GA", "Stone Mountain"),
            ("Tampa", "FL", "Brandon"),
            ("Indianapolis", "IN", "Lafayette Rd"),
            ("Columbus", "OH", "Whitehall"),
            ("Charlotte", "NC", "University City"),
            ("Dallas", "TX", "Garland"),
            ("Memphis", "TN", "Bartlett"),
            ("Cleveland", "OH", "Parma"),
            ("Cincinnati", "OH", "Mason"),
            ("Pittsburgh", "PA", "Monroeville"),
            ("San Antonio", "TX", "Southside"),
        ],
        "store_sqft_range": (1200, 2800),
        "categories": ["meat", "veggie", "bread_cheese", "pantry", "beverage"],
        "vendor_by_category": {
            "meat":          ("Detroit Meat Co.", 2),
            "veggie":        ("Midwest Produce", 1),
            "bread_cheese":  ("Wayne Dough Supply", 3),
            "pantry":        ("LCE Commissary", 3),
            "beverage":      ("PepsiCo Foodservice", 2),
        },
        "item_names": {
            "meat":         ["Pepperoni (5lb)", "Italian Sausage (5lb)", "Beef Topping (5lb)", "Bacon Crumbles (3lb)", "Ham (5lb)", "Chicken Wings (10lb)", "Canadian Bacon (3lb)"],
            "veggie":       ["Mushrooms (#10 can)", "Green Peppers (case)", "Banana Peppers (5gal)", "Black Olives (#10 can)", "Yellow Onions (50lb)", "Jalapenos (1gal)", "Pineapple (case)"],
            "bread_cheese": ["Dough Balls (case)", "Mozzarella (10lb)", "Parmesan (5lb)", "Crazy Bread Mix (case)", "Italian Cheese Blend (10lb)", "Stuffed Crust Cheese (5lb)", "Garlic Knot Mix (case)"],
            "pantry":       ["Pizza Sauce (#10 can)", "Crazy Sauce (case)", "Garlic Butter (5gal)", "Ranch Dip (case)", "Pizza Boxes (medium)", "Pizza Boxes (large)", "To-go Bags", "Buffalo Wing Sauce (1gal)", "BBQ Wing Sauce (1gal)"],
            "beverage":     ["Pepsi Syrup (BIB)", "Diet Pepsi (BIB)", "Mountain Dew (BIB)", "Aquafina (case)", "Tropicana OJ (case)", "Lipton Iced Tea (BIB)"],
        },
        "review_templates": {
            "pickup_wait":    [
                "Hot-N-Ready was anything but ready at {city}. Waited {n} min.",
                "Friday pickup at {city} was slow. Pizza was lukewarm by the time I got home.",
                "Online order said ready but waited {n} min at the {city} window.",
            ],
            "stockout":       [
                "{city} was out of Crazy Bread again. Second time this month.",
                "Sold out of pepperoni by 6pm at {city}. Lame.",
                "No Stuffed Crust available at {city}. Had to get classic.",
            ],
            "friendly_staff": [
                "Manager at {city} remembered my order. Solid crew.",
                "Cashier at {city} hooked us up with extra Crazy Sauce. Awesome.",
                "Staff at {city} always upbeat and quick. Keeps me coming back.",
            ],
            "freshness":      [
                "Pizza at {city} was hot and fresh, exactly what I wanted.",
                "Crazy Bread at {city} was straight out of the oven. Perfect.",
                "Cheese was bubbly and crust crispy at {city}. Best pizza in town.",
            ],
            "value":          [
                "Five bucks for a pizza at {city} still wins. Can't beat it.",
                "Family deal at {city} was a great value. Fed everyone.",
                "Lunch combo at {city} hit the spot. Worth the money.",
            ],
            "other":          [
                "Quick visit at {city}. Got my Hot-N-Ready and left. Standard.",
                "Stopped at {city} on a road trip. Pizza was decent.",
                "{city} location is clean and easy parking.",
            ],
        },
        "reply_brand_phrase": "Little Caesars",
    },
    "qsr_mexican": {
        "brand": "QSR Mexican",
        "store_locations": None,  # use Faker random cities
        "store_sqft_range": (1500, 6000),
        "categories": ["produce", "proteins", "dry_goods", "beverage"],
        "vendor_by_category": {
            "produce":   ("Bay Produce Co.", 1),
            "proteins":  ("Golden Gate Proteins", 2),
            "dry_goods": ("Pacific Dry Goods", 3),
            "beverage":  ("Coastal Beverage Supply", 2),
        },
        "item_names": {
            "produce":   ["Hass Avocado", "Romaine Hearts", "Roma Tomato", "Yellow Onion", "Jalapeno", "Cilantro", "Lime", "Bell Pepper", "Garlic", "Lemon"],
            "proteins":  ["Grilled Chicken", "Carnitas", "Carne Asada", "Black Beans", "Pinto Beans", "Tofu", "Ground Beef", "Shrimp", "Chorizo", "Eggs"],
            "dry_goods": ["Rice", "Tortilla (Flour)", "Tortilla (Corn)", "Cheese (Cheddar)", "Sour Cream", "Salsa Verde", "Chips (Tortilla)", "Guacamole", "Pickled Onion", "Hot Sauce"],
            "beverage":  ["Agua Fresca", "Bottled Water", "Cola", "Lemonade", "Cold Brew", "Iced Tea", "Margarita Mix", "Sparkling Water", "Mexican Coke", "Horchata"],
        },
        "review_templates": {
            "pickup_wait":    [
                "Mobile order said ready but I waited {n} min at the {city} pickup window.",
                "Friday lunch at {city} was understaffed at mobile pickup. Slow.",
                "Waited too long for an online order at {city}. Food was fine once it arrived.",
            ],
            "stockout":       [
                "{city} was out of guac again. Second time this month.",
                "Carnitas was 86'd by 1pm at {city}. Disappointing.",
                "No agua fresca at {city} today. Hard pass on the swap.",
            ],
            "friendly_staff": [
                "Cashier at {city} remembered my usual. Best service in town.",
                "Manager at {city} went above and beyond when my order got mixed up.",
                "Staff at {city} is always upbeat. Keeps me coming back.",
            ],
            "freshness":      [
                "Lunch bowl at {city} was perfect. Fresh and bright.",
                "Salsa at {city} tastes house-made. Great quality.",
                "Tortillas at {city} were warm and fresh today.",
            ],
            "value":          [
                "Portion sizes at {city} have shrunk. Same price though.",
                "Decent value at {city} for the lunch combo.",
                "{city} bowl filled me up. Worth the money.",
            ],
            "other":          [
                "Quick visit at {city}. Nothing remarkable, nothing wrong.",
                "Stopped at {city} on a road trip. Standard.",
                "{city} location is clean and easy parking.",
            ],
        },
        "reply_brand_phrase": "our team",
    },
}


# Brand-agnostic constants
REGIONS = ["West", "Central", "East"]
ROLES = ["cook", "cashier", "lead", "manager"]
ROLE_RATES = {"cook": 18.50, "cashier": 17.25, "lead": 21.00, "manager": 28.00}

DAYPARTS = [
    ("breakfast", 6, 10, 0.14, 220),
    ("lunch",     11, 14, 0.54, 760),
    ("dinner",    17, 20, 0.19, 280),
    ("late",      20, 23, 0.13, 180),
]

ROLE_MIX = {
    "breakfast": {"cook": 0.40, "cashier": 0.40, "lead": 0.20, "manager": 0.00},
    "lunch":     {"cook": 0.45, "cashier": 0.35, "lead": 0.13, "manager": 0.07},
    "dinner":    {"cook": 0.45, "cashier": 0.33, "lead": 0.15, "manager": 0.07},
    "late":      {"cook": 0.43, "cashier": 0.43, "lead": 0.14, "manager": 0.00},
}
ROLE_FLOORS = {
    "breakfast": {"cook": 1, "cashier": 1, "lead": 1, "manager": 0},
    "lunch":     {"cook": 2, "cashier": 1, "lead": 1, "manager": 1},
    "dinner":    {"cook": 2, "cashier": 1, "lead": 1, "manager": 1},
    "late":      {"cook": 1, "cashier": 1, "lead": 1, "manager": 0},
}
TARGET_RPLH = {"breakfast": 80, "lunch": 100, "dinner": 85, "late": 60}

FEEDBACK_CHANNELS = ["google", "yelp", "app", "survey", "social"]
THEME_WEIGHTS = {"pickup_wait": 0.15, "stockout": 0.10, "friendly_staff": 0.25, "freshness": 0.20, "value": 0.10, "other": 0.20}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_spark(profile: str):
    from databricks.connect import DatabricksSession  # type: ignore
    return DatabricksSession.builder.profile(profile).serverless().getOrCreate()


def write_table(spark, rows, table):
    if not rows:
        return
    df = spark.createDataFrame(rows)
    print(f"writing {table}: {df.count():,} rows")
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(table)


def dec(x):
    return Decimal(f"{x:.2f}")


# ---------------------------------------------------------------------------
# Dim generators
# ---------------------------------------------------------------------------

def gen_stores(fake: Faker, n: int, cfg: dict):
    """Generate store rows. Store names stay generic (`#NNNN - City Neighborhood`)
    so the dataset doesn't bake in a brand. The company config only controls
    which (city, state) locations are used.
    """
    rows = []
    locs = cfg.get("store_locations")
    sqft_lo, sqft_hi = cfg.get("store_sqft_range", (1500, 6000))
    for i in range(n):
        if locs:
            city, state, neighborhood = locs[i % len(locs)]
            store_name = f"#{i+1:04d} - {city} {neighborhood}".rstrip(" -")
        else:
            city, state, neighborhood = fake.city(), fake.state_abbr(), ""
            store_name = f"#{i+1:04d} - {city}"
        rows.append({
            "store_id": f"S{i+1:03d}",
            "store_name": store_name,
            "region": STATE_TO_REGION.get(state, "Central"),
            "city": city,
            "state": state,
            "square_footage": random.randint(sqft_lo, sqft_hi),
        })
    return rows


def gen_items(n: int, cfg: dict):
    rows = []
    cats = cfg["categories"]
    item_names = cfg["item_names"]
    sku_n = 1
    while len(rows) < n:
        cat = random.choice(cats)
        name = random.choice(item_names[cat])
        cost = round(random.uniform(0.5, 12.0), 2)
        retail = round(cost * random.uniform(1.5, 3.0), 2)
        rows.append({
            "sku": f"SKU-{sku_n:04d}",
            "item_name": name,
            "category": cat,
            "retail_price": dec(retail),
            "cost": dec(cost),
        })
        sku_n += 1
    return rows


def gen_employees(fake: Faker, stores, end_date):
    rows = []
    eid = 1
    plan = [("cook", 5), ("cashier", 4), ("lead", 2), ("manager", 1)]
    for s in stores:
        for role, count in plan:
            for _ in range(count):
                rows.append({
                    "employee_id": f"E{eid:05d}",
                    "store_id": s["store_id"],
                    "name": fake.name(),
                    "role": role,
                    "hourly_rate": dec(ROLE_RATES[role] + random.uniform(-1.0, 2.0)),
                    "hire_date": end_date - timedelta(days=random.randint(30, 5*365)),
                })
                eid += 1
    return rows


# ---------------------------------------------------------------------------
# Fact generators
# ---------------------------------------------------------------------------

def gen_sales_daypart(stores, days, end_date):
    rows = []
    for d in range(days):
        cur = end_date - timedelta(days=d)
        wd_factor = 1.15 if cur.weekday() in (4, 5) else 0.95 if cur.weekday() == 1 else 1.0
        for s in stores:
            store_total = random.uniform(13000, 18000) * wd_factor
            store_traffic = int(random.uniform(450, 700) * wd_factor)
            for daypart, hs, he, rev_share, traffic_share in DAYPARTS:
                share = rev_share + random.uniform(-0.02, 0.02)
                rev = max(0.0, store_total * share)
                traffic = int(store_traffic * (traffic_share / 1440.0))
                fcast_rev = rev * random.uniform(0.92, 1.08)
                fcast_traffic = int(traffic * random.uniform(0.92, 1.08))
                rows.append({
                    "date": cur, "store_id": s["store_id"], "daypart": daypart,
                    "hour_start": hs, "hour_end": he,
                    "revenue": dec(rev), "forecast_revenue": dec(fcast_rev),
                    "traffic": traffic, "forecast_traffic": fcast_traffic,
                })
    return rows


def _staffing(revenue, daypart):
    hours_per_shift = [d for d in DAYPARTS if d[0]==daypart][0][2] - [d for d in DAYPARTS if d[0]==daypart][0][1]
    labor_hours = max(0.0, revenue / TARGET_RPLH[daypart])
    headcount = max(0, int(round(labor_hours / hours_per_shift)))
    floors = ROLE_FLOORS[daypart]
    mix = ROLE_MIX[daypart]
    assigned = {r: floors[r] for r in ROLES}
    remaining = max(0, headcount - sum(assigned.values()))
    order = sorted(ROLES, key=lambda r: -mix[r])
    i = 0
    while remaining > 0:
        assigned[order[i % len(order)]] += 1
        remaining -= 1
        i += 1
    out = {}
    for r, hc in assigned.items():
        h = hc * hours_per_shift
        c = h * ROLE_RATES[r]
        out[r] = (hc, round(h, 1), round(c, 2))
    return out


def gen_labor_daypart(sales_dp_rows):
    rows = []
    for sr in sales_dp_rows:
        dp = sr["daypart"]
        actual = _staffing(float(sr["revenue"]), dp)
        forecast = _staffing(float(sr["forecast_revenue"]), dp)
        for role in ROLES:
            ah, ahours, acost = actual[role]
            fh, fhours, fcost = forecast[role]
            rows.append({
                "date": sr["date"], "store_id": sr["store_id"], "daypart": dp, "role": role,
                "headcount": ah, "total_hours": ahours, "labor_cost": dec(acost),
                "forecast_headcount": fh, "forecast_labor_cost": dec(fcost),
            })
    return rows


def gen_sales_inventory(stores, items, days, end_date):
    """Generate per-SKU daily inventory + sales.

    Daily usage is small (1-7 units of the SKU/day; a "unit" is the package
    size — case of pepperoni, bag of mozzarella, etc). On-hand is correlated
    with reorder_point so realistic days-of-cover lands in the 3-9 day range
    when at par, 0.5-2 days when below par.
    """
    rows = []
    for d in range(days):
        cur = end_date - timedelta(days=d)
        for s in stores:
            for it in items:
                units = max(0, int(random.gauss(4, 1.5)))
                rev = round(units * float(it["retail_price"]), 2)
                reorder = random.choice([10, 20, 30])
                # 75% at-or-above par, 25% below par.
                if random.random() < 0.75:
                    on_hand = max(0, int(random.gauss(reorder * 1.3, reorder * 0.3)))
                else:
                    on_hand = max(0, int(random.gauss(reorder * 0.4, reorder * 0.2)))
                rows.append({
                    "date": cur, "store_id": s["store_id"], "sku": it["sku"],
                    "units_sold": units, "revenue": dec(rev),
                    "on_hand_eod": on_hand, "reorder_point": reorder,
                })
    return rows


def gen_purchase_orders(stores, items, inventory_rows, end_date, cfg, pos_per_store=5):
    now = datetime.combine(end_date, datetime.min.time()).replace(hour=13)
    items_by_sku = {it["sku"]: it for it in items}
    latest = {}
    for r in inventory_rows:
        key = (r["store_id"], r["sku"])
        if key not in latest or r["date"] > latest[key]["date"]:
            latest[key] = r
    vendors = cfg["vendor_by_category"]
    rows = []
    po_n = 1
    for s in stores:
        low = []
        for sku, it in items_by_sku.items():
            snap = latest.get((s["store_id"], sku))
            if snap and snap["on_hand_eod"] < snap["reorder_point"]:
                low.append((it, snap))
        if not low:
            continue
        by_cat = {}
        for it, snap in low:
            by_cat.setdefault(it["category"], []).append((it, snap))
        for cat in list(by_cat.keys())[:pos_per_store]:
            vendor_name, lead = vendors.get(cat, ("General Supply", 2))
            po_id = f"PO-{po_n:06d}"
            po_n += 1
            created = now - timedelta(hours=random.randint(2, 20))
            eta = created + timedelta(days=lead, hours=random.randint(-2, 6))
            status = random.choices(["staged", "released", "delivered"], weights=[6, 3, 1])[0]
            for it, snap in by_cat[cat][:6]:
                par = snap["reorder_point"]
                qty = max(1, par - snap["on_hand_eod"] + random.randint(0, 4))
                line_total = round(qty * float(it["cost"]), 2)
                trend = random.choices(["+22% usage", "+18% usage", "+9% usage", "steady", "steady"], k=1)[0]
                rows.append({
                    "po_id": po_id, "store_id": s["store_id"],
                    "vendor_name": vendor_name, "vendor_category": cat, "lead_time_days": lead,
                    "sku": it["sku"], "qty": qty,
                    "unit_cost": dec(float(it["cost"])), "line_total": dec(line_total),
                    "on_hand_at_creation": snap["on_hand_eod"], "par": par, "usage_trend": trend,
                    "created_at": created, "eta": eta, "status": status,
                })
    return rows


def _drafted_reply(rating, theme, city, cfg):
    brand_phrase = cfg.get("reply_brand_phrase", "our team")
    if rating >= 4:
        return f"Thanks for the kind words about our {city} location! We'll share this with the team."
    if rating == 3 and theme == "stockout":
        return f"Hi, sorry we ran out at {city}. We've bumped the order and you should be covered next time."
    if rating == 3 and theme == "pickup_wait":
        return f"Thanks for the patience at {city}. We're adding a runner for that pickup window."
    if rating == 3:
        return f"Appreciate the feedback. We'd love to make your next visit even better."
    if theme == "pickup_wait":
        return f"Hi, sorry we held you up at {city}. We've added a runner for the busy pickup window."
    if theme == "stockout":
        return f"Hi, sorry the item was out at {city}. {brand_phrase} has increased the order so you'll be covered on your next visit."
    return f"Hi, we're sorry your {city} visit fell short. Reach out to our store manager so we can make it right."


def gen_feedback(fake: Faker, stores, n: int, end_date, cfg):
    rows = []
    themes_list = list(THEME_WEIGHTS.keys())
    weights = list(THEME_WEIGHTS.values())
    templates_by_theme = cfg["review_templates"]
    for i in range(n):
        s = random.choice(stores)
        ch = random.choice(FEEDBACK_CHANNELS)
        rating = random.choices([1, 2, 3, 4, 5], weights=[1, 1, 2, 4, 4])[0]
        theme = random.choices(themes_list, weights=weights)[0]
        if rating >= 4 and theme in ("pickup_wait", "stockout", "value"):
            theme = "friendly_staff" if random.random() < 0.5 else "freshness"
        if rating <= 2 and theme in ("friendly_staff", "freshness"):
            theme = random.choices(["pickup_wait", "stockout", "value"], k=1)[0]
        sent = "pos" if rating >= 4 else ("neg" if rating <= 2 else "neu")
        text = random.choice(templates_by_theme[theme]).format(city=s["city"], n=random.randint(10, 25))
        needs_reply = (rating <= 3 and random.random() < 0.6) or random.random() < 0.05
        rows.append({
            "feedback_id": f"FB-{i+1:06d}",
            "date": end_date - timedelta(days=random.randint(0, 60)),
            "store_id": s["store_id"], "channel": ch, "rating": rating,
            "feedback_text": text, "sentiment_label": sent, "theme": theme,
            "nps": (rating * 25 - 50) if ch == "survey" else None,
            "needs_reply": needs_reply,
            "ai_drafted_reply": _drafted_reply(rating, theme, s["city"], cfg),
        })
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="DEFAULT")
    ap.add_argument("--catalog", default="ioc_sandbox")
    ap.add_argument("--schema", default="vibe_workshop")
    ap.add_argument("--company", default="lce", choices=sorted(COMPANY_CONFIGS.keys()),
                    help="Brand / company config to use for items, stores, and review language")
    ap.add_argument("--stores", type=int, default=20)
    ap.add_argument("--items", type=int, default=50)
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--end-date", type=parse_date, default=date.today(),
                    help="Latest date in the generated data, YYYY-MM-DD. Defaults to today.")
    ap.add_argument("--feedback", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)
    fake = Faker()
    Faker.seed(args.seed)

    cfg = COMPANY_CONFIGS[args.company]
    print(f"generating company={args.company} ({cfg['brand']}), end_date={args.end_date}, days={args.days}")

    spark = build_spark(args.profile)
    spark.sql(f"USE CATALOG {args.catalog}")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {args.schema}")
    spark.sql(f"USE SCHEMA {args.schema}")

    stores = gen_stores(fake, args.stores, cfg)
    items = gen_items(args.items, cfg)
    employees = gen_employees(fake, stores, args.end_date)
    write_table(spark, stores, "dims_stores")
    write_table(spark, items, "dims_items")
    write_table(spark, employees, "dims_employees")

    sales_dp = gen_sales_daypart(stores, args.days, args.end_date)
    write_table(spark, sales_dp, "facts_sales_daypart")

    labor_dp = gen_labor_daypart(sales_dp)
    write_table(spark, labor_dp, "facts_labor_daypart")

    inventory = gen_sales_inventory(stores, items, args.days, args.end_date)
    write_table(spark, inventory, "facts_sales_inventory_daily")

    pos = gen_purchase_orders(stores, items, inventory, args.end_date, cfg)
    write_table(spark, pos, "facts_purchase_orders")

    feedback = gen_feedback(fake, stores, args.feedback, args.end_date, cfg)
    write_table(spark, feedback, "facts_customer_feedback")

    print("done.")


if __name__ == "__main__":
    main()
