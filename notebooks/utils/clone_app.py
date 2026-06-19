# Databricks notebook source
# MAGIC %md
# MAGIC # Helper: Clone the Command Center App from the Template
# MAGIC
# MAGIC Called by `attendee_setup` via `%run`. It does the steps the in-workspace
# MAGIC coding agent (Genie Code) refuses to do: it copies the app source
# MAGIC (including binary assets), creates your app, binds its service principal
# MAGIC (SP) to the shared resources, grants the SP the warehouse and Unity Catalog
# MAGIC access it needs, and deploys.
# MAGIC
# MAGIC **What it solves that the agent cannot:**
# MAGIC - `apps update` resource bindings and `user_api_scopes` (permission calls).
# MAGIC - SQL `GRANT` on the catalog and schema (covers the tables and the metric view).
# MAGIC - Warehouse `CAN_USE` (a workspace-level permission, set via REST).
# MAGIC - Two runtime gotchas baked in: a faithful binary-safe source copy, and the
# MAGIC   `use_cloud_fetch=False` SQL-connector fix the Apps runtime requires.
# MAGIC
# MAGIC **Prerequisites:** the facilitator has deployed the `command-center-dev`
# MAGIC template app, and the attendee group already has `SELECT` on the schema,
# MAGIC `CAN_USE` on the warehouse, and `CAN_CONNECT` on Lakebase.
# MAGIC
# MAGIC Running this standalone (not through `attendee_setup`)? Run
# MAGIC `%pip install -q --upgrade "databricks-sdk>=0.40"` then
# MAGIC `dbutils.library.restartPython()` in cells above first. `attendee_setup`
# MAGIC already does this, so do not repeat it when called via `%run`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 0: Configuration
# MAGIC
# MAGIC Set your initials. Everything else (catalog, schema, tables, warehouse,
# MAGIC Lakebase, OBO scopes) is read from the template app in Step 1, so there is
# MAGIC a single source of truth and nothing to keep in sync by hand.

# COMMAND ----------

dbutils.widgets.text("initials", "", "Your initials (e.g. jjw)")
dbutils.widgets.text("template_app", "command-center-dev", "Template app to clone")
dbutils.widgets.text("source_override", "", "Source path override (blank = use template's)")
dbutils.widgets.dropdown("overwrite_source", "false", ["false", "true"], "Overwrite existing source dir")

INITIALS = dbutils.widgets.get("initials").strip().lower()
TEMPLATE_APP = dbutils.widgets.get("template_app").strip()
SOURCE_OVERRIDE = dbutils.widgets.get("source_override").strip()
OVERWRITE_SOURCE = dbutils.widgets.get("overwrite_source") == "true"

if not INITIALS:
    raise ValueError("Set the 'initials' widget before running (e.g. jjw).")

NEW_APP = f"{INITIALS}-command-center"

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
ME = w.current_user.me().user_name
NEW_APP_SOURCE = f"/Workspace/Users/{ME}/{NEW_APP}"

print(f"Template : {TEMPLATE_APP}")
print(f"New app  : {NEW_APP}")
print(f"You      : {ME}")
print(f"Source   : {NEW_APP_SOURCE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Read the template app
# MAGIC
# MAGIC The resources (warehouse, the 8 UC tables, Lakebase), the OBO scopes, and
# MAGIC the source path all come from the template. We reuse them verbatim.

# COMMAND ----------

template = w.api_client.do("GET", f"/api/2.0/apps/{TEMPLATE_APP}")

RESOURCES = template.get("resources", [])
USER_API_SCOPES = template.get("user_api_scopes", [])
TEMPLATE_SOURCE = SOURCE_OVERRIDE or template.get("default_source_code_path", "")


def _resource_kind(r):
    """Return the typed key of an app resource (sql_warehouse, uc_securable, ...)."""
    for k in ("sql_warehouse", "uc_securable", "database", "genie_space", "serving_endpoint", "secret"):
        if k in r:
            return k
    return "?"


if not TEMPLATE_SOURCE:
    raise ValueError(
        f"Template app '{TEMPLATE_APP}' has no default_source_code_path and no "
        "source_override was given. Set the 'source_override' widget to the app "
        "source path (e.g. the dab/src/app folder in your cloned Git folder)."
    )

print(f"Template source : {TEMPLATE_SOURCE}")
print(f"Resources ({len(RESOURCES)}):")
for r in RESOURCES:
    print(f"  [{_resource_kind(r)}] {r.get('name')}")
print(f"OBO scopes      : {USER_API_SCOPES}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Copy the source (binary-safe)
# MAGIC
# MAGIC `shutil.copytree` copies the whole tree, including the TTF fonts and SVGs
# MAGIC an editor-based agent cannot write. This is the reliable way to get a
# MAGIC faithful copy of an app that ships static assets.

# COMMAND ----------

import os
import shutil

if os.path.exists(NEW_APP_SOURCE):
    if OVERWRITE_SOURCE:
        shutil.rmtree(NEW_APP_SOURCE)
        print(f"Removed existing {NEW_APP_SOURCE} (overwrite_source=true).")
    else:
        print(
            f"Source already exists: {NEW_APP_SOURCE}\n"
            "Leaving it in place. Set the 'overwrite_source' widget to true to "
            "replace it with a fresh copy of the template."
        )

if not os.path.exists(NEW_APP_SOURCE):
    shutil.copytree(TEMPLATE_SOURCE, NEW_APP_SOURCE)
    n_files = sum(len(files) for _, _, files in os.walk(NEW_APP_SOURCE))
    print(f"Copied {n_files} files to {NEW_APP_SOURCE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Patch `use_cloud_fetch=False`
# MAGIC
# MAGIC The Apps runtime cannot reach the cloud-fetch storage endpoint, so the
# MAGIC Databricks SQL connector fails with `Max retries exceeded` on every query
# MAGIC unless cloud fetch is disabled. Idempotent: skips if the template already
# MAGIC has the fix or does not use the SQL connector.

# COMMAND ----------

DEPS_PATH = os.path.join(NEW_APP_SOURCE, "lib", "deps.py")

if not os.path.exists(DEPS_PATH):
    print(f"No {DEPS_PATH}; skipping (app may not use databricks-sql-connector).")
else:
    with open(DEPS_PATH) as f:
        content = f.read()
    if "use_cloud_fetch=False" in content:
        print("use_cloud_fetch=False already present; no patch needed.")
    elif "credentials_provider=lambda: w.config.authenticate," in content:
        content = content.replace(
            "credentials_provider=lambda: w.config.authenticate,",
            "credentials_provider=lambda: w.config.authenticate,\n"
            "        use_cloud_fetch=False,  # required in the Apps runtime",
        )
        with open(DEPS_PATH, "w") as f:
            f.write(content)
        print("Patched use_cloud_fetch=False into lib/deps.py")
    else:
        print(
            "Could not find the dbsql.connect(...) anchor in lib/deps.py. "
            "If the app queries SQL and fails with 'Max retries exceeded', add "
            "use_cloud_fetch=False to the connect() call by hand."
        )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Create the app (idempotent)
# MAGIC
# MAGIC Creates the app shell and its service principal. Code is deployed later in
# MAGIC Step 8. Re-running is safe: an existing app is left in place.

# COMMAND ----------

from databricks.sdk.service.apps import App

try:
    existing = w.api_client.do("GET", f"/api/2.0/apps/{NEW_APP}")
    print(f"App '{NEW_APP}' already exists; skipping create.")
except Exception:
    w.apps.create(App(name=NEW_APP, description=f"Operator Command Center (clone of {TEMPLATE_APP})")).result()
    print(f"Created app '{NEW_APP}'.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Bind resources + OBO scopes, and read the SP
# MAGIC
# MAGIC The PATCH below is the privileged call the agent blocks. It binds the
# MAGIC warehouse, the 8 tables, and Lakebase to the app SP, and sets the OBO
# MAGIC scopes (genie, sql, dashboards.genie). The binding is what grants the SP
# MAGIC its resource access. Resources MUST be bound before the code deploy.

# COMMAND ----------

app_info = w.api_client.do("GET", f"/api/2.0/apps/{NEW_APP}")
# The OAuth client id of the app's SP is the principal used for grants below.
SP_ID = app_info.get("service_principal_client_id") or app_info.get("id")
print(f"App SP client id : {SP_ID}")

result = w.api_client.do(
    "PATCH",
    f"/api/2.0/apps/{NEW_APP}",
    body={"resources": RESOURCES, "user_api_scopes": USER_API_SCOPES},
)
print(f"Bound {len(result.get('resources', []))} resources; scopes: {result.get('user_api_scopes')}")
for r in result.get("resources", []):
    print(f"  [{_resource_kind(r)}] {r.get('name')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Grant the SP Unity Catalog access
# MAGIC
# MAGIC A table-level resource binding still needs `USE CATALOG` and `USE SCHEMA`
# MAGIC up the chain, or queries fail. We grant at the SCHEMA level rather than
# MAGIC table by table, so a single `SELECT ON SCHEMA` covers the 8 tables, the
# MAGIC `command_center_metrics` metric view, and anything added later. The catalog
# MAGIC and schema are derived from the bound `uc_securable` resources, so there is
# MAGIC a single source of truth.
# MAGIC
# MAGIC If you do not own the catalog (the shared workshop catalog is owned by the
# MAGIC facilitator), these GRANTs will be denied. That is expected: the cell
# MAGIC catches it and prints the exact statements for the facilitator to run.

# COMMAND ----------

from databricks.sdk.service.sql import StatementState

# Derive catalog/schema and the warehouse from the bound resources.
TABLES = sorted(
    r["uc_securable"]["securable_full_name"]
    for r in RESOURCES
    if "uc_securable" in r and r["uc_securable"].get("securable_type") == "TABLE"
)
WAREHOUSE_ID = next((r["sql_warehouse"]["id"] for r in RESOURCES if "sql_warehouse" in r), None)

if not TABLES:
    print("No uc_securable TABLE resources found; cannot derive the catalog/schema to grant.")
else:
    catalog = TABLES[0].split(".")[0]
    schema = ".".join(TABLES[0].split(".")[:2])

    # Resolve a warehouse once (prefer the app's bound warehouse).
    wh_id = WAREHOUSE_ID
    if not wh_id:
        whs = list(w.warehouses.list())
        wh_id = next((x.id for x in whs if x.state and "RUNNING" in str(x.state)), whs[0].id if whs else None)
    if not wh_id:
        raise RuntimeError("No SQL warehouse available to run GRANT statements.")

    def run_sql(stmt):
        resp = w.statement_execution.execute_statement(statement=stmt, warehouse_id=wh_id, wait_timeout="30s")
        if resp.status.state != StatementState.SUCCEEDED:
            raise RuntimeError(f"{resp.status.state}: {resp.status.error}")

    # Schema-level SELECT covers every table AND the metric view in one grant.
    statements = [
        f"GRANT USE CATALOG ON CATALOG {catalog} TO `{SP_ID}`",
        f"GRANT USE SCHEMA ON SCHEMA {schema} TO `{SP_ID}`",
        f"GRANT SELECT ON SCHEMA {schema} TO `{SP_ID}`",
    ]

    failed = []
    for stmt in statements:
        try:
            run_sql(stmt)
            print(f"ok: {stmt}")
        except Exception as e:
            failed.append(stmt)
            print(f"DENIED: {stmt}\n       {e}")

    if failed:
        print(
            "\nYou lack grant authority on this catalog (expected for the shared "
            "workshop catalog). Send your facilitator your SP id and ask them to "
            f"run these as a catalog owner (SP id: {SP_ID}):\n"
        )
        for stmt in failed:
            print(f"  {stmt};")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Grant the SP `CAN_USE` on the warehouse
# MAGIC
# MAGIC Warehouse access is a workspace-level permission, not Unity Catalog, so it
# MAGIC is set via the permissions REST API (additive: existing grants are kept).

# COMMAND ----------

if not WAREHOUSE_ID:
    print("No sql_warehouse resource bound; skipping warehouse permission.")
else:
    try:
        w.api_client.do(
            "PATCH",
            f"/api/2.0/permissions/warehouses/{WAREHOUSE_ID}",
            body={"access_control_list": [{"service_principal_name": SP_ID, "permission_level": "CAN_USE"}]},
        )
        print(f"Granted CAN_USE on warehouse {WAREHOUSE_ID} to SP {SP_ID}.")
    except Exception as e:
        print(
            f"Could not set warehouse permission: {e}\n"
            "If the attendee group already has CAN_USE on this warehouse, the SP "
            "inherits it and you can ignore this. Otherwise ask the facilitator."
        )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8: Start compute and deploy
# MAGIC
# MAGIC A freshly created app is STOPPED. It must be ACTIVE before deploy.

# COMMAND ----------

import time

from databricks.sdk.service.apps import AppDeployment


def wait_for_compute(states, timeout=600, poll=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        info = w.api_client.do("GET", f"/api/2.0/apps/{NEW_APP}")
        state = (info.get("compute_status") or {}).get("state", "")
        print(f"  compute={state}")
        if state in states:
            return state
        time.sleep(poll)
    raise TimeoutError(f"Timed out waiting for compute state in {states}.")


compute_state = (w.api_client.do("GET", f"/api/2.0/apps/{NEW_APP}").get("compute_status") or {}).get("state", "")
print(f"Compute state: {compute_state}")
if compute_state in ("STOPPED", ""):
    print("Starting app compute ...")
    w.apps.start(NEW_APP)
    wait_for_compute({"ACTIVE"})
elif compute_state == "STARTING":
    wait_for_compute({"ACTIVE"})
print("Compute is ACTIVE.")

# COMMAND ----------

deployment = w.apps.deploy(app_name=NEW_APP, app_deployment=AppDeployment(source_code_path=NEW_APP_SOURCE))
print(f"Deployment started: {deployment.deployment_id}")

state = "PENDING"
for _ in range(36):  # up to ~6 minutes
    info = w.api_client.do("GET", f"/api/2.0/apps/{NEW_APP}")
    dep = info.get("active_deployment") or info.get("pending_deployment") or {}
    state = (dep.get("status") or {}).get("state", "UNKNOWN")
    print(f"  deployment={state}")
    if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
        break
    time.sleep(10)
print(f"Deployment finished: {state}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 9: Verify

# COMMAND ----------

final = w.api_client.do("GET", f"/api/2.0/apps/{NEW_APP}")
url = final.get("url", "")
print("=" * 60)
print(f"App        : {final.get('name')}")
print(f"URL        : {url or '(pending)'}")
print(f"App status : {(final.get('app_status') or {}).get('state')}")
print(f"Compute    : {(final.get('compute_status') or {}).get('state')}")
print(f"Deployment : {(final.get('active_deployment') or {}).get('status', {}).get('state')}")
print(f"Resources  : {len(final.get('resources', []))}")
print(f"OBO scopes : {final.get('user_api_scopes')}")
print(f"SP id      : {final.get('service_principal_client_id') or final.get('id')}")
print("=" * 60)
if url:
    print(f"\nOpen your app: {url}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 10: Save your session for Lab 01
# MAGIC
# MAGIC Persists your initials (and app URL) to a small workspace file so the
# MAGIC `01-workshop-prompts` lab can auto-fill your prompts. You will not have to
# MAGIC retype your initials.

# COMMAND ----------

import base64
import json as _json

SESSION_DIR = f"/Workspace/Users/{ME}/command-center-lab"
SESSION_PATH = f"{SESSION_DIR}/session.json"
try:
    w.api_client.do("POST", "/api/2.0/workspace/mkdirs", body={"path": SESSION_DIR})
except Exception:
    pass
_session = _json.dumps({"initials": INITIALS, "app_name": NEW_APP, "app_url": url}, indent=2)
w.api_client.do(
    "POST",
    "/api/2.0/workspace/import",
    body={
        "path": SESSION_PATH,
        "format": "AUTO",
        "content": base64.b64encode(_session.encode()).decode(),
        "overwrite": True,
    },
)
print(f"Saved {SESSION_PATH}")
print(_session)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Metric view, Lakebase, Genie, and the dashboard
# MAGIC
# MAGIC - **Metric view (`command_center_metrics`):** covered by the `SELECT ON
# MAGIC   SCHEMA` grant in Step 6. The SP can query it directly, the same as the
# MAGIC   tables, with no extra step. (If the app reaches the metric view only via
# MAGIC   Genie or the dashboard, those run as you over OBO and need no SP grant.)
# MAGIC - **Lakebase:** the template's `database` resource came across in Step 5, so
# MAGIC   the SP has `CAN_CONNECT_AND_CREATE` on the instance. The write-back tables
# MAGIC   were granted to `PUBLIC` by the facilitator setup, so the SP can read and
# MAGIC   write them with no extra step.
# MAGIC - **Genie space and AI/BI dashboard:** the app calls Genie with your own
# MAGIC   token (OBO, via `X-Forwarded-Access-Token`) and embeds the dashboard as
# MAGIC   you, so the SP does not need access to them: you own both. There is no
# MAGIC   upfront grant to make. If you ever switch the app off OBO, grant the SP
# MAGIC   `CAN_RUN` on the space and `CAN_READ` on the dashboard from their
# MAGIC   permission dialogs once they exist.
