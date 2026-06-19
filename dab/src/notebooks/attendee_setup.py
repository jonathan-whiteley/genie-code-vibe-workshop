# Databricks notebook source
# MAGIC %md
# MAGIC # Attendee Setup (run this once, before the workshop)
# MAGIC
# MAGIC This is your only pre-req. It does the two things the in-workspace coding
# MAGIC agent (Genie Code) cannot do for you, so the rest of the workshop is pure
# MAGIC prompting:
# MAGIC
# MAGIC 1. **Install the ai-dev-kit skills into Genie Code** so the agent knows how
# MAGIC    to build metric views, Genie spaces, dashboards, and apps on Databricks.
# MAGIC 2. **Create your `<initials>-command-center` app** from the shared template,
# MAGIC    and wire its service principal to the warehouse, the catalog and schema
# MAGIC    (which covers the tables and the metric view), Lakebase, and the OBO
# MAGIC    scopes, then deploy it.
# MAGIC
# MAGIC Both steps live in `utils/` so this notebook stays readable. You do not need
# MAGIC to open them; just set your initials below and Run All.
# MAGIC
# MAGIC **Before you run:** clone this repo as a Workspace Git folder (Workspace >
# MAGIC Create > Git folder, paste the repo URL). Open this notebook from inside that
# MAGIC Git folder so the `%run ./utils/...` calls resolve.

# COMMAND ----------

# MAGIC %pip install -q --upgrade "databricks-sdk>=0.40"

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Set your initials
# MAGIC This is the only value you enter. Everything else is read from the shared
# MAGIC template app and the facilitator config, so there is nothing to keep in sync.

# COMMAND ----------

dbutils.widgets.text("initials", "", "Your initials (e.g. jjw)")
INITIALS = dbutils.widgets.get("initials").strip().lower()
if not INITIALS:
    raise ValueError("Set the 'initials' widget at the top, then Run All.")
print(f"Setting up for: {INITIALS}")
print(f"Your app will be: {INITIALS}-command-center")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Install ai-dev-kit skills into Genie Code

# COMMAND ----------

# MAGIC %run ./utils/install_genie_code_skills

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Create and deploy your app, wired with permissions and scopes

# COMMAND ----------

# MAGIC %run ./utils/clone_app

# COMMAND ----------

# MAGIC %md
# MAGIC ## You are ready
# MAGIC
# MAGIC - Your `<initials>-command-center` app is deployed and wired (see the URL
# MAGIC   printed above; open `<url>/api/wiring` to confirm it is green).
# MAGIC - The ai-dev-kit skills are installed.
# MAGIC
# MAGIC **Next:** open Genie Code, start a **new Agent-mode chat** (hard refresh if
# MAGIC the skills do not appear), and work through the module prompts in the lab
# MAGIC companion guide, starting with the metric view.
