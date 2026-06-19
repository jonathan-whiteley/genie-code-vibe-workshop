# Genie Code Vibe Workshop: Operator Command Center (Design)

**Status:** approved-for-planning
**Date:** 2026-06-18
**Author:** Jonathan Whiteley
**Builds on:** [`jonathan-whiteley/ucode-vibe-workshop`](https://github.com/jonathan-whiteley/ucode-vibe-workshop)

---

## 1. Summary

A 3-hour, hands-on workshop where each attendee builds a working Databricks
App end-to-end **entirely inside the Databricks Workspace using Genie Code**:
no local install of `uv`, Node, the Databricks CLI, `ucode`, Claude Code, or
Codex. The reference build is the same **Command Center** store-operations
console (Labor / Inventory / Guest Feedback) over the LCE-flavored synthetic
dataset, but the build is re-architected around a **Metric View as the spine**:
define governed KPIs once, then hang every downstream surface off them.

This is a deliberate departure from the original `ucode-vibe-workshop` on two
axes:

1. **Tooling:** Genie Code (in-workspace agent) replaces all local CLI tooling.
2. **Build order:** Metric-View-first instead of App-shell-first.

The dataset, branding, and end-state (deployed App embedding a Genie space + an
AI/BI dashboard) are carried over so the asset is proven.

---

## 2. Goals & non-goals

**Goals**
- Each attendee ends with a deployed `<initials>-command-center` Databricks App
  that embeds their own Genie space and AI/BI dashboard, all built on a single
  governed Metric View.
- Zero local installation. The only pre-work is running one notebook to load
  ai-dev-kit skills into Genie Code.
- Six succinct prompts, one per build step, demonstrating "tell it *what*; the
  skills know *how*."

**Non-goals**
- Not changing the business domain (store-ops is reused, per decision).
- Not teaching local agent setup (ucode / Claude Code / Codex), explicitly
  removed.
- Not building net-new synthetic data; the tables are "already landed" before
  the workshop.

---

## 3. Key decisions (locked)

| # | Decision | Choice |
|---|---|---|
| 1 | Dataset / domain | Reuse store-ops 8-table schema (`ioc_sandbox.vibe_workshop`) |
| 2 | Deliverable scope | Plan + both guides + new repo scaffold |
| 3 | ai-dev-kit → Genie Code install path | **Attendees run the notebook installer** (`install_genie_code_skills.py`) |
| 4 | Metric View architecture | **A: single unified metric view at `store × date` grain** |
| 5 | Repo location | `~/Desktop/Projects/genie-code-vibe-workshop` |
| 6 | Branding | Keep store-ops "Command Center" + LCE branding |

---

## 4. How ai-dev-kit skills reach Genie Code (pre-work)

Genie Code loads skills from a `.assistant/skills/` directory in the Workspace:
- **User skills:** `/Users/<username>/.assistant/skills/` (personal)
- **Workspace skills:** `Workspace/.assistant/skills/` (all users; admin-managed)

**Chosen path:** each attendee runs the ai-dev-kit notebook installer
([`install_genie_code_skills.py`](https://github.com/databricks-solutions/ai-dev-kit/blob/main/databricks-skills/install_genie_code_skills.py))
in their own workspace, which copies the ai-dev-kit skill folders into their
user `.assistant/skills/`. Genie Code auto-loads relevant skills in **Agent
mode**; they can also be invoked with `@skill-name`.

**Caveats to bake into the guides:**
- Skills only work in **Agent mode**; after install, attendees must open a
  **new chat thread** (sometimes a hard browser refresh) for skills to register.
- `databricks aitools` does NOT support Genie Code; that CLI path is for local
  IDEs only, so it is not used here.
- Skill parity is not 1:1 with local ai-dev-kit; some skills reference
  capabilities Genie Code lacks. The 6 build steps were chosen to use skills
  that are known to work in Genie Code (metric views, genie, AI/BI dashboards,
  apps, jobs).
- Verify skills landed after install (smoke test prompt in the guide).

**Facilitator note (alternative, documented but not the default):** for a
workspace-wide, always-current install, a facilitator can deploy the
`mcp-ai-dev-kit` Databricks App (from `databricks-field-eng/india-gcc`), which
pushes skills to `Workspace/.assistant/skills/` for all users and serves the
tools at `/mcp`. This removes the per-attendee notebook step. Captured in the
facilitator plan as an optional upgrade.

References:
- Genie Code skills docs: https://docs.databricks.com/aws/en/genie-code/skills
- ai-dev-kit repo (Genie section): https://github.com/databricks-solutions/ai-dev-kit#genie-code-skills
- New source-of-truth repo: https://github.com/databricks/databricks-agent-skills

---

## 5. The Metric View (the spine)

**Object:** `ioc_sandbox.vibe_workshop.command_center_metrics`
(per-attendee: `<initials>_command_center_metrics`).

**Grain:** `store × date`.

**Source:** a SQL query joining `facts_sales_daypart` and `facts_labor_daypart`
rolled up to daily per store, left-joined to daily rollups of
`facts_sales_inventory_daily` (stock health) and `facts_customer_feedback`
(sentiment), with `dims_stores` for region/attributes.

**Dimensions:** store, region, date, day-of-week (+ store attributes).

**Measures (the governed KPIs reused everywhere):**
- `revenue`: sum of actual revenue
- `labor_cost`: sum of actual labor cost
- `labor_pct_of_sales`: labor cost ÷ revenue
- `days_of_cover`: on-hand ÷ avg daily units sold
- `sell_through_pct`: units sold ÷ (units sold + on-hand)
- `net_sentiment`: positive - negative feedback, normalized

**Why approach A:** a single metric view makes the "define metrics once,
governed; everything downstream reuses them" lesson land. Daypart/role/sku
detail collapses to daily in the view, but those raw tables remain in the schema
for Genie to drill into when a question needs finer grain. The metric view is
authored in YAML (`metric-views/command_center_metrics.yaml`) and created via
the ai-dev-kit metric-views skill.

---

## 6. The six build steps (attendee day-of prompts)

Each prompt is succinct (2-4 lines). The agent already knows the attendee's
initials and resource names from a one-time **Session setup** prompt (carried
over from the original guide's pattern).

1. **Metric View**
   > Create a metric view named `<initials>_command_center_metrics` over my
   > workshop tables at store×date grain. Measures: revenue, labor cost, labor %
   > of sales, days of cover, sell-through %, net sentiment. Dimensions: store,
   > region, date, day-of-week. Validate it returns rows.

2. **Genie Space (on the metric view)**
   > Create a Genie space on my metric view `<initials>_command_center_metrics`.
   > Add 6 sample questions (2 per pillar: Labor / Inventory / Guest Feedback)
   > grounded in the metric view's measures. Test one per pillar, then remember
   > the space ID.

3. **AI/BI Dashboard (on the metric view)**
   > Create an AI/BI dashboard on my metric view with 4 widgets: labor % of
   > sales (30-day line), revenue by region (bar), stock health / days of cover
   > (stacked bar), net sentiment timeline (line). Publish it and remember the
   > dashboard ID.

4. **Databricks App**
   > Create an App named `<initials>-command-center` using the existing
   > **command-center-dev** app as a template. Give it Labor / Inventory / Guest
   > Feedback tabs. Make it pop with LCE branding (logo `branding/lce/logo.svg`,
   > primary `#FF671B`, dark navbar, title "Command Center | LCE"). Deploy and
   > print the URL.

5. **Embed Genie + Dashboard into the App**
   > Embed my Genie space and my AI/BI dashboard into my app: dashboard tiles
   > per pillar tab, plus an "Ask Genie" panel. Make the embed work cleanly:
   >  - Use **OBO (on-behalf-of-user) auth** for Genie, NOT the app service
   >    principal (Genie spaces are user-permissioned; the user token is in the
   >    `X-Forwarded-Access-Token` header).
   >  - Declare `user_api_scopes: [genie, sql, dashboards.genie]` on the app
   >    resource so the forwarded token has the genie scope; redeploy and
   >    re-consent on first open.
   >  - For the dashboard, use the published dashboard's embed/iframe URL scoped
   >    to my dashboard ID; grant the app SP / user `CAN_VIEW` on the dashboard.
   >  - Support multi-turn Genie: start-conversation on first ask, then post to
   >    the conversation's messages endpoint; poll until COMPLETED and return the
   >    answer + generated SQL.

6. **BONUS: Job**
   > Add a daily job `<initials>-command-center-refresh` at 6am ET that refreshes
   > the metric view's source rollups and redeploys my app.

---

## 7. Repo structure (deliverable)

```
genie-code-vibe-workshop/
├── README.md                          # Genie-Code framing; no-local-install quick start
├── docs/
│   ├── facilitator-plan.md            # rewritten: skills-via-notebook, metric-view-first agenda
│   ├── lab-companion-guide.md         # rewritten: 6 succinct Genie Code prompts
│   └── superpowers/specs/             # this design doc
├── data/                              # adapted store-ops generator + ddl.sql (tables pre-landed)
│   ├── ddl.sql
│   ├── generate_data.py
│   └── README.md
├── metric-views/
│   └── command_center_metrics.yaml    # the spine (new)
├── dab/                               # reference bundle, adapted
│   ├── databricks.yml
│   ├── resources/                     # metric-view · genie · dashboard · app · job · lakebase
│   └── src/
│       ├── notebooks/                 # create metric view → create genie → (data already landed)
│       ├── dashboards/                # lvdash json on the metric view
│       └── app/                       # command-center-dev reference app (template for prompt 4)
└── branding/lce/                      # logo, favicon, palette (carried over)
```

**Authoring approach:**
- **Adapt** (from the original repo): `data/`, `dab/src/app/`, `branding/lce/`,
  DAB resource scaffolding.
- **Write fresh:** `metric-views/command_center_metrics.yaml`, both guides,
  README, the metric-view + genie creation notebooks, and the dashboard JSON
  (rebound to the metric view instead of raw tables).

---

## 8. Agenda (rewritten)

| Time | Module | Outcome |
|---|---|---|
| pre (async) | Setup | ai-dev-kit skills installed into Genie Code via notebook |
| 0:00-0:10 | Welcome + demo | See finished app; get env values + session-setup prompt |
| 0:10-0:25 | Module 1: Metric View | Governed KPIs over landed tables |
| 0:25-0:45 | Module 2: Genie Space | NL Q&A on the metric view |
| 0:45-1:05 | Module 3: AI/BI Dashboard | 4 widgets on the metric view |
| 1:05-1:15 | Break | |
| 1:15-1:45 | Module 4: App from template | `<initials>-command-center` deployed, LCE-branded |
| 1:45-2:25 | Module 5: Embed | Genie + dashboard live in the app |
| 2:25-2:50 | Module 6 (BONUS): Job | Scheduled refresh |
| 2:50-3:00 | Demo round + wrap | Share App URL |

(Times relative; facilitator sets the wall clock.)

---

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| ai-dev-kit skills don't load in Genie Code | New-thread + hard-refresh note; smoke-test prompt; facilitator fallback to mcp-ai-dev-kit app |
| Metric View skill gaps in Genie Code | Pre-validate the metric-view skill in the target workspace T-1 week; ship a reference YAML to crib |
| Genie/dashboard embed auth (403s) | OBO + `user_api_scopes` spelled out in prompt 5; reference app shows the working pattern |
| Single metric view loses daypart/sku detail | Raw tables remain in schema; Genie can drill into them |
| App-from-template step assumes `command-center-dev` exists | Facilitator deploys the reference `command-center-dev` app T-1 week as the template |
| Attendees skip pre-work | Reminder 24h out; reserve 10 min at start for stragglers |

---

## 10. Success criteria

- Every attendee runs all 6 prompts and ends with a green-wired, LCE-branded
  `<initials>-command-center` app embedding their Genie space + dashboard.
- No attendee installed anything locally.
- The metric view is the single source of measures for both the Genie space and
  the dashboard.
