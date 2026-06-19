-- ucode Vibe Coding Workshop: Operator Command Center schema
-- Target: ioc_sandbox.vibe_workshop  (dev: jdub_demo.vibe_workshop)
--
-- 8 tables (3 dims + 5 facts). Every chart and AI insight in the design has a
-- backing column or table; nothing is computed via on-the-fly AI calls. SQL
-- rollups are still expected (e.g. daily sentiment timeline is GROUP BY on
-- sentiment_label).

USE CATALOG ioc_sandbox;
CREATE SCHEMA IF NOT EXISTS vibe_workshop;
USE SCHEMA vibe_workshop;

-- ========================================================================
-- DIMS
-- ========================================================================

CREATE OR REPLACE TABLE dims_stores (
  store_id        STRING NOT NULL,
  store_name      STRING,
  region          STRING,
  city            STRING,
  state           STRING,
  square_footage  INT
);

CREATE OR REPLACE TABLE dims_items (
  sku           STRING NOT NULL,
  item_name     STRING,
  category      STRING,
  retail_price  DECIMAL(10,2),
  cost          DECIMAL(10,2)
);

-- Team-member roster. Drives the role mix on the Labor planner and the
-- "who is scheduled?" view. Per design: roles are cook / cashier / lead / manager.
CREATE OR REPLACE TABLE dims_employees (
  employee_id  STRING NOT NULL,
  store_id     STRING,
  name         STRING,
  role         STRING,
  hourly_rate  DECIMAL(6,2),
  hire_date    DATE
);

-- ========================================================================
-- FACTS
-- ========================================================================

-- Daypart-grain sales. Drives the Labor planner hero (predicted sales,
-- labor % verdict) and the 4 daypart cards (Breakfast / Lunch / Dinner / Late).
-- Forecast columns are pre-staged so the UI never calls ai_forecast at render.
CREATE OR REPLACE TABLE facts_sales_daypart (
  date              DATE,
  store_id          STRING,
  daypart           STRING,            -- breakfast | lunch | dinner | late
  hour_start        INT,
  hour_end          INT,
  revenue           DECIMAL(10,2),
  forecast_revenue  DECIMAL(10,2),
  traffic           INT,
  forecast_traffic  INT
);

-- Daypart x role-grain labor. Drives the Labor planner crew/cost
-- recommendations and the labor-% on the hero.
CREATE OR REPLACE TABLE facts_labor_daypart (
  date                  DATE,
  store_id              STRING,
  daypart               STRING,
  role                  STRING,
  headcount             INT,
  total_hours           DOUBLE,
  labor_cost            DECIMAL(10,2),
  forecast_headcount    INT,
  forecast_labor_cost   DECIMAL(10,2)
);

-- SKU-grain inventory + per-SKU sales. Drives the Inventory stock-health
-- donut, days-of-cover, fill-rate-by-category, stock-value trend, and the
-- watched-items list.
CREATE OR REPLACE TABLE facts_sales_inventory_daily (
  date           DATE,
  store_id       STRING,
  sku            STRING,
  units_sold     INT,
  revenue        DECIMAL(10,2),
  on_hand_eod    INT,
  reorder_point  INT
);

-- Pre-staged purchase orders. One row per (PO, SKU) line; vendor info is
-- denormalized onto the row to keep the table count low.
CREATE OR REPLACE TABLE facts_purchase_orders (
  po_id                STRING NOT NULL,
  store_id             STRING,
  vendor_name          STRING,
  vendor_category      STRING,         -- produce | proteins | dry_goods | beverage
  lead_time_days       INT,
  sku                  STRING,
  qty                  INT,
  unit_cost            DECIMAL(10,2),
  line_total           DECIMAL(10,2),
  on_hand_at_creation  INT,
  par                  INT,
  usage_trend          STRING,         -- '+22% usage' | 'steady' | ...
  created_at           TIMESTAMP,
  eta                  TIMESTAMP,
  status               STRING          -- staged | released | delivered
);

-- Guest feedback with pre-staged sentiment, theme, and AI-drafted reply.
-- Sentiment timeline + theme tiles are SQL rollups against this table.
CREATE OR REPLACE TABLE facts_customer_feedback (
  feedback_id        STRING NOT NULL,
  date               DATE,
  store_id           STRING,
  channel            STRING,           -- google | yelp | app | survey | social
  rating             INT,              -- 1-5
  feedback_text      STRING,
  sentiment_label    STRING,           -- pos | neu | neg
  theme              STRING,           -- pickup_wait | stockout | friendly_staff | freshness | value | other
  nps                INT,              -- populated only for channel = survey
  needs_reply        BOOLEAN,
  ai_drafted_reply   STRING
);
