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
| 0:45-1:05 | Module 3: AI/BI Dashboard | Insight charts across every measure and dimension (no KPI tiles) |
| 1:05-1:15 | Break | |
| 1:15-1:45 | Module 4: App polish | `<initials>-command-center` already deployed; verify it loads + optional branding tweaks |
| 1:45-2:10 | Module 5: Embed | Genie + dashboard live in the app |
| 2:10-2:35 | Module 6: Live AI | (A) Company News feed in the app via the `web_search_mcp` MCP server; (B) `ai_query()` briefing function for the Genie space |
| 2:35-2:50 | Module 7 (BONUS): Job | Multi-task refresh job: validate, refresh dashboard, redeploy app |
| 2:50-3:00 | Demo round + wrap | Share App URL |

Times are relative; your facilitator sets the wall clock.

---

## How to use this guide

Every prompt below is in a **code block**: hit the copy button, paste into **Genie Code** in the workspace. **You only fill in `<INITIALS>` once**, in the **Session setup** prompt at the start of the day-of section. Every prompt after that says "my metric view", "my Genie space", etc.; the agent already knows the values from the setup prompt.

Prompts are short on purpose. The agent has **ai-dev-kit** skills loaded: it knows how to build metric views, Genie spaces, dashboards, apps, and jobs on Databricks. Tell it *what*; the skills know *how*. **Always read what it generates before running it.**

This workshop also ships a **`command-center-patterns`** skill: field-tested patterns for the trickier steps (metric view, dashboard embed, Genie swap, MCP feed, Genie functions). Genie Code loads it automatically, and the hardest prompts also name the exact pattern file.

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
Create my Command Center metric view at store x date grain.

- Name it <my initials>_command_center_metrics, over facts_sales_daypart
  and facts_labor_daypart plus dims_stores. One metric view, no
  intermediary views.
- Pre-aggregate each fact table to one row per store per date in its own
  subquery before joining (the daypart and role grain double-counts otherwise).
- Measures: revenue, forecast revenue, traffic, labor cost,
  forecast labor cost, labor % of sales.
- Dimensions: store, region, date, day-of-week.
- Then run a verification SELECT.
```

---

### Module 2: Genie Space (0:25-0:45)

```text
Create a Genie space on two kinds of source so it can answer both governed-KPI and finer-grained questions:
- my metric view (<my initials>_command_center_metrics), and
- the raw tables in ioc_sandbox.vibe_workshop (dims_stores, dims_items, dims_employees, facts_sales_daypart, facts_labor_daypart, facts_sales_inventory_daily, facts_purchase_orders, facts_customer_feedback).

Add a space instruction: use the metric view for the governed KPIs (revenue, forecast, traffic, labor cost, labor % of sales at store x date grain); use the raw tables for detail the metric view does not cover (SKU / inventory, employees, purchase orders, customer feedback / sentiment, and daypart or role breakdowns).

Add 6 sample questions that span both: a couple of KPI questions and a couple of detail questions.
```

**Follow-up: add a benchmark set.** Benchmarks measure how accurately Genie answers known questions. Generate 10 and add them to your space, then run them in the Genie UI to score it.

```text
Come up with 10 benchmark questions for my Genie space based on the metric view's measures and dimensions, and add them to the space.
```

---

### Module 3: AI/BI Dashboard (0:45-1:05)

```text
Create a visual-first AI/BI dashboard on my metric view. No KPI counter tiles,
just a handful of charts that surface insight.

Charts:
- Revenue share by region: pie / donut
- Revenue trend, last 30 days: line
- Revenue vs forecast revenue by store: bar
- Labor % of sales by store: bar, sorted high to low
- Revenue by day-of-week: bar

Theme it for visual interest, like a polished editorial dashboard. Set the dashboard theme with both light and dark variants (not just per-widget colors):
- Canvas background: light #FDF8F3, dark #1A1210
- Widget cards: light #FFFFFF, dark #2A1F1A; borders light #E8DDD4, dark #3D2E24
- Font color: light #3B2316, dark #F5EDE6; serif family (Georgia); left-align headers
- Selection / accent: light #FF671B (LCE orange), dark #FF8A4C
- Visualization palette (same in both): #FF671B (LCE orange, lead), #7B9E6B, #8B4557, #D4A853, #5B8FA8, #D4785C, #6B5B8A, #3D7A6E
- A title with the Little Caesars feel

Publish it and tell me the dashboard ID.
```

---

### Module 4: App polish (1:15-1:45)

Your `<initials>-command-center` app was already created, branded, and deployed by the setup notebook (it copied `command-center-dev`, wired permissions, and deployed). This module confirms it is running and lets you polish the branding if you like.

```text
My app <initials>-command-center is already deployed (the setup notebook created it from command-center-dev).

Open its URL and confirm it loads.

Now give it Little Caesars branding and make it pop:
- copy the LCE logo from my workshop Git folder (docs/branding/lce/logo.svg) into the app's static assets and use it in the header
- copy the favicon from my workshop Git folder (docs/branding/lce/favicon.svg) into the app's static assets and wire it up with a <link rel="icon"> in the page <head> so it shows in the browser tab
- use LCE orange (#FF671B) as the accent throughout: buttons, links, active tabs, and KPI highlights
- add a bold hero header on the Today tab with the logo and the store name
- give the tiles and cards rounded corners, soft shadows, and a subtle hover lift
- add a thin LCE-orange top accent bar and a dark navbar
- set the browser tab title (the HTML <title> tag) to exactly "Command Center" with no store number

Then redeploy.
```

**Follow-up: dark mode for the Today tab.** Give the home (Today) tab a sleek dark theme while keeping the LCE accents.

```text
Restyle the Today tab in dark mode: a deep dark background with light text, and keep the LCE orange (#FF671B) accents popping against it. Leave the other tabs as they are. Then redeploy.

Follow docs/patterns/app-editing-pattern.md for the contrast and editing gotchas.
```

---

### Module 5: Embed Genie + Dashboard (1:45-2:10)

Your app already has an Ask Genie panel and a home page with 3 tiles. You are swapping in your own Genie space and adding your dashboard below the tiles.

> **Important:** the genie, sql, and dashboards.genie OBO scopes are already set on your app by the 00-setup notebook, and the Ask Genie panel already uses on-behalf-of-user auth. Do not rebuild the panel or change scopes.

```text
My app already has an Ask Genie panel and a home page with 3 tiles.
Make these two changes, then redeploy:

1. Swap the Ask Genie panel to use MY Genie space (the space ID from
   Module 2), following docs/patterns/genie-swap-pattern.md. Point it at
   my space ID; do not rebuild the panel or its auth.

2. Embed my published AI/BI dashboard as an iframe below the 3 tiles,
   following docs/patterns/dashboard-embed-pattern.md.
```

> **If running low on time:** the Genie space swap is the higher-impact change, so do that first.

---

### Module 6: Live AI in your Command Center (2:10-2:35)

Two AI features: **A**, a Company News feed in the app fetched live through the `web_search_mcp` MCP server; and **B**, a store briefing your Genie space can generate with `ai_query()`.

#### A: a live Company News feed (MCP)

Add a Company News feature to your app that pulls live headlines through the `web_search_mcp` MCP server and summarizes them with `ai_query()`. The prompt points Genie Code at a proven pattern (with the gotchas already solved) in `docs/patterns/mcp-company-news-pattern.md`.

> **If it 403s:** the app must call the MCP server as its **service principal**, which the admin grants access to. The forwarded user token does not have MCP scope.

```text
Add a "Company News" feature to my app, then redeploy.

Follow the pattern in docs/patterns/mcp-company-news-pattern.md:
- fetch live news from the web_search_mcp MCP server,
- summarize the results with ai_query,
- show 3 bullets in a bell-icon dropdown in the header.
```

#### B: the store briefing (Genie function)

Give Genie a generative skill: a Unity Catalog function that calls Claude through `ai_query()` over your metric view and returns a plain-language briefing of the latest day plus a recommended Next Best Action. Once it's registered with your Genie space, Genie can call it on request, including from the **Ask Genie** panel in your app: no app code change, because the panel already runs as you.

> **If the briefing returns a permission error:** the function runs `ai_query()` as **you** (Genie executes as the asking user), so your workshop group needs `CAN_QUERY` on the `databricks-claude-sonnet-4-6` endpoint. Genie Code can't grant that: flag it to your facilitator.

```text
Create an AI store-briefing function named <my initials>_store_briefing and register it with my Genie space, following docs/patterns/genie-space-pattern.md (it has the function shape and the registration steps).

The function reads my store's latest-day numbers from the metric view (revenue, forecast revenue, labor % of sales, traffic, prior-day revenue) and passes them to ai_query() on databricks-claude-sonnet-4-6 for a 3-bullet manager briefing plus a "Next Best Action", under 100 words.

Do not call it from here; I'll try it in the Ask Genie panel.
```

**Follow-up: make it one click.** Surface the briefing as a starter question so anyone can trigger it in the space and in your app's Ask Genie panel.

```text
Add "Give me today's store briefing" as a starter question in two
places, then redeploy the app:
- as a sample question on my Genie space, and
- as a suggested question in my app's Ask Genie panel UI.
```

---

### Module 7: Job (BONUS) (2:35-2:50)

```text
Create my weekly job <my initials>-command-center-refresh, scheduled for 6am ET every Monday, with these tasks run in order (each depends on the one before):

1. Validate the metric view: a SQL task that selects a few MEASURE() rows from my metric view and fails if it returns no rows (a freshness / quality gate).
2. Refresh the dashboard: a dashboard task that refreshes my AI/BI dashboard so its datasets recompute.
3. Redeploy the app: a task that redeploys my <my initials>-command-center app so it serves the latest.

Add an email notification to me on failure. The job runs as me, so no extra permissions are needed.
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
| LCE branding folder (in repo) | `docs/branding/lce/` |
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
| **Operational pattern** (deploy commands, gotchas, fallbacks) | [`dab/README.md`](../dab/README.md) |
| **Repo** | https://github.com/jonathan-whiteley/genie-code-vibe-workshop |
