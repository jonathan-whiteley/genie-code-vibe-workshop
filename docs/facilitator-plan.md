# Genie Code Workshop: Operator Command Center: Facilitator Plan

**Workshop:** Build an AI-powered Command Center **inside Databricks Genie Code** (metric-view-first, no local install required).
**Audience:** Field Engineers, analysts, or customer engineers (8-15 attendees recommended).
**Duration:** 3 hours.
**End state:** Each attendee has their own deployed Databricks App that surfaces a Genie space and an AI/BI dashboard, both built on a single governed Metric View, across three operational pillars: **Labor, Inventory, Guest Feedback**. Everything is packaged as a Databricks Asset Bundle.

### Quick Links

- **Workshop repo:** [github.com/jonathan-whiteley/genie-code-vibe-workshop](https://github.com/jonathan-whiteley/genie-code-vibe-workshop)
- **ai-dev-kit skills:** [github.com/databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit#genie-code-skills)
- **Genie Code skills docs:** [docs.databricks.com/aws/en/genie-code/skills](https://docs.databricks.com/aws/en/genie-code/skills)
- **Catalog.schema:** `ioc_sandbox.vibe_workshop`

---

## Agenda

Times are relative; facilitator sets the wall clock.

| Time | Module | Outcome |
|---|---|---|
| pre (async) | Setup | ai-dev-kit skills installed into Genie Code via notebook; new Agent-mode chat open |
| 0:00-0:10 | Welcome + demo | See finished app; get env values + session-setup prompt |
| 0:10-0:25 | Module 1: Metric View | Governed KPIs defined over landed tables |
| 0:25-0:45 | Module 2: Genie Space | Natural-language Q&A on the metric view |
| 0:45-1:05 | Module 3: AI/BI Dashboard | 4 widgets driven by the metric view |
| 1:05-1:15 | Break | |
| 1:15-1:45 | Module 4: App from template | `<initials>-command-center` deployed, LCE-branded |
| 1:45-2:25 | Module 5: Embed | Genie + dashboard live in the app |
| 2:25-2:50 | Module 6 (BONUS): Job | Scheduled refresh job |
| 2:50-3:00 | Demo round + wrap | Share App URL |

---

## Pre-Workshop Checklist

> **Source of truth:** [`dab/README.md`](../dab/README.md) holds the deploy commands and gotchas. This section is everything that must be true **before** you run that runbook.

### T-1 week: features + permissions + deploy

#### Features the admin must enable

| Feature | Why |
|---|---|
| **Databricks Apps** | Hosts the Command Center App |
| **Genie spaces** | Natural-language Q&A pillar |
| **Metric Views** (Unity Catalog) | The spine: governed KPIs defined once, reused by Genie and the dashboard |
| **Foundation Model API + AI Gateway** with `databricks-claude-sonnet-4-6` | Single endpoint for `ai_query()` in the app; confirm attendee group has `CAN_USE` |
| **Lakebase** (Postgres preview) | Write-back persistence (release POs, replies, schedule approvals) |

> **Note on AI Gateway:** the endpoint serves `ai_query()` in the reference app only. The attendee agent (Genie Code) does not require an AI Gateway route; skills run within Genie Code's built-in agent runtime.

#### Skills in Genie Code

Each attendee installs ai-dev-kit skills into their personal Genie Code environment before the workshop.

**How it works:**

1. Attendee opens a notebook in the Databricks workspace.
2. Attendee runs the installer script from ai-dev-kit:
   `https://github.com/databricks-solutions/ai-dev-kit/blob/main/databricks-skills/install_genie_code_skills.py`
3. Skills land in `/Users/<username>/.assistant/skills/` in the workspace file system.
4. Attendee opens Genie Code, starts a **new Agent-mode chat thread**, and verifies skills loaded (try `@databricks-metric-views` or ask "what skills do you have?").

**Caveats (communicate to all attendees before the workshop):**

- Skills only work in **Agent mode**. Standard Genie Code chat does not invoke skills.
- After install, attendees must open a **new chat thread** and may need a hard browser refresh for skills to register.
- `databricks aitools` does NOT support Genie Code. That CLI path is for local IDE setups only and is not used here.
- Skill parity is not 1:1 with local ai-dev-kit; the 6 build steps were chosen to use skills known to work in Genie Code (metric views, genie, AI/BI dashboards, apps, jobs).

**Optional upgrade (facilitator, workspace-wide):** deploy the `mcp-ai-dev-kit` Databricks App (from `databricks-field-eng/india-gcc`). This pushes skills to `Workspace/.assistant/skills/` for all users and serves the tools at `/mcp`, removing the per-attendee notebook install step. Captured here as a facilitator upgrade path; the default workshop flow uses the per-attendee notebook installer.

#### Who needs what permission

**Facilitator (deployer)**
- **Workspace admin:** required to create the Lakebase instance and bind App resources
- Authenticated CLI profile: `databricks auth login --host <url> --profile lce`
- **Fallback if you're not admin:** see [`dab/README.md` section "Lakebase binding fallback"](../dab/README.md#lakebase-binding-fallback); admin pre-creates the instance and you deploy with `lakebase.yml` commented out

**Reference App's service principal**
- `CAN_USE` on the warehouse; `SELECT` on the 8 UC tables; access to the Lakebase instance
- Auto-granted at deploy time via [`dab/resources/app.yml`](../dab/resources/app.yml). The bootstrap step must pre-create the tables before deploy, or bindings fail to validate.

**Attendee group** (e.g. `workshop-attendees`)
- Databricks SQL entitlement; workspace access; serverless jobs entitlement
- `SELECT` on `ioc_sandbox.vibe_workshop.*`; `CAN_USE` on the shared warehouse
- `CAN_VIEW` on the reference Genie space; `CAN_USE` on the FMAPI/AI Gateway endpoint
- `CAN_CREATE` for new Apps in their own scope
- `CAN_MANAGE` or `CAN_EDIT` on Metric Views (to create their own)

The setup job handles UC grants automatically when you deploy with `--var attendee_group=<group>` (default `users`). For warehouse, Genie, and endpoint permissions, paste this into a SQL warehouse query (substitute `<attendee_group>`):

```sql
-- UC grants (also auto-applied by command_center_setup with --var attendee_group=<group>):
GRANT USE CATALOG ON CATALOG ioc_sandbox TO `<attendee_group>`;
GRANT USE SCHEMA ON SCHEMA ioc_sandbox.vibe_workshop TO `<attendee_group>`;
GRANT SELECT ON SCHEMA ioc_sandbox.vibe_workshop TO `<attendee_group>`;
```

Warehouse `CAN_USE`, Genie `CAN_VIEW`, and endpoint `CAN_USE` grants are set via the workspace UI or REST API.

**Each attendee's App service principal** (created in Module 4)
- Same shape as the reference App SP, scoped to attendee's own resources
- The ai-dev-kit apps skill scaffolds the `app.yaml` resources block; attendee runs `apps update --json` then `apps deploy`

#### Other prep

- [ ] Branding assets in `branding/lce/` (logo SVG + brand color hex) already shipped in repo
- [ ] Workspace quotas verified (defaults fit); edge cases in [`dab/README.md` section "Common gotchas"](../dab/README.md#common-deploy-gotchas)
- [ ] **Metric view smoke test:** run `SELECT * FROM ioc_sandbox.vibe_workshop.command_center_metrics LIMIT 5` (must return rows)
- [ ] **Genie smoke test:** ask the reference Genie space one question per pillar; verify answers
- [ ] **App smoke test:** the `command-center-dev` reference app renders with live KPIs and a green wiring banner

---

### Deploy the reference build

Full runbook with explanations: [`dab/README.md`](../dab/README.md). After `databricks auth login --profile lce`, from the repo root:

```bash
# 1. Pre-create catalog/schema + 8 empty UC tables (once per workspace).
#    Required because App resource bindings are validated at deploy time.
#    Note: scripts/bootstrap.py can be copied from the source repo if not yet
#    present in this repo; flag as a follow-up if needed.
python3 scripts/bootstrap.py --profile lce --warehouse-id <id> --catalog ioc_sandbox

# 2. Validate
cd dab && databricks bundle validate -t lce --var warehouse_id=<id>

# 3. Deploy (Lakebase + dashboard + app + job)
databricks bundle deploy -t lce --var warehouse_id=<id>

# 4. Run the setup job (~3-4 min):
#    generate_data (task 1) -> create_metric_view (task 2) -> create_genie_space (task 3)
#    init_lakebase (task 4, parallel with create_metric_view)
databricks bundle run command_center_setup -t lce

# 5. Start the reference app (this IS the command-center-dev template attendees clone in Module 4)
databricks bundle run command_center_app -t lce
```

**Smoke-test the result:**

- [ ] All 5 steps exit clean
- [ ] Metric view returns rows: `SELECT * FROM ioc_sandbox.vibe_workshop.command_center_metrics LIMIT 5`
- [ ] Reference Genie space answers one metric-view question (e.g. "Which store had the highest labor % of sales last week?")
- [ ] Reference dashboard renders 4 widgets with data
- [ ] App wiring banner is **green** with live counts and "Genie: Command Center reference"
- [ ] The `command-center-dev` app renders (this is the template for Module 4)

**What you just deployed:**

| Resource | Notes |
|---|---|
| 8-table dataset in `ioc_sandbox.vibe_workshop` | 60 days anchored to workshop date; `company=lce` brand config |
| Metric view `command_center_metrics` | Store x date grain; 5 measures + 5 dimensions; the spine for all downstream surfaces |
| Lakebase instance `command-center-lakebase` | 3 write-back tables; sequence grants applied |
| Reference Genie space "Command Center reference" | 6 sample questions; example SQLs grounded in the metric view |
| AI/BI dashboard | 4 widgets: labor % of sales; revenue by region; stock health (days of cover); net sentiment timeline |
| Reference App `command-center-<target>` | FastAPI + routers; live KPIs; Lakebase writes; LCE branding |
| `command-center-dev` App | The template attendees clone in Module 4 |

The App reads `/Workspace/Shared/command-center/config.json` (written by the setup job) at startup, so the same `app.yaml` ships dev and prod with no hand-edits.

---

### T-1 day: attendee comms + final warmup

- [ ] Attendee permissions confirmed (everyone can reach the workspace and has the entitlements above)
- [ ] Send attendees the **Lab Companion Guide** and workshop env values: workspace URL, catalog, warehouse name, AI Gateway endpoint, branding folder (`branding/lce/`)
- [ ] Remind attendees to run the ai-dev-kit notebook installer and open a new Agent-mode chat before the session
- [ ] Warm the SQL warehouse by running the reference dashboard once
- [ ] Smoke-test the reference Genie space with 2-3 questions per pillar
- [ ] Confirm `command-center-dev` App is running (attendees reference its URL in Module 4)

---

## Synthetic Data Schema (8 tables: 3 dims + 5 facts)

Materialized in `ioc_sandbox.vibe_workshop` (dev mirror at `jdub_demo.vibe_workshop`). 60 days of history anchored to the workshop date so `current_date()` queries on workshop day return real rows. Every chart and AI insight in the reference design has a backing column or table; nothing is computed on-the-fly via AI calls.

**Dims (3):**
- `dims_stores`: 20 stores at real LCE-presence locations (Detroit, Chicago, Houston, etc.)
- `dims_items`: 50 SKUs (pizza ingredients, beverages, packaging)
- `dims_employees`: approx. 12 per store (cook / cashier / lead / manager mix)

**Facts (5):**
- `facts_sales_daypart`: daypart-grain revenue and forecast (breakfast / lunch / dinner / late)
- `facts_labor_daypart`: daypart x role-grain crew, cost, and forecast
- `facts_sales_inventory_daily`: SKU-grain inventory and per-SKU sales
- `facts_purchase_orders`: pre-staged POs with vendor info
- `facts_customer_feedback`: guest reviews with pre-staged `sentiment_label`, `theme`, and `ai_drafted_reply` columns

**Metric view (the spine):**
The setup job creates `command_center_metrics` over these tables at `store x date` grain. Measures: `revenue`, `labor_cost`, `labor_pct_of_sales`, `days_of_cover`, `sell_through_pct`, `net_sentiment`. The metric view inner-joins `dims_stores`, so fact rows with no matching store are dropped. The `days_of_cover` and `sell_through_pct` measures sum `on_hand_eod` across the selected date window (a snapshot-summed semantic); anticipate Genie questions that span multiple days to reflect this.

See [`data/README.md`](../data/README.md) and [`metric-views/command_center_metrics.yaml`](../metric-views/command_center_metrics.yaml) for column-level details.

---

## Pre-Workshop: Attendee Setup (async, before the session)

Single source of truth: **[Lab Companion Guide section "Pre-Work"](lab-companion-guide.md#pre-work)**. Send that section to attendees 1-3 days out. Stragglers should ping the workshop channel before the session starts.

**Attendee pre-work steps (no local install):**

1. Open the Databricks workspace (URL provided by facilitator).
2. Navigate to **Workspace > ai-dev-kit installer** and run `install_genie_code_skills.py`.
3. Open **Genie Code**, start a new **Agent-mode chat**, and verify skills loaded.
4. Keep that chat open; copy the session-setup prompt from the Lab Companion Guide.

---

## Troubleshooting

Sorted by likelihood. Highest-impact items first.

### High likelihood

| Symptom | Fix |
|---|---|
| **First-time deploy fails:** `SCHEMA_DOES_NOT_EXIST` or `TABLE_OR_VIEW_NOT_FOUND` | Run `scripts/bootstrap.py` **before** `bundle deploy`. App's `uc_securable` bindings are validated at deploy time, so the 8 tables must exist (even empty). |
| **Skills not loading in Genie Code** | Open a **new Agent-mode chat** after running the installer (do not reuse the same thread). Hard-refresh the browser if skills still do not appear. Verify skills landed under `/Users/<username>/.assistant/skills/` in the workspace file browser. Note: `databricks aitools` does NOT support Genie Code and is not used here. |
| **Attendees skip pre-workshop setup** | Send reminder 24h before; reserve 10 min at session start for stragglers (cuts into Module 1). |
| **AI Gateway endpoint not granted to attendees** | Test 1 week before; confirm `CAN_USE` on the endpoint for the attendee group; have a facilitator-owned backup endpoint identified. |

### Medium likelihood

| Symptom | Fix |
|---|---|
| **Metric view DDL syntax error** | The `CREATE OR REPLACE VIEW ... WITH METRICS LANGUAGE YAML` syntax may be runtime-version-dependent. Confirm the DDL against the `databricks-metric-views` skill in the target workspace T-1 week. The T-1-week smoke test (verify the metric view returns rows) catches this before the workshop. |
| **MEASURE() or identifier() over a metric view fails at runtime** | At first deploy, verify that dashboard datasets and Genie example SQLs using `MEASURE(...)` and `identifier(:catalog||'.'||:schema||'.command_center_metrics')` resolve over the metric view. If the runtime rejects those constructs, hardcode the fully-qualified table name as a fallback. |
| **Embed 403s: "Invalid scope" or "PermissionDenied"** on attendee apps | Genie spaces are user-permissioned: use OBO auth (`X-Forwarded-Access-Token` header) instead of the App service principal. Declare `user_api_scopes: [genie, sql, dashboards.genie]` on the App resource, then redeploy and re-consent on first open. Reference pattern: [`dab/src/app/routers/genie.py`](../dab/src/app/routers/genie.py). |
| **Warehouse name lookup fails** on `bundle deploy` | The bundle's `warehouse_id` is a lookup by name (`Serverless Starter Warehouse`); not every workspace has one. Always pass `--var warehouse_id=<id>`. |
| **SQL warehouse 500s** after idle or cold-start | Reference App's `sql_utils.py` retries on `RequestError` and session expiry. Attendees writing their own backend should mirror that pattern. |
| **Facilitator is not workspace admin** (cannot create Lakebase) | Two fallbacks in [`dab/README.md` section "Lakebase binding fallback"](../dab/README.md#lakebase-binding-fallback): admin pre-creates the instance, or comment out `lakebase.yml`. |
| **Lakebase write-back fails** (permission or sequence grants) | Setup job grants `INSERT/SELECT` on tables and `USAGE/SELECT` on SERIAL sequences. If an attendee's App cannot write, fall back to read-only demo mode. |
| **FMAPI endpoint slow or over quota** | Pre-warm the endpoint; have a backup endpoint identified before the workshop. |

### Low likelihood

| Symptom | Fix |
|---|---|
| **Synthetic data has bad joins or null columns** | Reference Genie and dashboard exercise the schema during the T-1-week setup. The metric view inner-joins `dims_stores`, so stores missing from that dim will have no rows; verify the store count matches expectations. |
| **Module overruns** | The `dab/` starter is fully working; attendees customize, not build from scratch. The metric-view and Genie steps (Modules 1-2) are the most likely to take extra time. |
| **SDK version drift** in serverless notebook runtime | Setup notebooks pin `databricks-sdk>=0.40` and include a raw REST fallback (`/api/2.0/database/{instances,credentials}`). |
| **App resource bindings not applied before deploy** | Drill the `apps update --json` before `apps deploy` order (Module 4). The ai-dev-kit apps skill handles this; the reference App in `dab/` shows the working pattern. |

---

## Per-Attendee Asset Naming Convention

All attendee-created assets include their initials to avoid collisions:

| Asset | Naming |
|---|---|
| App name | `<initials>-command-center` |
| Metric view | `<initials>_command_center_metrics` |
| Genie space | `"<initials> Command Center"` |
| Dashboard | `"<initials> Operator Insights"` |
| DAB bundle | `<initials>-command-center` |
| Job name | `<initials>-command-center-refresh` |
| Sandbox schema (optional) | `ioc_sandbox.<initials>_sandbox` (only if attendees write derived tables) |

The shared workshop schema `ioc_sandbox.vibe_workshop` and the shared `command-center-lakebase` are read-write for all attendees (Lakebase) and read-only (UC tables).

---

## Cost Controls & Governance

A 3-hour workshop with approximately 10 attendees typically costs **$50-150 total** across serverless SQL, Apps, Lakebase, and Claude FMAPI calls. Cost overruns come from **assets left running after the workshop**, not from the workshop itself. Three guardrails:

### 1. Tags (cost attribution + cleanup discovery)

The bundle tags all setup-job resources with:

```yaml
tags:
  purpose: workshop
  workshop: genie-code-vibe-command-center
  owner: facilitator
  environment: ${bundle.target}
  cost_center: fe-workshop
```

Swap `cost_center: fe-workshop` for whatever code your account team uses. These tags flow into `system.billing.usage` so finance can attribute DBUs to the workshop. The cleanup script (below) uses the `workshop` tag and naming patterns to find what to delete.

### 2. Budget policy (alert at $100, hard cap at $300)

Set up a workspace-level budget policy before the workshop:

```bash
databricks --profile lce api post /api/2.1/budget-policies --json '{
  "policy_name": "genie-code-vibe-workshop",
  "custom_tags": [{"key": "workshop", "value": "genie-code-vibe-command-center"}],
  "limit_config": {"max_dbu": 300, "alert_thresholds_dbu": [100, 200]}
}'
```

Or set this in the Account Console under **Settings > Compute > Budget policies**. Assign the policy to the attendee group so their workspace activity rolls up to the same cap.

### 3. Auto-stop verification

- **SQL warehouse `serverless`:** confirm auto-stop at or under 10 min idle (default for serverless).
- **Databricks Apps:** auto-suspend after approximately 30 min of no traffic (built-in). Each attendee app is small (roughly $0.04/hr); even forgotten ones cost cents.
- **Lakebase:** **no auto-stop**. The instance bills hourly until deleted. This is the highest cleanup priority.
- **Claude `ai_query()`:** AI Gateway should have rate limits set on the endpoint (Account Console > Serving > endpoint > Rate limits). 10 calls/min per user is a sane workshop cap.

### 4. Apps quota

Default workspace quota is 300 apps. 10 attendees plus facilitator references fits comfortably. Verify before the workshop:

```bash
databricks --profile lce apps list | jq '.apps | length'
```

---

## Cleanup

Run the cleanup script 24-48h after the workshop ends. Without this, the Lakebase instance keeps billing and attendee-created Apps and Genie spaces clutter the workspace.

> **Note:** `scripts/cleanup.py` can be copied from the source repo (`jonathan-whiteley/ucode-vibe-workshop`) if it is not yet present in this repo; flag as a follow-up.

```bash
# 1. DRY RUN: see what would be deleted
python3 scripts/cleanup.py --profile lce --catalog ioc_sandbox

# 2. APPLY: delete everything matching the workshop patterns
python3 scripts/cleanup.py --profile lce --catalog ioc_sandbox \
    --warehouse-id <id> --apply

# 3. (optional) Drop the bundle-owned facilitator resources too
cd dab && databricks bundle destroy -t lce --auto-approve
```

The script sweeps and deletes:

| Item | Match | Notes |
|---|---|---|
| Apps | `*-command-center` / `command-center-*` | Skips reference build with `--keep-reference` |
| Genie spaces | `* Command Center` / `Command Center reference` | Skips `Command Center reference` with `--keep-reference` |
| Dashboards | `* Operator Insights` / `command_center_*` | Skips `command_center_dash` with `--keep-reference` |
| Lakebase instance | `command-center-lakebase` exact match | Skip with `--skip-lakebase` |
| UC schema | `<catalog>.vibe_workshop` (CASCADE) | Drops all 8 tables; needs `--warehouse-id`. Skip with `--skip-schema` |
| Workspace config | `/Workspace/Shared/command-center/` | Removes the per-target config JSON |

The script will not touch the catalog itself or anything outside the workshop's naming patterns.

---

## Companion Documents

| | |
|---|---|
| **Lab Companion Guide** (attendee-facing: setup, prompts, tips) | [`docs/lab-companion-guide.md`](lab-companion-guide.md) |
| **README** (repo overview, quick start, schema) | [`README.md`](../README.md) |
| **Operational runbook** (deploy commands, gotchas, fallbacks) | [`dab/README.md`](../dab/README.md): source of truth for ops |
| **Metric view definition** | [`metric-views/command_center_metrics.yaml`](../metric-views/command_center_metrics.yaml) |
| **Repo** | https://github.com/jonathan-whiteley/genie-code-vibe-workshop |
