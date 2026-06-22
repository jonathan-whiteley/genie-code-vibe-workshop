# Databricks notebook source
# MAGIC %md
# MAGIC # Helper: Clone the Command Center App from the Template
# MAGIC
# MAGIC Clones the template app, binds its service principal, grants the SP warehouse and Unity Catalog access, and deploys: the privileged steps Genie Code cannot do.
# MAGIC Called by `00-setup` via `%run` (which installs the SDK and restarts Python first).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configure and read the template

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

print(f"New app  : {NEW_APP}  (source: {NEW_APP_SOURCE})")

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

print(f"Read template: {len(RESOURCES)} resources, scopes {USER_API_SCOPES}, source {TEMPLATE_SOURCE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Copy and patch the source

# COMMAND ----------

import os
import shutil

if os.path.exists(NEW_APP_SOURCE):
    if OVERWRITE_SOURCE:
        shutil.rmtree(NEW_APP_SOURCE)
        print(f"Removed existing {NEW_APP_SOURCE} (overwrite_source=true).")
    else:
        print(f"Source already exists; leaving in place (set overwrite_source=true to replace): {NEW_APP_SOURCE}")

if not os.path.exists(NEW_APP_SOURCE):
    shutil.copytree(TEMPLATE_SOURCE, NEW_APP_SOURCE)
    n_files = sum(len(files) for _, _, files in os.walk(NEW_APP_SOURCE))
    print(f"Copied {n_files} files to {NEW_APP_SOURCE}")

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
            "WARNING: dbsql.connect(...) anchor not found in lib/deps.py. "
            "If the app queries SQL and fails with 'Max retries exceeded', add "
            "use_cloud_fetch=False to the connect() call by hand."
        )

CONFIG_PY_PATH = os.path.join(NEW_APP_SOURCE, "lib", "config.py")

if not os.path.exists(CONFIG_PY_PATH):
    print(f"No {CONFIG_PY_PATH}; skipping.")
else:
    with open(CONFIG_PY_PATH) as f:
        content = f.read()

    OLD = 'genie_space_id=ws_cfg.get("genie_space_id") or os.getenv("GENIE_SPACE_ID", "")'
    NEW = 'genie_space_id=os.getenv("GENIE_SPACE_ID", "") or ws_cfg.get("genie_space_id", "")'

    if NEW in content:
        print("genie_space_id priority already patched; skipping.")
    elif OLD in content:
        content = content.replace(OLD, NEW)
        with open(CONFIG_PY_PATH, "w") as f:
            f.write(content)
        print("Patched config.py: GENIE_SPACE_ID env var now takes priority over shared config.")
    else:
        print("WARNING: Expected genie_space_id line not found in config.py; manual review needed.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create the app, bind resources, grant access

# COMMAND ----------

from databricks.sdk.service.apps import App

try:
    existing = w.api_client.do("GET", f"/api/2.0/apps/{NEW_APP}")
    print(f"App '{NEW_APP}' already exists; skipping create.")
except Exception:
    w.apps.create(App(name=NEW_APP, description=f"Operator Command Center (clone of {TEMPLATE_APP})")).result()
    print(f"Created app '{NEW_APP}'.")

app_info = w.api_client.do("GET", f"/api/2.0/apps/{NEW_APP}")
# The OAuth client id of the app's SP is the principal used for grants below.
SP_ID = app_info.get("service_principal_client_id") or app_info.get("id")
print(f"App SP client id : {SP_ID}")

# Bind only the warehouse + OBO scopes here. Skip two resource kinds the attendee
# cannot bind, and does not need to:
# - uc_securable (the 8 tables + metric view): binding a table GRANTS the app SP
#   SELECT, which requires the binder to own / have MANAGE on the catalog. On a
#   fresh or facilitator-owned catalog the attendee does not, so the bind
#   hard-fails ("nobody has USE CATALOG ... you don't have MANAGE to grant it").
#   Table access instead comes from the SELECT ON SCHEMA grant in the next step,
#   which prints a facilitator fallback if the attendee lacks grant authority.
# - database (Lakebase): admin-only bind, and no module uses it (write-back is out
#   of scope; the app's Lakebase pool is lazy, so the app still starts).
SKIP_KINDS = ("uc_securable", "database")
BIND_RESOURCES = [r for r in RESOURCES if not any(k in r for k in SKIP_KINDS)]
skipped = [r for r in RESOURCES if any(k in r for k in SKIP_KINDS)]

result = w.api_client.do(
    "PATCH",
    f"/api/2.0/apps/{NEW_APP}",
    body={"resources": BIND_RESOURCES, "user_api_scopes": USER_API_SCOPES},
)
print(f"Bound {len(result.get('resources', []))} resources; scopes: {result.get('user_api_scopes')}")
if skipped:
    print(
        f"Skipped {len(skipped)} resource binding(s): UC tables get SELECT ON SCHEMA "
        "in the next step; Lakebase is admin-only and unused (write-back stays read-only)."
    )

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
            "workshop catalog). A catalog owner / metastore admin must run the "
            "statements below. They target this app's SERVICE PRINCIPAL "
            f"(SP id: {SP_ID}) on purpose: granting to a user group like "
            "`account users` does NOT cover the app SP, since a service principal "
            "is not a member of that group. The app reads tables as this SP, so "
            "these must grant the SP id specifically:\n"
        )
        for stmt in failed:
            print(f"  {stmt};")

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
# MAGIC ## Start compute and deploy

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
# MAGIC ## Verify and save the session

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
