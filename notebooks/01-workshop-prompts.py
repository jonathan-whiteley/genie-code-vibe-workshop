# Databricks notebook source
# MAGIC %md
# MAGIC # Lab 01: Build Your Command Center with Genie Code 🏗️
# MAGIC
# MAGIC You will build a complete Command Center by prompting Genie Code: a governed
# MAGIC metric view, a Genie space and an AI/BI dashboard on top of it, and an app
# MAGIC that embeds both. Each step is a short prompt you copy into Genie Code.
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC Each module below produces one of these:
# MAGIC - **Module 1:** a metric view that governs your KPIs at store x date grain
# MAGIC - **Module 2:** a Genie space for natural-language Q&A on the metric view
# MAGIC - **Module 3:** an AI/BI dashboard on the metric view
# MAGIC - **Module 4:** your app (deployed in Lab 00), confirmed and branded
# MAGIC - **Module 5:** your Genie space and dashboard embedded in the app
# MAGIC - **Module 6 (bonus):** a scheduled job that refreshes everything

# COMMAND ----------

# MAGIC %md
# MAGIC ## How Genie Code works here (ground rules) 📋
# MAGIC
# MAGIC - You build everything by prompting Genie Code. The ai-dev-kit skills (installed
# MAGIC   in Lab 00) tell it how to build on Databricks. You tell it WHAT; the skills know HOW.
# MAGIC - Genie Code can author and run SQL or DDL you are authorized for, and call
# MAGIC   Databricks APIs (create metric views, Genie spaces, dashboards, deploy apps).
# MAGIC - Genie Code will NOT run permission or grant commands, and it cannot bind app
# MAGIC   resources or set app OBO scopes. That is why Lab 00 already created your app,
# MAGIC   granted its service principal the warehouse, catalog and schema (which covers
# MAGIC   the tables and the metric view) and Lakebase, and set the genie, sql, and
# MAGIC   dashboards.genie scopes. So no prompt here asks Genie Code to grant anything.
# MAGIC - Always read what Genie Code generates before you run it.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Personalize your prompts 🔧
# MAGIC
# MAGIC Run the next cell. It reads the initials you entered in **Lab 00** and prints
# MAGIC your session-setup prompt, already filled in. Copy the printed prompt and paste
# MAGIC it into Genie Code as your **first** message.
# MAGIC
# MAGIC > **Tip:** If you did not run Lab 00 in this workspace, type your initials into the
# MAGIC > `initials` widget that appears at the top of this notebook, then run the cell again.

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
            print(f"Loaded your initials from Lab 00: {initials}")
    except Exception as e:
        print(f"(Could not read the Lab 00 session file: {type(e).__name__})")

if not initials:
    raise ValueError(
        "No initials found. Run the 00-setup notebook first, or type your initials "
        "into the 'initials' widget at the top of this notebook and run this cell again."
    )

session_setup_prompt = f"""I am doing the Genie Code Command Center lab. Remember these for the whole chat:
  My initials:  {initials}
  Catalog:      ioc_sandbox.vibe_workshop
  Warehouse:    serverless
  Model:        databricks-claude-sonnet-4-6   (for ai_query() only)
My resources (use exactly these names):
  metric view:  {initials}_command_center_metrics
  Genie space:  "{initials} Command Center"
  dashboard:    "{initials} Operator Insights"
  app:          {initials}-command-center   (already created and deployed for me by Lab 00)
  job:          {initials}-command-center-refresh
As we go, remember my Genie space ID, dashboard ID, and app URL.
Confirm, then wait for my first prompt."""

print("\nCopy everything below this line into Genie Code as your first message:\n")
print(session_setup_prompt)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 1: Build the metric view 📊
# MAGIC
# MAGIC The metric view is the spine: define your KPIs once, then everything else reuses
# MAGIC them. Copy the prompt in the next cell into Genie Code.
# MAGIC
# MAGIC > **Note:** Genie Code runs the `CREATE` statement for you, but you need `CREATE`
# MAGIC > on the schema. If it is denied, ask your facilitator to grant your group `CREATE`
# MAGIC > on `ioc_sandbox.vibe_workshop`, or create the view in your own sandbox schema.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Create my Command Center metric view over the workshop tables at store x date
# MAGIC grain. Use the metric view name from my session setup. Measures: revenue, labor
# MAGIC cost, labor % of sales, days of cover, sell-through %, net sentiment. Dimensions:
# MAGIC store, region, date, day-of-week. Put all the joins and rollups inside the metric
# MAGIC view's own source query; do not create any intermediary or base view, only the
# MAGIC single metric view. Then run a SELECT to confirm it returns rows.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 2: Create a Genie space on the metric view 🧞
# MAGIC
# MAGIC A Genie space lets anyone ask questions in natural language, grounded in your
# MAGIC governed measures.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Create a Genie space on my metric view. Add 6 sample questions, 2 per pillar
# MAGIC (Labor / Inventory / Guest Feedback), grounded in the metric view measures. Ask
# MAGIC one question per pillar to test it, then tell me the space ID.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 3: Create an AI/BI dashboard on the metric view 📈
# MAGIC
# MAGIC The dashboard reuses the same governed measures, so the numbers match the Genie
# MAGIC space exactly.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Create an AI/BI dashboard on my metric view with 4 widgets: labor % of sales
# MAGIC (30-day line), revenue by region (bar), days of cover / stock health (bar), net
# MAGIC sentiment timeline (line). Publish it and tell me the dashboard ID.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 4: Confirm and polish your app 🎨
# MAGIC
# MAGIC Your app was already created, permissioned, scoped, and deployed by Lab 00. This
# MAGIC step does not recreate it.
# MAGIC
# MAGIC > **Note:** Genie Code can edit the app source and redeploy, but it cannot change
# MAGIC > resources or scopes (and does not need to: Lab 00 set them).

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC My Command Center app is already deployed (Lab 00 created it). Open its URL and
# MAGIC confirm it loads. Optional: restyle the LCE branding in the app
# MAGIC source (logo branding/lce/logo.svg, primary #FF671B, dark navbar, title
# MAGIC "Command Center | LCE") and redeploy. Do not change the app's resources or scopes.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 5: Embed your Genie space and dashboard 🔗
# MAGIC
# MAGIC Point your app at the Genie space and dashboard you just built.
# MAGIC
# MAGIC > **Important:** the genie, sql, and dashboards.genie OBO scopes are already set on
# MAGIC > your app by Lab 00. Do not ask Genie Code to add scopes (it cannot, and they are
# MAGIC > not needed).

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Update my app to embed my Genie space (the ID from the Genie step) and my dashboard
# MAGIC (the ID from the dashboard step), then redeploy:
# MAGIC   - Call Genie on behalf of the signed-in user using the X-Forwarded-Access-Token
# MAGIC     header (OBO), not the app service principal, so it uses my access to my space.
# MAGIC   - Embed my published dashboard by its ID, rendered as the signed-in user.
# MAGIC   - Support multi-turn: start-conversation on the first ask, then post to the
# MAGIC     conversation messages endpoint; poll until COMPLETED; return the answer and
# MAGIC     the SQL Genie generated.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 6 (BONUS): Schedule a refresh job ⏰
# MAGIC
# MAGIC Automate the refresh so the data and app stay current.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Create my daily refresh job at 6am ET that refreshes my metric view's source
# MAGIC rollups and redeploys my app. The job runs as me, so no extra permissions are needed.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion 🏁
# MAGIC
# MAGIC You built a governed metric view and hung a Genie space, an AI/BI dashboard, and a
# MAGIC deployed app off it, all by prompting Genie Code. Share your app URL with the group,
# MAGIC show one Genie question that worked, and one dashboard tile.
