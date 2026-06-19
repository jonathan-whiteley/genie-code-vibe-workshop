# Databricks notebook source
# MAGIC %md
# MAGIC # Create Genie space bound to the command_center_metrics metric view
# MAGIC
# MAGIC Creates a Genie space titled "Command Center reference" with the
# MAGIC command_center_metrics metric view as the primary data source and
# MAGIC pre-baked sample questions aligned to the governed measures. Idempotent:
# MAGIC if a space with the same title already exists in this workspace, it is
# MAGIC PATCHed in place.
# MAGIC
# MAGIC Lifted from the lakehouse-market 06_ensure_genie_space pattern
# MAGIC (proto schema v2, sorted ids for stable diffs).

# COMMAND ----------
dbutils.widgets.text("catalog", "ioc_sandbox")
dbutils.widgets.text("schema", "vibe_workshop")
dbutils.widgets.text("warehouse_id", "")
dbutils.widgets.text("space_id", "")

# COMMAND ----------
# MAGIC %pip install -q --upgrade "databricks-sdk>=0.40"

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
# Re-read widgets after the Python restart.
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
WAREHOUSE_ID = dbutils.widgets.get("warehouse_id")
EXISTING_SPACE_ID = dbutils.widgets.get("space_id").strip()

if not WAREHOUSE_ID:
    raise ValueError("warehouse_id task parameter is required")

TITLE = "Command Center reference"
DESCRIPTION = (
    "Reference Genie space for the ucode Vibe Coding workshop. Answers questions "
    "about sales performance and labor efficiency across 20 stores. "
    "Powered by the command_center_metrics metric view. Drives the Ask Genie panel "
    "in the Command Center app."
)
INSTRUCTIONS = (
    "You are answering questions for an operator using the Command Center app. "
    "The primary data source is the command_center_metrics metric view, which "
    "provides governed sales and labor measures at store x date grain: "
    "revenue (total sales), forecast_revenue (planned revenue target), "
    "traffic (guest count), labor_cost (total labor spend), "
    "forecast_labor_cost (planned labor budget), and labor_pct_of_sales "
    "(labor cost divided by revenue). "
    "Dimensions available are date, store_id, store_name, region, and day_of_week. "
    "The dataset covers 20 stores. Anchor 'today' to MAX(date) in the metric view, "
    "not current_date(). Use MEASURE() syntax when querying governed measures "
    "(e.g. SELECT date, MEASURE(labor_pct_of_sales) FROM command_center_metrics). "
    "If the user asks about daypart breakdowns that require the underlying "
    "fact tables, note that more granular data may not be available in this space."
)

import json
from uuid import uuid4

from databricks.sdk import WorkspaceClient

# The metric view is the primary (and sole required) data source.
# Raw fact tables may be added here as secondary sources for daypart or
# SKU-level drill-downs if needed; keep the metric view first.
TABLES = [
    f"{CATALOG}.{SCHEMA}.command_center_metrics",
]

SAMPLE_QUESTIONS = [
    "Which 5 stores had the highest labor % of sales last week?",
    "How has labor % of sales trended over the last 30 days?",
    "Which stores are below their revenue forecast this week?",
    "Show the revenue trend over the last 30 days.",
    "How did labor cost track against its forecast this week?",
    "Which region has the highest revenue this month?",
]

EXAMPLE_SQLS = [
    {
        "title": "Revenue by region, last 30 days",
        "sql": (
            f"SELECT region, MEASURE(revenue) AS revenue "
            f"FROM {CATALOG}.{SCHEMA}.command_center_metrics "
            f"WHERE date >= (SELECT MAX(date) - 30 FROM {CATALOG}.{SCHEMA}.command_center_metrics) "
            f"GROUP BY region ORDER BY revenue DESC"
        ),
    },
    {
        "title": "Labor % of sales trend by date, last 30 days",
        "sql": (
            f"SELECT date, MEASURE(labor_pct_of_sales) AS labor_pct "
            f"FROM {CATALOG}.{SCHEMA}.command_center_metrics "
            f"WHERE date >= (SELECT MAX(date) - 30 FROM {CATALOG}.{SCHEMA}.command_center_metrics) "
            f"GROUP BY date ORDER BY date"
        ),
    },
    {
        "title": "Revenue vs forecast by store, current week",
        "sql": (
            f"SELECT store_name, MEASURE(revenue) AS revenue, MEASURE(forecast_revenue) AS forecast_revenue "
            f"FROM {CATALOG}.{SCHEMA}.command_center_metrics "
            f"WHERE date >= (SELECT MAX(date) - 7 FROM {CATALOG}.{SCHEMA}.command_center_metrics) "
            f"GROUP BY store_name ORDER BY revenue DESC"
        ),
    },
    {
        "title": "Top 5 stores by labor % of sales, last 7 days",
        "sql": (
            f"SELECT store_name, MEASURE(labor_pct_of_sales) AS labor_pct "
            f"FROM {CATALOG}.{SCHEMA}.command_center_metrics "
            f"WHERE date >= (SELECT MAX(date) - 7 FROM {CATALOG}.{SCHEMA}.command_center_metrics) "
            f"GROUP BY store_name ORDER BY labor_pct DESC LIMIT 5"
        ),
    },
]


def build_serialized_space() -> dict:
    example_sqls = sorted(
        [
            {"id": uuid4().hex, "question": [e["title"]], "sql": [e["sql"]]}
            for e in EXAMPLE_SQLS
        ],
        key=lambda x: x["id"],
    )
    sample_qs = sorted(
        [{"id": uuid4().hex, "question": [q]} for q in SAMPLE_QUESTIONS],
        key=lambda x: x["id"],
    )
    return {
        "version": 2,
        "data_sources": {
            "tables": sorted(
                [{"identifier": t} for t in TABLES],
                key=lambda x: x["identifier"],
            )
        },
        "instructions": {
            "text_instructions": [{"id": uuid4().hex, "content": [INSTRUCTIONS]}],
            "example_question_sqls": example_sqls,
        },
        "config": {"sample_questions": sample_qs},
    }


# COMMAND ----------
w = WorkspaceClient()

# Look for an existing space with our title (idempotent).
space_id = EXISTING_SPACE_ID
if not space_id:
    try:
        listing = w.api_client.do("GET", "/api/2.0/genie/spaces") or {}
        for sp in listing.get("spaces", []):
            if sp.get("title") == TITLE:
                space_id = sp.get("space_id", "")
                break
    except Exception as e:
        print(f"WARNING: could not list existing spaces ({e}); will attempt create")

payload = {
    "title": TITLE,
    "description": DESCRIPTION,
    "warehouse_id": WAREHOUSE_ID,
    "serialized_space": json.dumps(build_serialized_space()),
}

if space_id:
    print(f"Patching existing Genie space {space_id} ...")
    resp = w.api_client.do("PATCH", f"/api/2.0/genie/spaces/{space_id}", body=payload)
    final_space_id = resp.get("space_id") or space_id
    print(f"Patched: {resp.get('title')} ({final_space_id})")
else:
    print("Creating new Genie space ...")
    resp = w.api_client.do("POST", "/api/2.0/genie/spaces", body=payload)
    final_space_id = resp.get("space_id")
    print(f"Created: {resp.get('title')} ({final_space_id})")
    print(f"  URL: {w.config.host}/genie/rooms/{final_space_id}")

# Publish the resolved config to a known workspace file so the App can pick
# it up at startup without any app.yaml hand-edit or env-var rewiring.
import base64
config_path = "/Workspace/Shared/command-center/config.json"
config_payload = {
    "catalog": CATALOG,
    "schema": SCHEMA,
    "warehouse_id": WAREHOUSE_ID,
    "genie_space_id": final_space_id,
}
config_json = json.dumps(config_payload, indent=2)
# Ensure parent dir exists. mkdirs is idempotent.
try:
    w.api_client.do("POST", "/api/2.0/workspace/mkdirs", body={"path": "/Workspace/Shared/command-center"})
except Exception:
    pass
w.api_client.do(
    "POST",
    "/api/2.0/workspace/import",
    body={
        "path": config_path,
        "format": "AUTO",
        "content": base64.b64encode(config_json.encode()).decode(),
        "overwrite": True,
    },
)
print()
print(f"  Wrote {config_path}:")
print(config_json)
print()
print("  Restart the App (`databricks bundle run command_center_app -t <target>`)")
print("  to pick up the new config.")
