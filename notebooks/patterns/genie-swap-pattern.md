# Pointing the Ask Genie Panel at the Attendee's Own Genie Space

Module 5 swaps the app's existing "Ask Genie" panel from the facilitator's shared reference space to the attendee's OWN Genie space. The panel and its on-behalf-of-user (OBO) auth already work; you are only changing which space ID it talks to, then redeploying. Do NOT rebuild the panel, its router, or its scopes.

---

## Goal

- Point the existing Ask Genie panel at the attendee's Genie space ID (built in the Genie step / Module 2).
- Keep the working OBO auth and `user_api_scopes` exactly as Lab 00 set them.
- Redeploy so the change takes effect.

---

## How the space ID flows

The app resolves its Genie space from `lib/config.get_settings().genie_space_id`. That value comes from one of two sources:

1. The `GENIE_SPACE_ID` env var on the app (set in the app env / `app.yaml`). This is the per-attendee knob.
2. The facilitator's shared `/Workspace/Shared/command-center/config.json` file (written by the setup job), which carries the reference space ID as a default.

`routers/genie.py` reads `s.genie_space_id`; if it is set, it uses it directly (no discovery). So setting `GENIE_SPACE_ID` to the attendee's space is the whole mechanism: no code change to the router is needed.

---

## Key Gotchas & Fixes

### 1. Precedence: the shared config file used to win over the env var (the headline issue)

`config.py`'s boot order reads the shared workspace file FIRST, and originally let any key in that file override the env var:

```python
genie_space_id=ws_cfg.get("genie_space_id") or os.getenv("GENIE_SPACE_ID", "")
```

Since every cloned app reads the SAME facilitator file (`/Workspace/Shared/command-center/config.json`), the attendee's `GENIE_SPACE_ID` was ignored and the panel kept using the shared reference space.

- **Fix:** the env var must win for `genie_space_id`; the shared file stays as a fallback default:

```python
genie_space_id=os.getenv("GENIE_SPACE_ID", "") or ws_cfg.get("genie_space_id", "")
```

- `dab/src/app/lib/config.py` is frozen in the template, so the patch is applied per clone. `clone_app.py` Step 3b rewrites this one line in each cloned app's `lib/config.py` at clone time (the same place Step 3 patches `use_cloud_fetch=False`). The boot order from `config.py`'s docstring still holds: `get_settings()` runs once, tries the shared file, falls back to env vars; only the precedence for `genie_space_id` is inverted.

### 2. Restart / cache: changes need a redeploy

`get_settings()` is `@lru_cache(maxsize=1)` and config is read ONCE at app boot. Changing `GENIE_SPACE_ID` (or the shared file) does nothing until the app is redeployed or restarted. `routers/genie.py` also caches the resolved `GenieInfo` in-process, so a restart is the clean way to pick up a new space.

### 3. OBO auth: Genie spaces are user-permissioned

The panel must call Genie with the LOGGED-IN USER's token, not the app service principal. Databricks Apps forwards the user identity in the `X-Forwarded-Access-Token` header; `routers/genie.py` reads that header and calls the Genie REST API with `Authorization: Bearer <user_token>`.

- The required OBO scopes are `genie`, `sql`, `dashboards.genie`. These `user_api_scopes` are set by Lab 00 / `clone_app.py` and must NOT be changed.
- If you see a **403 "Invalid scope, required scopes: genie"** (or a generic PermissionDenied), the panel is using the app SP token instead of OBO. Follow the working pattern in `dab/src/app/routers/genie.py`: forward `X-Forwarded-Access-Token` and call Genie as the user. Do not switch the panel to the SP `WorkspaceClient`.

### 4. Adding a starter / suggested question is an app-code change

Wiring a suggested question into the Ask Genie panel UI (a starter chip the user can click) is a frontend change, not a config change. Make the edit, then redeploy.

---

## From-Scratch Checklist

1. Get the attendee's Genie space ID from the Genie step (Module 2).
2. Set `GENIE_SPACE_ID=<attendee space id>` in the app env (`app.yaml`).
3. Confirm the precedence patch is in the cloned app's `lib/config.py` (env var first, shared file as fallback): `os.getenv("GENIE_SPACE_ID", "") or ws_cfg.get("genie_space_id", "")`. `clone_app.py` Step 3b does this at clone time; verify if editing by hand.
4. Do NOT touch `user_api_scopes` or the OBO logic in `routers/genie.py`; they already work.
5. (Optional) Add a starter question to the Ask Genie panel UI.
6. Redeploy / restart the app so `get_settings()` re-reads config (it is `lru_cached`).
7. Open the app, re-consent if prompted, and ask a question. If you get a 403 "Invalid scope: genie", the call is using the SP token, not OBO: recheck against `routers/genie.py`.
