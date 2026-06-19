# Databricks notebook source
# MAGIC %md
# MAGIC # Helper: Install ai-dev-kit skills into Genie Code
# MAGIC
# MAGIC Called by `attendee_setup` via `%run`. Genie Code loads skills from your
# MAGIC user folder `/Users/<you>/.assistant/skills/`. This helper delegates to the
# MAGIC official, maintained installer in the ai-dev-kit repo so it never drifts:
# MAGIC it clones (or updates) ai-dev-kit as a Workspace Git folder, then runs
# MAGIC `databricks-skills/install_genie_code_skills`.
# MAGIC
# MAGIC Every network call is wrapped: if the automated path is blocked (no Git
# MAGIC integration, etc.), it prints the exact manual steps instead of failing.

# COMMAND ----------

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
ME = w.current_user.me().user_name

AI_DEV_KIT_URL = "https://github.com/databricks-solutions/ai-dev-kit"
REPO_PATH = f"/Workspace/Users/{ME}/ai-dev-kit"
# The installer is a notebook inside the repo; reference it without the .py suffix.
INSTALLER_PATH = f"{REPO_PATH}/databricks-skills/install_genie_code_skills"

print(f"ai-dev-kit target : {REPO_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Clone or update ai-dev-kit
# MAGIC Idempotent: updates the existing Git folder if present, else clones it.

# COMMAND ----------

cloned = False
try:
    existing = next((r for r in w.repos.list() if r.path == REPO_PATH), None)
    if existing:
        # Provider/branch field names can vary by SDK version; confirm if this errors.
        w.repos.update(existing.id, branch="main")
        print("Updated existing ai-dev-kit Git folder to latest main.")
    else:
        w.repos.create(url=AI_DEV_KIT_URL, provider="gitHub", path=REPO_PATH)
        print("Cloned ai-dev-kit into your workspace.")
    cloned = True
except Exception as e:
    print(f"Could not clone or update via the Repos API: {e}\n")
    print("Manual fallback (do this once, then re-run attendee_setup):")
    print(f"  1. In the workspace, create a Git folder from {AI_DEV_KIT_URL}")
    print(f"  2. Open {INSTALLER_PATH} and Run All")
    print("  3. Open Genie Code and start a new chat")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run the official skills installer
# MAGIC Runs the ai-dev-kit installer notebook, which copies the skill folders into
# MAGIC your `/Users/<you>/.assistant/skills/` so Genie Code can load them.

# COMMAND ----------

if cloned:
    try:
        result = dbutils.notebook.run(INSTALLER_PATH, 600)
        print(f"Skills installer finished: {result}")
    except Exception as e:
        print(f"Could not auto-run the installer: {e}\n")
        print(f"Open {INSTALLER_PATH} and Run All by hand, then continue.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## After this step
# MAGIC Skills load when you open a **new chat thread**. Once setup finishes,
# MAGIC open Genie Code, start a new chat, and hard refresh the browser if the
# MAGIC skills do not appear. Verify with the smoke-test prompt in the lab
# MAGIC companion guide (list the 8 tables in the schema).
