# Editing the App: Reliable Writes and Dark-Mode / Rebrand Technique

Modules 4 to 6 all edit the app's source (branding, dark mode, the Genie swap, the dashboard embed, the Company News feature). This pattern covers two things that save iterations: how to write app files reliably, and how to restyle (dark mode, rebrand) without playing whack-a-mole with colors.

---

## Writing app source reliably

### Prefer Python `open()` over `editAsset` for batches

For large batches of edits, or any time `editAsset` is flaky, skip it and write files with plain Python `open(path, "r")` / `open(path, "w")` against the file's `/Workspace/...` path. It is atomic, verifiable in the same cell, and immune to the workspace API's timeout and rate-limit behavior. Default to `open()` for any multi-file or multi-patch pass (for example a dark-mode pass that touches a dozen spots), not only when `editAsset` has already failed.

Related: the Workspace Files API rate-limits bursty parallel writes (roughly 4 to 5 in the same second 429s), so if you do use the API, save one file at a time. `open()` sidesteps that path entirely.

### Verify on disk before you deploy

Deploying immediately after `editAsset` calls risks snapshotting un-edited files: the edits may not have landed yet. Before you deploy, do a Python `open()` read of every file you changed and confirm the new content is actually on disk. Read, confirm, then deploy.

---

## Dark mode and rebranding technique

### Audit contrast before writing a line

Before changing anything, list every `background`, `color`, and `border` value that appears in the target component, and confirm each text-on-background pair has enough contrast. Darkening only the text is not enough: for example the `Card` component defaults to `background: '#fff'`, so dark-mode text left on it stayed white-on-white and the module names went invisible. A contrast audit up front catches this in zero iterations.

### Override CSS tokens, do not hunt inline colors

Change the design tokens at the root (for example `--db-lava-600: #FF671B` in `:root`) rather than chasing individual inline color values. One token change propagates everywhere automatically: buttons, active states, sparklines, and focus rings all update for free.

---

## Checklist

1. For multi-file or multi-patch edits, write with Python `open()`, not `editAsset` (atomic, verifiable, no rate-limit).
2. Audit the target component's `background` / `color` / `border` values and text-on-background contrast BEFORE editing (watch for `Card` defaulting to `#fff`).
3. Restyle by overriding CSS tokens in `:root`, not by editing inline colors.
4. `open()`-read every changed file and confirm the edits are on disk.
5. Only then deploy.
