---
name: frontend-design
description: Redesign the Vue 3 client UI into a modern SaaS layout with a vertical left sidebar nav, clean card layouts, design tokens, and consistent spacing. Use this skill when asked to restyle the app, replace the top nav with a sidebar, introduce a design system, or do a UI/UX polish pass on client/.
---

# Frontend Design Redesign

This skill turns the Factory Inventory Management client into a modern SaaS-style
interface: a fixed vertical navigation sidebar on the left (replacing the top nav
bar), a real design-token layer, a consistent spacing scale, and clean card layouts.
The default visual direction is soft / approachable SaaS (rounded corners, generous
spacing, gentle shadows, a friendly accent).

It runs plan-first: audit the app, propose concrete values, wait for approval, then
implement on a branch and verify. Do not skip the approval stop.

## Reference files

Read these before starting. They hold the concrete values so this document stays a
workflow.

- `references/design-tokens.css` — the token set to install, plus a hex-to-token
  translation table for the sweep.
- `references/sidebar-shell.md` — the target `App.vue` template, collapse behavior,
  responsive rules, and where the switchers and `FilterBar` move.
- `references/component-sweep.md` — a per-file checklist for every view, component,
  and modal, including the known style divergences to fix and the `BaseModal.vue`
  extraction.

## Hard rules for this repo

- **Any time you create or significantly modify a `.vue` file, delegate it to the
  `vue-expert` subagent.** This skill drives the plan and the ordering; `vue-expert`
  makes the edits. This is a mandatory rule from the root `CLAUDE.md`.
- After the sweep, run the `code-reviewer` subagent on the diff.
- Browser verification uses Playwright MCP (`mcp__playwright__*`) against
  `http://localhost:3000`. GitHub operations use `mcp__github__*`; local branches
  use `git checkout -b`.
- No emojis in the UI. Charts stay hand-rolled inline SVG / CSS — do not add a
  charting or icon library.
- The repo is PUBLIC. Do not modify `client/.npmrc` or `client/package-lock.json`.
  Load fonts with a `<link>` in `client/index.html`, never an npm package.
- Keep all global CSS in `client/src/App.vue`'s single unscoped `<style>` block —
  that is the documented global sheet. Do not add a separate `.css` file.
- Behavior is out of scope. Preserve every prop, emit, ref, computed, i18n key,
  `v-for` key, and date guard. Do not touch `server/` or the `api.js` contract
  (adding a client method that calls an existing endpoint is fine).

## Phase 0 — Preconditions

1. Confirm both dev servers are up (`/start` or the `start` skill) so Playwright can
   reach `http://localhost:3000` and `http://localhost:8001`.
2. Confirm a clean working tree (`git status`).
3. Create a branch: `git checkout -b frontend-design` (or reuse the `/demo-branch`
   auto-numbering if the user prefers a demo branch).

## Phase 1 — Audit

Read and inventory the current UI:

- `client/src/App.vue` — template (top nav, `.nav-container`, `.nav-tabs`, logo,
  `FilterBar` placement, `main-content`, modals) and the global `<style>`.
- `client/src/main.js` — the six routes and their components.
- `client/src/components/FilterBar.vue` — the `top: 70px` coupling to nav height.
- Every `client/src/views/*.vue` and `client/src/components/*.vue` `<style>` block.
- Root `CLAUDE.md` `## Design System` section.

Produce a short written inventory: nav structure, the hardcoded palette in use, the
spacing values in use, and the coupling points below.

**Coupling points to break during the redesign:**
- `.nav-container { max-width: 1600px; height: 70px }` in `App.vue`
- `.main-content { max-width: 1600px }` in `App.vue`
- `FilterBar.vue` `.filters-bar { position: sticky; top: 70px }`
- `.app { flex-direction: column }` -> becomes `row`
- No `:root` / CSS custom properties exist anywhere yet — the token layer is net new.
- No `@media` queries exist yet — the responsive breakpoint is net new.

## Phase 2 — Propose, then STOP for approval

Present to the user, and wait for an explicit yes (or edits) before any `.vue` edit:

1. **Token table** — the values from `references/design-tokens.css` rendered as a
   table (font, neutral ramp, accent, semantic status, spacing scale, radius scale,
   shadow scale, type scale, layout dims). State plainly how far this departs from
   the current slate + `#2563eb` look.
2. **Sidebar structure** — width (`--sidebar-w`), collapsed width, the breakpoint
   behavior, what moves into it (brand, icon nav, `LanguageSwitcher` + `ProfileMenu`
   in the footer), and that `FilterBar` becomes a sticky sub-header of the content
   column.
3. **Card system** — the redesigned `.card` / `.stat-card` / table container:
   radius, padding, hairline border plus `--shadow-xs`, header treatment, hover.
4. **File list** — every file to be modified, grouped (shell, per-view,
   per-component, per-modal, i18n, docs) from `references/component-sweep.md`.
5. **Known divergences to fix** — `Reports.vue` (local style redefinitions,
   hardcoded English, direct axios), the `#667eea`/`#764ba2` purple gradients in
   `TasksModal.vue` and `Dashboard.vue`, the six modals' copy-pasted overlay CSS
   (-> `BaseModal.vue`), `Demand.vue`'s `↑ → ↓` text glyphs (-> inline SVG), the
   missing Inter font.
6. **Flag, do not fix** — orphaned `Backlog.vue` and the missing `PurchaseOrderModal`
   referenced by `Dashboard.vue`. Ask what to do; do not silently change either.

## Phase 3 — Execute (via `vue-expert`)

Order matters — install the foundation before the sweep.

1. **Font** — add the Inter `<link>` (+ `preconnect`) to `client/index.html`.
2. **Tokens + primitives** — `vue-expert` adds the `:root` block, the reset, and the
   refreshed shared primitives (`.card`, `.stat-card`, `table`, `th`, `td`,
   `.badge`, `.page-header`, `.loading`, `.error`, layout classes) into the existing
   global `<style>` in `App.vue`.
3. **Shell** — `vue-expert` rebuilds the `App.vue` template per
   `references/sidebar-shell.md`: `.app` to `row`, `<aside class="sidebar">`, the
   content column, the `sidebarCollapsed` ref with `localStorage`, the one
   `@media (max-width: 1024px)` block with the off-canvas drawer + hamburger.
4. **FilterBar** — restyle to tokens, drop `top: 70px`, allow mobile wrap.
5. **Sweep** — work `references/component-sweep.md` top to bottom: each view, each
   component, then extract `BaseModal.vue` and refactor the six modals onto it, then
   fix `Reports.vue`.
6. **i18n** — add `nav.reports`, `nav.collapseSidebar`, and keys for any strings
   that were hardcoded English, to both `en.js` and `ja.js`.
7. **Docs** — update the `## Design System` section of root `CLAUDE.md` and the
   "Styling Best Practices" section of `client/CLAUDE.md`.

## Phase 4 — Verify

1. **Playwright** against `http://localhost:3000`:
   - Snapshot each route: `/`, `/inventory`, `/orders`, `/spending`, `/demand`,
     `/reports`.
   - Toggle the sidebar collapsed and expanded.
   - Resize to 900px wide; confirm the drawer + hamburger; open and close it.
   - Exercise one `FilterBar` select and confirm data still updates.
   - Open one modal (e.g. an inventory row) and close it.
   - Switch locale EN -> JA -> EN.
2. **`code-reviewer` subagent** on the full diff.
3. **Report**: routes verified with screenshots, the `code-reviewer` findings, and
   the open follow-ups (`Backlog.vue`, `PurchaseOrderModal`). If the user does not
   want the result, reset with `/reset-branch`.

## Re-running

This skill is idempotent enough to re-run for iteration. On a second run: skip the
`:root` install if tokens already exist, adjust values in place, and re-sweep only
the files the user wants changed. Always re-audit first — the app may have drifted.
