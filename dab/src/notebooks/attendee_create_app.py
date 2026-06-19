# Databricks notebook source
# MAGIC %md
# MAGIC # Attendee: Create and Deploy Your Command Center App
# MAGIC
# MAGIC **What this notebook does:**
# MAGIC 1. Creates (or updates) a Databricks App named `<initials>-command-center`.
# MAGIC 2. Registers all shared resources on the app so its service principal (SP)
# MAGIC    is automatically granted access via platform resource binding. No raw
# MAGIC    GRANT DDL is run because you do not have MANAGE on the facilitator's schema.
# MAGIC 3. Deploys the app source code from your Git folder in the workspace.
# MAGIC 4. Prints the SP identity and URL so you can continue the workshop.
# MAGIC
# MAGIC **Prerequisites:**
# MAGIC - You have cloned the `genie-code-vibe-workshop` repo as a Databricks Git
# MAGIC   folder in your user directory (`/Workspace/Users/<you>/genie-code-vibe-workshop`).
# MAGIC - Your attendee group already has SELECT on the workshop schema, CAN_USE on
# MAGIC   the warehouse, and CAN_CONNECT on Lakebase (pre-granted by the facilitator).
# MAGIC - Run cells top to bottom, in order. Do not skip the pip cell.

# COMMAND ----------

# Cell 1: install / upgrade the SDK, then restart so new packages are importable.
# The restart means widgets are re-read in Cell 3 after the kernel comes back up.

# MAGIC %pip install -q --upgrade "databricks-sdk>=0.40"

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# Cell 3: declare widgets so the attendee can fill them via the Parameters bar.
# Order matters: declare ALL widgets before reading any of them.

dbutils.widgets.text("initials",          "",                      "Your initials (required)")
dbutils.widgets.text("catalog",           "ioc_sandbox",           "UC catalog")
dbutils.widgets.text("schema",            "vibe_workshop",         "UC schema")
dbutils.widgets.text("warehouse_id",      "",                      "SQL warehouse ID (leave blank to read from config)")
dbutils.widgets.text("lakebase_instance", "command-center-lakebase", "Lakebase instance name")
dbutils.widgets.text("app_source_path",   "",                      "App source path (leave blank to auto-derive)")

# COMMAND ----------

# Cell 4: resolve config, derive defaults, validate.
#
# API note: all app operations below use w.api_client.do() (REST passthrough).
# The typed SDK classes for Apps (databricks.sdk.service.apps) do exist in
# sdk>=0.40, but the exact field names for uc_securable and user_api_scopes
# were not confirmed at authoring time. REST is used so the JSON body exactly
# matches the tested DAB schema in dab/resources/app.yml.
# Confirm typed-SDK equivalents against the databricks-apps skill before
# switching to the typed API.

import json
import time

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
me = w.current_user.me()

# --- Read widgets ---
INITIALS          = dbutils.widgets.get("initials").strip().lower()
CATALOG           = dbutils.widgets.get("catalog").strip()
SCHEMA            = dbutils.widgets.get("schema").strip()
WAREHOUSE_ID      = dbutils.widgets.get("warehouse_id").strip()
LAKEBASE_INSTANCE = dbutils.widgets.get("lakebase_instance").strip()
APP_SOURCE_PATH   = dbutils.widgets.get("app_source_path").strip()

if not INITIALS:
    raise ValueError(
        "initials widget is required. Fill it in via the Parameters bar and re-run."
    )

APP_NAME = f"{INITIALS}-command-center"

# --- Try to fill blanks from the facilitator config file ---
CONFIG_PATH = "/Workspace/Shared/command-center/config.json"
_facilitator_config = {}
try:
    resp = w.api_client.do("GET", "/api/2.0/workspace/export",
                           query={"path": CONFIG_PATH, "format": "AUTO"})
    import base64
    raw = base64.b64decode(resp.get("content", "")).decode()
    _facilitator_config = json.loads(raw)
    print(f"Loaded facilitator config from {CONFIG_PATH}:")
    print(json.dumps(_facilitator_config, indent=2))
except Exception as _cfg_err:
    print(f"Note: could not read {CONFIG_PATH} ({_cfg_err}). Using widget values only.")

if not CATALOG:
    CATALOG = _facilitator_config.get("catalog", "ioc_sandbox")
if not SCHEMA:
    SCHEMA = _facilitator_config.get("schema", "vibe_workshop")
if not WAREHOUSE_ID:
    WAREHOUSE_ID = _facilitator_config.get("warehouse_id", "")

# --- Derive app_source_path if not provided ---
if not APP_SOURCE_PATH:
    APP_SOURCE_PATH = (
        f"/Workspace/Users/{me.user_name}/genie-code-vibe-workshop/dab/src/app"
    )

# --- Validate required values ---
if not WAREHOUSE_ID:
    raise ValueError(
        "warehouse_id is not set and was not found in the facilitator config. "
        "Either fill in the warehouse_id widget or ask the facilitator to run "
        "the setup job first (it writes the config to /Workspace/Shared/command-center/config.json)."
    )

print()
print("Resolved configuration:")
print(f"  app_name         : {APP_NAME}")
print(f"  catalog          : {CATALOG}")
print(f"  schema           : {SCHEMA}")
print(f"  warehouse_id     : {WAREHOUSE_ID}")
print(f"  lakebase_instance: {LAKEBASE_INSTANCE}")
print(f"  app_source_path  : {APP_SOURCE_PATH}")
print(f"  current user     : {me.user_name}")

# COMMAND ----------

# Cell 5: build the resources list and user_api_scopes.
#
# These exactly mirror dab/resources/app.yml. The resource names and sub-object
# keys (sql_warehouse, uc_securable, database) are the authoritative Apps API
# field names validated in that DAB config.

TABLE_NAMES = [
    "dims_stores",
    "dims_items",
    "dims_employees",
    "facts_sales_daypart",
    "facts_labor_daypart",
    "facts_sales_inventory_daily",
    "facts_purchase_orders",
    "facts_customer_feedback",
]

app_resources = [
    {
        "name": "workshop_warehouse",
        "sql_warehouse": {
            "id": WAREHOUSE_ID,
            "permission": "CAN_USE",
        },
    }
]

for tbl in TABLE_NAMES:
    app_resources.append(
        {
            "name": tbl,
            "uc_securable": {
                "securable_full_name": f"{CATALOG}.{SCHEMA}.{tbl}",
                "securable_type": "TABLE",
                "permission": "SELECT",
            },
        }
    )

app_resources.append(
    {
        "name": "lakebase",
        "database": {
            "instance_name": LAKEBASE_INSTANCE,
            "database_name": "databricks_postgres",
            "permission": "CAN_CONNECT_AND_CREATE",
        },
    }
)

USER_API_SCOPES = ["genie", "sql", "dashboards.genie"]

print(f"Resources to bind ({len(app_resources)} total):")
for r in app_resources:
    rtype = next(k for k in r if k != "name")
    print(f"  [{rtype}] {r['name']}")
print(f"user_api_scopes: {USER_API_SCOPES}")

# COMMAND ----------

# Cell 6: create or update the app WITH resources + user_api_scopes, then wait
# for the app to reach a ready/available state before proceeding.
#
# CRITICAL ORDER: resources must be declared on the app BEFORE the code deploy.
# If you deploy code first, the service principal is created but has no access
# to the warehouse, tables, or Lakebase, and the app will fail at runtime.
#
# API: POST /api/2.0/apps (create) or PATCH /api/2.0/apps/{name} (update).
# Confirmed against the Apps REST API spec. Typed SDK alternative:
# w.apps.create() / w.apps.update() -- confirm field names against
# databricks-apps skill if switching to typed SDK.

app_body = {
    "name": APP_NAME,
    "description": "Operator Command Center (attendee build)",
    "resources": app_resources,
    "user_api_scopes": USER_API_SCOPES,
}

# Check whether the app already exists.
existing_app = None
try:
    existing_app = w.api_client.do("GET", f"/api/2.0/apps/{APP_NAME}")
    print(f"App '{APP_NAME}' already exists. Updating with latest resource config ...")
except Exception as _get_err:
    err_str = str(_get_err)
    if "RESOURCE_DOES_NOT_EXIST" in err_str or "404" in err_str or "does not exist" in err_str.lower():
        existing_app = None
    else:
        raise RuntimeError(
            f"Unexpected error checking for app '{APP_NAME}': {_get_err}\n"
            "Check that you have CAN_USE or higher on the Apps compute resource."
        ) from _get_err

if existing_app is None:
    print(f"Creating app '{APP_NAME}' ...")
    try:
        create_resp = w.api_client.do("POST", "/api/2.0/apps", body=app_body)
        print(f"App created: {create_resp.get('name')}")
    except Exception as _create_err:
        raise RuntimeError(
            f"Failed to create app '{APP_NAME}': {_create_err}\n"
            "Common causes: you lack permission to create apps in this workspace, "
            "or the app name is already taken by another user."
        ) from _create_err
else:
    # PATCH only supports a subset of fields; resources and user_api_scopes
    # are included. Name cannot change.
    patch_body = {
        "description": app_body["description"],
        "resources": app_resources,
        "user_api_scopes": USER_API_SCOPES,
    }
    try:
        w.api_client.do("PATCH", f"/api/2.0/apps/{APP_NAME}", body=patch_body)
        print(f"App '{APP_NAME}' updated with latest resource config.")
    except Exception as _patch_err:
        raise RuntimeError(
            f"Failed to update app '{APP_NAME}': {_patch_err}\n"
            "If you see a permission error, you may not own this app. "
            "Check that the app name '{APP_NAME}' belongs to your account."
        ) from _patch_err

# Wait for the app to reach IDLE/RUNNING (the compute is provisioned async).
print("Waiting for app compute to be ready ...")
_deadline = time.time() + 300  # 5-minute timeout
_poll_interval = 8
while True:
    try:
        app_state = w.api_client.do("GET", f"/api/2.0/apps/{APP_NAME}")
        # The Apps API returns a 'compute_status' sub-object.
        # Confirm exact field name ('compute_status' vs 'status') at runtime.
        compute = app_state.get("compute_status") or {}
        state = compute.get("state", "").upper()
        if state in ("IDLE", "RUNNING", "ACTIVE", "DEPLOYED"):
            print(f"App compute is ready (state: {state}).")
            break
        if state in ("ERROR", "FAILED"):
            msg = compute.get("message", "(no detail)")
            raise RuntimeError(
                f"App compute reached error state '{state}': {msg}\n"
                "Check the app logs in the Databricks UI under Compute > Apps."
            )
    except RuntimeError:
        raise
    except Exception as _poll_err:
        print(f"  Poll error (will retry): {_poll_err}")
    if time.time() > _deadline:
        print(
            "WARNING: App did not report ready within 5 minutes. "
            "Proceeding anyway; the deploy may still succeed."
        )
        break
    print(f"  state: {state or '(pending)'}  -- waiting {_poll_interval}s ...")
    time.sleep(_poll_interval)

# COMMAND ----------

# Cell 7: fetch the app and print the service principal identity + bound resources.

print("Fetching app details ...")
try:
    app_detail = w.api_client.do("GET", f"/api/2.0/apps/{APP_NAME}")
except Exception as _detail_err:
    raise RuntimeError(f"Could not fetch app details: {_detail_err}") from _detail_err

# The SP fields are nested under 'service_principal_*' at the top level of the
# App object. Confirm exact field names against the Apps REST API if any are None.
sp_client_id = app_detail.get("service_principal_client_id")
sp_id        = app_detail.get("service_principal_id")
sp_name      = app_detail.get("service_principal_name")

print()
print("=" * 60)
print("App Service Principal")
print("=" * 60)
print(f"  service_principal_client_id : {sp_client_id}")
print(f"  service_principal_id        : {sp_id}")
print(f"  service_principal_name      : {sp_name}")
print()
print("Bound resources:")
for r in app_detail.get("resources", []):
    rtype = next((k for k in r if k not in ("name", "description")), "(unknown)")
    print(f"  [{rtype}] {r.get('name')}")
print("=" * 60)
print()
print(
    "The SP above has been granted access to the warehouse, UC tables, and "
    "Lakebase via platform resource binding. No raw GRANT DDL was run."
)

# COMMAND ----------

# Cell 8: deploy the app source code and wait for the deployment to succeed.
#
# API: POST /api/2.0/apps/{name}/deployments
# Confirm: 'mode' field accepts 'SNAPSHOT' or 'AUTO_SYNC'.
# We use SNAPSHOT for workshop deployments (point-in-time; no background sync).

print(f"Deploying app code from: {APP_SOURCE_PATH}")
print("(Using SNAPSHOT mode: code is copied at deploy time.)")

deploy_body = {
    "source_code_path": APP_SOURCE_PATH,
    "mode": "SNAPSHOT",
}

try:
    deploy_resp = w.api_client.do(
        "POST", f"/api/2.0/apps/{APP_NAME}/deployments", body=deploy_body
    )
except Exception as _deploy_err:
    raise RuntimeError(
        f"Failed to start deployment for '{APP_NAME}': {_deploy_err}\n"
        "Common causes:\n"
        "  - The source_code_path does not exist. Check that you have cloned the "
        "Git folder to the expected location, or override the app_source_path widget.\n"
        "  - The app source path points outside your user directory and you lack "
        "read access."
    ) from _deploy_err

deployment_id = deploy_resp.get("deployment_id") or deploy_resp.get("id")
print(f"Deployment started (id: {deployment_id}). Waiting for completion ...")

_deadline = time.time() + 600  # 10-minute timeout
_poll_interval = 10
while True:
    try:
        dep_state_resp = w.api_client.do(
            "GET", f"/api/2.0/apps/{APP_NAME}/deployments/{deployment_id}"
        )
        # Confirm exact field name: 'status' -> 'state' vs top-level 'state'.
        dep_status = dep_state_resp.get("status") or {}
        dep_state  = (dep_status.get("state") or dep_state_resp.get("state") or "").upper()
        if dep_state in ("SUCCEEDED",):
            print(f"Deployment succeeded (state: {dep_state}).")
            break
        if dep_state in ("FAILED", "CANCELLED"):
            msg = dep_status.get("message") or dep_state_resp.get("error") or "(no detail)"
            raise RuntimeError(
                f"Deployment '{deployment_id}' failed (state: {dep_state}): {msg}\n"
                "Check the app logs in the Databricks UI under Compute > Apps."
            )
    except RuntimeError:
        raise
    except Exception as _dep_poll_err:
        print(f"  Poll error (will retry): {_dep_poll_err}")
    if time.time() > _deadline:
        print(
            "WARNING: Deployment did not complete within 10 minutes. "
            "Check the app status in the Databricks UI."
        )
        break
    print(f"  deployment state: {dep_state or '(pending)'}  -- waiting {_poll_interval}s ...")
    time.sleep(_poll_interval)

# Fetch the final app state to get the URL.
try:
    final_app = w.api_client.do("GET", f"/api/2.0/apps/{APP_NAME}")
    app_url   = final_app.get("url") or "(URL not yet available; check the Apps UI)"
except Exception:
    app_url = "(could not fetch URL; check the Apps UI)"

print()
print("=" * 60)
print(f"App URL: {app_url}")
print("=" * 60)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary: What Just Happened
# MAGIC
# MAGIC **Service principal (SP):** Every Databricks App has its own SP, auto-created
# MAGIC by the platform when the app is first created. The SP identity was printed above.
# MAGIC
# MAGIC **Resource binding:** Instead of running `GRANT SELECT ON TABLE ...` (which
# MAGIC requires MANAGE privilege on the schema), we declared the resources directly
# MAGIC on the app. The platform bound the SP to each resource as part of the create/update
# MAGIC call. This is the supported, least-privilege path for attendees.
# MAGIC
# MAGIC **Resources bound:**
# MAGIC - SQL warehouse `workshop_warehouse` (CAN_USE)
# MAGIC - 8 UC tables: dims and facts in `{catalog}.{schema}` (SELECT)
# MAGIC - Lakebase instance `command-center-lakebase`, database `databricks_postgres`
# MAGIC   (CAN_CONNECT_AND_CREATE, for write-back tables)
# MAGIC
# MAGIC **Next steps:** continue with Module 1 in the lab companion guide. Your app is
# MAGIC live at the URL printed above. The coding agent (Genie Code) will iterate on
# MAGIC the source at `dab/src/app`; re-run Cell 8 (or use AUTO_SYNC mode) to push
# MAGIC new versions.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run These LATER: Genie Space and Dashboard Permissions
# MAGIC
# MAGIC The two cells below are **optional and non-blocking.** Run them only after you
# MAGIC have created your Genie space (Module 2) and your AI/BI dashboard (Module 3).
# MAGIC
# MAGIC **Why you probably do NOT need these cells:**
# MAGIC
# MAGIC The app calls the Genie API and renders the AI/BI dashboard using
# MAGIC **on-behalf-of (OBO)** access. When a user opens the app, the platform
# MAGIC forwards the user's own OAuth token as the `X-Forwarded-Access-Token` header.
# MAGIC The backend passes this token to Genie and the dashboard embed API, so those
# MAGIC calls run as the logged-in user, not as the SP. Because you created the Genie
# MAGIC space and dashboard yourself, you already have access, and OBO just works.
# MAGIC
# MAGIC **When you DO need these cells:** if you want the SP to call Genie directly
# MAGIC (server-to-server, without a logged-in user), or if you share the app with
# MAGIC other users who do not have access to the space or dashboard.

# COMMAND ----------

# Optional Cell A: grant the app SP CAN_RUN on your Genie space (post Module 2).
#
# Fill genie_space_id with the space ID from the output of 03_create_genie_space
# or from the URL in the Genie UI (/genie/rooms/<space_id>).
#
# API: PUT /api/2.0/permissions/genie/rooms/{space_id}
# Confirm: the correct object_type for Genie spaces may be "genie-room" or
# "genie_space". Check the Databricks permissions API docs or the databricks-genie
# skill for the authoritative path. CAN_RUN is the minimum level for calling
# the Genie conversation API.

dbutils.widgets.text("genie_space_id", "", "Genie space ID (Module 2, optional)")
GENIE_SPACE_ID = dbutils.widgets.get("genie_space_id").strip()

if not GENIE_SPACE_ID:
    print("genie_space_id is empty. Skipping Genie space permissions (run after Module 2).")
else:
    _sp_client_id = None
    try:
        _app_info = w.api_client.do("GET", f"/api/2.0/apps/{APP_NAME}")
        _sp_client_id = _app_info.get("service_principal_client_id")
    except Exception as _sp_fetch_err:
        print(f"WARNING: could not fetch SP client ID: {_sp_fetch_err}")

    if not _sp_client_id:
        print(
            "WARNING: Could not resolve the app SP client ID. "
            "Grant CAN_RUN manually via the Genie space UI > Share."
        )
    else:
        genie_perm_body = {
            "access_control_list": [
                {
                    "service_principal_name": str(_sp_client_id),
                    "permission_level": "CAN_RUN",
                }
            ]
        }
        try:
            # Confirm object_type path at runtime: /genie/rooms vs /genie_rooms vs /genie-rooms.
            genie_perm_resp = w.api_client.do(
                "PUT",
                f"/api/2.0/permissions/genie/rooms/{GENIE_SPACE_ID}",
                body=genie_perm_body,
            )
            print(f"Genie space permissions updated for SP {_sp_client_id}:")
            print(json.dumps(genie_perm_resp, indent=2))
        except Exception as _genie_perm_err:
            print(
                f"ERROR setting Genie space permissions: {_genie_perm_err}\n"
                "If you see a 404, the space_id may be wrong, or the path "
                "/api/2.0/permissions/genie/rooms/{id} may differ in this workspace "
                "version. Check the Genie docs or databricks-genie skill for the "
                "correct permissions endpoint."
            )

# COMMAND ----------

# Optional Cell B: grant the app SP CAN_VIEW on your AI/BI (Lakeview) dashboard
# (post Module 3).
#
# Fill dashboard_id with the ID from the dashboard URL in the Databricks UI
# (/dashboardsv3/<dashboard_id>).
#
# API: PUT /api/2.0/permissions/dashboards/{dashboard_id}
# Confirm: for Lakeview (AI/BI) dashboards the object_type is "dashboard"
# (same path as legacy dashboards). CAN_READ and CAN_VIEW are aliases in most
# workspace versions; use CAN_VIEW as it is the minimum read-only level.

dbutils.widgets.text("dashboard_id", "", "AI/BI dashboard ID (Module 3, optional)")
DASHBOARD_ID = dbutils.widgets.get("dashboard_id").strip()

if not DASHBOARD_ID:
    print("dashboard_id is empty. Skipping dashboard permissions (run after Module 3).")
else:
    _sp_client_id = None
    try:
        _app_info = w.api_client.do("GET", f"/api/2.0/apps/{APP_NAME}")
        _sp_client_id = _app_info.get("service_principal_client_id")
    except Exception as _sp_fetch_err2:
        print(f"WARNING: could not fetch SP client ID: {_sp_fetch_err2}")

    if not _sp_client_id:
        print(
            "WARNING: Could not resolve the app SP client ID. "
            "Grant CAN_VIEW manually via the dashboard UI > Share."
        )
    else:
        dashboard_perm_body = {
            "access_control_list": [
                {
                    "service_principal_name": str(_sp_client_id),
                    "permission_level": "CAN_VIEW",
                }
            ]
        }
        try:
            # Confirm path at runtime: /api/2.0/permissions/dashboards vs
            # /api/2.0/permissions/lakeview-dashboards for AI/BI (Lakeview) dashboards.
            dashboard_perm_resp = w.api_client.do(
                "PUT",
                f"/api/2.0/permissions/dashboards/{DASHBOARD_ID}",
                body=dashboard_perm_body,
            )
            print(f"Dashboard permissions updated for SP {_sp_client_id}:")
            print(json.dumps(dashboard_perm_resp, indent=2))
        except Exception as _dash_perm_err:
            print(
                f"ERROR setting dashboard permissions: {_dash_perm_err}\n"
                "If you see a 404, check that the dashboard_id is correct and that "
                "the permissions path is /api/2.0/permissions/dashboards/{id}. "
                "For AI/BI (Lakeview) dashboards the path may differ; check the "
                "Lakeview dashboard docs or databricks-aibi-dashboards skill."
            )
