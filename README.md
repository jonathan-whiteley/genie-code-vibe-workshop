# Genie Code Vibe Workshop: Operator Command Center

![Databricks](https://img.shields.io/badge/Databricks-FF3621?logo=databricks&logoColor=white)
![Genie Code](https://img.shields.io/badge/Genie%20Code-in--workspace%20agent-1F9E73)
![No local install](https://img.shields.io/badge/setup-no%20local%20install-2272B4)
![Workshop](https://img.shields.io/badge/format-3%20hr%20workshop-FF671B)
![Status](https://img.shields.io/badge/state-deployed-2272B4)

> In one afternoon, build and deploy a **real Databricks app** end to end, just by chatting with **Genie Code**, the agent built into your Databricks workspace. No local setup, no glue code, no leaving the browser.

You will stand up a complete **Command Center**: a store-operations console that answers business questions in plain language, shows live KPIs, and runs on governed data, all created by prompting an agent. The reference build is for a single-store **Little Caesars** operator over a synthetic Sales and Labor dataset; swap the data and the same flow fits any business.

---

## What you'll build

By the end, all created through Genie Code prompts, you will have:

- A **governed KPI layer** so every number means the same thing everywhere
- A **Genie space** to ask questions of your data in plain English
- An **AI/BI dashboard** of the key metrics
- A **deployed web app** that embeds your Genie space and dashboard, writes an AI store briefing, and pulls in live company news
- A **scheduled job** that keeps it all fresh

You do not write the code. You describe what you want; Genie Code builds it on Databricks.

---

## Why Databricks + Genie Code

Genie Code is not just a chat box. Because it builds on Databricks, your app is governed, connected to your data, and production-ready from the very first prompt:

| | | |
|---|---|---|
| 🧠 | **In-workspace agent** | Build by chatting in your browser. No local install, no IDE, no API keys to manage. |
| 🔐 | **Unity Catalog governance** | The agent can only touch data your identity allows, and everything it creates is governed the same way. |
| 📐 | **Metric Views** | Define a KPI once; Genie, the dashboard, and your app all reuse the same governed numbers, so the metrics never drift. |
| 🧞 | **Genie** | Natural-language Q&A grounded in your governed measures, embeddable straight into your app. |
| 📊 | **AI/BI Dashboards** | The same measures, visualized, with zero re-definition. |
| 🚀 | **Databricks Apps** | Deploy a real web app on the platform, right next to your data. |
| 🤖 | **ai_query + Foundation Models** | Call Claude from SQL or app code through one governed model endpoint. |
| 🔌 | **MCP connections** | Reach external tools (like live web search) through governed Unity Catalog connections. |

<details>
<summary><strong>🧠 What supercharges Genie Code: the ai-dev-kit skills (expand)</strong></summary>

Genie Code already ships with built-in intelligence about your workspace and your data. The **[ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit)** skills (installed for you in `notebooks/00-setup`) supercharge that with the latest, field-tested patterns for **every surface that touches Databricks**, so the agent builds metric views, Genie spaces, AI/BI dashboards, apps, and jobs the right way instead of guessing at APIs.

| Category | Skills |
|---|---|
| AI & Agents | agent-bricks, genie, ai-functions, mlflow-eval, model-serving |
| Analytics | aibi-dashboards, unity-catalog, metric-views |
| Data Engineering | declarative-pipelines, jobs, structured-streaming, synthetic-data, zerobus-ingest |
| Development | asset-bundles, apps, python-sdk, config, spark-data-source |
| Storage | lakebase, vector-search |
| Reference | docs, dbsql, pdf-generation |

This workshop adds a few of its own **project patterns** in [`docs/patterns/`](docs/patterns/) that the module prompts point Genie Code at for the trickier steps.
</details>

---

## At a glance

| | |
|---|---|
| **Duration** | 3 hours |
| **Audience** | 8-15 engineers / analysts per cohort, no Databricks expertise required |
| **Pre-work** | Clone repo as a Workspace Git folder; run `notebooks/00-setup` (installs skills + deploys your app) |
| **Modules** | Metric View → Genie → Dashboard → App → Embed → Live AI, plus a bonus refresh Job |
| **Stack** | Metric Views · Genie · AI/BI Dashboards · Databricks Apps · ai_query · MCP · DABs |
| **Default brand** | Little Caesars (swap via the `company` config in the data generator) |

---

## Quick start (attendee)

No local install required. Everything runs inside the Databricks Workspace:

1. **Clone this repo as a Workspace Git folder.** In the workspace, go to **Workspace > Create > Git folder**, paste the repo URL, and click Create.
2. **Open `notebooks/00-setup`, set your initials, and click Run All.** This installs the ai-dev-kit skills into Genie Code AND creates and deploys your `<initials>-command-center` app with all permissions and scopes already wired.
3. **Open a new chat** in Genie Code (new thread; hard-refresh the browser if the skills do not appear).

Then work through the prompts in `notebooks/01-workshop-prompts`. Full setup and module-by-module prompts: [`docs/lab-companion-guide.md`](docs/lab-companion-guide.md).

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

Five steps from a fresh workspace to a fully-wired reference deployment. See [`dab/README.md`](dab/README.md) for order-of-ops details and caveats. The facilitator also deploys `command-center-dev` as the attendee template (Module 4 starts from it).

---

## Important links

| | |
|---|---|
| Genie Code skills docs | https://docs.databricks.com/aws/en/genie-code/skills |
| ai-dev-kit | https://github.com/databricks-solutions/ai-dev-kit |
| Workshop repo | https://github.com/jonathan-whiteley/genie-code-vibe-workshop |

---

<details>
<summary><strong>What's in this repo</strong></summary>

```
genie-code-vibe-workshop/
├── README.md                              This file
│
├── docs/                                  Guides, design docs, branding, and reusable patterns
│   ├── facilitator-plan.md                Pre-workshop checklist, agenda, risks, prompts
│   ├── lab-companion-guide.md             Attendee-facing: session setup, modules, prompts
│   ├── patterns/                          Reference patterns the prompts point Genie Code at
│   └── branding/lce/                      LCE branding: logo, favicon, palette guide
│
├── notebooks/                             Attendee notebooks (run from a Workspace Git folder)
│   ├── 00-setup.py                        Pre-req: install skills + create/deploy your app
│   ├── 01-workshop-prompts.py             Hands-on lab: the Genie Code module prompts
│   └── utils/                             install_genie_code_skills · clone_app (called by 00-setup)
│
├── data/                                  Synthetic dataset (pre-landed before workshop)
│   ├── README.md
│   ├── ddl.sql                            CREATE TABLE statements for the 8 workshop tables
│   ├── generate_data.py                   Faker + Databricks Connect; --company lce | qsr_mexican
│   ├── requirements.txt
│   └── metric-views/
│       └── command_center_metrics.yaml    The governed KPI definition (created in Module 1)
│
└── dab/                                   Facilitator's deployable bundle
    ├── databricks.yml                     Targets: dev (jdub_demo), lce (ioc_sandbox)
    ├── resources/                         job · dashboard · app · lakebase YAMLs
    └── src/
        ├── notebooks/                     Setup tasks: create metric view, create Genie space
        ├── dashboards/                    operator_command_center.lvdash.json
        └── app/                           command-center-dev reference App (attendee template)
```
</details>

<details>
<summary><strong>Reference dataset (8 tables)</strong></summary>

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

60 days of history, anchored to **2026-06-22**. Item catalog and store roster are driven by a `company` config in the generator (defaults to `lce`). Column-level detail: [`data/README.md`](data/README.md).
</details>

---

## What the bundle deploys

| Resource | What it is |
|---|---|
| `command_center_setup` job | 2 sequential tasks: create the governed KPI view + create the Genie space (data already landed) |
| `command_center_dash` AI/BI dashboard | KPI counters (revenue, labor % of sales, revenue vs forecast, traffic) plus revenue and labor charts |
| `command-center-dev` Databricks App | FastAPI + Homebase UI; the reference template attendees extend in Module 4 |

The App's catalog, schema, and Genie space ID are published to `/Workspace/Shared/command-center/config.json` by the setup job and read by the App at startup; the same `app.yaml` ships dev and prod with no hand-edits.

---

## Reusing for another customer

1. Add an entry to `COMPANY_CONFIGS` in `data/generate_data.py` (store roster + item catalog + review templates)
2. Drop logo + colors into `docs/branding/<customer>/`
3. Deploy with `--var company=<key>` (e.g. `databricks bundle deploy -t prod --var company=acme`)
4. The KPI measures, Genie questions, dashboard widgets, and App structure stay constant; the brand surface is the only delta

---

## Companion Documents

| | |
|---|---|
| **Lab Companion Guide** (attendee-facing: setup, prompts, tips) | [`docs/lab-companion-guide.md`](docs/lab-companion-guide.md) |
| **Facilitator Plan** (deploy checklist, agenda, troubleshooting) | [`docs/facilitator-plan.md`](docs/facilitator-plan.md) |
| **Project patterns** (the references the prompts point Genie Code at) | [`docs/patterns/`](docs/patterns/) |
| **Operational runbook** (deploy commands, gotchas, fallbacks) | [`dab/README.md`](dab/README.md) |
| **Repo** | https://github.com/jonathan-whiteley/genie-code-vibe-workshop |
