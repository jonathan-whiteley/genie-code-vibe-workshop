#!/usr/bin/env python3
"""Post-workshop cleanup for the Genie Code Vibe workshop.

`databricks bundle destroy` only drops the bundle-owned resources
(reference App, dashboard, job); it does NOT drop:
  - The Lakebase instance
  - The UC catalog/schema + tables
  - Attendee-built Apps, Genie spaces, dashboards (those weren't
    deployed by this bundle)

This script sweeps the workspace for everything matching the workshop's
naming pattern + tags, then deletes it. Runs in --dry-run by default;
pass --apply to actually destroy.

Typical workshop wind-down (24-48h after the workshop ends):

    # 1. See what would be deleted
    python3 dab/scripts/cleanup.py --profile lce --catalog ioc_sandbox

    # 2. Actually delete
    python3 dab/scripts/cleanup.py --profile lce --catalog ioc_sandbox --apply

    # 3. (optional) Drop the bundle-owned resources too
    databricks bundle destroy -t lce --auto-approve

What it cleans up (anything matching the patterns below):
  - Apps named `*-command-center` or `command-center-*`
  - Genie spaces titled `* Command Center` or "Command Center reference"
  - Dashboards titled `* Operator Insights` or `command_center_*`
  - The Lakebase instance `command-center-lakebase`
  - The UC schema `<catalog>.vibe_workshop` (CASCADE)
  - The workspace config file `/Workspace/Shared/command-center/`

It will NOT touch:
  - The catalog itself (only the workshop schema inside it)
  - Apps / Genie / dashboards that don't match the naming patterns
  - Anything outside `vibe_workshop` schema
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Any


def run(cmd: list[str], *, capture: bool = True) -> str:
    res = subprocess.run(cmd, capture_output=capture, text=True)
    if res.returncode != 0:
        sys.stderr.write(f"$ {' '.join(cmd)}\n{res.stderr}\n")
        raise SystemExit(res.returncode)
    return res.stdout


def api(profile: str, method: str, path: str, body: dict | None = None) -> dict:
    cmd = ["databricks", "--profile", profile, "api", method.lower(), path]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    out = run(cmd).strip()
    if not out:
        return {}
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"_raw": out}


def list_apps(profile: str) -> list[dict]:
    resp = api(profile, "GET", "/api/2.0/apps")
    return resp.get("apps") or []


def list_genie_spaces(profile: str) -> list[dict]:
    resp = api(profile, "GET", "/api/2.0/genie/spaces")
    return resp.get("spaces") or []


def list_dashboards(profile: str) -> list[dict]:
    out: list[dict] = []
    page: str | None = None
    while True:
        path = "/api/2.0/lakeview/dashboards"
        if page:
            path += f"?page_token={page}"
        resp = api(profile, "GET", path)
        out.extend(resp.get("dashboards") or [])
        page = resp.get("next_page_token")
        if not page:
            break
    return out


def drop_schema(profile: str, warehouse_id: str, catalog: str, schema: str) -> None:
    sql = f"DROP SCHEMA IF EXISTS {catalog}.{schema} CASCADE"
    body = {"statement": sql, "warehouse_id": warehouse_id, "wait_timeout": "30s"}
    api(profile, "POST", "/api/2.0/sql/statements", body)


APP_PAT = re.compile(r"(.+-command-center|command-center-.+)$")
GENIE_PAT = re.compile(r"(.+ Command Center|Command Center reference)$")
DASH_PAT = re.compile(r"(.+ Operator Insights|command_center_.+)$")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", required=True, help="Databricks CLI profile (e.g. lce)")
    ap.add_argument("--catalog", required=True, help="UC catalog containing the workshop schema")
    ap.add_argument("--schema", default="vibe_workshop", help="UC schema to drop (default: vibe_workshop)")
    ap.add_argument("--warehouse-id", help="SQL warehouse ID (required when --apply drops the schema)")
    ap.add_argument("--lakebase-instance", default="command-center-lakebase", help="Lakebase instance name to delete")
    ap.add_argument("--apply", action="store_true", help="Actually delete. Without this flag, only prints what would be deleted.")
    ap.add_argument("--skip-lakebase", action="store_true", help="Don't touch the Lakebase instance")
    ap.add_argument("--skip-schema", action="store_true", help="Don't drop the UC schema")
    ap.add_argument("--keep-reference", action="store_true", help="Don't delete the facilitator's reference build (Command Center reference / command-center-* / command_center_dash)")
    args = ap.parse_args()

    profile = args.profile
    apply = args.apply
    mode = "APPLY" if apply else "DRY RUN"
    print(f"=== Workshop cleanup [{mode}] · profile={profile} catalog={args.catalog} ===\n")

    if args.keep_reference:
        reference_app = {"command-center-lce", "command-center-dev", "command-center-azure", "command-center-e2demo"}
        reference_genie = {"Command Center reference"}
        reference_dash = {"command_center_dash"}
    else:
        reference_app = reference_genie = reference_dash = set()

    # 1) Apps
    print("APPS")
    apps = list_apps(profile)
    app_kill: list[str] = []
    for a in apps:
        name = a.get("name", "")
        if APP_PAT.match(name) and name not in reference_app:
            app_kill.append(name)
    for name in app_kill:
        print(f"  [delete] {name}")
        if apply:
            api(profile, "DELETE", f"/api/2.0/apps/{name}")
    if not app_kill:
        print("  (none match)")
    print()

    # 2) Genie spaces
    print("GENIE SPACES")
    spaces = list_genie_spaces(profile)
    sp_kill: list[tuple[str, str]] = []
    for sp in spaces:
        title = sp.get("title", "")
        sid = sp.get("space_id", "")
        if GENIE_PAT.match(title) and title not in reference_genie:
            sp_kill.append((title, sid))
    for title, sid in sp_kill:
        print(f"  [delete] {title} ({sid})")
        if apply:
            api(profile, "DELETE", f"/api/2.0/genie/spaces/{sid}")
    if not sp_kill:
        print("  (none match)")
    print()

    # 3) Dashboards
    print("DASHBOARDS")
    dashes = list_dashboards(profile)
    d_kill: list[tuple[str, str]] = []
    for d in dashes:
        dn = d.get("display_name", "")
        did = d.get("dashboard_id", "")
        if DASH_PAT.match(dn) and dn not in reference_dash:
            d_kill.append((dn, did))
    for dn, did in d_kill:
        print(f"  [trash] {dn} ({did})")
        if apply:
            api(profile, "DELETE", f"/api/2.0/lakeview/dashboards/{did}")
    if not d_kill:
        print("  (none match)")
    print()

    # 4) Lakebase
    print("LAKEBASE")
    if args.skip_lakebase:
        print("  (skipped via --skip-lakebase)")
    else:
        print(f"  [delete] instance {args.lakebase_instance}")
        if apply:
            try:
                api(profile, "DELETE", f"/api/2.0/database/instances/{args.lakebase_instance}")
            except SystemExit:
                print("  (instance may not exist; continuing)")
    print()

    # 5) UC schema
    print("UC SCHEMA")
    if args.skip_schema:
        print("  (skipped via --skip-schema)")
    else:
        target = f"{args.catalog}.{args.schema}"
        print(f"  [drop cascade] {target}")
        if apply:
            if not args.warehouse_id:
                print("  ERROR: --warehouse-id is required to drop the schema. Skipping.")
            else:
                drop_schema(profile, args.warehouse_id, args.catalog, args.schema)
    print()

    # 6) Workspace config
    print("WORKSPACE CONFIG")
    print("  [delete] /Workspace/Shared/command-center/")
    if apply:
        try:
            api(profile, "POST", "/api/2.0/workspace/delete", {"path": "/Workspace/Shared/command-center", "recursive": True})
        except SystemExit:
            print("  (config may not exist; continuing)")
    print()

    if not apply:
        print("=== DRY RUN complete. Re-run with --apply to actually delete. ===")
    else:
        print("=== Cleanup complete. ===")
        print("Run `databricks bundle destroy -t <target> --auto-approve` to also drop the bundle-owned facilitator resources.")


if __name__ == "__main__":
    main()
