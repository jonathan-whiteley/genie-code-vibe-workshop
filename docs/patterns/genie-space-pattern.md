# Creating a Genie Space: Sample Questions and Registering an ai_query Function

Module 2 creates a Genie space on the metric view and seeds it with sample questions. If the `manage_genie` tool (ai-dev-kit genie skill) is available, use it. If it is not, drive the Genie REST API directly: the endpoint and payload below were found by trial and error and are not in the public docs, so this pattern saves you from rediscovering them.

---

## Key Gotchas & Fixes

### 1. `manage_genie` may not be in the toolset

The genie skill documents `manage_genie` as the primary tool for creating and updating spaces with sample questions, but it is not always available at runtime. If it is missing, do not give up and do not hand-edit in the UI: drive the REST API directly with the shapes below.

### 2. Only `PATCH` works for updates

These look right but are dead ends (confirmed non-working): `GET /spaces/{id}/export`, `GET /spaces/{id}/config`, `PUT /spaces/{id}`, `POST /spaces/{id}/import`. `PUT` and `POST /import` do not exist.

The one endpoint that updates a space (including adding sample questions) is:

```
PATCH /api/2.0/genie/spaces/{space_id}
```

### 3. `serialized_space` is a JSON-encoded STRING with a specific structure

The PATCH body is `{"serialized_space": "<json string>"}`. The value is `json.dumps(...)` of this structure (not a nested object, and not just the questions):

```json
{
  "version": 2,
  "config": {
    "sample_questions": [
      {"id": "<32-char-hex>", "question": ["the question text"]}
    ]
  },
  "data_sources": {
    "tables": [{"identifier": "catalog.schema.view"}]
  }
}
```

Send the **complete** structure: `sample_questions` live under `config`, and you must include `data_sources.tables` so the PATCH does not drop the space's data sources. List **every** source the space should reach: the metric view AND the raw tables (the metric view answers governed KPIs; the raw tables answer SKU / inventory, employee, feedback, and daypart-level questions the metric view does not expose). Add a `config` instruction telling Genie to prefer the metric view for KPIs and the raw tables for detail.

### 4. The sample-question object shape is strict

Each question is an OBJECT, not a string:

- **`id` is required**: a 32-character lowercase hex UUID with **no dashes** (`uuid.uuid4().hex`, not `str(uuid.uuid4())`).
- **`question` is an array of strings**, not a plain string.
- A plain string (or a plain string array for `sample_questions`) is rejected: each element must be an object.
- Field names that were tried and rejected: `display_string`, `content`, `text`, `display_name`.

### 5. Do not run Genie queries or benchmarks from a notebook: test in the UI

Two limits make programmatic Genie testing impractical, so leave running to the Genie UI:

- The Genie **Conversation API is rate-limited to about 5 queries per minute**. Any notebook- or agent-driven run (auto-testing sample questions, running a benchmark) queues or 429s.
- Writing a `benchmarks` block into `serialized_space` is separately **blocked by the workspace safety layer**: it reads as a potentially destructive write (the same guard that blocks a merge-overwrite of an existing space).

So generate the sample and benchmark questions and add them to the space, but **do not auto-run any of them** from a notebook. Run the benchmark and spot-check answers in the Genie UI.

---

## Reference: add sample questions via REST (Python, verified)

```python
import json
import uuid
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
space_id = "<your space id>"
view = "ioc_sandbox.vibe_workshop.<initials>_command_center_metrics"

questions = [
    "Which 5 stores had the highest labor % of sales last week?",
    "How has revenue trended over the last 30 days?",
]

# Each question is an object: 32-char dashless hex id, and the text as an ARRAY.
sample_questions = [{"id": uuid.uuid4().hex, "question": [q]} for q in questions]

w.api_client.do(
    "PATCH",
    f"/api/2.0/genie/spaces/{space_id}",
    body={
        "serialized_space": json.dumps({
            "version": 2,
            "config": {"sample_questions": sample_questions},
            "data_sources": {"tables": [{"identifier": view}]},
        })
    },
)
```

---

## Registering an `ai_query` function (the briefing)

Module 6 registers a UC function (the store briefing) with the Genie space. Genie calls every registered function as a **table-valued function**: it generates `SELECT * FROM func()`. That one fact drives all of the gotchas below, in build order.

### 1. Return a TABLE, not a scalar

Because Genie calls `SELECT * FROM func()`, a `RETURNS STRING` scalar fails immediately with `NOT_A_TABLE_FUNCTION`. Define it as `RETURNS TABLE (briefing STRING)`. There is no setting that changes how Genie calls functions.

### 2. No CTEs in a `RETURNS TABLE` body on Serverless

`WITH today AS (...), yesterday AS (...)` in the RETURN body throws a parse error on Serverless (the identical CTEs are fine in a scalar body). Rewrite with inline subqueries: same result, no `WITH`.

### 3. `$` in SQL string literals is corrupted by `editAsset`

Dollar signs in `CONCAT` literals (for example `'revenue=$'`) are silently dropped when the DDL is applied as an `editAsset` patch. Use `chr(36)` in the SQL, or run the DDL via `executeCode` directly. Either survives the round-trip. (See also `app-editing-pattern.md`: prefer `open()` / direct execution over `editAsset` for anything fiddly.)

### 4. Register via a `sql_example`, not `serialized_space` `sql_functions`

Adding the function under `instructions.sql_functions` in a `serialized_space` PATCH "succeeds" at the API, but Genie stores it as a CERTIFIED_ANSWER whose question and SQL are both the bare function name. When triggered, Genie runs `SELECT * FROM func` (no parentheses), gets `TABLE_OR_VIEW_NOT_FOUND`, and fails.

The fix is a **`sql_example` instruction** (via `addInstructionsToSpace`) that maps a natural-language question to `SELECT * FROM <cat>.<sch>.<func>()`. That is what makes Genie call it cleanly.

If you ever do use `sql_functions`: the per-entry field is `identifier` (like tables and metric views in `data_sources`), not `function_name` (rejected: "Unknown field"), and it lives under `instructions`, not `config` (rejected: "Unknown field 'functions'"). But the `sql_example` path is the one that works.

### 5. TVF output renders as a data table, not prose

The attachment type is `query`, not `text`, so Genie shows the briefing as a collapsible data-table widget under the SQL box: the text is in the row, but it does not read like a conversational answer. The `sql_example` question mapping is what makes Genie pick it up and present it as the answer.

### Working recipe (end to end)

1. Create the function as `RETURNS TABLE (briefing STRING)`, body using inline subqueries (no CTEs), `chr(36)` for any `$`; run the DDL via `executeCode`, not `editAsset`.
2. Register it in the space via `addInstructionsToSpace` as a `sql_example` mapping the question to `SELECT * FROM <cat>.<sch>.<func>()`.
3. Optionally add a `sample_question` so it appears as a starter chip in the UI.

---

## From-Scratch Checklist

1. Prefer the genie skill / `manage_genie` if it is present.
2. If not, update the space via `PATCH /api/2.0/genie/spaces/{space_id}` (not `PUT`, `import`, `export`, or `config`).
3. Build the body as `{"serialized_space": json.dumps({...})}` with `version`, `config.sample_questions`, and `data_sources.tables` (include the metric view identifier).
4. Build each sample question as `{"id": uuid.uuid4().hex, "question": [text]}`: 32-char dashless hex id, question as an array of strings.
5. `GET /api/2.0/genie/spaces/{space_id}` to confirm the questions and data source registered.
6. Generate the sample and benchmark questions and add them to the space, but do NOT auto-run them from a notebook: the Genie API is ~5 QPM and a programmatic `benchmarks` write is safety-blocked. Run and test in the Genie UI.
7. For a function (the briefing): define it `RETURNS TABLE` (Genie calls `SELECT * FROM func()`), use inline subqueries not CTEs, `chr(36)` for any `$`, and create it via `executeCode`.
8. Register the function with a `sql_example` instruction (`addInstructionsToSpace`) mapping the question to `SELECT * FROM <cat>.<sch>.<func>()`, NOT via `serialized_space` `sql_functions`.
