# Genie Code Workshop: Operator Command Center: Lab Companion Guide

**You'll build:** "Command Center", a Databricks App that surfaces AI insights and analytics across **Sales and Labor** for store operations. Your app will embed a Genie space and an AI/BI dashboard, both built on a single governed **Metric View** you define first. Everything runs inside the Databricks workspace using **Genie Code** (no local install required).

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
| 1:15-1:45 | Module 4: App polish | `<initials>-command-center` already deployed; verify it loads + optional branding tweaks |
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
I am doing the Genie Code Command Center lab. Use these settings for the whole chat:

| Setting | Value |
|---|---|
| My initials | <INITIALS> |
| Catalog | ioc_sandbox.vibe_workshop |
| Warehouse | serverless |
| Model (for ai_query only) | databricks-claude-sonnet-4-6 |

Create these with exactly these names:

| Resource | Name |
|---|---|
| Metric view | <initials>_command_center_metrics |
| Genie space | <initials> Command Center |
| Dashboard | <initials> Operator Insights |
| App | <initials>-command-center (already created and deployed by Lab 00) |
| Job | <initials>-command-center-refresh |

As we go, remember my Genie space ID, dashboard ID, and app URL. Confirm these back to me, then wait for my first prompt.
```

Now paste each module prompt in order; the agent already knows your initials and resource names.

---

### Module 1: Metric View (0:10-0:25)

> **Note:** Genie Code runs the CREATE statement for you, but you need CREATE on the schema. If it is denied, ask the facilitator to grant your group CREATE on `ioc_sandbox.vibe_workshop`, or create the view in your own sandbox schema.

```text
Create my Command Center metric view at store x date grain, from just two tables: facts_sales_daypart and facts_labor_daypart.

Roll each table up to one row per store per date in its own subquery first (sum revenue, forecast revenue, and traffic from sales; sum labor cost and forecast labor cost from labor), then join the two rollups on date and store, and join dims_stores for region. Do not create any separate or intermediary view, only the single metric view.

Measures:
- revenue
- forecast revenue
- traffic
- labor cost
- forecast labor cost
- labor % of sales (labor cost / revenue)

Dimensions: store, region, date, day-of-week.

Run a SELECT to confirm it returns rows and that labor % of sales is realistic (around 20 to 35%).
```

---

### Module 2: Genie Space (0:25-0:45)

```text
Create a Genie space on my metric view.

Add 6 sample questions grounded in the metric view measures (revenue, forecast, labor cost, labor % of sales).

Ask a few questions to test it, then tell me the space ID.
```

**Follow-up: add a benchmark set.** Benchmarks measure how accurately Genie answers known questions. Add 10, then run them to score your space.

```text
Add these 10 benchmark questions to my Genie space, then run the benchmark and tell me how many Genie answered correctly:

- Which 5 stores had the highest labor % of sales last week?
- How has labor % of sales trended over the last 30 days across all stores?
- Which region has the lowest labor % of sales this month?
- Which stores are below their revenue forecast this week?
- Show the revenue trend over the last 30 days.
- How did labor cost track against its forecast this week?
- Which 5 stores have the highest revenue this month?
- Rank regions by total revenue this month.
- What is the busiest day of week by revenue?
- Which stores improved labor % of sales the most over the last 30 days?
```

---

### Module 3: AI/BI Dashboard (0:45-1:05)

```text
Create a rich AI/BI dashboard on my metric view.

Start with a row of KPI counters (latest day):
- total revenue
- labor % of sales
- revenue vs forecast
- traffic

Then add these charts:
- revenue trend, last 30 days (line)
- labor % of sales, last 30 days (line)
- revenue by region (bar)
- revenue vs forecast by store (bar)
- labor cost vs forecast by store (bar)
- revenue by day-of-week (bar)

Give it Little Caesars branding and make it pop:
- use the LCE orange (#FF671B) as the primary accent across the charts
- set a bold, cool dashboard background color
- use vibrant, high-contrast colors so the charts really stand out
- add a title with the Little Caesars feel

Publish it and remember the dashboard ID.
```

---

### Module 4: App polish (1:15-1:45)

Your `<initials>-command-center` app was already created, branded, and deployed by the setup notebook (it copied `command-center-dev`, wired permissions, and deployed). This module confirms it is running and lets you polish the branding if you like.

```text
My app <initials>-command-center is already deployed (the setup notebook created it from command-center-dev).

Open its URL and confirm it loads.

Now give it Little Caesars branding and make it pop:
- copy the LCE logo from my workshop Git folder (branding/lce/logo.svg) into the app's static assets and use it in the header
- use LCE orange (#FF671B) as the accent throughout: buttons, links, active tabs, and KPI highlights
- add a bold hero header on the Today tab with the logo and the store name
- give the tiles and cards rounded corners, soft shadows, and a subtle hover lift
- add a thin LCE-orange top accent bar and a dark navbar
- title the app "Command Center | LCE"

Then redeploy.
```

**Follow-up: dark mode for the Today tab.** Give the home (Today) tab a sleek dark theme while keeping the LCE accents.

```text
Restyle the Today tab in dark mode: a deep dark background with light text, and keep the LCE orange (#FF671B) accents popping against it. Leave the other tabs as they are. Then redeploy.
```

---

### Module 5: Embed Genie + Dashboard (1:45-2:25)

Your app already has an Ask Genie panel and a home page with 3 tiles. You are swapping in your own Genie space and adding your dashboard below the tiles.

> **Important:** the genie, sql, and dashboards.genie OBO scopes are already set on your app by the 00-setup notebook, and the Ask Genie panel already uses on-behalf-of-user auth. Do not rebuild the panel or change scopes.

```text
My app already has an Ask Genie panel wired to a Genie space, and a home page with 3 tiles. Make these two changes, then redeploy:

1. Swap the Ask Genie panel to use MY Genie space (the space ID from Module 2). Do not rebuild the panel or its auth; just point it at my space ID.

2. Embed my published AI/BI dashboard as an iframe on the home page, directly below the 3 tiles. To avoid a "refused to connect" iframe error:
   - use the dashboard's published EMBED url (the /embed/ link from the dashboard's Share then Embed), NOT the normal dashboard link; the normal workspace link sets X-Frame-Options and refuses to be framed.
   - make sure the dashboard is Published with embedding enabled, and add my app's domain (the .databricksapps.com host of my app URL) to the dashboard's list of approved domains for embedding.
```

> **If running low on time:** the Genie space swap is the higher-impact change, so do that first.

---

### Module 6: Job (BONUS) (2:25-2:50)

```text
Module 6. Add a daily job <initials>-command-center-refresh at 6am ET with these steps:
- refresh the metric view's source rollups
- redeploy my app
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
