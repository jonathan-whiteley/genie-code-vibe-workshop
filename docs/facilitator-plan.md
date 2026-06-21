# Genie Code Workshop: Operator Command Center: Facilitator Plan

**Workshop:** Build an AI-powered Command Center **inside Databricks Genie Code** (metric-view-first, no local install required).
**Audience:** Field Engineers, analysts, or customer engineers (8-15 attendees recommended).
**Duration:** 3 hours.
**End state:** Each attendee has their own deployed Databricks App that surfaces a Genie space and an AI/BI dashboard, both built on a single governed Metric View covering **Sales and Labor** (inventory and feedback raw tables remain in the schema for the app, but are not in the metric view). Everything is packaged as a Databricks Asset Bundle.

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
| pre (async) | Setup | Repo cloned as Git folder; `notebooks/00-setup` notebook ran (skills installed + app deployed); new chat open |
| 0:00-0:10 | Welcome + demo | See finished app; get env values + session-setup prompt |
| 0:10-0:25 | Module 1: Metric View | Governed KPIs defined over landed tables |
| 0:25-0:45 | Module 2: Genie Space | Natural-language Q&A on the metric view |
| 0:45-1:05 | Module 3: AI/BI Dashboard | Insight charts across every measure and dimension (no KPI tiles) |
| 1:05-1:15 | Break | |
| 1:15-1:45 | Module 4: App polish | `<initials>-command-center` already deployed; verify it loads + optional branding tweaks |
| 1:45-2:10 | Module 5: Embed | Genie + dashboard live in the app |
| 2:10-2:35 | Module 6: Live AI | (A) `ai_query()` briefing function for the Genie space; (B) Company News feed in the app via the `web_search_mcp` MCP server |
| 2:35-2:50 | Module 7 (BONUS): Job | Scheduled refresh job |
| 2:50-3:00 | Demo round + wrap | Share App URL |

---

## Pre-Workshop Checklist

> **Source of truth:** [`dab/README.md`](../dab/README.md) holds the deploy commands and gotchas. This section is everything that must be true **before** you run that pattern.

### T-1 week: features + permissions + deploy

#### Features the admin must enable

| Feature | Why |
|---|---|
| **Databricks Apps** | Hosts the Command Center App |
| **Genie spaces** | Natural-language Q&A pillar |
| **Metric Views** (Unity Catalog) | The spine: governed KPIs defined once, reused by Genie and the dashboard |
| **Foundation Model API + AI Gateway** with `databricks-claude-sonnet-4-6` | One endpoint, two uses: it backs the Genie Code agent, and in Module 6 attendees call `ai_query()` from a Genie-registered UC function. Because Genie runs queries as the asking **user**, the **attendee group needs `CAN_QUERY`** on this endpoint (Serving → endpoint → Permissions) |
| **Lakebase** (Postgres preview) | Write-back persistence (release POs, replies, schedule approvals) |
| **AI/BI dashboard embedding allowlist** | Module 5 embeds the dashboard as an iframe in each attendee's app. Without this, every attendee hits a "refused to connect" / approved-domains error |

> **Note on `ai_query()` permissions (Module 6):** in Module 6 each attendee creates a UC function that wraps `ai_query()` and registers it with their Genie space. Genie executes that function as the **asking user** (and the app's Ask Genie panel forwards the user's token via OBO), so the call inherits the attendee's permissions, not the app service principal's. This is why the approach is a Genie function and not an app feature: it sidesteps having to grant each `<initials>-command-center` app SP query access. The one grant you do need is **`CAN_QUERY` on `databricks-claude-sonnet-4-6` for the attendee group** (see checklist). Genie Code itself does not require an AI Gateway route; its skills run within Genie Code's built-in agent runtime.

> **Note on dashboard embedding (admin-only, do once):** the approved-domains allowlist is a **workspace-admin setting** attendees cannot change. Set it once for the whole workshop: **Settings → Security → External access → Embed dashboards → Allow approved domains → Manage**, add **`*.databricksapps.com`**, Save. The single `*` matches any subdomain depth (CSP grammar), so this one entry covers every attendee's `<initials>-command-center-<id>.<cloud>.databricksapps.com` app host: no per-attendee step. Takes effect within ~2 minutes (pod cache); a hard refresh / incognito tab picks it up. This is the only thing attendees need from the admin in Module 5: they just use the dashboard's `/embed/` URL. Internal refs: `go/iframe`, `go/embedded-analytics`.

#### Attendee pre-req: single setup notebook

Each attendee runs one notebook before the workshop. It handles both skills installation and app creation; there is no separate installer step.

**How it works:**

1. Attendee clones the workshop repo as a **Workspace Git folder** (Workspace > Create > Git folder, paste the repo URL).
2. Attendee opens `notebooks/00-setup`, sets their initials widget, and clicks **Run All**.
3. The notebook orchestrates two helpers:
   - `notebooks/utils/install_genie_code_skills.py`: installs ai-dev-kit skills into `/Users/<username>/.assistant/skills/` (delegates to the official ai-dev-kit installer).
   - `notebooks/utils/clone_app.py`: copies the `command-center-dev` template, creates the attendee's `<initials>-command-center` app, binds its service principal to the warehouse, catalog/schema (SELECT ON SCHEMA covers all 8 tables and the metric view), and Lakebase, sets OBO scopes (genie, sql, dashboards.genie), and deploys.
4. Attendee opens Genie Code, starts a **new chat thread**, and verifies skills loaded.

The attendee's app is fully created, permissioned, and deployed BEFORE the live session. Module 4 in the workshop is now app verification and optional polish, not app creation.

**Caveats (communicate to all attendees before the workshop):**

- Open a **new chat thread** after installing skills so Genie Code loads them.
- After setup, attendees must open a **new chat thread** and may need a hard browser refresh for skills to register.
- `databricks aitools` does NOT support Genie Code. That CLI path is for local IDE setups only and is not used here.
- Skill parity is not 1:1 with local ai-dev-kit; the 6 build steps were chosen to use skills known to work in Genie Code (metric views, genie, AI/BI dashboards, apps, jobs).
- **The `command-center-dev` template app must be deployed before attendees run setup** (it is the source `clone_app.py` copies from). Verify it is running as part of your T-1-week checklist.

**Optional upgrade (facilitator, workspace-wide):** deploy the `mcp-ai-dev-kit` Databricks App (from `databricks-field-eng/india-gcc`). This pushes skills to `Workspace/.assistant/skills/` for all users and serves the tools at `/mcp`. Captured here as a facilitator upgrade path; the default workshop flow uses the per-attendee setup notebook.

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
- `CAN_CREATE` for new Apps in their own scope; permission to create Workspace Git folders
- `CAN_MANAGE` or `CAN_EDIT` on Metric Views (to create their own)
- `CREATE` on `ioc_sandbox.vibe_workshop` so attendees can create their metric view in Module 1 (alternatively, attendees create the view in a personal sandbox schema such as `ioc_sandbox.<initials>_sandbox`)
- `CAN_CONNECT` on the shared Lakebase instance (the setup notebook binds attendee apps; the instance itself must be accessible)

The setup job handles UC grants automatically when you deploy with `--var attendee_group=<group>` (default `users`). For warehouse, Genie, and endpoint permissions, paste this into a SQL warehouse query (substitute `<attendee_group>`):

```sql
-- UC grants (also auto-applied by command_center_setup with --var attendee_group=<group>):
GRANT USE CATALOG ON CATALOG ioc_sandbox TO `<attendee_group>`;
GRANT USE SCHEMA ON SCHEMA ioc_sandbox.vibe_workshop TO `<attendee_group>`;
GRANT SELECT ON SCHEMA ioc_sandbox.vibe_workshop TO `<attendee_group>`;
GRANT CREATE ON SCHEMA ioc_sandbox.vibe_workshop TO `<attendee_group>`;
```

Warehouse `CAN_USE`, Genie `CAN_VIEW`, and endpoint `CAN_USE` grants are set via the workspace UI or REST API.

**Each attendee's App service principal** (created by `notebooks/00-setup` during pre-req)
- Same shape as the reference App SP, scoped to attendee's own resources
- `clone_app.py` binds the SP via app resources and runs GRANT USE CATALOG / USE SCHEMA / SELECT ON SCHEMA automatically
- If the attendee group lacks grant authority on the shared facilitator-owned catalog, `clone_app.py` prints the exact GRANT statements with the SP id; the facilitator pastes them into a SQL warehouse as catalog owner
- The SELECT ON SCHEMA grant covers all 8 tables and the `command_center_metrics` metric view in a single statement
- Attendees need permission to create Workspace Git folders and Databricks Apps in their own scope

#### Other prep

- [ ] Branding assets in `branding/lce/` (logo SVG + brand color hex) already shipped in repo
- [ ] Workspace quotas verified (defaults fit); edge cases in [`dab/README.md` section "Common gotchas"](../dab/README.md#common-deploy-gotchas)
- [ ] **Metric view smoke test:** run `SELECT * FROM ioc_sandbox.vibe_workshop.command_center_metrics LIMIT 5` (must return rows)
- [ ] **Genie smoke test:** ask the reference Genie space 2-3 revenue and labor questions; verify answers
- [ ] **App smoke test:** the `command-center-dev` reference app renders with live KPIs and a green wiring banner

---

### Deploy the reference build

Full pattern with explanations: [`dab/README.md`](../dab/README.md). After `databricks auth login --profile lce`, from the repo root:

```bash
# 1. Pre-create catalog/schema + 8 empty UC tables (once per workspace).
#    Required because App resource bindings are validated at deploy time.
cd dab
python3 scripts/bootstrap.py --profile lce --warehouse-id <id> --catalog ioc_sandbox

# 2. Validate (already in dab/)
databricks bundle validate -t lce --var warehouse_id=<id>

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
- [ ] Reference Genie space answers one metric-view question (e.g. "Which stores are below their revenue forecast this week?")
- [ ] Reference dashboard renders with data (KPI counters + revenue and labor charts)
- [ ] App wiring banner is **green** with live counts and "Genie: Command Center reference"
- [ ] The `command-center-dev` app renders (this is the template for Module 4)

**What you just deployed:**

| Resource | Notes |
|---|---|
| 8-table dataset in `ioc_sandbox.vibe_workshop` | 60 days anchored to workshop date; `company=lce` brand config |
| Metric view `command_center_metrics` | Store x date grain; sales + labor only (6 measures + 5 dimensions); the spine for all downstream surfaces |
| Lakebase instance `command-center-lakebase` | 3 write-back tables; sequence grants applied |
| Reference Genie space "Command Center reference" | 6 sample questions grounded in revenue and labor measures |
| AI/BI dashboard | KPI counters (revenue, labor % of sales, revenue vs forecast, traffic) + revenue and labor charts |
| Reference App `command-center-<target>` | FastAPI + routers; live KPIs; Lakebase writes; LCE branding |
| `command-center-dev` App | The template `clone_app.py` copies during `notebooks/00-setup` (must be deployed before attendees run pre-req) |

The App reads `/Workspace/Shared/command-center/config.json` (written by the setup job) at startup, so the same `app.yaml` ships dev and prod with no hand-edits.

---

### T-1 day: attendee comms + final warmup

- [ ] Attendee permissions confirmed (everyone can reach the workspace, create Git folders, and has the entitlements above)
- [ ] `command-center-dev` template app is deployed and running (attendees' `notebooks/00-setup` notebook copies from it)
- [ ] Dashboard embedding allowlist set: `*.databricksapps.com` added under Settings → Security → External access → Embed dashboards (admin-only; without it Module 5 iframes fail for everyone)
- [ ] **`ai_query()` endpoint grant for Module 6:** the attendee group has `CAN_QUERY` on `databricks-claude-sonnet-4-6` (Serving → endpoint → Permissions). Module 6's briefing function runs `ai_query()` as the asking user via Genie, so without this the briefing returns a permission error. Genie Code cannot grant this
- [ ] **MCP web search for Module 6 (Feature B):** the `web_search_mcp` UC connection (managed MCP server) exists in the workshop workspace, and each attendee app service principal has access to it (admin-configured; the app calls the MCP server as its SP, not the user). Note the URL is workspace-specific: `https://<workspace-host>/api/2.0/mcp/external/web_search_mcp`. Pattern + gotchas: [`docs/patterns/mcp-company-news-pattern.md`](patterns/mcp-company-news-pattern.md)
- [ ] Send attendees the **Lab Companion Guide** and workshop env values: workspace URL, catalog, warehouse name, AI Gateway endpoint, branding folder (`branding/lce/`)
- [ ] Remind attendees to clone the repo as a Git folder, run `notebooks/00-setup`, and open a new chat before the session
- [ ] Warm the SQL warehouse by running the reference dashboard once
- [ ] Smoke-test the reference Genie space with 2-3 revenue and labor questions
- [ ] **Pre-test the dashboard iframe embed in a company-managed-laptop browser profile** (Chrome/Edge, normal window). If MDM hard-blocks third-party cookies with no user override, decide the fallback now (open `/embed/` in its own tab from a tile, or screenshot) rather than discovering it live: see the troubleshooting table row on the approved-domains/cookie error
- [ ] Confirm at least one test-attendee run of `notebooks/00-setup` completed successfully (app deployed, wiring green)

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
The setup job creates `command_center_metrics` over `facts_sales_daypart` and `facts_labor_daypart` at `store x date` grain. Each table is pre-aggregated to one row per store per date in its own subquery before joining, to avoid fan-out. Measures: `revenue`, `forecast_revenue`, `traffic`, `labor_cost`, `forecast_labor_cost`, `labor_pct_of_sales`. Dimensions: `date`, `store_id`, `store_name`, `region`, `day_of_week`. The metric view inner-joins `dims_stores`, so fact rows with no matching store are dropped. Inventory and feedback measures were dropped from the metric view for reliability; the raw source tables still exist in the schema for the reference app.

See [`data/README.md`](../data/README.md) and [`data/metric-views/command_center_metrics.yaml`](../data/metric-views/command_center_metrics.yaml) for column-level details.

---

## Pre-Workshop: Attendee Setup (async, before the session)

Single source of truth: **[Lab Companion Guide section "Pre-Work"](lab-companion-guide.md#pre-work)**. Send that section to attendees 1-3 days out. Stragglers should ping the workshop channel before the session starts.

**Attendee pre-work steps (no local install):**

1. Open the Databricks workspace (URL provided by facilitator).
2. Clone the workshop repo as a **Workspace Git folder** (Workspace > Create > Git folder, paste the repo URL).
3. Open `notebooks/00-setup`, set the initials widget, and click **Run All**. This single notebook installs the ai-dev-kit skills into Genie Code AND creates, permissions, and deploys the attendee's `<initials>-command-center` app. The app is fully live before the session starts.
4. The hands-on lab prompts are in `notebooks/01-workshop-prompts` (identical to the Lab Companion Guide; attendees can follow either).
5. Open **Genie Code**, start a **new chat**, and verify skills loaded.
6. Keep that chat open; copy the session-setup prompt from the Lab Companion Guide.

**Facilitator prerequisite:** the `command-center-dev` template app must be deployed and running before any attendee runs `notebooks/00-setup`. The `clone_app.py` helper copies from it.

---

## Troubleshooting

Sorted by likelihood. Highest-impact items first.

### High likelihood

| Symptom | Fix |
|---|---|
| **First-time deploy fails:** `SCHEMA_DOES_NOT_EXIST` or `TABLE_OR_VIEW_NOT_FOUND` | Run `dab/scripts/bootstrap.py` (from repo root, or `scripts/bootstrap.py` from `dab/`) **before** `bundle deploy`. App's `uc_securable` bindings are validated at deploy time, so the 8 tables must exist (even empty). |
| **Skills not loading in Genie Code** | Open a **new chat** after running the installer (do not reuse the same thread). Hard-refresh the browser if skills still do not appear. Verify skills landed under `/Users/<username>/.assistant/skills/` in the workspace file browser. Note: `databricks aitools` does NOT support Genie Code and is not used here. |
| **Attendees skip pre-workshop setup** | Send reminder 24h before; reserve 10 min at session start for stragglers (cuts into Module 1). |
| **Attendee app SP lacks catalog access** | `clone_app.py` binds the SP via app resources and runs GRANT USE CATALOG / USE SCHEMA / SELECT ON SCHEMA automatically. If the attendee group lacks grant authority on the shared facilitator-owned catalog, `clone_app.py` prints the exact GRANT statements with the SP id; the facilitator pastes them into a SQL warehouse as catalog owner. The SELECT ON SCHEMA grant covers all 8 tables AND the `command_center_metrics` metric view in a single statement. |
| **`notebooks/00-setup` fails: `command-center-dev` not found** | The template app must be deployed before attendees run setup. Verify `command-center-dev` is running (T-1-week smoke test) and that attendees have workspace access to its source path. |
| **AI Gateway endpoint not granted to attendees** | Test 1 week before; confirm `CAN_USE` on the endpoint for the attendee group; have a facilitator-owned backup endpoint identified. |

### Medium likelihood

| Symptom | Fix |
|---|---|
| **Metric view DDL syntax error** | The `CREATE OR REPLACE VIEW ... WITH METRICS LANGUAGE YAML` syntax may be runtime-version-dependent. Confirm the DDL against the `databricks-metric-views` skill in the target workspace T-1 week. The T-1-week smoke test (verify the metric view returns rows) catches this before the workshop. |
| **MEASURE() or identifier() over a metric view fails at runtime** | At first deploy, verify that dashboard datasets and Genie example SQLs using `MEASURE(...)` and `identifier(:catalog||'.'||:schema||'.command_center_metrics')` resolve over the metric view. If the runtime rejects those constructs, hardcode the fully-qualified table name as a fallback. |
| **Module 2: sample questions won't add / `manage_genie` not in the toolset** | The genie tool isn't always available to Genie Code; fall back to the REST shape in [`docs/patterns/genie-space-pattern.md`](patterns/genie-space-pattern.md). Only `PATCH /api/2.0/genie/spaces/{id}` works (not PUT/import/export), `serialized_space` is a `json.dumps` string with `version`/`config.sample_questions`/`data_sources.tables`, and each question is `{"id": uuid4().hex, "question": [text]}`. |
| **Embed 403s: "Invalid scope" or "PermissionDenied"** on attendee apps | Genie spaces are user-permissioned: use OBO auth (`X-Forwarded-Access-Token` header) instead of the App service principal. Declare `user_api_scopes: [genie, sql, dashboards.genie]` on the App resource, then redeploy and re-consent on first open. Reference pattern: [`dab/src/app/routers/genie.py`](../dab/src/app/routers/genie.py). |
| **Dashboard iframe blank / "refused to connect" / approved-domains error** even though the allowlist is set | Basic dashboard embedding rides the viewer's Databricks **session cookie**, which the browser treats as a **third-party cookie** relative to the `*.databricksapps.com` app domain. Most common triggers, in order: (1) **Incognito / InPrivate window** blocks third-party cookies by default: use a normal window; (2) **managed-laptop MDM policy** (`BlockThirdPartyCookies`) blocks them even in a normal window: add a site exception for `[*.]databricks.com` (Chrome: Settings → Privacy → Cookies → "Sites that can always use cookies"; Edge: same, or `CookiesAllowedForUrls` policy); (3) app opened **inside the workspace preview pane** (nested iframe): open the top-level `…databricksapps.com` URL. **On company-managed laptops, pre-test the embed in one attendee's actual browser/device profile during the T-1-week smoke test** — if MDM hard-blocks third-party cookies with no user override, fall back to opening the dashboard's `/embed/` URL in its own browser tab (linked from a tile) instead of inline, or screenshot the dashboard for the demo. |
| **Module 6 briefing fails: "PermissionDenied" / "does not have permission to query endpoint"** | The Genie-registered briefing function runs `ai_query()` as the **asking user** (Genie is user-permissioned; the app's Ask Genie panel forwards the user token via OBO). Grant the **attendee group `CAN_QUERY`** on `databricks-claude-sonnet-4-6` (Serving → endpoint → Permissions). Set this before the session: see the pre-req checklist. Genie Code cannot grant it. |
| **Module 6 function not invoked / Genie answers from tables instead** | Genie calls a registered function only when its purpose is clear. Make sure the UC function has a descriptive `COMMENT`, and that it was actually added to the space's functions (not just created in UC). The Module 6 follow-up adds a "Give me today's store briefing" sample question that reliably triggers it. |
| **Module 6 Feature B (Company News) 403s or returns empty** | The app must call `web_search_mcp` as its **service principal** (`lib/deps.py` `workspace_client`); the forwarded user token lacks MCP scope and 403s. Confirm the app SP has admin-granted access to the connection. Other documented traps (router-vs-inline, `:param` regex on URLs, markdown fences in `ai_query` output) and the working code are in [`docs/patterns/mcp-company-news-pattern.md`](patterns/mcp-company-news-pattern.md). |
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
| **App resource bindings not applied before deploy** | `clone_app.py` (run during `notebooks/00-setup`) handles `apps update --json` before `apps deploy` automatically. If an attendee re-deploys manually during Module 4 polish, remind them to run `apps update --json` first. The reference App in `dab/` shows the working pattern. |

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

```bash
# 1. DRY RUN: see what would be deleted
cd dab
python3 scripts/cleanup.py --profile lce --catalog ioc_sandbox

# 2. APPLY: delete everything matching the workshop patterns
python3 scripts/cleanup.py --profile lce --catalog ioc_sandbox \
    --warehouse-id <id> --apply

# 3. (optional) Drop the bundle-owned facilitator resources too
databricks bundle destroy -t lce --auto-approve
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
| **Operational pattern** (deploy commands, gotchas, fallbacks) | [`dab/README.md`](../dab/README.md): source of truth for ops |
| **Metric view definition** | [`data/metric-views/command_center_metrics.yaml`](../data/metric-views/command_center_metrics.yaml) |
| **Repo** | https://github.com/jonathan-whiteley/genie-code-vibe-workshop |
