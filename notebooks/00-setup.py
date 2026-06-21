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

# COMMAND ----------

# MAGIC %pip install -q --upgrade "databricks-sdk>=0.40"

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Enter your initials 🔤
# MAGIC
# MAGIC Your initials prefix every resource you create today, so they must be unique in
# MAGIC the workshop. Enter two or three lowercase letters in the widget at the top, then
# MAGIC **Run All**.

# COMMAND ----------

dbutils.widgets.text("initials", "", "Your initials (e.g. jjw)")
INITIALS = dbutils.widgets.get("initials").strip().lower()
if not INITIALS:
    raise ValueError("Set the 'initials' widget at the top, then Run All.")
print(f"Setting up for: {INITIALS}")
print(f"Your app will be: {INITIALS}-command-center")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Install the ai-dev-kit skills 🤖
# MAGIC
# MAGIC Installs the [ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit)
# MAGIC skills into your workspace: the knowledge Genie Code uses to build on Databricks
# MAGIC (metric views, Genie spaces, dashboards, apps).
# MAGIC
# MAGIC > If the skills do not appear in Genie Code afterward, hard-refresh the browser
# MAGIC > (Cmd+Shift+R / Ctrl+Shift+R) before starting Lab 01.

# COMMAND ----------

# MAGIC %run ./utils/install_genie_code_skills

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Clone your app from a template 🚀
# MAGIC
# MAGIC Clones a ready-made Databricks App template under your initials and deploys it,
# MAGIC with all permissions and OBO scopes wired for you. It is the same kind of starter
# MAGIC app you can browse on the [Databricks Developer Hub](https://developers.databricks.com/),
# MAGIC which hosts templates for Genie analytics apps, Lakebase apps, and more.
# MAGIC
# MAGIC ![Databricks Developer Hub templates](https://raw.githubusercontent.com/jonathan-whiteley/genie-code-vibe-workshop/main/docs/images/developer-hub-templates.png)
# MAGIC
# MAGIC > Run this once. If your app looks off later, open its URL (printed below) to
# MAGIC > confirm it loads before re-running.

# COMMAND ----------

# MAGIC %run ./utils/clone_app

# COMMAND ----------

# MAGIC %md
# MAGIC ## You are ready! 🎉
# MAGIC
# MAGIC Your very own Operator Command Center app is deployed (open its URL, printed
# MAGIC above, to confirm it loads) and the ai-dev-kit skills are installed.
# MAGIC
# MAGIC **Next steps:**
# MAGIC
# MAGIC 1. Open Genie Code and start a **new chat** (hard-refresh if the skills are missing).
# MAGIC 2. Open the **`01-workshop-prompts`** notebook and work through it from the
# MAGIC    session setup prompt onward.
