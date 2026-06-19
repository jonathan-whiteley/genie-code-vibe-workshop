# Workshop Data

**8 tables** under `ioc_sandbox.vibe_workshop` (dev: `jdub_demo.vibe_workshop`). 3 dims + 5 facts. Every chart and AI insight in the Homebase design has a backing column or table; nothing is left to be computed at runtime via on-the-fly AI calls.

## Volume targets

- 20 stores
- 50 SKUs
- 365 days of history
- 4 dayparts per day per store (breakfast / lunch / dinner / late)
- ~12 employees per store (5 cooks, 4 cashiers, 2 leads, 1 manager)
- ~1000 customer feedback rows (pre-staged with sentiment, theme, AI-drafted reply)
- ~5 staged purchase orders per store

## Tables

### Dims

**`dims_stores`**

| Column | Type |
|---|---|
| `store_id` | STRING |
| `store_name` | STRING |
| `region` | STRING |
| `city` | STRING |
| `state` | STRING |
| `square_footage` | INT |

**`dims_items`**

| Column | Type |
|---|---|
| `sku` | STRING |
| `item_name` | STRING |
| `category` | STRING (produce \| proteins \| dry_goods \| beverage) |
| `retail_price` | DECIMAL(10,2) |
| `cost` | DECIMAL(10,2) |

**`dims_employees`** — team-member roster; drives the Labor planner role mix

| Column | Type |
|---|---|
| `employee_id` | STRING |
| `store_id` | STRING |
| `name` | STRING |
| `role` | STRING (cook \| cashier \| lead \| manager) |
| `hourly_rate` | DECIMAL(6,2) |
| `hire_date` | DATE |

### Facts

**`facts_sales_daypart`** — daypart-grain sales + forecast

| Column | Type | Notes |
|---|---|---|
| `date` | DATE | |
| `store_id` | STRING | FK |
| `daypart` | STRING | breakfast \| lunch \| dinner \| late |
| `hour_start`, `hour_end` | INT | e.g. breakfast = 6-10 |
| `revenue`, `traffic` | DECIMAL / INT | Actuals |
| `forecast_revenue`, `forecast_traffic` | DECIMAL / INT | Pre-staged so the App never calls ai_forecast |

**`facts_labor_daypart`** — daypart × role-grain labor + forecast

| Column | Type | Notes |
|---|---|---|
| `date` | DATE | |
| `store_id` | STRING | FK |
| `daypart` | STRING | |
| `role` | STRING | cook \| cashier \| lead \| manager |
| `headcount`, `total_hours`, `labor_cost` | mixed | Actuals |
| `forecast_headcount`, `forecast_labor_cost` | mixed | Pre-staged |

**`facts_sales_inventory_daily`** — SKU-grain inventory + per-SKU sales

| Column | Type | Notes |
|---|---|---|
| `date` | DATE | |
| `store_id` | STRING | FK |
| `sku` | STRING | FK to `dims_items` |
| `units_sold` | INT | |
| `revenue` | DECIMAL(10,2) | |
| `on_hand_eod` | INT | End-of-day inventory |
| `reorder_point` | INT | |

**`facts_purchase_orders`** — pre-staged POs; flattened, one row per PO line

| Column | Type | Notes |
|---|---|---|
| `po_id` | STRING | |
| `store_id` | STRING | FK |
| `vendor_name`, `vendor_category`, `lead_time_days` | mixed | Denormalized vendor info |
| `sku`, `qty`, `unit_cost`, `line_total` | mixed | Line detail |
| `on_hand_at_creation`, `par`, `usage_trend` | mixed | Context the design shows on each line |
| `created_at`, `eta` | TIMESTAMP | |
| `status` | STRING | staged \| released \| delivered |

**`facts_customer_feedback`** — guest reviews with pre-staged AI outputs

| Column | Type | Notes |
|---|---|---|
| `feedback_id` | STRING | |
| `date` | DATE | |
| `store_id` | STRING | FK |
| `channel` | STRING | google \| yelp \| app \| survey \| social |
| `rating` | INT | 1-5 |
| `feedback_text` | STRING | |
| `sentiment_label` | STRING | pos \| neu \| neg (pre-staged) |
| `theme` | STRING | pickup_wait \| stockout \| friendly_staff \| freshness \| value \| other (pre-staged) |
| `nps` | INT | populated only for `channel = survey` |
| `needs_reply` | BOOLEAN | |
| `ai_drafted_reply` | STRING | pre-staged template reply |

## Regenerating the data

```bash
cd data
pip install -r requirements.txt
python generate_data.py --profile DEFAULT --catalog jdub_demo --schema vibe_workshop
```

CLI flags: `--stores`, `--items`, `--days`, `--feedback`, `--seed`.

## Granting access

After generation, grant the attendee group `SELECT` on all 8 tables and `USE CATALOG` / `USE SCHEMA`:

```sql
GRANT USE CATALOG ON CATALOG ioc_sandbox TO `<attendee_group>`;
GRANT USE SCHEMA ON SCHEMA ioc_sandbox.vibe_workshop TO `<attendee_group>`;
GRANT SELECT ON SCHEMA ioc_sandbox.vibe_workshop TO `<attendee_group>`;
```
