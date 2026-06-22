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
# MAGIC - **Module 6:** live AI in your Command Center: an `ai_query()` briefing function + a Company News feed via MCP web search
# MAGIC - **Module 7 (bonus):** a scheduled job that refreshes everything

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
# MAGIC   the tables and the metric view), and set the genie, sql, and
# MAGIC   dashboards.genie scopes. So no prompt here asks Genie Code to grant anything.
# MAGIC - This workshop also ships a `command-center-patterns` skill: field-tested
# MAGIC   patterns for the trickier steps (metric view, dashboard embed, Genie swap,
# MAGIC   MCP feed, Genie functions). Genie Code loads it automatically; the hardest
# MAGIC   prompts also name the exact pattern file.
# MAGIC - Always read what Genie Code generates before you run it.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Personalize your prompts 🔧
# MAGIC
# MAGIC Run the two cells below. The second prints your session-setup prompt, filled in
# MAGIC with your initials. Copy its **entire output** (that whole cell is the prompt) and
# MAGIC paste it into Genie Code as your **first** message.
# MAGIC
# MAGIC > **Tip:** If you did not run Lab 00 in this workspace, type your initials into the
# MAGIC > `initials` widget at the top of this notebook, then run the cells again.

# COMMAND ----------

# MAGIC %run ./utils/session_setup

# COMMAND ----------

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
# MAGIC Create my Command Center metric view at store x date grain.
# MAGIC
# MAGIC - Name it <my initials>_command_center_metrics, over facts_sales_daypart
# MAGIC   and facts_labor_daypart plus dims_stores. One metric view, no
# MAGIC   intermediary views.
# MAGIC - Pre-aggregate each fact table to one row per store per date in its own
# MAGIC   subquery before joining (the daypart and role grain double-counts otherwise).
# MAGIC - Measures: revenue, forecast revenue, traffic, labor cost,
# MAGIC   forecast labor cost, labor % of sales.
# MAGIC - Dimensions: store, region, date, day-of-week.
# MAGIC - Then run a verification SELECT.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 2: Create a Genie space on the metric view 🧞
# MAGIC
# MAGIC A Genie space lets anyone ask questions in natural language. It is grounded in
# MAGIC your governed measures (the metric view) and can also reach the raw tables for
# MAGIC finer detail (SKU, employees, feedback, daypart) the metric view does not expose.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Create a Genie space on two kinds of source so it can answer both governed-KPI
# MAGIC and finer-grained questions:
# MAGIC - my metric view (<my initials>_command_center_metrics), and
# MAGIC - the raw tables in ioc_sandbox.vibe_workshop (dims_stores, dims_items,
# MAGIC   dims_employees, facts_sales_daypart, facts_labor_daypart,
# MAGIC   facts_sales_inventory_daily, facts_purchase_orders, facts_customer_feedback).
# MAGIC
# MAGIC Add a space instruction: use the metric view for the governed KPIs (revenue,
# MAGIC forecast, traffic, labor cost, labor % of sales at store x date grain); use the
# MAGIC raw tables for detail the metric view does not cover (SKU / inventory, employees,
# MAGIC purchase orders, customer feedback / sentiment, and daypart or role breakdowns).
# MAGIC
# MAGIC Add 6 sample questions that span both: a couple of KPI questions and a couple of
# MAGIC detail questions.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### Module 2 follow-up: add a benchmark set 🎯
# MAGIC
# MAGIC Benchmarks measure how accurately Genie answers known questions. Add a set of 10
# MAGIC to your space, then run them in the Genie UI to see how it scores. Copy the prompt below.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Come up with 10 benchmark questions for my Genie space based on the metric view's
# MAGIC measures and dimensions, and add them to the space.
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
# MAGIC Create a visual-first AI/BI dashboard on my metric view. No KPI counter
# MAGIC tiles, just a handful of charts that surface insight.
# MAGIC
# MAGIC Charts:
# MAGIC - Revenue share by region: pie / donut
# MAGIC - Revenue trend, last 30 days: line
# MAGIC - Revenue vs forecast revenue by store: bar
# MAGIC - Labor % of sales by store: bar, sorted high to low
# MAGIC - Revenue by day-of-week: bar
# MAGIC
# MAGIC Theme it for visual interest, like a polished editorial dashboard. Set the
# MAGIC dashboard theme with both light and dark variants (not just per-widget colors):
# MAGIC - Canvas background: light #FDF8F3, dark #1A1210
# MAGIC - Widget cards: light #FFFFFF, dark #2A1F1A; borders light #E8DDD4, dark #3D2E24
# MAGIC - Font color: light #3B2316, dark #F5EDE6; serif family (Georgia); left-align headers
# MAGIC - Selection / accent: light #FF671B (LCE orange), dark #FF8A4C
# MAGIC - Visualization palette (same in both): #FF671B (LCE orange, lead), #7B9E6B,
# MAGIC   #8B4557, #D4A853, #5B8FA8, #D4785C, #6B5B8A, #3D7A6E
# MAGIC - A title with the Little Caesars feel
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
# MAGIC - copy the LCE logo from my workshop Git folder (docs/branding/lce/logo.svg) into the app's static assets and use it in the header
# MAGIC - copy the favicon from my workshop Git folder (docs/branding/lce/favicon.svg) into the app's static assets and wire it up with a <link rel="icon"> in the page <head> so it shows in the browser tab
# MAGIC - use LCE orange (#FF671B) as the accent throughout: buttons, links, active tabs, and KPI highlights
# MAGIC - add a bold hero header on the Today tab with the logo and the store name
# MAGIC - give the tiles and cards rounded corners, soft shadows, and a subtle hover lift
# MAGIC - add a thin LCE-orange top accent bar and a dark navbar
# MAGIC - set the browser tab title (the HTML <title> tag) to exactly "Command Center" with no store number
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
# MAGIC
# MAGIC Follow docs/patterns/app-editing-pattern.md: audit each component's background/color/border for contrast first (the Card defaults to a white background), override CSS tokens in :root instead of hunting inline colors, and edit the files with Python open() then verify on disk before redeploying.
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
# MAGIC My app already has an Ask Genie panel and a home page with 3 tiles.
# MAGIC Make these two changes, then redeploy:
# MAGIC
# MAGIC 1. Swap the Ask Genie panel to use MY Genie space (the space ID from
# MAGIC    the Genie step), following docs/patterns/genie-swap-pattern.md. Point it
# MAGIC    at my space ID; do not rebuild the panel or its auth.
# MAGIC
# MAGIC 2. Embed my published AI/BI dashboard as an iframe below the 3 tiles,
# MAGIC    following docs/patterns/dashboard-embed-pattern.md (use the
# MAGIC    /embed/ URL, and add an "Open in Databricks" fallback link above it).
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 6: Bring live AI into your Command Center 🤖
# MAGIC
# MAGIC Two AI features here:
# MAGIC - **A: a store briefing** your Genie space can generate with `ai_query()` over your metric view
# MAGIC - **B: a Company News feed** in the app, fetched live through the `web_search_mcp` MCP server
# MAGIC
# MAGIC > **Pre-reqs (facilitator/admin):** Feature A runs `ai_query()` as the asking user, so
# MAGIC > your workshop group needs `CAN_QUERY` on `databricks-claude-sonnet-4-6`. Feature B's
# MAGIC > app calls the `web_search_mcp` MCP server as the app's **service principal**, which the
# MAGIC > admin must grant access to. Genie Code cannot grant either; flag permission errors to
# MAGIC > your facilitator.

# COMMAND ----------

# MAGIC %md
# MAGIC ### A: the store briefing (Genie function) 📋
# MAGIC
# MAGIC A Unity Catalog function that calls Claude through `ai_query()` over your metric view
# MAGIC and returns a plain-language briefing of the latest day plus a recommended Next Best
# MAGIC Action. Register it with your Genie space and Genie can call it on request, including
# MAGIC from the **Ask Genie** panel in your app: no app code change, because the panel already
# MAGIC runs as you.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Create an AI store-briefing function and register it with my Genie space,
# MAGIC following docs/patterns/genie-space-pattern.md. Genie calls functions as
# MAGIC SELECT * FROM func(), which dictates the shape:
# MAGIC
# MAGIC - Create a UC function <my initials>_store_briefing() in my metric view's
# MAGIC   catalog/schema that RETURNS TABLE (briefing STRING). Use inline subqueries,
# MAGIC   NOT CTEs. Read my store's latest-day numbers (revenue, forecast revenue,
# MAGIC   labor % of sales, traffic, prior-day revenue) from the metric view and pass
# MAGIC   them to ai_query() on databricks-claude-sonnet-4-6 for a 3-bullet manager
# MAGIC   briefing plus a "Next Best Action", under 100 words. Use chr(36) for any $
# MAGIC   in string literals, and create the function via executeCode (not editAsset).
# MAGIC - Register it in my Genie space as a sql_example instruction
# MAGIC   (addInstructionsToSpace) mapping a question to
# MAGIC   SELECT * FROM <cat>.<sch>.<my initials>_store_briefing(). Do NOT use
# MAGIC   serialized_space sql_functions (it creates a broken certified answer).
# MAGIC - Optionally add "Give me today's store briefing" as a sample question chip.
# MAGIC
# MAGIC Do not call it from here; I'll try it in the Ask Genie panel.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### A follow-up: make it one click 🎯
# MAGIC
# MAGIC Surface the briefing as a starter question so anyone can trigger it instantly,
# MAGIC in the space and in your app's Ask Genie panel.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Add "Give me today's store briefing" as a starter question in two
# MAGIC places, then redeploy the app:
# MAGIC - as a sample question on my Genie space, and
# MAGIC - as a suggested question in my app's Ask Genie panel UI.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### B: a live Company News feed (MCP) 📰
# MAGIC
# MAGIC Add a Company News feature to your app that pulls live headlines through the
# MAGIC `web_search_mcp` MCP server and summarizes them with `ai_query()`. There is a proven
# MAGIC pattern (and the gotchas that bite you) in your workshop Git folder at
# MAGIC `docs/patterns/mcp-company-news-pattern.md`: the prompt below points Genie Code at it.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Add a "Company News" feature to my app, then redeploy.
# MAGIC
# MAGIC Follow the pattern in docs/patterns/mcp-company-news-pattern.md:
# MAGIC - fetch live news from the web_search_mcp MCP server,
# MAGIC - summarize the results with ai_query,
# MAGIC - show 3 bullets in a bell-icon dropdown in the header.
# MAGIC
# MAGIC Save the app files one at a time, not in parallel (the Workspace Files API rate-limits bursty writes).
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 7 (BONUS): Schedule a multi-task refresh job ⏰
# MAGIC
# MAGIC Automate the whole refresh as a multi-task job: validate the data, refresh the
# MAGIC dashboard, then redeploy the app, so everything stays current each week.

# COMMAND ----------

# MAGIC %md
# MAGIC ```text
# MAGIC Create my weekly job <my initials>-command-center-refresh, scheduled for 6am ET
# MAGIC every Monday, with these tasks run in order (each depends on the one before):
# MAGIC
# MAGIC 1. Validate the metric view: a SQL task that selects a few MEASURE() rows from
# MAGIC    my metric view and fails if it returns no rows (a freshness / quality gate).
# MAGIC 2. Refresh the dashboard: a dashboard task that refreshes my AI/BI dashboard so
# MAGIC    its datasets recompute.
# MAGIC 3. Redeploy the app: a task that redeploys my <my initials>-command-center app
# MAGIC    so it serves the latest.
# MAGIC
# MAGIC Add an email notification to me on failure. The job runs as me, so no extra
# MAGIC permissions are needed.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion 🏁
# MAGIC
# MAGIC You built a governed metric view and hung a Genie space, an AI/BI dashboard, and a
# MAGIC deployed app off it, all by prompting Genie Code. Share your app URL with the group,
# MAGIC show one Genie question that worked, and one dashboard tile.
