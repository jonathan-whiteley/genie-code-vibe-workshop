# Genie Code Vibe Workshop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `genie-code-vibe-workshop` repo: a 3-hour, no-local-install workshop run entirely in Genie Code, where attendees build a Metric View → Genie Space → AI/BI Dashboard → Databricks App → Embed → (bonus) Job over the existing store-ops dataset.

**Architecture:** Adapt the proven `ucode-vibe-workshop` assets (data generator, DAB, reference app, branding) and re-architect around a single governed Metric View as the spine. The Genie space and dashboard both bind to the metric view rather than raw tables. Two attendee-facing guides are rewritten for Genie Code (in-workspace agent, skills loaded via the ai-dev-kit notebook installer).

**Tech Stack:** Databricks Asset Bundles (DABs), Unity Catalog Metric Views (YAML), Genie spaces (REST/SDK), AI/BI Lakeview dashboards (JSON), Databricks Apps (FastAPI + static UI), serverless notebooks, Genie Code + ai-dev-kit skills.

**Source repo to adapt from:** cloned at `/tmp/ucode-vibe-workshop` (or re-clone `https://github.com/jonathan-whiteley/ucode-vibe-workshop`).

## Global Constraints

- **No em dashes or en dashes** in any prose/docs — use colons, semicolons, commas, or parentheses (hyphens only for ranges).
- **No local install** is required of attendees anywhere in the guides: no `uv`, Node, Databricks CLI, `ucode`, Claude Code, or Codex. The only pre-work is running the ai-dev-kit notebook installer in the workspace.
- **Metric View is the spine:** the Genie space (step 2) and dashboard (step 3) bind to the metric view, not raw tables.
- Shared catalog.schema: `ioc_sandbox.vibe_workshop` (dev mirror `jdub_demo.vibe_workshop`).
- Metric view object name: `command_center_metrics` (per-attendee `<initials>_command_center_metrics`).
- Reference app name used as the attendee template: **`command-center-dev`**.
- Model endpoint for `ai_query()`: `databricks-claude-sonnet-4-6`.
- Data anchored to `2026-06-22` (60 days history); "today" = `MAX(date)`, never `current_date()`.
- ai-dev-kit → Genie Code install path: **attendee notebook installer** (`install_genie_code_skills.py`); facilitator `mcp-ai-dev-kit` app documented as optional upgrade only.
- Branding: keep "Command Center" + LCE (logo `branding/lce/logo.svg`, primary `#FF671B`).
- The 6 attendee prompts must stay **succinct** (2-4 lines each).

---

### Task 1: Repo skeleton, .gitignore, and README

**Files:**
- Create: `~/Desktop/Projects/genie-code-vibe-workshop/.gitignore`
- Create: `~/Desktop/Projects/genie-code-vibe-workshop/README.md`
- (Directory `docs/superpowers/` already exists with spec + this plan.)

**Interfaces:**
- Produces: the directory layout every later task writes into (`data/`, `metric-views/`, `dab/resources/`, `dab/src/notebooks/`, `dab/src/dashboards/`, `dab/src/app/`, `branding/lce/`, `docs/`).

- [ ] **Step 1: Create the directory skeleton**

```bash
cd ~/Desktop/Projects/genie-code-vibe-workshop
mkdir -p data metric-views dab/resources dab/src/notebooks dab/src/dashboards dab/src/app branding/lce docs
```

- [ ] **Step 2: Write `.gitignore`**

```
__pycache__/
*.pyc
.databricks/
.venv/
node_modules/
dist/
.DS_Store
*.log
```

- [ ] **Step 3: Write `README.md`**

Mirror the structure of the original `/tmp/ucode-vibe-workshop/README.md` (badges, "At a glance", "What's in this repo" tree, "Reference schema" table, "What the bundle deploys") but rewrite the framing for Genie Code. Required deltas:
- Title: `# Genie Code Vibe Workshop: Operator Command Center`
- One-line pitch: built **entirely in Genie Code** in the Databricks Workspace, **no local install**.
- "At a glance" table: Duration 3 hours; Pre-work = run the ai-dev-kit skills notebook installer; Modules = `Metric View → Genie → Dashboard → App → Embed → Job`; Stack = Metric Views · Genie · AI/BI Dashboards · Databricks Apps · DABs · FMAPI.
- Replace the attendee "Quick start" `curl/uv/ucode` block with: *"Open Genie Code in the workspace, run the skills installer notebook, start a new Agent-mode chat."*
- Keep the facilitator DAB quick start (adapted commands from Task 4/5).
- "Important links" table: Genie Code skills docs (`https://docs.databricks.com/aws/en/genie-code/skills`), ai-dev-kit (`https://github.com/databricks-solutions/ai-dev-kit`), this repo.
- Reuse the 8-table reference schema table verbatim from the original (the dataset is unchanged).
- Add a short "The Metric View spine" subsection naming `command_center_metrics` and its 6 measures.

- [ ] **Step 4: Verify structure**

Run: `cd ~/Desktop/Projects/genie-code-vibe-workshop && find . -type d -not -path './.git/*' | sort`
Expected: shows `./data`, `./metric-views`, `./dab/resources`, `./dab/src/app`, `./dab/src/dashboards`, `./dab/src/notebooks`, `./branding/lce`, `./docs`.

- [ ] **Step 5: Commit**

```bash
git add .gitignore README.md
git commit -m "Repo skeleton + Genie Code README"
```

---

### Task 2: Carry over data + branding assets (unchanged dataset)

**Files:**
- Create (copy): `data/ddl.sql`, `data/generate_data.py`, `data/requirements.txt`, `data/README.md`
- Create (copy): `branding/lce/logo.svg`, `branding/lce/favicon.svg`, `branding/lce/README.md`

**Interfaces:**
- Produces: the 8-table schema (`dims_stores`, `dims_items`, `dims_employees`, `facts_sales_daypart`, `facts_labor_daypart`, `facts_sales_inventory_daily`, `facts_purchase_orders`, `facts_customer_feedback`) that the metric view (Task 3) reads.

- [ ] **Step 1: Copy data + branding from the source repo**

```bash
cd ~/Desktop/Projects/genie-code-vibe-workshop
cp /tmp/ucode-vibe-workshop/data/{ddl.sql,generate_data.py,requirements.txt,README.md} data/
cp /tmp/ucode-vibe-workshop/branding/lce/{logo.svg,favicon.svg,README.md} branding/lce/
```

- [ ] **Step 2: Verify the 8 tables are defined in ddl.sql**

Run: `grep -c "CREATE OR REPLACE TABLE" data/ddl.sql`
Expected: `8`

- [ ] **Step 3: Verify branding logo present**

Run: `test -f branding/lce/logo.svg && head -1 branding/lce/logo.svg`
Expected: an SVG opening tag prints, exit 0.

- [ ] **Step 4: Commit**

```bash
git add data branding
git commit -m "Carry over store-ops data generator + LCE branding"
```

---

### Task 3: Author the Metric View YAML (the spine)

**Files:**
- Create: `metric-views/command_center_metrics.yaml`

**Interfaces:**
- Consumes: the 8 tables from Task 2 (`facts_sales_daypart`, `facts_labor_daypart`, `facts_sales_inventory_daily`, `facts_customer_feedback`, `dims_stores`).
- Produces: metric view `command_center_metrics` at `store × date` grain with measures `revenue`, `labor_cost`, `labor_pct_of_sales`, `days_of_cover`, `sell_through_pct`, `net_sentiment` and dimensions `store_id`, `store_name`, `region`, `date`, `day_of_week`. The Genie notebook (Task 5) and dashboard JSON (Task 5) bind to this object.

- [ ] **Step 1: Write the metric view YAML**

Use the Unity Catalog metric view spec (version 0.1). The `source` is a SQL query that rolls the daypart/sku facts to `store × date` and joins the daily rollups. Write:

```yaml
version: "0.1"
source: |
  SELECT
    s.date,
    s.store_id,
    st.store_name,
    st.region,
    date_format(s.date, 'EEEE')           AS day_of_week,
    s.revenue,
    l.labor_cost,
    inv.units_sold,
    inv.on_hand_eod,
    fb.pos_cnt,
    fb.neg_cnt,
    fb.total_cnt
  FROM (
    SELECT date, store_id, SUM(revenue) AS revenue
    FROM ioc_sandbox.vibe_workshop.facts_sales_daypart
    GROUP BY date, store_id
  ) s
  LEFT JOIN (
    SELECT date, store_id, SUM(labor_cost) AS labor_cost
    FROM ioc_sandbox.vibe_workshop.facts_labor_daypart
    GROUP BY date, store_id
  ) l USING (date, store_id)
  LEFT JOIN (
    SELECT date, store_id,
           SUM(units_sold) AS units_sold,
           SUM(on_hand_eod) AS on_hand_eod
    FROM ioc_sandbox.vibe_workshop.facts_sales_inventory_daily
    GROUP BY date, store_id
  ) inv USING (date, store_id)
  LEFT JOIN (
    SELECT date, store_id,
           SUM(CASE WHEN sentiment_label = 'pos' THEN 1 ELSE 0 END) AS pos_cnt,
           SUM(CASE WHEN sentiment_label = 'neg' THEN 1 ELSE 0 END) AS neg_cnt,
           COUNT(*) AS total_cnt
    FROM ioc_sandbox.vibe_workshop.facts_customer_feedback
    GROUP BY date, store_id
  ) fb USING (date, store_id)
  JOIN ioc_sandbox.vibe_workshop.dims_stores st USING (store_id)

dimensions:
  - name: date
    expr: date
  - name: store_id
    expr: store_id
  - name: store_name
    expr: store_name
  - name: region
    expr: region
  - name: day_of_week
    expr: day_of_week

measures:
  - name: revenue
    expr: SUM(revenue)
  - name: labor_cost
    expr: SUM(labor_cost)
  - name: labor_pct_of_sales
    expr: SUM(labor_cost) / NULLIF(SUM(revenue), 0)
  - name: days_of_cover
    expr: SUM(on_hand_eod) / NULLIF(SUM(units_sold), 0)
  - name: sell_through_pct
    expr: SUM(units_sold) / NULLIF(SUM(units_sold) + SUM(on_hand_eod), 0)
  - name: net_sentiment
    expr: (SUM(pos_cnt) - SUM(neg_cnt)) / NULLIF(SUM(total_cnt), 0)
```

- [ ] **Step 2: Verify YAML parses**

Run: `python3 -c "import yaml,sys; d=yaml.safe_load(open('metric-views/command_center_metrics.yaml')); print(sorted(m['name'] for m in d['measures']))"`
Expected: `['days_of_cover', 'labor_cost', 'labor_pct_of_sales', 'net_sentiment', 'revenue', 'sell_through_pct']`

- [ ] **Step 3: (Workspace gate) Verify the source query returns rows**

If a Databricks profile is available, validate the source SQL against the landed tables:

Run: `databricks --profile <profile> sql query --warehouse-id <id> --query "$(sed -n '/^source:/,/^dimensions:/p' metric-views/command_center_metrics.yaml | sed '1d;$d' | sed 's/^  //')" 2>&1 | head -5`
Expected: rows return (store × date grain). If no profile is available in this session, mark this step deferred to the facilitator T-1-week smoke test and note it in `docs/facilitator-plan.md` (Task 7).

- [ ] **Step 4: Commit**

```bash
git add metric-views/command_center_metrics.yaml
git commit -m "Add command_center_metrics metric view (store x date spine)"
```

---

### Task 4: DAB scaffold — bundle config + resources

**Files:**
- Create: `dab/databricks.yml`
- Create: `dab/resources/metric_view.yml`
- Create: `dab/resources/genie.yml` (job-driven; see Task 5 — the genie space is created by a notebook task, so this file is the dashboard + app + job + metric-view bundling)
- Create: `dab/resources/dashboard.yml`
- Create: `dab/resources/app.yml`
- Create: `dab/resources/job.yml`
- Create: `dab/resources/lakebase.yml` (copy from source unchanged)

**Interfaces:**
- Consumes: metric view YAML (Task 3), app source (Task 6), notebooks + dashboard JSON (Task 5).
- Produces: a bundle named `genie-code-vibe-workshop` with targets `dev` (jdub_demo) and `lce` (ioc_sandbox), variables `catalog`, `schema`, `warehouse_id`, `fmapi_endpoint`, `data_end_date`, `attendee_group`, `company`.

- [ ] **Step 1: Write `dab/databricks.yml`**

Copy `/tmp/ucode-vibe-workshop/dab/databricks.yml` and change: `bundle.name: genie-code-vibe-workshop`; update the header comment to describe the metric-view-first reference build; keep the same `variables` and `targets` blocks (dev/lce/e2demo/azure). Keep `fmapi_endpoint` default `databricks-claude-sonnet-4-6`.

- [ ] **Step 2: Copy `lakebase.yml` unchanged**

```bash
cp /tmp/ucode-vibe-workshop/dab/resources/lakebase.yml dab/resources/lakebase.yml
```

- [ ] **Step 3: Write `dab/resources/metric_view.yml`**

Register the metric view as a UC schema object created by the setup job (metric views have no native DAB resource type in all runtimes, so it is created via the notebook in Task 5). This file documents the binding for the dashboard:

```yaml
# The command_center_metrics metric view is created by the setup job's
# create_metric_view task (../src/notebooks/02_create_metric_view.py).
# Object: ${var.catalog}.${var.schema}.command_center_metrics
# The reference dashboard and Genie space both bind to it.
#
# No standalone DAB resource is declared here; this file is a placeholder
# documenting the dependency so the bundle's resource set is self-describing.
```

- [ ] **Step 4: Write `dab/resources/dashboard.yml`**

Adapt the source `dashboard.yml`: rename to `command_center_dash`, `display_name: "Operator Command Center"`, `file_path: ../src/dashboards/operator_command_center.lvdash.json`, keep `warehouse_id`/`dataset_catalog`/`dataset_schema` from vars, keep `CAN_RUN` for `${var.attendee_group}`.

- [ ] **Step 5: Copy + adjust `app.yml` (template app name)**

```bash
cp /tmp/ucode-vibe-workshop/dab/resources/app.yml dab/resources/app.yml
```
Then edit: set `name: "command-center-${bundle.target}"` (so the `dev` target produces **`command-center-dev`**, the template attendees clone in prompt 4). Keep the `user_api_scopes: [genie, sql, dashboards.genie]` block and the 8 `uc_securable` SELECT bindings and the lakebase resource verbatim.

- [ ] **Step 6: Write `dab/resources/job.yml`**

Adapt the source job to the metric-view flow. Job name `"Operator Command Center setup"`, tags `workshop: genie-code-vibe-command-center`. Tasks (sequential):
1. `generate_data` → `../src/notebooks/01_generate_data.py` (unchanged base_parameters from source).
2. `create_metric_view` → `../src/notebooks/02_create_metric_view.py`, depends_on `generate_data`, base_parameters `catalog`, `schema`, `warehouse_id`.
3. `create_genie_space` → `../src/notebooks/03_create_genie_space.py`, depends_on `create_metric_view`, base_parameters `catalog`, `schema`, `warehouse_id`.
4. `init_lakebase` → `../src/notebooks/04_init_lakebase.py`, depends_on `generate_data`, base_parameters `lakebase_instance_name`, `attendee_group`.

Keep serverless `environments` block (`client: "2"`), `max_concurrent_runs: 1`, `CAN_VIEW` for `${var.attendee_group}`, and the `parameters` block.

- [ ] **Step 7: Verify all resource files are valid YAML**

Run: `for f in dab/databricks.yml dab/resources/*.yml; do python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"; done`
Expected: `OK` for every file.

- [ ] **Step 8: (Workspace gate) bundle validate**

If a profile is available: `cd dab && databricks bundle validate -t dev --var warehouse_id=<id>` → expected "Validation OK". If no profile, mark deferred to facilitator and note in `docs/facilitator-plan.md`.

- [ ] **Step 9: Commit**

```bash
git add dab/databricks.yml dab/resources
git commit -m "DAB scaffold: bundle + metric-view-first resources"
```

---

### Task 5: Setup notebooks + dashboard JSON (rebound to the metric view)

**Files:**
- Create (copy): `dab/src/notebooks/01_generate_data.py`
- Create (new): `dab/src/notebooks/02_create_metric_view.py`
- Create (adapt): `dab/src/notebooks/03_create_genie_space.py`
- Create (copy → renumber): `dab/src/notebooks/04_init_lakebase.py`
- Create (adapt): `dab/src/dashboards/operator_command_center.lvdash.json`

**Interfaces:**
- Consumes: metric view YAML (Task 3), 8 tables (Task 2).
- Produces: the `command_center_metrics` object in UC; a Genie space bound to the metric view; a Lakeview dashboard whose datasets query the metric view; the `/Workspace/Shared/command-center/config.json` the app reads.

- [ ] **Step 1: Copy the data + lakebase notebooks**

```bash
cp /tmp/ucode-vibe-workshop/dab/src/notebooks/01_generate_data.py dab/src/notebooks/01_generate_data.py
cp /tmp/ucode-vibe-workshop/dab/src/notebooks/02_init_lakebase.py dab/src/notebooks/04_init_lakebase.py
```

- [ ] **Step 2: Write `02_create_metric_view.py`**

A serverless notebook that creates the metric view from the YAML using `CREATE OR REPLACE VIEW ... WITH METRICS`. It reads widgets `catalog`, `schema`, `warehouse_id`, loads `metric-views/command_center_metrics.yaml` content (inline the YAML string in the notebook so it is self-contained on serverless), and runs:

```python
# Databricks notebook source
dbutils.widgets.text("catalog", "ioc_sandbox")
dbutils.widgets.text("schema", "vibe_workshop")
dbutils.widgets.text("warehouse_id", "")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")

# The metric view YAML (kept in sync with metric-views/command_center_metrics.yaml).
METRIC_YAML = r'''
version: "0.1"
source: |
  SELECT s.date, s.store_id, st.store_name, st.region,
         date_format(s.date,'EEEE') AS day_of_week,
         s.revenue, l.labor_cost, inv.units_sold, inv.on_hand_eod,
         fb.pos_cnt, fb.neg_cnt, fb.total_cnt
  FROM (SELECT date, store_id, SUM(revenue) revenue
        FROM {cat}.{sch}.facts_sales_daypart GROUP BY date, store_id) s
  LEFT JOIN (SELECT date, store_id, SUM(labor_cost) labor_cost
        FROM {cat}.{sch}.facts_labor_daypart GROUP BY date, store_id) l USING (date, store_id)
  LEFT JOIN (SELECT date, store_id, SUM(units_sold) units_sold, SUM(on_hand_eod) on_hand_eod
        FROM {cat}.{sch}.facts_sales_inventory_daily GROUP BY date, store_id) inv USING (date, store_id)
  LEFT JOIN (SELECT date, store_id,
               SUM(CASE WHEN sentiment_label='pos' THEN 1 ELSE 0 END) pos_cnt,
               SUM(CASE WHEN sentiment_label='neg' THEN 1 ELSE 0 END) neg_cnt,
               COUNT(*) total_cnt
        FROM {cat}.{sch}.facts_customer_feedback GROUP BY date, store_id) fb USING (date, store_id)
  JOIN {cat}.{sch}.dims_stores st USING (store_id)
dimensions:
  - name: date
    expr: date
  - name: store_id
    expr: store_id
  - name: store_name
    expr: store_name
  - name: region
    expr: region
  - name: day_of_week
    expr: day_of_week
measures:
  - name: revenue
    expr: SUM(revenue)
  - name: labor_cost
    expr: SUM(labor_cost)
  - name: labor_pct_of_sales
    expr: SUM(labor_cost) / NULLIF(SUM(revenue),0)
  - name: days_of_cover
    expr: SUM(on_hand_eod) / NULLIF(SUM(units_sold),0)
  - name: sell_through_pct
    expr: SUM(units_sold) / NULLIF(SUM(units_sold)+SUM(on_hand_eod),0)
  - name: net_sentiment
    expr: (SUM(pos_cnt)-SUM(neg_cnt)) / NULLIF(SUM(total_cnt),0)
'''.format(cat=CATALOG, sch=SCHEMA)

fqn = f"{CATALOG}.{SCHEMA}.command_center_metrics"
spark.sql(f"CREATE OR REPLACE VIEW {fqn} WITH METRICS LANGUAGE YAML AS $$ {METRIC_YAML} $$")
print(f"Created metric view {fqn}")
display(spark.sql(f"SELECT * FROM {fqn} LIMIT 5"))
```

> Note: confirm the exact `WITH METRICS` DDL syntax against the `databricks-metric-views` skill at execution time; if the runtime expects `CREATE VIEW ... WITH METRICS LANGUAGE YAML AS $$...$$`, use that. The skill is authoritative on syntax.

- [ ] **Step 3: Adapt `03_create_genie_space.py` to bind to the metric view**

Copy the source notebook, then change `data_sources` to the metric view and update title/instructions:
- `TITLE = "Command Center reference"`
- `TABLES = [f"{CATALOG}.{SCHEMA}.command_center_metrics"]` (the metric view is the single data source; raw fact tables MAY be added as secondary sources for daypart/sku drill-downs — keep the metric view first).
- Update `INSTRUCTIONS` to say the primary source is the `command_center_metrics` metric view whose governed measures are labor_pct_of_sales, days_of_cover, sell_through_pct, net_sentiment, revenue, labor_cost at store×date grain; anchor "today" to MAX(date).
- Rewrite `SAMPLE_QUESTIONS` to be answerable from the metric view measures (2 per pillar):
  - "Which 5 stores had the highest labor % of sales last week?"
  - "Show labor % of sales trend over the last 30 days."
  - "Which region has the lowest days of cover right now?"
  - "Show sell-through % by store for the latest date."
  - "What's the net sentiment trend over the last 30 days?"
  - "Which stores have negative net sentiment this week?"
- Keep the idempotent create/patch logic and the `config.json` write (catalog, schema, warehouse_id, genie_space_id) verbatim.

- [ ] **Step 4: Adapt the dashboard JSON to query the metric view**

Copy `/tmp/ucode-vibe-workshop/dab/src/dashboards/operator_command_center.lvdash.json`, then rebind its datasets so queries select from `command_center_metrics` using the measures (e.g. `SELECT date, MEASURE(labor_pct_of_sales) ...`). Four widgets: labor % of sales (30-day line), revenue by region (bar), days of cover by store (bar), net sentiment timeline (line). Verify it is valid JSON (Step 6).

- [ ] **Step 5: Verify notebooks are syntactically importable**

Run: `python3 -m py_compile dab/src/notebooks/02_create_metric_view.py dab/src/notebooks/03_create_genie_space.py && echo OK`
Expected: `OK` (note: `# Databricks notebook source` + `# COMMAND ----------` lines are comments and compile fine; `dbutils`/`spark` are runtime-injected so only syntax is checked).

- [ ] **Step 6: Verify dashboard JSON parses**

Run: `python3 -c "import json; json.load(open('dab/src/dashboards/operator_command_center.lvdash.json')); print('OK')"`
Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add dab/src/notebooks dab/src/dashboards
git commit -m "Setup notebooks (metric view + genie) + rebound dashboard"
```

---

### Task 6: Reference app (`command-center-dev` template)

**Files:**
- Create (copy): everything under `dab/src/app/` from the source repo.

**Interfaces:**
- Consumes: the 8 tables, Lakebase, Genie space (via `config.json`).
- Produces: the deployed reference app `command-center-dev` that attendees clone as the template in prompt 4, and whose `routers/genie.py` shows the working OBO embed pattern referenced by prompt 5.

- [ ] **Step 1: Copy the app source tree**

```bash
cp -R /tmp/ucode-vibe-workshop/dab/src/app/ dab/src/app/
```

- [ ] **Step 2: Verify the app entrypoint + genie router copied**

Run: `test -f dab/src/app/app.py && test -f dab/src/app/routers/genie.py && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify no stray `ucode` references remain in app config**

Run: `grep -ri "ucode" dab/src/app/ || echo "clean"`
Expected: `clean` (or only incidental matches in comments — if any reference local tooling, remove it).

- [ ] **Step 4: Commit**

```bash
git add dab/src/app
git commit -m "Carry over reference app as command-center-dev template"
```

---

### Task 7: Rewrite the Facilitator Plan

**Files:**
- Create: `docs/facilitator-plan.md`

**Interfaces:**
- Consumes: the metric-view-first agenda, the notebook-installer skills path, the DAB deploy commands (Task 4/5).

- [ ] **Step 1: Write `docs/facilitator-plan.md`**

Use the source `/tmp/ucode-vibe-workshop/docs/facilitator-plan.md` as the structural template (Agenda, Pre-Workshop Checklist, Deploy the reference build, T-1-day, Troubleshooting, Naming convention, Cost controls, Cleanup, Companion docs). Required rewrites:

- Title: `# Genie Code Workshop: Operator Command Center: Facilitator Plan`. Summary line: built in **Genie Code**, metric-view-first, no local install.
- **Agenda** matches the spec §8 (Metric View → Genie → Dashboard → App → Embed → bonus Job).
- **Remove** the "ucode + IDE + ai-dev-kit" pre-work row and the AI-Gateway-for-`ucode-codex` rationale. Pre-work becomes: attendees open Genie Code, run the ai-dev-kit notebook installer, start a new Agent-mode chat.
- Add a **"Skills in Genie Code"** subsection:
  - Path: each attendee runs `install_genie_code_skills.py` (`https://github.com/databricks-solutions/ai-dev-kit/blob/main/databricks-skills/install_genie_code_skills.py`) → skills land in `/Users/<me>/.assistant/skills/`.
  - Caveats: Agent mode only; new chat thread (+ hard refresh) after install; verify skills loaded; `databricks aitools` does NOT support Genie Code.
  - Optional upgrade (facilitator, workspace-wide): deploy the `mcp-ai-dev-kit` Databricks App (from `databricks-field-eng/india-gcc`) to push skills to `Workspace/.assistant/skills/` for all users + serve tools at `/mcp`.
- **Features the admin must enable:** Databricks Apps; Genie spaces; **Metric Views** (UC); FMAPI + AI Gateway → `databricks-claude-sonnet-4-6` (for `ai_query()` only now, not for a local agent); Lakebase.
- **Deploy the reference build** runbook (facilitator), adapted to the new task order:
  ```bash
  # 1. Pre-create catalog/schema + 8 empty tables
  python3 scripts/bootstrap.py --profile lce --warehouse-id <id> --catalog ioc_sandbox
  # 2. Validate
  cd dab && databricks bundle validate -t lce --var warehouse_id=<id>
  # 3. Deploy (Lakebase + dashboard + app + job)
  databricks bundle deploy -t lce --var warehouse_id=<id>
  # 4. Run setup (data → metric view → genie space → lakebase → config json)
  databricks bundle run command_center_setup -t lce
  # 5. Start the reference app (this is the command-center-dev template)
  databricks bundle run command_center_app -t lce
  ```
  (If `scripts/bootstrap.py`/`cleanup.py` are wanted, note they can be copied from the source repo; flag as a follow-up if not carried over.)
- **Smoke test** adds: metric view returns rows (`SELECT * FROM <cat>.vibe_workshop.command_center_metrics LIMIT 5`); Genie answers one metric-view question; the `command-center-dev` app renders.
- **Per-attendee naming:** App `<initials>-command-center`; Metric view `<initials>_command_center_metrics`; Genie `"<initials> Command Center"`; Dashboard `"<initials> Operator Insights"`; Job `<initials>-command-center-refresh`.
- **Troubleshooting** adds rows: skills not loading in Genie Code (new thread + hard refresh); metric view DDL syntax (defer to `databricks-metric-views` skill); embed 403 (OBO + `user_api_scopes`).
- Keep Cost Controls / Cleanup sections; swap the `workshop` tag value to `genie-code-vibe-command-center`.
- **No em/en dashes** anywhere.

- [ ] **Step 2: Verify no em/en dashes**

Run: `grep -nP "[\x{2013}\x{2014}]" docs/facilitator-plan.md && echo "FOUND DASHES" || echo "clean"`
Expected: `clean`

- [ ] **Step 3: Verify no leftover local-tooling instructions**

Run: `grep -niE "uv tool install|ucode claude|ucode codex|brew install|uv python install" docs/facilitator-plan.md && echo "FOUND" || echo "clean"`
Expected: `clean`

- [ ] **Step 4: Commit**

```bash
git add docs/facilitator-plan.md
git commit -m "Rewrite facilitator plan for Genie Code + metric-view-first"
```

---

### Task 8: Rewrite the Lab Companion Guide (attendee-facing, 6 prompts)

**Files:**
- Create: `docs/lab-companion-guide.md`

**Interfaces:**
- Consumes: the session-setup pattern + the 6 build-step prompts from spec §6.

- [ ] **Step 1: Write `docs/lab-companion-guide.md`**

Use the source `/tmp/ucode-vibe-workshop/docs/lab-companion-guide.md` as the structural template (intro "You'll build", Agenda, "How to use this guide", Pre-reqs, Day-of prompts, Environment table, Vibe Coding Tips, Reference Links). Required rewrites:

- Title: `# Genie Code Workshop: Operator Command Center: Lab Companion Guide`.
- "How to use this guide": prompts are pasted into **Genie Code in Agent mode** in the workspace; the agent has ai-dev-kit skills loaded; tell it *what*, the skills know *how*; always read what it generates.
- **Pre-reqs** section replaces ALL shell/OS install blocks with a single Genie Code path:
  1. Open the workspace → open **Genie Code**.
  2. Import the ai-dev-kit skills installer notebook and **Run All**:
     `https://github.com/databricks-solutions/ai-dev-kit/blob/main/databricks-skills/install_genie_code_skills.py`
  3. Start a **new Agent-mode chat** (hard-refresh the browser if skills don't show).
  4. Smoke-test prompt: *"List the tables in ioc_sandbox.vibe_workshop. I should see 8 (3 dims_, 5 facts_)."*
  - Pre-work checklist: skills installed; new Agent chat open; smoke test passed.
- **Session setup** prompt (paste FIRST), adapted from the source but: drop the AI-Gateway/`ucode codex` line; add the metric view and dashboard/app/genie/job resource names; reference the `command-center-dev` template app and the repo for cribbing patterns:
  ```text
  I'm running the Genie Code Command Center workshop. Remember these values
  for the whole conversation:
    My initials:  <INITIALS>
    Catalog:      ioc_sandbox.vibe_workshop
    Warehouse:    serverless
    Model endpt:  databricks-claude-sonnet-4-6   (for ai_query())
  Resources I'll build (use exactly these names):
    - metric view:  <initials>_command_center_metrics
    - Genie space:  "<initials> Command Center"
    - dashboard:    "<initials> Operator Insights"
    - app:          <initials>-command-center   (template: command-center-dev)
    - job:          <initials>-command-center-refresh
  Capture as we go: my Genie space ID, dashboard ID, app URL.
  Confirm, then wait for my first module prompt.
  ```
- **The 6 day-of module prompts**, verbatim from spec §6 (Metric View, Genie on the view, Dashboard on the view, App from `command-center-dev` template with LCE branding, Embed with the OBO/`user_api_scopes`/dashboard-iframe/multi-turn detail, bonus Job). Each in its own copy-paste code block.
- Keep the "If running low on time" tip on the embed module (drop per-tab dashboard tiles, keep Ask Genie).
- **Environment table** updated: remove the AI Gateway row; add the metric view name row; keep workspace URL, catalog, warehouse, model endpoint, captured IDs.
- **No em/en dashes** anywhere.

- [ ] **Step 2: Verify all 6 module prompts present**

Run: `grep -cE "^#### .*Module [1-6]|^### .*Module [1-6]" docs/lab-companion-guide.md`
Expected: `6` (adjust the grep to whatever heading level you used; the point is six distinct module prompt sections exist).

- [ ] **Step 3: Verify no em/en dashes and no local-tooling instructions**

Run: `grep -nP "[\x{2013}\x{2014}]" docs/lab-companion-guide.md && echo "FOUND DASHES" || echo "clean"`
Expected: `clean`
Run: `grep -niE "uv tool install|ucode claude|ucode codex|curl -LsSf|brew install node" docs/lab-companion-guide.md && echo "FOUND" || echo "clean"`
Expected: `clean`

- [ ] **Step 4: Commit**

```bash
git add docs/lab-companion-guide.md
git commit -m "Rewrite lab companion guide: 6 succinct Genie Code prompts"
```

---

### Task 9: Final consistency pass + README cross-links

**Files:**
- Modify: `README.md` (link the two guides), `docs/facilitator-plan.md` and `docs/lab-companion-guide.md` (cross-link each other).

**Interfaces:**
- Consumes: all prior tasks.

- [ ] **Step 1: Add Companion Documents cross-links**

In `README.md` and both guides, add a "Companion Documents" block linking `docs/facilitator-plan.md` and `docs/lab-companion-guide.md` and the repo URL (match the original repo's pattern).

- [ ] **Step 2: Verify resource names are consistent across all docs**

Run:
```bash
grep -rn "command_center_metrics" docs README.md metric-views dab | wc -l
grep -rn "command-center-dev" docs README.md dab | wc -l
```
Expected: both > 0; spot-check that the metric view name, template app name, and the 6 module order match between `README.md`, `docs/facilitator-plan.md`, and `docs/lab-companion-guide.md`.

- [ ] **Step 3: Verify the whole repo has no em/en dashes in docs**

Run: `grep -rnP "[\x{2013}\x{2014}]" docs README.md && echo "FOUND" || echo "clean"`
Expected: `clean`

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Cross-link guides + final consistency pass"
```

---

## Self-Review

**Spec coverage:**
- Concept/two shifts → Task 1 (README), Tasks 7-8 (guides). ✓
- ai-dev-kit notebook-installer path + caveats → Task 7 (facilitator), Task 8 (pre-reqs). ✓
- Metric view spine (approach A, store×date, 6 measures) → Task 3 (YAML) + Task 5 (creation notebook). ✓
- Genie on the metric view → Task 5 step 3. ✓
- Dashboard on the metric view → Task 5 step 4. ✓
- App from `command-center-dev` template + LCE branding → Task 6 + prompt in Task 8. ✓
- Embed with OBO/`user_api_scopes`/dashboard iframe/multi-turn → Task 8 prompt 5 + Task 6 (reference router). ✓
- Bonus Job → Task 4 (job.yml) + Task 8 prompt 6. ✓
- Repo scaffold (data, branding, dab, metric-views) → Tasks 2,4,5,6. ✓
- Rewritten agenda → Task 7. ✓
- Risks (skills load, embed auth, metric-view detail loss, template app exists) → covered in Task 7 troubleshooting + facilitator deploy. ✓

**Placeholder scan:** The `metric_view.yml` is intentionally a documenting placeholder (metric views are created by notebook, not a DAB resource type) — this is explained, not a gap. Dashboard JSON rebinding (Task 5 step 4) describes the transformation rather than reproducing the full ~hundreds-of-lines JSON; the source file is available to crib and the verification gate (valid JSON + measures present) bounds it. Metric-view DDL syntax flagged to defer to the `databricks-metric-views` skill at execution — acceptable since that skill is authoritative and runtime-version-dependent.

**Type/name consistency:** `command_center_metrics` (metric view), `command-center-dev` (template app), the 6 measures (`revenue`, `labor_cost`, `labor_pct_of_sales`, `days_of_cover`, `sell_through_pct`, `net_sentiment`), and the 6-module order are used identically across Tasks 3, 4, 5, 7, 8, 9.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-18-genie-code-vibe-workshop.md`.
