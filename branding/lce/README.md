# LCE Branding

Drop-in brand assets for a Little Caesars Enterprises themed build of the
Operator Command Center.

Workshop attendees can point their AppKit build at this folder to override the
default Databricks design tokens. **Don't use these by default** — the design
ships with the Databricks system (Navy + Lava). LCE branding is opt-in.

## Files

| File | Purpose |
|---|---|
| `logo.svg` | Primary logo. Use in the sidebar wordmark and the topbar. |
| `favicon.svg` | Same artwork as the logo, served as the browser favicon. Modern browsers (Chrome 80+, Firefox, Safari) render SVG favicons; ship a 32x32 PNG fallback if you need IE/legacy support. |
| `README.md` | This file — colors, fonts, usage notes. |

## Primary Palette

| Token | Hex | Usage |
|---|---|---|
| LCE Orange (primary) | `#FF671B` | Hero accents, primary CTAs, active states, brand wordmark, sidebar rail |
| LCE Orange Dark | `#CC4F11` | Hover / pressed states for primary buttons |
| LCE Orange Tint | `#FFE5D6` | Subtle background fills (badges, banners) |
| LCE Black | `#111111` | Sidebar background, headlines on light surfaces |
| LCE White | `#FFFFFF` | Surface, text on dark backgrounds |
| LCE Cream | `#FAF6EE` | Canvas background (Lakehouse Market's Oat-light equivalent) |

The SVG itself uses `#FF671B` and `#FFFFFF` only; the rest are recommended
neutrals to round out the palette and play well with the orange.

## Supporting Palette (semantic)

Mirrors the Databricks design system's semantic slots; only the hue choice
changes:

| Token | Hex | Usage |
|---|---|---|
| Success | `#1F9E73` | Green pills, positive deltas |
| Warning | `#E0A21D` | Yellow pills, caution states |
| Danger | `#D6322C` | Red pills, alerts (kept distinct from LCE Orange) |
| Info | `#2272B4` | Neutral blue (for non-LCE-themed informational chips) |

## Typography

LCE doesn't publish a public type system; for a clean operator-facing app,
keep the same stack the reference prototype uses:

| Family | Use |
|---|---|
| `DM Sans` | Body, headlines, UI |
| `DM Mono` | Numbers in dashboards, code, timestamps |

Already loaded in `app/reference-prototype/colors_and_type.css`. Type scale
and weights are unchanged from the Databricks system.

If you want a more LCE-flavored display face, `Roboto` or `Source Sans Pro`
both pair well with the orange and read cleanly at large sizes.

## Token Mapping (CSS overrides)

To re-theme the reference prototype with LCE branding, override these CSS
variables (defined in `colors_and_type.css`). Drop this block into
`Homebase.html`'s `<style>` element to flip the look:

```css
:root {
  --db-lava-300: #FFD2BC;   /* tint */
  --db-lava-400: #FF9D72;
  --db-lava-500: #FF7F45;
  --db-lava-600: #FF671B;   /* LCE Orange — primary */
  --db-lava-700: #CC4F11;
  --db-navy-800: #111111;   /* LCE Black */
  --db-navy-900: #000000;   /* sidebar background */
  --db-oat-light: #FAF6EE;  /* canvas */
  --db-oat-medium: #F1ECE0;
  --fg-accent: #FF671B;
  --fg-link: #CC4F11;
}
```

Logo swap (in `app/shell.jsx` Logo component):

```jsx
<img src="branding/lce/logo.svg" alt="LCE" />
<span>Operator Command Center</span>
```

## Usage Rules

- Don't tint the logo. Keep `#FF671B` on `#FFFFFF` (or `#111111` on dark).
- Don't pair LCE Orange with other warm primaries (red, magenta). It clashes.
- For destructive states (delete, danger toasts), use `#D6322C`, not LCE Orange.
- Maintain WCAG AA contrast on text: LCE Orange (`#FF671B`) on white is **not**
  AA-compliant for small body text — only use it as accent, button background,
  or large display text. For body links, use `#CC4F11` against light backgrounds.

## Attribution

`logo.svg` is the Little Caesars Pizza brand mark, used here for an internal
training workshop. Do not redistribute externally.
