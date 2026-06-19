# Databricks notebook source
# MAGIC %md
# MAGIC # Init Lakebase: workshop write-back tables
# MAGIC
# MAGIC Creates 3 Postgres tables in the shared `command-center-lakebase`
# MAGIC instance. All attendee Apps' SPs get INSERT/SELECT on these so the
# MAGIC Release / Reply / Approve actions in the UI persist somewhere.
# MAGIC
# MAGIC Tables:
# MAGIC - `purchase_orders_released` — Reorders module Release button
# MAGIC - `review_replies` — Guest Feedback Send Reply button
# MAGIC - `schedules_approved` — Labor planner Approve Schedule button

# COMMAND ----------
dbutils.widgets.text("lakebase_instance_name", "command-center-lakebase")
dbutils.widgets.text("attendee_group", "users")

# COMMAND ----------
# MAGIC %pip install -q psycopg2-binary "databricks-sdk>=0.40"

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
# Re-read widgets after the Python restart wipes the global namespace.
LAKEBASE_NAME = dbutils.widgets.get("lakebase_instance_name")
ATTENDEE_GROUP = dbutils.widgets.get("attendee_group")

from databricks.sdk import WorkspaceClient
import psycopg2

w = WorkspaceClient()

# Lakebase API surface varies across SDK versions. Prefer w.database; fall back
# to raw REST so this notebook keeps working as the SDK evolves.
def _get_instance(name: str) -> dict:
    if hasattr(w, "database"):
        inst = w.database.get_database_instance(name=name)
        return {"name": inst.name, "read_write_dns": inst.read_write_dns}
    out = w.api_client.do("GET", f"/api/2.0/database/instances/{name}")
    return {
        "name": out.get("name", name),
        "read_write_dns": out.get("read_write_dns") or out.get("readWriteDns"),
    }


def _mint_credential(name: str) -> str:
    if hasattr(w, "database"):
        cred = w.database.generate_database_credential(instance_names=[name])
        token = getattr(cred, "token", None) or (cred if isinstance(cred, str) else None)
        if token:
            return token
    out = w.api_client.do(
        "POST",
        "/api/2.0/database/credentials",
        body={"instance_names": [name], "request_id": "workshop-setup"},
    )
    token = out.get("token") if isinstance(out, dict) else None
    if not token:
        raise RuntimeError(f"could not mint Lakebase credential: {out!r}")
    return token


try:
    inst = _get_instance(LAKEBASE_NAME)
except Exception as e:
    raise RuntimeError(
        f"Lakebase instance '{LAKEBASE_NAME}' not found. "
        f"Either the bundle deploy failed to create it (admin required), or it was named differently. "
        f"Create it manually in the workspace UI and rerun this task. Underlying error: {e}"
    )

print(f"Lakebase instance: {inst['name']}")
print(f"  read_write_dns: {inst['read_write_dns']}")

token = _mint_credential(LAKEBASE_NAME)

# COMMAND ----------
# Connect via psycopg2 and apply DDL + grants.
conn = psycopg2.connect(
    host=inst["read_write_dns"],
    port=5432,
    database="databricks_postgres",
    user=w.current_user.me().user_name,
    password=token,
    sslmode="require",
)
conn.autocommit = True
cur = conn.cursor()

DDL = [
    """CREATE TABLE IF NOT EXISTS purchase_orders_released (
         event_id SERIAL PRIMARY KEY,
         po_id TEXT NOT NULL,
         store_id TEXT,
         total_amount NUMERIC,
         released_by TEXT NOT NULL,
         released_at TIMESTAMP DEFAULT NOW()
       )""",
    """CREATE TABLE IF NOT EXISTS review_replies (
         event_id SERIAL PRIMARY KEY,
         feedback_id TEXT NOT NULL,
         store_id TEXT,
         reply_text TEXT NOT NULL,
         replied_by TEXT NOT NULL,
         replied_at TIMESTAMP DEFAULT NOW()
       )""",
    """CREATE TABLE IF NOT EXISTS schedules_approved (
         event_id SERIAL PRIMARY KEY,
         schedule_date DATE NOT NULL,
         store_id TEXT,
         total_hours NUMERIC,
         approved_by TEXT NOT NULL,
         approved_at TIMESTAMP DEFAULT NOW()
       )""",
]
for stmt in DDL:
    cur.execute(stmt)
    print(f"applied: {stmt.split('(')[0].strip()}")

GRANTS = [
    "GRANT INSERT, SELECT ON purchase_orders_released TO PUBLIC",
    "GRANT INSERT, SELECT ON review_replies TO PUBLIC",
    "GRANT INSERT, SELECT ON schedules_approved TO PUBLIC",
    # SERIAL columns are backed by sequences; INSERT requires USAGE on the seq.
    "GRANT USAGE, SELECT ON SEQUENCE purchase_orders_released_event_id_seq TO PUBLIC",
    "GRANT USAGE, SELECT ON SEQUENCE review_replies_event_id_seq TO PUBLIC",
    "GRANT USAGE, SELECT ON SEQUENCE schedules_approved_event_id_seq TO PUBLIC",
]
for stmt in GRANTS:
    try:
        cur.execute(stmt)
        print(f"granted: {stmt}")
    except Exception as e:
        print(f"grant warning ({stmt}): {e}")

cur.close()
conn.close()
print("done.")
