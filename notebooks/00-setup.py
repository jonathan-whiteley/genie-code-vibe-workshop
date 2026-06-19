# Databricks notebook source
# MAGIC %md
# MAGIC # Lab 00: Setup (run this first) 🛠️
# MAGIC
# MAGIC Welcome to the Genie Code Command Center workshop! Before you start building,
# MAGIC this notebook completes two pieces of prep that Genie Code cannot do on its own:
# MAGIC it installs the ai-dev-kit skills so the agent knows how to provision Databricks
# MAGIC resources, and it creates and deploys your personal app with all the permissions
# MAGIC and OBO scopes already wired. Once this notebook finishes, everything else in the
# MAGIC workshop is pure prompting.
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC
# MAGIC By the end of this setup you will have:
# MAGIC - Installed the ai-dev-kit Genie Code skills into your workspace
# MAGIC - Created your personal `<initials>-command-center` app from the shared template
# MAGIC - Granted the app service principal access to the warehouse, catalog/schema,
# MAGIC   and Lakebase
# MAGIC - Set the genie, sql, and dashboards.genie OBO scopes on the app
# MAGIC - Deployed the app and confirmed it is reachable at `/api/wiring`
# MAGIC
# MAGIC > **Before you run:** clone this repo as a Workspace Git folder (Workspace >
# MAGIC > Create > Git folder, paste the repo URL). Open this notebook from inside that
# MAGIC > Git folder so the `%run ./utils/...` calls resolve correctly.

# COMMAND ----------

# MAGIC %pip install -q --upgrade "databricks-sdk>=0.40"

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Enter your initials 🔤
# MAGIC
# MAGIC This is the only value you need to provide. Everything else (template app,
# MAGIC facilitator config, warehouse, catalog) is read automatically. Your initials
# MAGIC become the prefix for every resource you create today, so they must be unique
# MAGIC within the workshop (use two or three lowercase letters, no spaces).
# MAGIC
# MAGIC Enter your initials in the widget at the top of the page, then continue to
# MAGIC **Run All**.
# MAGIC
# MAGIC > **Tip:** Use the same initials throughout the entire workshop. The session
# MAGIC > setup prompt in Lab 01 will ask you to enter them once more so Genie Code
# MAGIC > remembers them for the full chat.

# COMMAND ----------

dbutils.widgets.text("initials", "", "Your initials (e.g. jjw)")
INITIALS = dbutils.widgets.get("initials").strip().lower()
if not INITIALS:
    raise ValueError("Set the 'initials' widget at the top, then Run All.")
print(f"Setting up for: {INITIALS}")
print(f"Your app will be: {INITIALS}-command-center")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Install ai-dev-kit skills into Genie Code 🤖
# MAGIC
# MAGIC The ai-dev-kit skills are what give Genie Code the knowledge to build on
# MAGIC Databricks: creating metric views, Genie spaces, AI/BI dashboards, and apps.
# MAGIC Without them, Genie Code would not know the correct APIs or payload shapes.
# MAGIC The utility script below installs them directly into your workspace so they
# MAGIC are available the next time you open Genie Code in Agent mode.
# MAGIC
# MAGIC > **Note:** If the skills do not appear in Genie Code after this step, do a
# MAGIC > hard refresh of the browser tab (Cmd+Shift+R / Ctrl+Shift+R) before starting
# MAGIC > Lab 01.

# COMMAND ----------

# MAGIC %run ./utils/install_genie_code_skills

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create and deploy your app 🚀
# MAGIC
# MAGIC This step clones the shared workshop app template under your initials, grants
# MAGIC the app service principal the necessary warehouse and catalog/schema permissions
# MAGIC (which also covers the metric view you will build in Module 1), attaches
# MAGIC Lakebase, sets the genie/sql/dashboards.genie OBO scopes, and deploys the app.
# MAGIC
# MAGIC This is the only time permissions and scopes are configured. No prompt in Lab 01
# MAGIC will ever ask Genie Code to grant permissions or set scopes, because they are
# MAGIC already in place after this step completes.
# MAGIC
# MAGIC > **Important:** Do not run this cell a second time during the workshop. If
# MAGIC > something looks wrong with your app, open `/api/wiring` in the app URL
# MAGIC > (printed below when the step finishes) to diagnose before re-running.

# COMMAND ----------

# MAGIC %run ./utils/clone_app

# COMMAND ----------

# MAGIC %md
# MAGIC ## You are ready! 🎉
# MAGIC
# MAGIC Setup is complete. Here is what was done for you:
# MAGIC
# MAGIC - Your `<initials>-command-center` app is deployed and wired. Open
# MAGIC   `<url>/api/wiring` (URL printed above) to confirm the green status.
# MAGIC - The ai-dev-kit skills are installed in your workspace.
# MAGIC
# MAGIC **Next steps:**
# MAGIC
# MAGIC 1. Open Genie Code and start a **new Agent-mode chat** (hard refresh if the
# MAGIC    skills do not appear in the tool list).
# MAGIC 2. Open **Lab 01: Build Your Command Center with Genie Code** and follow the
# MAGIC    module prompts from top to bottom.
# MAGIC 3. Start with the session setup prompt to give Genie Code your initials and
# MAGIC    resource names, then work through Modules 1-6.
# MAGIC
# MAGIC > **Tip:** Keep this notebook open in a separate tab. If you ever need to
# MAGIC > check your app URL or re-run a utility, it is right here.
