# Databricks notebook source
# MAGIC %md
# MAGIC # Helper: build the Lab 01 session-setup prompt
# MAGIC
# MAGIC Resolves your initials (from the `initials` widget, or the file `00-setup`
# MAGIC saved) and builds `session_setup_prompt`. Called by `01-workshop-prompts`
# MAGIC via `%run`; the calling notebook prints the result so the prompt is the only
# MAGIC thing in that cell's output, clean to copy.

# COMMAND ----------

dbutils.widgets.text("initials", "", "Your initials (auto-filled from Lab 00 if blank)")

import base64
import json

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Resolve initials: the widget wins; otherwise read the file Lab 00 saved.
initials = dbutils.widgets.get("initials").strip().lower()
if not initials:
    me = w.current_user.me().user_name
    try:
        resp = w.api_client.do(
            "GET",
            "/api/2.0/workspace/export",
            query={
                "path": f"/Workspace/Users/{me}/command-center-lab/session.json",
                "format": "SOURCE",
                "direct_download": False,
            },
        )
        content = (resp or {}).get("content") if isinstance(resp, dict) else None
        if content:
            initials = json.loads(base64.b64decode(content).decode()).get("initials", "").strip().lower()
    except Exception:
        pass

if not initials:
    raise ValueError(
        "No initials found. Run the 00-setup notebook first, or type your initials "
        "into the 'initials' widget at the top of this notebook and run the cells again."
    )

session_setup_prompt = f"""I am doing the Genie Code Command Center lab. Use these settings for the whole chat:

| Setting | Value |
|---|---|
| My initials | {initials} |
| Catalog | ioc_sandbox.vibe_workshop |
| Warehouse | serverless |
| Model (for ai_query only) | databricks-claude-sonnet-4-6 |

Create these with exactly these names:

| Resource | Name |
|---|---|
| Metric view | {initials}_command_center_metrics |
| Genie space | {initials} Command Center |
| Dashboard | {initials} Operator Insights |
| App | {initials}-command-center (already created and deployed by Lab 00) |
| Job | {initials}-command-center-refresh |

As we go, remember my Genie space ID, dashboard ID, and app URL. Confirm these back to me, then wait for my first prompt."""
