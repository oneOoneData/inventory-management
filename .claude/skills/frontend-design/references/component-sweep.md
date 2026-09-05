# Component sweep — per-file checklist

After the tokens are installed in `App.vue` and the sidebar shell is built, work
through every file below. Each `.vue` create/edit goes through the `vue-expert`
subagent. Line ranges are approximate (from the last audit) — re-read each file
first.

## Global rules for every file

1. Replace every hardcoded hex with the matching `var(--token)` (see the translation
   table at the bottom of `design-tokens.css`).
2. Snap every `padding` / `margin` / `gap` to a `--space-*` step.
3. Replace `border-radius` literals with `--radius-sm|md|lg`.
4. Replace every `box-shadow` literal with `--shadow-xs|sm|md`.
5. Delete any scoped rule that only re-declares what the global sheet already
   provides (`.card`, `.card-header`, `.card-title`, `table`, `th`, `td`, `.badge`,
   `.page-header`, `.stat-card`, `.loading`, `.error`).
6. Keep behavior identical: same props, emits, refs, computed, i18n keys, `v-for`
   keys, date guards. This is a restyle, not a rewrite.
7. No emojis. Keep charts as hand-rolled inline SVG / CSS (no chart library).

## Shell / globals

| File | What to do |
|---|---|
| `client/index.html` | Add `<link rel="preconnect">` + font `<link>` for Inter (400/500/600/700). Add `<meta name="theme-color">`. |
| `client/src/App.vue` | Install `:root` tokens + reset + refreshed shared primitives into the existing global `<style>` (lines ~164-486). Rebuild template per `sidebar-shell.md`. Add the one `@media (max-width: 1024px)` block. |
| `client/src/components/FilterBar.vue` (L103-194) | Restyle to tokens. Remove `position: sticky; top: 70px` — it now stickies within `.app__content` (`top: 0`). Let `.filters-grid` wrap on mobile. |

## Views

| File | Style range | Notes |
|---|---|---|
| `client/src/views/Dashboard.vue` | L729-1271 | Largest. `.kpi-grid` / `.charts-grid` / `.summary-section` → token spacing. Donut SVG: keep geometry, recolor segments to `var(--color-success-fg)` etc. **Replace the `#667eea`/`#764ba2` gradient (~L1146) and `accent-color:#667eea` (~L1206) with `var(--accent)`.** `PurchaseOrderModal` is referenced in the template but the file does not exist — see "Flag, do not fix". |
| `client/src/views/Inventory.vue` | L227-339 | `.search-box` → tokenized input, `--control-h`, `--focus-ring`. Card + table inherit globals. |
| `client/src/views/Orders.vue` | L174-279 | Fixed table column widths stay (functional). Status `.stat-card` accent colors → semantic tokens. `<details>` dropdown → token surface + `--shadow-sm`. |
| `client/src/views/Demand.vue` | L226-369 | `.trend-card` left borders → semantic tokens. **Replace the `↑ → ↓` text glyphs in `.trend-icon` (template ~L14/33/53) with small inline SVG arrows.** |
| `client/src/views/Spending.vue` | L494-853 | Two CSS bar charts + legend dots → token colors. `.two-column-grid` `minmax(450px,1fr)` → `minmax(360px,1fr)` so it stacks sooner. Sticky transactions thead → token bg. |
| `client/src/views/Reports.vue` | L319-488 | **Biggest cleanup.** (a) Route its two `axios.get('http://localhost:8001/...')` calls through `client/src/api.js` (add `getQuarterlyReports()` / `getMonthlyTrends()` methods). (b) Delete its local `.card` / `.card-title` / `.stat-card` / `.badge` / `.loading` / `.error` redefinitions — use the globals. (c) Add i18n keys and replace the hardcoded English strings; add `nav.reports`. (d) Remove the `console.log` calls. Keep it Options API if converting to `<script setup>` risks scope creep — restyle is the priority. |
| `client/src/views/Backlog.vue` | (no `<style>`) | Not routed. See "Flag, do not fix". If in scope later: add `nav`/route, i18n, a scoped block. |

## Components

| File | Style range | Notes |
|---|---|---|
| `client/src/components/ProfileMenu.vue` | L118-281 | Move into `.sidebar__footer`; dropdown opens `left: 0` (or `left: 100%` when collapsed). Avatar gradient → `var(--accent)` flat or a subtle accent gradient. Chevron/menu-item icons keep `currentColor`. |
| `client/src/components/LanguageSwitcher.vue` | L91-184 | Same footer move + dropdown direction flip. Near-duplicate dropdown CSS with ProfileMenu — acceptable to leave duplicated, or extract a tiny `DropdownMenu.vue` if time allows (not required). |

## Modals — extract `BaseModal.vue`

All six modals copy-paste the same overlay/container/transition CSS and the same
`<Teleport to="body">` + `<Transition name="modal">` wrapper. Create
`client/src/components/BaseModal.vue`:

```vue
<script setup>
defineProps({ isOpen: Boolean, title: String, size: { type: String, default: 'md' } })
defineEmits(['close'])
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container" :class="`modal-container--${size}`" role="dialog" aria-modal="true">
          <header class="modal-header">
            <h2>{{ title }}</h2>
            <button class="modal-close" @click="$emit('close')" aria-label="Close"><!-- x svg --></button>
          </header>
          <div class="modal-body"><slot /></div>
          <footer v-if="$slots.footer" class="modal-footer"><slot name="footer" /></footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
```

Overlay/container/transition styles live here once, tokenized (`--radius-lg`,
`--shadow-md`, `--space-*`, `z-index` from a single `--z-modal: 2000`). `size`
variants map to `max-width` (`sm` 420px, `md` 600px, `lg` 860px).

Then refactor each modal to `<BaseModal :is-open="..." :title="..." @close="...">`
+ its unique body content, deleting the per-file overlay CSS:

| File | Lines | size | Extra |
|---|---|---|---|
| `ProfileDetailsModal.vue` | 281 | md | — |
| `TasksModal.vue` | 622 | lg | **Replace `#667eea`/`#764ba2` gradient buttons with `var(--accent)`.** Keep the add/toggle/delete task logic. |
| `ProductDetailModal.vue` | 335 | md | Hardcoded English — add i18n keys. |
| `BacklogDetailModal.vue` | 380 | md | Hardcoded English — add i18n keys. |
| `CostDetailModal.vue` | 384 | md | — |
| `InventoryDetailModal.vue` | 450 | md | Hardcoded English — add i18n keys. |

## i18n

Add to `client/src/locales/en.js` and `client/src/locales/ja.js`:
- `nav.reports`
- `nav.collapseSidebar`
- keys for any modal / Reports strings that were previously hardcoded English
Keep the existing `nav.*`, `filters.*`, `dashboard.*` keys untouched.

## Docs

- Root `CLAUDE.md` — rewrite the `## Design System` section: token file location,
  the palette summary, radius/shadow/spacing scales, "sidebar shell (see the
  frontend-design skill)".
- `client/CLAUDE.md` — update "Styling Best Practices" to say tokens are defined in
  `App.vue` `:root` and consumed via `var(--...)`; note the `@media` breakpoint.

## Flag, do not fix (report to the user as follow-ups)

- **`client/src/views/Backlog.vue`** — 152-line view, not in `main.js` routes, not
  linked. Restyling it is wasted effort until it is wired up (or deleted). Ask.
- **`PurchaseOrderModal`** — referenced in `Dashboard.vue` (~L289) with handlers
  (`openPOModal`, `viewPO`, `handlePOCreated`, `poModalMode`) but the component file
  does not exist and it is not imported. This is a latent runtime warning unrelated
  to the redesign. Ask whether to stub it, remove the references, or leave it.
