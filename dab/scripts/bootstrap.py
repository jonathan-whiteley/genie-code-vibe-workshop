#!/usr/bin/env python3
"""Pre-deploy bootstrap for the Genie Code Vibe workshop bundle.

The App resource block in `resources/app.yml` binds the App's service
principal to 8 specific Unity Catalog tables (uc_securable / TABLE). DAB
validates those bindings AT DEPLOY TIME by looking the tables up: if
they don't exist yet, deploy fails with `SCHEMA_DOES_NOT_EXIST` or
`TABLE_OR_VIEW_NOT_FOUND`. The setup job creates the real tables, but
the setup job is deployed BY the bundle, so the App can't bind on first
deploy of a clean workspace.

This script breaks the chicken-and-egg by pre-creating the catalog/schema
and 8 empty tables via the SQL Statements API. Once tables exist (even
empty), bundle deploy succeeds; the setup job then overwrites them with
synthetic data.

Run once per fresh workspace, then proceed with the normal flow:

    cd dab
    python3 scripts/bootstrap.py --profile e2-demo-west --warehouse-id <id> \
        --catalog jdub_demo_aws --schema vibe_workshop
    databricks bundle deploy -t e2demo --var warehouse_id=<id>
    databricks bundle run command_center_setup -t e2demo
    databricks bundle run command_center_app -t e2demo
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

DDL_PATH = Path(__file__).resolve().parents[2] / "data" / "ddl.sql"


def parse_statements(catalog: str, schema: str) -> list[str]:
    """Read data/ddl.sql, strip USE statements, retarget to <catalog>.<schema>."""
    raw = DDL_PATH.read_text()
    statements: list[str] = [f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}"]
    current: list[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        if s.upper().startswith("USE ") or s.upper().startswith("CREATE SCHEMA"):
            continue
        current.append(line)
        if s.endswith(";"):
            stmt = "\n".join(current).rstrip(";").strip()
            if stmt:
                stmt = stmt.replace(
                    "CREATE OR REPLACE TABLE ",
                    f"CREATE OR REPLACE TABLE {catalog}.{schema}.",
                )
                statements.append(stmt)
            current = []
    return statements


def run_statement(profile: str, warehouse_id: str, statement: str) -> dict:
    """Execute one statement via the SQL Statements API."""
    body = {"statement": statement, "warehouse_id": warehouse_id, "wait_timeout": "30s"}
    result = subprocess.run(
        ["databricks", "--profile", profile, "api", "post",
         "/api/2.0/sql/statements", "--json", json.dumps(body)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return {"state": "FAILED", "error": result.stderr.strip()[:300]}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"state": "FAILED", "error": "could not parse response"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", required=True, help="databricks CLI profile")
    ap.add_argument("--warehouse-id", required=True, help="SQL warehouse to execute DDL on")
    ap.add_argument("--catalog", required=True, help="Unity Catalog catalog")
    ap.add_argument("--schema", default="vibe_workshop", help="UC schema (default: vibe_workshop)")
    args = ap.parse_args()

    statements = parse_statements(args.catalog, args.schema)
    print(f"Bootstrapping {args.catalog}.{args.schema} via {args.profile} (warehouse {args.warehouse_id})")
    print(f"  {len(statements)} statements: 1 CREATE SCHEMA + {len(statements)-1} CREATE TABLE")
    print()

    any_failed = False
    for i, stmt in enumerate(statements, 1):
        # Friendly label
        head = stmt.split("(")[0].strip()
        label = head if i == 1 else head.split(".")[-1]
        result = run_statement(args.profile, args.warehouse_id, stmt)
        state = (result.get("status") or {}).get("state") or result.get("state")
        # Poll if RUNNING/PENDING (rare for empty DDL but safe)
        statement_id = result.get("statement_id")
        deadline = time.time() + 60
        while state in {"PENDING", "RUNNING"} and time.time() < deadline:
            time.sleep(1)
            poll = subprocess.run(
                ["databricks", "--profile", args.profile, "api", "get",
                 f"/api/2.0/sql/statements/{statement_id}"],
                capture_output=True, text=True,
            )
            try:
                pj = json.loads(poll.stdout)
                state = (pj.get("status") or {}).get("state")
            except Exception:
                break
        ok = state == "SUCCEEDED"
        if not ok:
            any_failed = True
            err = (result.get("status") or {}).get("error") or result.get("error") or "(no error)"
        print(f"  [{i}/{len(statements)}] {label[:60]:60s}  {state}")
        if not ok:
            print(f"        {err}")

    if any_failed:
        print("\nbootstrap had failures; resolve before bundle deploy")
        return 1
    print("\nbootstrap done. next:")
    print(f"  databricks bundle deploy -t <target> --var warehouse_id={args.warehouse_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
