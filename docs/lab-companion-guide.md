# Genie Code Workshop: Operator Command Center: Lab Companion Guide

**You'll build:** "Command Center", a Databricks App that surfaces AI insights and analytics across **Labor, Inventory, and Guest Feedback** for store operations. Your app will embed a Genie space and an AI/BI dashboard, both built on a single governed **Metric View** you define first. Everything runs inside the Databricks workspace using **Genie Code** (no local install required).

**Duration:** 3 hours.

### Quick Links

- **Workshop repo:** [github.com/jonathan-whiteley/genie-code-vibe-workshop](https://github.com/jonathan-whiteley/genie-code-vibe-workshop)
- **ai-dev-kit skills:** [github.com/databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit#genie-code-skills)
- **Genie Code skills docs:** [docs.databricks.com/aws/en/genie-code/skills](https://docs.databricks.com/aws/en/genie-code/skills)
- **Workspace:** provided by your facilitator

---

## Agenda

| Time | Module | Outcome |
|---|---|---|
| pre (async) | Setup | Repo cloned as Git folder; `notebooks/00-setup` notebook ran (skills installed + app deployed) |
| 0:00-0:10 | Welcome + demo | See finished app; get env values + session-setup prompt |
| 0:10-0:25 | Module 1: Metric View | Governed KPIs defined over landed tables |
| 0:25-0:45 | Module 2: Genie Space | Natural-language Q&A on the metric view |
| 0:45-1:05 | Module 3: AI/BI Dashboard | 4 widgets driven by the metric view |
| 1:05-1:15 | Break | |
| 1:15-1:45 | Module 4: App polish | `<initials>-command-center` already deployed; verify wiring + optional branding tweaks |
| 1:45-2:25 | Module 5: Embed | Genie + dashboard live in the app |
| 2:25-2:50 | Module 6 (BONUS): Job | Scheduled refresh job |
| 2:50-3:00 | Demo round + wrap | Share App URL |

Times are relative; your facilitator sets the wall clock.

---

## How to use this guide

Every prompt below is in a **code block**: hit the copy button, paste into **Genie Code** in the workspace. **You only fill in `<INITIALS>` once**, in the **Session setup** prompt at the start of the day-of section. Every prompt after that says "my metric view", "my Genie space", etc.; the agent already knows the values from the setup prompt.

Prompts are short on purpose. The agent has **ai-dev-kit** skills loaded: it knows how to build metric views, Genie spaces, dashboards, apps, and jobs on Databricks. Tell it *what*; the skills know *how*. **Always read what it generates before running it.**

---

## Pre-Work (complete before the workshop)

No local software to install. All steps happen inside the Databricks workspace.

### Steps

1. **Clone this workshop repo as a Workspace Git folder.** In the workspace, go to **Workspace > Create > Git folder**, paste the repo URL, and click Create. This makes the notebooks available directly inside your workspace.

2. **Open `notebooks/00-setup`, set your initials widget, and click Run All.** This single notebook does everything you would otherwise do manually: it installs the ai-dev-kit skills into Genie Code AND creates and deploys your `<initials>-command-center` app with all permissions and OBO scopes already wired. You do not need to run any separate installer or create the app yourself. Once setup finishes, the hands-on lab lives in the `notebooks/01-workshop-prompts` notebook (you can follow it there or in this guide; the prompts are identical).

3. **Start a new chat in Genie Code.** After the setup notebook finishes, open a **new chat thread** in Genie Code (hard-refresh the browser if skills do not appear after opening a new thread).

4. **Run the smoke-test prompt** to confirm skills loaded and the workshop data is in place:

```text
List the tables in ioc_sandbox.vibe_workshop. I should see 8 (3 dims_, 5 facts_).
```

### Pre-work checklist

- [ ] Repo cloned as a Workspace Git folder
- [ ] `notebooks/00-setup` notebook ran successfully (skills installed + app deployed)
- [ ] New chat open in Genie Code
- [ ] Smoke test passed: agent lists 8 tables in `ioc_sandbox.vibe_workshop` (3 `dims_*`, 5 `facts_*`)

If anything fails, ping the facilitator in the workshop channel **before** the session starts.

---

## All Prompts in One Place

### Day-of prompts (run these in the workshop, in order)

#### Session setup (paste this FIRST)

Substitute `<INITIALS>` once (lowercase, e.g. `jjw`), paste, and hit enter. The agent will use these values for every module prompt below.

```text
I'm running the Genie Code Command Center workshop. Remember these values
for the whole conversation:
  My initials:  <INITIALS>
  Catalog:      ioc_sandbox.vibe_workshop
  Warehouse:    serverless
  Model endpt:  databricks-claude-sonnet-4-6   (for ai_query())
Resources (use exactly these names):
  - metric view:  <initials>_command_center_metrics
  - Genie space:  "<initials> Command Center"
  - dashboard:    "<initials> Operator Insights"
  - app:          <initials>-command-center   (already deployed by setup notebook)
  - job:          <initials>-command-center-refresh
Capture as we go: my Genie space ID, dashboard ID, app URL.
Confirm, then wait for my first module prompt.
```

Now paste each module prompt in order; the agent already knows your initials and resource names.

---

### Module 1: Metric View (0:10-0:25)

> **Note:** Genie Code runs the CREATE statement for you, but you need CREATE on the schema. If it is denied, ask the facilitator to grant your group CREATE on `ioc_sandbox.vibe_workshop`, or create the view in your own sandbox schema.

```text
Create a metric view named <initials>_command_center_metrics over my workshop
tables at store x date grain. Measures: revenue, labor cost, labor % of sales,
days of cover, sell-through %, net sentiment. Dimensions: store, region, date,
day-of-week. Put all the joins and rollups inside the metric view's own source
query; do not create any intermediary or base view, only the single metric view.
Validate it returns rows.
```

---

### Module 2: Genie Space (0:25-0:45)

```text
Module 2. Create a Genie space on my metric view <initials>_command_center_metrics.
Add 6 sample questions (2 per pillar: Labor / Inventory / Guest Feedback)
grounded in the metric view's measures. Test one per pillar, then remember
the space ID.
```

---

### Module 3: AI/BI Dashboard (0:45-1:05)

```text
Module 3. Create an AI/BI dashboard on my metric view with 4 widgets:
  (1) labor % of sales last 30 days as a line chart
  (2) revenue by region as a bar chart
  (3) days of cover / stock health as a stacked bar
  (4) net sentiment timeline as a line chart
Publish it and remember the dashboard ID.
```

---

### Module 4: App polish (1:15-1:45)

Your `<initials>-command-center` app was already created, branded, and deployed by the setup notebook (it copied `command-center-dev`, wired permissions, and deployed). This module confirms it is running and lets you polish the branding if you like.

```text
My app <initials>-command-center is already deployed (the setup notebook
created it from command-center-dev). Open its URL and confirm it loads. If
you want, tweak the LCE branding (logo
branding/lce/logo.svg, primary #FF671B, dark navbar, title "Command
Center | LCE") and redeploy.
```

---

### Module 5: Embed Genie + Dashboard (1:45-2:25)

> **Important:** the genie, sql, and dashboards.genie OBO scopes are already set on your app by the 00-setup notebook; do not ask Genie Code to add scopes (it cannot, and they are not needed).

```text
Module 5. Update my app to embed MY Genie space (the ID from Module 2) and MY
dashboard (the ID from Module 3), then redeploy:
  - Call Genie on behalf of the signed-in user using the X-Forwarded-Access-Token
    header (OBO), not the app service principal, so it uses my access to my space.
  - Embed my published dashboard by its ID, rendered as the signed-in user.
  - Support multi-turn: start-conversation on the first ask, then post to the
    conversation messages endpoint; poll until COMPLETED; return the answer and the
    SQL Genie generated.
```

> **If running low on time:** drop the per-tab dashboard tiles and keep only the Ask Genie panel. Genie is the higher-impact piece.

---

### Module 6: Job (BONUS) (2:25-2:50)

```text
Module 6. Add a daily job <initials>-command-center-refresh at 6am ET that
refreshes the metric view's source rollups and redeploys my app.
```

---

### Demo round + wrap (2:50-3:00)

1 min per attendee: share your App URL, show one Genie question that worked, show one metric from your dashboard. Ongoing questions in the workshop channel; optional office hours 1 week after.

---

## Workshop Environment (reference)

Pre-filled values used throughout the workshop. The **Session setup** prompt at the top already pastes these into the agent; this table is here in case you need to look one up manually.

| Item | Your value |
|---|---|
| Your initials (lowercase, e.g. `jjw`) | `<INITIALS>` (you fill this in) |
| Workspace URL | provided by your facilitator |
| Shared data catalog.schema | `ioc_sandbox.vibe_workshop` |
| SQL warehouse name | `serverless` |
| Model endpoint (for `ai_query()`) | `databricks-claude-sonnet-4-6` |
| Metric view name | `<initials>_command_center_metrics` |
| LCE branding folder (in repo) | `branding/lce/` |
| App template | `command-center-dev` |
| **Captured during workshop:** | |
| Your Genie space ID | `<GENIE_SPACE_ID>` |
| Your dashboard ID | `<DASHBOARD_ID>` |
| Your App URL | `<APP_URL>` |

---

## Vibe Coding Tips

- **Read every diff.** Agents move fast and are sometimes confidently wrong. Catch SQL that drops tables, code that hardcodes credentials, prompts that bypass auth.
- **Be specific about constraints when it matters** (for example: "use the Databricks SQL connector, not pyodbc"); otherwise let the skills decide.
- **Iterate in small chunks.** One feature at a time is easier to review and debug.
- **When stuck, ask the agent to explain its own code.** Often surfaces the bug.
- **Skills and new chats.** If the agent seems unaware of metric views, Genie, or apps, open a **new chat thread** after installing the skills.

---

## Reference Links

- [Workshop repo](https://github.com/jonathan-whiteley/genie-code-vibe-workshop)
- [ai-dev-kit skills](https://github.com/databricks-solutions/ai-dev-kit#genie-code-skills)
- [Genie Code skills docs](https://docs.databricks.com/aws/en/genie-code/skills)
- [Genie setup](https://docs.databricks.com/aws/en/genie/set-up)
- [Databricks Apps overview](https://docs.databricks.com/aws/en/dev-tools/databricks-apps)
- [AI/BI Dashboards](https://docs.databricks.com/aws/en/dashboards)
- [Metric Views (Unity Catalog)](https://docs.databricks.com/aws/en/sql/user/sql-ai-functions/metric-views)
- [Foundation Model APIs](https://docs.databricks.com/aws/en/machine-learning/foundation-models)
- [Databricks Asset Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles)

---

## Companion Documents

| | |
|---|---|
| **Facilitator Plan** (deploy checklist, agenda, troubleshooting) | [`docs/facilitator-plan.md`](facilitator-plan.md) |
| **Operational runbook** (deploy commands, gotchas, fallbacks) | [`dab/README.md`](../dab/README.md) |
| **Repo** | https://github.com/jonathan-whiteley/genie-code-vibe-workshop |
