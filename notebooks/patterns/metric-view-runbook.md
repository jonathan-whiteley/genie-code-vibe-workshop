# Authoring the Command Center Metric View

A Unity Catalog metric view that governs the workshop's KPIs at **store x date** grain, defined once over sales and labor facts and reused by Genie (Module 2) and the AI/BI dashboard (Module 3). Named `<initials>_command_center_metrics` in `ioc_sandbox.vibe_workshop`.

It spans two fact tables (`facts_sales_daypart`, `facts_labor_daypart`) plus the `dims_stores` dimension. Measures: revenue, forecast_revenue, traffic, labor_cost, forecast_labor_cost, labor_pct_of_sales. Dimensions: date, store_id, store_name, region, day_of_week.

---

## Key Gotchas & Fixes

### 1. The fan-out trap (most important)

Both fact tables are at **daypart** grain (multiple rows per store per date: breakfast, lunch, dinner, etc.). If you join them directly on `(date, store_id)` at raw daypart grain and then aggregate, every sales row matches every labor row for the same store-date, so rows multiply. The cross-product inflates the labor and revenue sums unevenly, and `labor_pct_of_sales` comes out impossible (often around 200%).

- **Fix**: pre-aggregate EACH fact table to exactly one row per `(date, store_id)` in its OWN subquery FIRST. Then join the two rollups on `(date, store_id)`, then join `dims_stores` for region. Never join raw daypart rows to raw daypart rows.
- The reference YAML's `source` SELECT below shows exactly this: two `GROUP BY date, store_id` subqueries, joined `USING (date, store_id)`, then `dims_stores` joined `USING (store_id)`.
- Do NOT create separate or intermediary views for the rollups; they live inline in the metric view's `source`.

### 2. Inner join to dims_stores drops rows

The `dims_stores` join is an inner `JOIN`, so any fact rows whose `store_id` has no matching store row are dropped. That is intentional (keeps the grain clean), but verify the resulting store count matches expectations; a missing store in the dim silently removes its data.

### 3. Metric view DDL syntax is runtime-version-dependent

The view is created with:

```sql
CREATE OR REPLACE VIEW ... WITH METRICS LANGUAGE YAML AS $$ ... $$
```

This `WITH METRICS LANGUAGE YAML` syntax may differ by Databricks runtime version. Confirm the exact DDL against the `databricks-metric-views` skill (or docs) in the target workspace before relying on it, and ALWAYS run a verification SELECT after creating the view.

### 4. Querying uses MEASURE(), not the raw expression

You cannot select the raw aggregate expression from a metric view. Wrap each measure in `MEASURE(...)` and reference dimensions by name:

```sql
SELECT region, MEASURE(revenue)
FROM <view>
GROUP BY region
```

Dashboards parameterize the view with `identifier(:catalog || '.' || :schema || '.<view>')`. If a runtime rejects `MEASURE()` or `identifier()`, fall back to the fully-qualified table name (`ioc_sandbox.vibe_workshop.<initials>_command_center_metrics`).

---

## Reference Implementation

The canonical working metric view (`metric-views/command_center_metrics.yaml`), verbatim:

```yaml
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
    FROM ioc_sandbox.vibe_workshop.facts_sales_daypart
    GROUP BY date, store_id
  ) s
  LEFT JOIN (
    SELECT date, store_id,
           SUM(labor_cost) AS labor_cost,
           SUM(forecast_labor_cost) AS forecast_labor_cost
    FROM ioc_sandbox.vibe_workshop.facts_labor_daypart
    GROUP BY date, store_id
  ) l USING (date, store_id)
  JOIN ioc_sandbox.vibe_workshop.dims_stores st USING (store_id)

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
```

Note the `NULLIF(SUM(revenue), 0)` guard on `labor_pct_of_sales`: it avoids divide-by-zero on store-dates with no revenue.

---

## Verification

After creating the view, confirm it returns rows and that the labor ratio is realistic:

```sql
SELECT
  MEASURE(revenue)            AS revenue,
  MEASURE(labor_cost)         AS labor_cost,
  MEASURE(labor_pct_of_sales) AS labor_pct
FROM <view>;
```

`labor_pct` should land roughly in the **0.20 to 0.35** range (20-35%). If it is near 2.0 (200%), the fan-out trap was not avoided: the facts were joined at raw daypart grain instead of being pre-aggregated first. A quick `SELECT * FROM <view> LIMIT 5` should also return rows (an empty result usually means the inner `dims_stores` join dropped everything).

---

## From-Scratch Checklist

1. Pre-aggregate `facts_sales_daypart` to one row per `(date, store_id)` in its own subquery (sum revenue, forecast_revenue, traffic).
2. Pre-aggregate `facts_labor_daypart` the same way in its own subquery (sum labor_cost, forecast_labor_cost).
3. Join the two rollups `USING (date, store_id)`, then join `dims_stores USING (store_id)` for region and store_name. No intermediary views.
4. Define dimensions: date, store_id, store_name, region, day_of_week (`day_of_week` via `date_format(date, 'EEEE')`).
5. Define measures: revenue, forecast_revenue, traffic, labor_cost, forecast_labor_cost, and labor_pct_of_sales as `SUM(labor_cost) / NULLIF(SUM(revenue), 0)`.
6. Create it with `CREATE OR REPLACE VIEW <initials>_command_center_metrics WITH METRICS LANGUAGE YAML AS $$ ... $$`; confirm the DDL against the `databricks-metric-views` skill first.
7. Run the verification SELECT with `MEASURE(...)`; confirm rows return and labor_pct_of_sales is 0.20-0.35.
8. If `MEASURE()` or `identifier()` is rejected at runtime, fall back to the fully-qualified table name.
