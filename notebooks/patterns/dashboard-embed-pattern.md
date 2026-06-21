# Embedding a Published AI/BI Dashboard as an iframe in a Databricks App

Embed a published AI/BI dashboard as an iframe on the app's home page, directly below the 3 tiles. Used in Module 5 so attendees see their dashboard live inside their own Databricks App.

---

## The One Rule That Matters Most

Use the dashboard's published **`/embed/` URL** (from the dashboard's **Share then Embed**), NOT the normal workspace dashboard link. The normal link sets `X-Frame-Options` and refuses to be framed: the iframe shows "refused to connect". The `/embed/` URL is the only one that can be hosted in another origin.

The dashboard must be **Published with embedding enabled** before the `/embed/` URL exists.

---

## Key Gotchas & Fixes

### 1. Admin-only approved-domains allowlist (the key facilitator pre-req)

The single most important pre-req, and the one attendees cannot fix themselves.

- The allowlist is a **workspace-admin setting**: **Settings > Security > External access > Embed dashboards > Allow approved domains > Manage**.
- Add **`*.databricksapps.com`**, Save.
- The single `*` matches any subdomain depth (CSP grammar), so this **one wildcard entry covers every attendee's** `<initials>-command-center-<id>.<cloud>.databricksapps.com` app host. No per-attendee step.
- Attendees cannot set this; the **facilitator sets it once** for the whole workshop.
- Takes effect within **~2 minutes** (pod cache). A hard refresh or fresh tab picks it up.

Without this, every attendee's iframe fails with a "refused to connect" / approved-domains error.

### 2. Third-party-cookie / managed-laptop gotcha (iframe blank even with allowlist set)

Basic dashboard embedding rides the viewer's Databricks **session cookie**, which the browser treats as a **third-party cookie** relative to the `*.databricksapps.com` app domain. If the iframe is blank or still refuses to connect after the allowlist is set, work through these triggers in order:

1. **Incognito / InPrivate window** blocks third-party cookies by default: use a **normal window**.
2. **Managed-laptop MDM policy** (`BlockThirdPartyCookies`) blocks them even in a normal window: add a site exception for `[*.]databricks.com`.
   - Chrome: Settings > Privacy > Cookies > "Sites that can always use cookies".
   - Edge: same path, or the `CookiesAllowedForUrls` policy.
3. **App opened inside the workspace preview pane** (a nested iframe): open the **top-level** `…databricksapps.com` URL instead.

On company-managed laptops, **pre-test the embed in a real attendee browser/device profile** before the workshop. If MDM hard-blocks third-party cookies with no user override, fall back to opening the dashboard's `/embed/` URL in **its own browser tab** (linked from a tile), or screenshot the dashboard for the demo.

### 3. Not the same as a Genie 403

A **403 "Invalid scope" / `PermissionDenied`** on a Genie embed is a **different problem** (on-behalf-of-user auth scopes, `user_api_scopes: [genie, sql, dashboards.genie]`). That is covered by the Genie swap pattern, not this one. This pattern is only about the dashboard iframe and the cookie/allowlist chain above.

---

## Implementation Notes

- Drop the `/embed/` URL into a plain `<iframe>` on the home page, below the 3 tiles.
- **Always add an "Open in Databricks" link above the iframe** that opens the full dashboard in a **new tab** (`target="_blank"`). This is the in-app fallback if the iframe does not render for any of the cookie reasons above.
- Width 100%, a fixed height (e.g. 720px) reads well below the tiles; let the iframe scroll internally.
- No `app.yaml` resource changes or `user_api_scopes` are needed for a basic dashboard embed (it rides the viewer's session, not the app SP). That is what makes the cookie behavior the dominant failure mode.

Sketch:

```jsx
<a href={DASHBOARD_FULL_URL} target="_blank" rel="noopener noreferrer">
  Open in Databricks ↗
</a>
<iframe
  src={DASHBOARD_EMBED_URL}   /* the /embed/ link, NOT the normal link */
  style={{ width: '100%', height: 720, border: 0, borderRadius: 12 }}
  title="Command Center dashboard"
/>
```

---

## From-Scratch Checklist

1. **Publish** the dashboard with **embedding enabled**.
2. Copy the **`/embed/` URL** from **Share > Embed** (never the normal workspace link).
3. Facilitator (admin) adds **`*.databricksapps.com`** under Settings > Security > External access > Embed dashboards; wait ~2 minutes.
4. Add the `<iframe>` below the tiles, plus an **"Open in Databricks" new-tab link** above it as a fallback.
5. Deploy the app.
6. **Test in a normal (non-incognito) window** on a real attendee/managed-laptop profile.
7. If still blank: check incognito, then MDM cookie policy (add `[*.]databricks.com` exception), then whether you are inside the workspace preview pane (open the top-level `databricksapps.com` URL).
8. If MDM hard-blocks with no override: fall back to the `/embed/` URL in its own tab, or screenshot.
9. Remember: a 403 "Invalid scope" is a Genie auth issue, not this; see the Genie swap pattern.
