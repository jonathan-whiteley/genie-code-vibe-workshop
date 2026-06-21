# Databricks notebook source
# MAGIC %md
# MAGIC # Create Metric View: command_center_metrics
# MAGIC
# MAGIC Creates (or replaces) the `command_center_metrics` metric view in Unity Catalog
# MAGIC using the governed YAML definition. The YAML is inlined here so the notebook
# MAGIC is self-contained on serverless compute with no external file reads required.
# MAGIC
# MAGIC Note: confirm the exact `WITH METRICS LANGUAGE YAML` DDL syntax against the
# MAGIC `databricks-metric-views` skill at execution time; if the runtime expects a
# MAGIC different form (e.g. `CREATE VIEW ... WITH METRICS AS $$...$$`), update
# MAGIC accordingly. The skill is authoritative on syntax.

# COMMAND ----------
dbutils.widgets.text("catalog", "ioc_sandbox")
dbutils.widgets.text("schema", "vibe_workshop")
dbutils.widgets.text("warehouse_id", "")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Inline YAML definition (kept in sync with data/metric-views/command_center_metrics.yaml)

# COMMAND ----------
# The metric view YAML (kept in sync with data/metric-views/command_center_metrics.yaml).
# Source tables use parameterized catalog/schema so the same notebook works across
# any target catalog without editing.
METRIC_YAML = r'''
version: "0.1"
source: |
  SELECT
    s.date, s.store_id, st.store_name, st.region,
    date_format(s.date, 'EEEE') AS day_of_week,
    s.revenue, s.forecast_revenue, s.traffic,
    l.labor_cost, l.forecast_labor_cost
  FROM (
    SELECT date, store_id,
           SUM(revenue) AS revenue,
           SUM(forecast_revenue) AS forecast_revenue,
           SUM(traffic) AS traffic
    FROM {cat}.{sch}.facts_sales_daypart
    GROUP BY date, store_id
  ) s
  LEFT JOIN (
    SELECT date, store_id,
           SUM(labor_cost) AS labor_cost,
           SUM(forecast_labor_cost) AS forecast_labor_cost
    FROM {cat}.{sch}.facts_labor_daypart
    GROUP BY date, store_id
  ) l USING (date, store_id)
  JOIN {cat}.{sch}.dims_stores st USING (store_id)
dimensions:
  - name: date
    expr: date
  - name: store_id
    expr: store_id
  - name: store_name
    expr: store_name
  - name: region
    expr: region
  - name: day_of_week
    expr: day_of_week
measures:
  - name: revenue
    expr: SUM(revenue)
  - name: forecast_revenue
    expr: SUM(forecast_revenue)
  - name: traffic
    expr: SUM(traffic)
  - name: labor_cost
    expr: SUM(labor_cost)
  - name: forecast_labor_cost
    expr: SUM(forecast_labor_cost)
  - name: labor_pct_of_sales
    expr: SUM(labor_cost) / NULLIF(SUM(revenue), 0)
'''.format(cat=CATALOG, sch=SCHEMA)

fqn = f"{CATALOG}.{SCHEMA}.command_center_metrics"
spark.sql(f"CREATE OR REPLACE VIEW {fqn} WITH METRICS LANGUAGE YAML AS $$ {METRIC_YAML} $$")
print(f"Created metric view {fqn}")
display(spark.sql(f"SELECT * FROM {fqn} LIMIT 5"))
