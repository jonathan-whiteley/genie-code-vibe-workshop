# Databricks notebook source
# MAGIC %md
# MAGIC # Lab 01: Build Your Command Center with Genie Code 🏗️
# MAGIC
# MAGIC In this lab you will build a fully governed operational command center for LCE
# MAGIC by prompting Genie Code in Agent mode. You tell it WHAT to build; the ai-dev-kit
# MAGIC skills installed in Lab 00 tell it HOW. You will go from raw workshop tables to a
# MAGIC live deployed app with an embedded Genie space and AI/BI dashboard, all without
# MAGIC leaving the chat.
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC
# MAGIC By the end of this lab you will have:
# MAGIC - Built a governed **metric view** over the workshop tables at store x date grain
# MAGIC - Created a **Genie space** grounded in your metric view with sample questions
# MAGIC - Published an **AI/BI dashboard** with four operational widgets
# MAGIC - Confirmed your **deployed app** from Lab 00 is running and optionally restyled it
# MAGIC - **Embedded** your Genie space and dashboard into the app with OBO authentication
# MAGIC - (Bonus) Scheduled a **daily refresh job** for your metric view and app

# COMMAND ----------

# MAGIC %md
# MAGIC ## How Genie Code works here (ground rules) 📋
# MAGIC
# MAGIC Before you start prompting, read these once:
# MAGIC
# MAGIC - **You build everything by prompting Genie Code in Agent mode.** The ai-dev-kit
# MAGIC   skills (installed in Lab 00) tell it how to build on Databricks. You tell it
# MAGIC   WHAT; the skills know HOW.
# MAGIC
# MAGIC - **Genie Code can author and run SQL/DDL** you are authorized for, and it can
# MAGIC   call Databricks APIs to create metric views, Genie spaces, dashboards, and
# MAGIC   deploy apps.
# MAGIC
# MAGIC - **Genie Code will NOT run permission or grant commands,** and it cannot bind
# MAGIC   app resources or set app OBO scopes. That is exactly why Lab 00 already:
# MAGIC   created your app, granted its service principal the warehouse and
# MAGIC   catalog/schema (which covers the tables and the metric view) and Lakebase, and
# MAGIC   set the genie/sql/dashboards.genie scopes. No prompt below ever asks Genie
# MAGIC   Code to grant anything or set scopes.
# MAGIC
# MAGIC - **Always read what Genie Code generates before running it.** If a generated
# MAGIC   statement looks wrong, ask Genie Code to explain or revise it before
# MAGIC   approving execution.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Session setup (paste this first) 🔧
# MAGIC
# MAGIC Open Genie Code, start a **new Agent-mode chat**, and paste the block below as
# MAGIC your very first message. Replace `<INITIALS>` with your actual initials (the same
# MAGIC ones you used in Lab 00). Do not send any other message until Genie Code
# MAGIC confirms.
# MAGIC
# MAGIC > **Important:** Use the same initials everywhere. The resource names must match
# MAGIC > exactly what Lab 00 created, otherwise Genie Code will try to create duplicates.
# MAGIC
# MAGIC ```text
# MAGIC I am doing the Genie Code Command Center lab in Agent mode. Remember these for the whole chat:
# MAGIC   My initials:  <INITIALS>
# MAGIC   Catalog:      ioc_sandbox.vibe_workshop
# MAGIC   Warehouse:    serverless
# MAGIC   Model:        databricks-claude-sonnet-4-6   (for ai_query() only)
# MAGIC My resources (use exactly these names):
# MAGIC   metric view:  <initials>_command_center_metrics
# MAGIC   Genie space:  "<initials> Command Center"
# MAGIC   dashboard:    "<initials> Operator Insights"
# MAGIC   app:          <initials>-command-center   (already created and deployed for me by Lab 00)
# MAGIC   job:          <initials>-command-center-refresh
# MAGIC As we go, remember my Genie space ID, dashboard ID, and app URL.
# MAGIC Confirm, then wait for my first module prompt.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 1: Build the metric view 📊
# MAGIC
# MAGIC A metric view is a governed semantic layer that defines your measures and
# MAGIC dimensions once so that Genie, dashboards, and SQL queries all speak the same
# MAGIC language. You will create one over the workshop tables at store x date grain.
# MAGIC Genie Code will author and execute the CREATE statement for you.
# MAGIC
# MAGIC > **Note:** Genie Code runs the CREATE statement for you. You need CREATE on
# MAGIC > the schema; if it is denied, ask your facilitator to grant your group CREATE
# MAGIC > on `ioc_sandbox.vibe_workshop`, or create the view in your own sandbox schema.
# MAGIC
# MAGIC ```text
# MAGIC Module 1. Create a metric view named <initials>_command_center_metrics over my
# MAGIC workshop tables at store x date grain. Measures: revenue, labor cost, labor % of
# MAGIC sales, days of cover, sell-through %, net sentiment. Dimensions: store, region,
# MAGIC date, day-of-week. Then run a SELECT to confirm it returns rows.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 2: Create a Genie space on the metric view 🧞
# MAGIC
# MAGIC A Genie space exposes your metric view to natural language queries. You will
# MAGIC create one with six sample questions covering the three operational pillars of
# MAGIC the command center: Labor, Inventory, and Guest Feedback.
# MAGIC
# MAGIC > **Tip:** After Genie Code creates the space, ask one question per pillar
# MAGIC > yourself before moving on. This confirms the space is grounded correctly and
# MAGIC > gives you the space ID you will need in Module 5.
# MAGIC
# MAGIC ```text
# MAGIC Module 2. Create a Genie space on my metric view <initials>_command_center_metrics.
# MAGIC Add 6 sample questions, 2 per pillar (Labor / Inventory / Guest Feedback), grounded
# MAGIC in the metric view measures. Ask one question per pillar to test it, then tell me
# MAGIC the space ID.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 3: Create an AI/BI dashboard on the metric view 📈
# MAGIC
# MAGIC An AI/BI dashboard gives stakeholders a visual snapshot of the same metrics your
# MAGIC Genie space answers conversationally. You will publish a four-widget dashboard
# MAGIC covering all three pillars. Make note of the dashboard ID that Genie Code returns
# MAGIC at the end; you will need it in Module 5.
# MAGIC
# MAGIC > **Tip:** Once Genie Code publishes the dashboard, open the link it returns to
# MAGIC > verify all four widgets render before moving on.
# MAGIC
# MAGIC ```text
# MAGIC Module 3. Create an AI/BI dashboard on my metric view with 4 widgets: labor % of
# MAGIC sales (30-day line), revenue by region (bar), days of cover / stock health (bar),
# MAGIC net sentiment timeline (line). Publish it and tell me the dashboard ID.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 4: Confirm and polish your app 🎨
# MAGIC
# MAGIC Lab 00 already created, permissioned, scoped, and deployed your app. This module
# MAGIC does not recreate it. You will confirm it is healthy and optionally restyle the
# MAGIC LCE branding before adding the embedded views in Module 5.
# MAGIC
# MAGIC > **Note:** Lab 00 already created, permissioned, scoped, and deployed your app.
# MAGIC > This module does not recreate it. Genie Code can edit source and redeploy, but
# MAGIC > it cannot change resources or scopes (and does not need to).
# MAGIC
# MAGIC ```text
# MAGIC Module 4. My app <initials>-command-center is already deployed (Lab 00 created it).
# MAGIC Open its URL and check that /api/wiring is green. Optional: restyle the LCE branding
# MAGIC in the app source (logo branding/lce/logo.svg, primary #FF671B, dark navbar, title
# MAGIC "Command Center | LCE") and redeploy. Do not change the app's resources or scopes.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 5: Embed your Genie space and dashboard 🔗
# MAGIC
# MAGIC Now you will wire the Genie space and the dashboard you built in Modules 2 and 3
# MAGIC into the app. The key requirement is on-behalf-of (OBO) authentication: the app
# MAGIC calls Genie and renders the dashboard as the signed-in user, not as the app
# MAGIC service principal, so each user sees only what they are authorized to see.
# MAGIC
# MAGIC > **Important:** The genie, sql, and dashboards.genie OBO scopes are already set
# MAGIC > on your app by Lab 00. Do not ask Genie Code to add scopes; it cannot, and
# MAGIC > they are not needed.
# MAGIC
# MAGIC ```text
# MAGIC Module 5. Update my app to embed MY Genie space (the ID from Module 2) and MY
# MAGIC dashboard (the ID from Module 3), then redeploy:
# MAGIC   - Call Genie on behalf of the signed-in user using the X-Forwarded-Access-Token
# MAGIC     header (OBO), not the app service principal, so it uses my access to my space.
# MAGIC   - Embed my published dashboard by its ID, rendered as the signed-in user.
# MAGIC   - Support multi-turn: start-conversation on the first ask, then post to the
# MAGIC     conversation messages endpoint; poll until COMPLETED; return the answer and the
# MAGIC     SQL Genie generated.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Module 6 (BONUS): Schedule a refresh job ⏰
# MAGIC
# MAGIC If you finish early, create a scheduled job that keeps your metric view and app
# MAGIC up to date. The job runs as you, so no extra permissions are needed beyond what
# MAGIC you already have.
# MAGIC
# MAGIC > **Tip:** After Genie Code creates the job, open the Jobs UI and confirm the
# MAGIC > schedule shows 6am ET before leaving the workshop.
# MAGIC
# MAGIC ```text
# MAGIC Module 6 (bonus). Create a daily job named <initials>-command-center-refresh at
# MAGIC 6am ET that refreshes my metric view's source rollups and redeploys my app. The
# MAGIC job runs as me, so no extra permissions are needed.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion 🏁
# MAGIC
# MAGIC You have built a fully governed operational command center by prompting Genie
# MAGIC Code, without writing a single line of boilerplate yourself. Starting from raw
# MAGIC workshop tables, you created a metric view that defines your measures once and
# MAGIC serves as the single source of truth for every layer above it. From that metric
# MAGIC view you hung a Genie space for natural language queries, an AI/BI dashboard for
# MAGIC visual reporting, and a deployed app that embeds both using OBO authentication so
# MAGIC every user sees data they are authorized for.
# MAGIC
# MAGIC **Share your app URL** with your facilitator or teammates to show the finished
# MAGIC command center. The URL is printed in your Lab 00 output and available from the
# MAGIC Databricks Apps UI.
# MAGIC
# MAGIC > **Next steps:** Take the patterns from today back to a real account. The same
# MAGIC > flow (metric view, Genie space, dashboard, app) works on any governed table in
# MAGIC > Unity Catalog. The ai-dev-kit skills remain installed in your workspace after
# MAGIC > the workshop ends.
