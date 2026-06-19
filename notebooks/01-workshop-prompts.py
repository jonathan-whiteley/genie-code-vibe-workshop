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
# MAGIC Create my Command Center metric view at store x date grain, from just two tables: facts_sales_daypart and facts_labor_daypart.
# MAGIC
# MAGIC Roll each table up to one row per store per date in its own subquery first (sum revenue, forecast revenue, and traffic from sales; sum labor cost and forecast labor cost from labor), then join the two rollups on date and store, and join dims_stores for region. Do not create any separate or intermediary view, only the single metric view.
# MAGIC
# MAGIC Measures:
# MAGIC - revenue
# MAGIC - forecast revenue
# MAGIC - traffic
# MAGIC - labor cost
# MAGIC - forecast labor cost
# MAGIC - labor % of sales (labor cost / revenue)
# MAGIC
# MAGIC Dimensions: store, region, date, day-of-week.
# MAGIC
# MAGIC Run a SELECT to confirm it returns rows and that labor % of sales is realistic (around 20 to 35%).
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
# MAGIC Create a Genie space on my metric view.
# MAGIC
# MAGIC Add 6 sample questions grounded in the metric view measures (revenue, forecast, labor cost, labor % of sales).
# MAGIC
# MAGIC Ask a few questions to test it, then tell me the space ID.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### Module 2 follow-up: add a benchmark set 🎯
# MAGIC
# MAGIC Benchmarks measure how accurately Genie answers known questions. Add a set of 10,
# MAGIC then run it to see how your space scores. Copy the prompt below.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Add these 10 benchmark questions to my Genie space, then run the benchmark and
# MAGIC tell me how many Genie answered correctly:
# MAGIC
# MAGIC - Which 5 stores had the highest labor % of sales last week?
# MAGIC - How has labor % of sales trended over the last 30 days across all stores?
# MAGIC - Which region has the lowest labor % of sales this month?
# MAGIC - Which stores are below their revenue forecast this week?
# MAGIC - Show the revenue trend over the last 30 days.
# MAGIC - How did labor cost track against its forecast this week?
# MAGIC - Which 5 stores have the highest revenue this month?
# MAGIC - Rank regions by total revenue this month.
# MAGIC - What is the busiest day of week by revenue?
# MAGIC - Which stores improved labor % of sales the most over the last 30 days?
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
# MAGIC Create a rich AI/BI dashboard on my metric view.
# MAGIC
# MAGIC Start with a row of KPI counters (latest day):
# MAGIC - total revenue
# MAGIC - labor % of sales
# MAGIC - revenue vs forecast
# MAGIC - traffic
# MAGIC
# MAGIC Then add these charts:
# MAGIC - revenue trend, last 30 days (line)
# MAGIC - labor % of sales, last 30 days (line)
# MAGIC - revenue by region (bar)
# MAGIC - revenue vs forecast by store (bar)
# MAGIC - labor cost vs forecast by store (bar)
# MAGIC - revenue by day-of-week (bar)
# MAGIC
# MAGIC Give it Little Caesars branding and make it pop:
# MAGIC - use the LCE orange (#FF671B) as the primary accent across the charts
# MAGIC - set a bold, cool dashboard background color
# MAGIC - use vibrant, high-contrast colors so the charts really stand out
# MAGIC - add a title with the Little Caesars feel
# MAGIC
# MAGIC Publish it and tell me the dashboard ID.
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
# MAGIC My Command Center app is already deployed (Lab 00 created it).
# MAGIC
# MAGIC Open its URL and confirm it loads.
# MAGIC
# MAGIC Now give it Little Caesars branding and make it pop:
# MAGIC - copy the LCE logo from my workshop Git folder (branding/lce/logo.svg) into the app's static assets and use it in the header
# MAGIC - use LCE orange (#FF671B) as the accent throughout: buttons, links, active tabs, and KPI highlights
# MAGIC - add a bold hero header on the Today tab with the logo and the store name
# MAGIC - give the tiles and cards rounded corners, soft shadows, and a subtle hover lift
# MAGIC - add a thin LCE-orange top accent bar and a dark navbar
# MAGIC - title the app "Command Center | LCE"
# MAGIC
# MAGIC Then redeploy.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### Module 4 follow-up: dark mode for the Today tab 🌙
# MAGIC
# MAGIC Give the home (Today) tab a sleek dark theme while keeping the LCE accents.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Restyle the Today tab in dark mode: a deep dark background with light text, and keep the LCE orange (#FF671B) accents popping against it. Leave the other tabs as they are. Then redeploy.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 5: Embed your Genie space and dashboard 🔗
# MAGIC
# MAGIC Your app already has an Ask Genie panel and a home page with 3 tiles. You are
# MAGIC swapping in your own Genie space and adding your dashboard below the tiles.
# MAGIC
# MAGIC > **Important:** the genie, sql, and dashboards.genie OBO scopes are already set on
# MAGIC > your app by Lab 00, and the Ask Genie panel already uses on-behalf-of-user auth.
# MAGIC > Do not rebuild the panel or change scopes.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC My app already has an Ask Genie panel wired to a Genie space, and a home page with 3 tiles. Make these two changes, then redeploy:
# MAGIC
# MAGIC 1. Swap the Ask Genie panel to use MY Genie space (the space ID from the Genie step). Do not rebuild the panel or its auth; just point it at my space ID.
# MAGIC
# MAGIC 2. Embed my published AI/BI dashboard as an iframe on the home page, directly below the 3 tiles. To avoid a "refused to connect" iframe error:
# MAGIC    - use the dashboard's published EMBED url (the /embed/ link from the dashboard's Share then Embed), NOT the normal dashboard link; the normal workspace link sets X-Frame-Options and refuses to be framed.
# MAGIC    - make sure the dashboard is Published with embedding enabled, and add my app's domain (the .databricksapps.com host of my app URL) to the dashboard's list of approved domains for embedding.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 6 (BONUS): Schedule a refresh job ⏰
# MAGIC
# MAGIC Automate the refresh so the data and app stay current.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Create my daily refresh job at 6am ET with these steps:
# MAGIC - refresh my metric view's source rollups
# MAGIC - redeploy my app
# MAGIC
# MAGIC The job runs as me, so no extra permissions are needed.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion 🏁
# MAGIC
# MAGIC You built a governed metric view and hung a Genie space, an AI/BI dashboard, and a
# MAGIC deployed app off it, all by prompting Genie Code. Share your app URL with the group,
# MAGIC show one Genie question that worked, and one dashboard tile.
