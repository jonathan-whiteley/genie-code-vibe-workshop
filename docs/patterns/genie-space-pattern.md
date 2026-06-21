# Creating a Genie Space and Adding Sample Questions

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

Send the **complete** structure: `sample_questions` live under `config`, and you must include `data_sources.tables` (the metric view identifier) so the PATCH does not drop the space's data source.

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

## From-Scratch Checklist

1. Prefer the genie skill / `manage_genie` if it is present.
2. If not, update the space via `PATCH /api/2.0/genie/spaces/{space_id}` (not `PUT`, `import`, `export`, or `config`).
3. Build the body as `{"serialized_space": json.dumps({...})}` with `version`, `config.sample_questions`, and `data_sources.tables` (include the metric view identifier).
4. Build each sample question as `{"id": uuid.uuid4().hex, "question": [text]}`: 32-char dashless hex id, question as an array of strings.
5. `GET /api/2.0/genie/spaces/{space_id}` to confirm the questions and data source registered.
6. Generate the sample and benchmark questions and add them to the space, but do NOT auto-run them from a notebook: the Genie API is ~5 QPM and a programmatic `benchmarks` write is safety-blocked. Run and test in the Genie UI.
