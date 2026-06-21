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
| 2:10-2:35 | Module 6: AI briefing | `ai_query()` briefing function your Genie space can call |
| 2:35-2:50 | Module 7 (BONUS): Job | Scheduled refresh job |
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
Create my Command Center metric view at store x date grain, following
the pattern in docs/patterns/metric-view-pattern.md.

- Name it <my initials>_command_center_metrics, over facts_sales_daypart
  and facts_labor_daypart plus dims_stores. One metric view, no
  intermediary views.
- Measures: revenue, forecast revenue, traffic, labor cost,
  forecast labor cost, labor % of sales.
- Dimensions: store, region, date, day-of-week.
- Then run the pattern's verification SELECT to confirm it returns rows
  and labor % of sales is realistic (20-35%, not ~200%).
```

---

### Module 2: Genie Space (0:25-0:45)

```text
Create a Genie space on my metric view.

Add 6 sample questions grounded in the metric view measures (revenue, forecast, labor cost, labor % of sales).

Ask a few questions to test it, then tell me the space ID.

If adding the sample questions through the genie tool fails, use the REST shape in docs/patterns/genie-space-pattern.md.
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

If writing the benchmark to the space is blocked by the safety layer, run the questions via the Conversation API instead (see docs/patterns/genie-space-pattern.md).
```

---

### Module 3: AI/BI Dashboard (0:45-1:05)

```text
Create a visual-first AI/BI dashboard on my metric view. No KPI counter tiles:
lead with charts that surface insight, and use every measure and dimension
across the page.

Charts:
- Revenue share by region: pie / donut
- Revenue trend, last 30 days: line
- Revenue vs forecast revenue by store: grouped bar
- Labor % of sales by store: bar, sorted high to low, flag the healthy 20-35% band
- Labor cost vs forecast labor cost, last 30 days: line, two series
- Revenue by day-of-week: bar
- Traffic vs revenue by store: scatter, one point per store
- Traffic by region: bar

Give it Little Caesars branding and make it pop:
- use LCE orange (#FF671B) as the primary accent
- a bold, cool background and vibrant, high-contrast chart colors
- a title with the Little Caesars feel

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

### Module 5: Embed Genie + Dashboard (1:45-2:10)

Your app already has an Ask Genie panel and a home page with 3 tiles. You are swapping in your own Genie space and adding your dashboard below the tiles.

> **Important:** the genie, sql, and dashboards.genie OBO scopes are already set on your app by the 00-setup notebook, and the Ask Genie panel already uses on-behalf-of-user auth. Do not rebuild the panel or change scopes.

```text
My app already has an Ask Genie panel and a home page with 3 tiles.
Make these two changes, then redeploy:

1. Swap the Ask Genie panel to use MY Genie space (the space ID from
   Module 2), following docs/patterns/genie-swap-pattern.md.
   Just point it at my space ID; do not rebuild the panel or its auth.

2. Embed my published AI/BI dashboard as an iframe below the 3 tiles,
   following docs/patterns/dashboard-embed-pattern.md (use the
   /embed/ URL, and add an "Open in Databricks" fallback link above it).
```

> **If running low on time:** the Genie space swap is the higher-impact change, so do that first.

---

### Module 6: Live AI in your Command Center (2:10-2:35)

Two AI features: **A**, a store briefing your Genie space can generate with `ai_query()`; and **B**, a Company News feed in the app fetched live through the `web_search_mcp` MCP server.

#### A: the store briefing (Genie function)

Give Genie a generative skill: a Unity Catalog function that calls Claude through `ai_query()` over your metric view and returns a plain-language briefing of the latest day plus a recommended Next Best Action. Once it's registered with your Genie space, Genie can call it on request, including from the **Ask Genie** panel in your app: no app code change, because the panel already runs as you.

> **If the briefing returns a permission error:** the function runs `ai_query()` as **you** (Genie executes as the asking user), so your workshop group needs `CAN_QUERY` on the `databricks-claude-sonnet-4-6` endpoint. Genie Code can't grant that: flag it to your facilitator.

```text
Create an AI briefing function for my Genie space, then test it.

- Create a Unity Catalog SQL function named <my initials>_store_briefing,
  in the same catalog/schema as my metric view (no args, RETURNS STRING).
- It selects my store's latest-day metric-view numbers: revenue,
  forecast revenue, labor % of sales, traffic, and prior-day revenue.
- It passes those to ai_query() on databricks-claude-sonnet-4-6 and
  returns, under 100 words:
  - a 3-bullet briefing (revenue vs forecast; is labor % of sales in the
    healthy 20-35% band; one thing to watch today), and
  - a "Next Best Action" recommendation.
- Give it a clear COMMENT so Genie knows when to call it.
- Add it to my Genie space as a callable function.
- Test with: give me today's store briefing.
```

**Follow-up: make it one click.** Surface the briefing as a starter question so anyone can trigger it in the space and in your app's Ask Genie panel.

```text
Add "Give me today's store briefing" as a starter question in two
places, then redeploy the app:
- as a sample question on my Genie space, and
- as a suggested question in my app's Ask Genie panel UI.
```

#### B: a live Company News feed (MCP)

Add a Company News feature to your app that pulls live headlines through the `web_search_mcp` MCP server and summarizes them with `ai_query()`. The prompt points Genie Code at a proven pattern (with the gotchas already solved) in `docs/patterns/mcp-company-news-pattern.md`.

> **If it 403s:** the app must call the MCP server as its **service principal**, which the admin grants access to. The forwarded user token does not have MCP scope.

```text
Add a "Company News" feature to my app, then redeploy.

Follow the pattern in docs/patterns/mcp-company-news-pattern.md:
- fetch live news from the web_search_mcp MCP server,
- summarize the results with ai_query,
- show 3 bullets in a bell-icon dropdown in the header.
```

---

### Module 7: Job (BONUS) (2:35-2:50)

```text
Module 7. Add a daily job <initials>-command-center-refresh at 6am ET with these steps:
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
| **Operational pattern** (deploy commands, gotchas, fallbacks) | [`dab/README.md`](../dab/README.md) |
| **Repo** | https://github.com/jonathan-whiteley/genie-code-vibe-workshop |
