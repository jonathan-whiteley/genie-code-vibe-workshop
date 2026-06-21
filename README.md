# Genie Code Vibe Workshop: Operator Command Center

![Databricks](https://img.shields.io/badge/Databricks-FF3621?logo=databricks&logoColor=white)
![Genie Code](https://img.shields.io/badge/Genie%20Code-in--workspace%20agent-1F9E73)
![Metric Views](https://img.shields.io/badge/Metric%20Views-spine-2272B4)
![Workshop](https://img.shields.io/badge/format-3%20hr%20workshop-FF671B)
![Status](https://img.shields.io/badge/state-deployed-2272B4)

> A 3-hour workshop where each attendee uses **Genie Code** (the in-workspace Databricks agent) to build a working Databricks app end-to-end, **no local install**. One Metric View governs the KPIs; every downstream surface (Genie space, AI/BI dashboard, embedded App) reuses the same governed measures.

The reference build is **Command Center**, a store-operations console for a single-store operator. It surfaces analytics and AI insights across **Sales and Labor** over an LCE-flavored synthetic dataset. Drop in a different schema and the same format works for any domain.

---

## At a glance

| | |
|---|---|
| **Duration** | 3 hours |
| **Audience** | 8-15 engineers / analysts per cohort |
| **Pre-work** | Clone repo as a Workspace Git folder; run `notebooks/00-setup` (installs skills + deploys app) |
| **Modules** | 6 modules: Metric View → Genie → Dashboard → App → Embed → Job |
| **Stack** | Metric Views · Genie · AI/BI Dashboards · Databricks Apps · DABs · FMAPI |
| **Default brand** | Little Caesars (swap via `company` config in the data generator) |

---

## Quick start (attendee)

No local install required. All workshop modules run entirely inside the Databricks Workspace:

1. **Clone this repo as a Workspace Git folder.** In the workspace, go to **Workspace > Create > Git folder**, paste the repo URL, and click Create.
2. **Open `notebooks/00-setup`, set your initials widget, and click Run All.** This single notebook installs the ai-dev-kit skills into Genie Code AND creates and deploys your `<initials>-command-center` app with all permissions and OBO scopes already wired.
3. **Open a new chat** in Genie Code (new thread; hard-refresh the browser if skills do not appear).

The hands-on lab prompts are in `notebooks/01-workshop-prompts`. Full setup instructions and module-by-module prompts: [`docs/lab-companion-guide.md`](docs/lab-companion-guide.md).

---

## Quick start (facilitator)

```bash
git clone https://github.com/jonathan-whiteley/genie-code-vibe-workshop
cd genie-code-vibe-workshop/dab

# Bootstrap: pre-create catalog/schema + empty tables (required on a fresh workspace).
# DAB validates the App's per-table resource bindings at deploy time, so the tables
# must exist (even empty) before `bundle deploy`. The setup job overwrites them later.
python3 scripts/bootstrap.py --profile <profile> --warehouse-id <id> --catalog <catalog>

databricks bundle validate -t <target>
databricks bundle deploy  -t <target> --var warehouse_id=<id>
databricks bundle run command_center_setup -t <target>
databricks bundle run command_center_app   -t <target>
```

Five steps from a fresh workspace to a fully-wired reference deployment. See [`dab/README.md`](dab/README.md) for order-of-ops details and caveats.

The facilitator also deploys `command-center-dev` as the attendee template (Module 4 uses it as the starting App).

---

## Important links

| | |
|---|---|
| Genie Code skills docs | https://docs.databricks.com/aws/en/genie-code/skills |
| ai-dev-kit | https://github.com/databricks-solutions/ai-dev-kit |
| Workshop repo | https://github.com/jonathan-whiteley/genie-code-vibe-workshop |

---

## What's in this repo

```
genie-code-vibe-workshop/
├── README.md                              This file
│
├── docs/                                  Guides and design docs
│   ├── facilitator-plan.md                Pre-workshop checklist, agenda, risks, prompts
│   └── lab-companion-guide.md             Attendee-facing: session setup, 6 modules, prompts
│
├── notebooks/                             Attendee notebooks (run from a Workspace Git folder)
│   ├── 00-setup.py                        Pre-req: install skills + create/deploy your app
│   ├── 01-workshop-prompts.py             Hands-on lab: the 6 Genie Code module prompts
│   └── utils/                             install_genie_code_skills · clone_app (called by 00-setup)
│
├── data/                                  Synthetic dataset (pre-landed before workshop)
│   ├── README.md
│   ├── ddl.sql                            CREATE TABLE statements for the 8 workshop tables
│   ├── generate_data.py                   Faker + Databricks Connect; --company lce | qsr_mexican
│   ├── requirements.txt
│   └── metric-views/
│       └── command_center_metrics.yaml    The Metric View spine (YAML authored for ai-dev-kit skill)
│
├── dab/                                   Facilitator's deployable bundle
│   ├── databricks.yml                     Targets: dev (jdub_demo), lce (ioc_sandbox)
│   ├── resources/                         job · dashboard · app · lakebase YAMLs
│   └── src/
│       ├── notebooks/                     Setup tasks: create metric view, create Genie space
│       ├── dashboards/                    operator_command_center.lvdash.json (on metric view)
│       └── app/                           command-center-dev reference App (attendee template)
│
└── branding/lce/                          LCE branding: logo, favicon, palette guide
```

---

## The Metric View spine

The workshop is architected around a single governed Metric View at `store x date` grain:

**Object:** `ioc_sandbox.vibe_workshop.command_center_metrics`
(per-attendee copy: `<initials>_command_center_metrics`)

**Six measures (the governed KPIs reused everywhere) -- sales + labor only, two-table view at store x date grain:**

| Measure | Definition |
|---|---|
| `revenue` | Sum of actual revenue across dayparts |
| `forecast_revenue` | Sum of forecast revenue across dayparts |
| `traffic` | Sum of guest traffic across dayparts |
| `labor_cost` | Sum of actual labor cost across dayparts |
| `forecast_labor_cost` | Sum of forecast labor cost across dayparts |
| `labor_pct_of_sales` | Labor cost divided by revenue |

**Five dimensions:** `date`, `store_id`, `store_name`, `region`, `day_of_week`.

The metric view joins `facts_sales_daypart` and `facts_labor_daypart` (each pre-aggregated to one row per store per date in its own subquery before joining), with `dims_stores` providing region and store attributes. Inventory and feedback raw tables remain in the schema for the reference app but are not included in the metric view, keeping the join fan-out-free.

Every downstream surface (the Genie space, the AI/BI dashboard, and the embedded App) draws from these same governed measures. Raw source tables remain in the schema so Genie can drill into daypart, role, or SKU detail when a question requires finer grain.

Authored in YAML at `data/metric-views/command_center_metrics.yaml` and created via the ai-dev-kit metric-views skill in Module 1.

---

## Reference schema (8 tables)

3 dims + 5 facts under `ioc_sandbox.vibe_workshop` (dev mirror: `jdub_demo.vibe_workshop`):

| Table | Grain | Rows | Purpose |
|---|---|---|---|
| `dims_stores` | store | 20 | 20 real LCE-presence locations (Detroit, Chicago, Houston, ...) |
| `dims_items` | sku | 50 | Pizza ingredients, beverages, packaging |
| `dims_employees` | employee | ~240 | ~12 per store (cook / cashier / lead / manager) |
| `facts_sales_daypart` | date x store x daypart | 4,800 | Revenue + traffic, actual + forecast |
| `facts_labor_daypart` | date x store x daypart x role | 19,200 | Crew + hours + cost, actual + forecast |
| `facts_sales_inventory_daily` | date x store x sku | 60,000 | Units sold + on-hand + reorder point |
| `facts_purchase_orders` | po line | ~250 | Pre-staged POs with vendor info |
| `facts_customer_feedback` | feedback | 1,000 | Reviews with pre-staged `sentiment_label`, `theme`, `ai_drafted_reply` |

60 days of history, anchored to **2026-06-22**. Item catalog + store roster driven by a `company` config in the generator (defaults to `lce`). Add a new entry in `COMPANY_CONFIGS` to re-skin for another customer.

Column-level detail: [`data/README.md`](data/README.md).

---

## What the bundle deploys

| Resource | What it is |
|---|---|
| `command_center_setup` job | 2 sequential tasks: create metric view + create Genie space (data already landed) |
| `command_center_dash` AI/BI dashboard | KPI counters (revenue, labor % of sales, revenue vs forecast, traffic) + revenue and labor charts on the metric view |
| `command-center-dev` Databricks App | FastAPI + Homebase UI; the reference template attendees extend in Module 4 |

The App's catalog, schema, and Genie space ID are published to `/Workspace/Shared/command-center/config.json` by the setup job and read by the App at startup; the same `app.yaml` ships dev and prod with no hand-edits.

---

## Reusing for another customer

1. Add an entry to `COMPANY_CONFIGS` in `data/generate_data.py` (store roster + item catalog + review templates)
2. Drop logo + colors into `branding/<customer>/`
3. Deploy with `--var company=<key>` (e.g. `databricks bundle deploy -t prod --var company=acme`)
4. The metric view measures, Genie space questions, dashboard widgets, and App structure stay constant; brand surface is the only delta

---

## Companion Documents

| | |
|---|---|
| **Facilitator Plan** (deploy checklist, agenda, troubleshooting) | [`docs/facilitator-plan.md`](docs/facilitator-plan.md) |
| **Lab Companion Guide** (attendee-facing: setup, prompts, tips) | [`docs/lab-companion-guide.md`](docs/lab-companion-guide.md) |
| **Operational runbook** (deploy commands, gotchas, fallbacks) | [`dab/README.md`](dab/README.md) |
| **Metric view definition** | [`data/metric-views/command_center_metrics.yaml`](data/metric-views/command_center_metrics.yaml) |
| **Repo** | https://github.com/jonathan-whiteley/genie-code-vibe-workshop |
