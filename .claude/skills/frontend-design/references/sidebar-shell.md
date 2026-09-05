# Sidebar shell — target structure for `client/src/App.vue`

The redesign replaces the sticky top nav bar with a fixed vertical sidebar on the
left. This file is the reference the `vue-expert` subagent implements against. All
values are tokens from `design-tokens.css`.

## Layout model

```
+-----------+--------------------------------------------------+
|           |  FilterBar  (sticky sub-header of the column)    |
|  sidebar  +--------------------------------------------------+
|  (fixed)  |                                                  |
|           |  <main>  (scrolls; max-width var(--content-max)) |
|  brand    |                                                  |
|  nav      |                                                  |
|  ...      |                                                  |
|  footer   |                                                  |
+-----------+--------------------------------------------------+
```

- `.app` changes from `flex-direction: column` to `flex-direction: row`.
- `.sidebar` is `position: fixed; inset: 0 auto 0 0; width: var(--sidebar-w)`.
- The content column gets `margin-left: var(--sidebar-w)` and is itself a
  `flex-direction: column` container holding `<FilterBar />` then `<main>`.
- The old couplings are deleted: `.nav-container { max-width: 1600px; height: 70px }`,
  `.main-content { max-width: 1600px }`, and `FilterBar.vue`'s `top: 70px`.

## Template skeleton

```vue
<template>
  <div class="app" :class="{ 'app--sidebar-collapsed': sidebarCollapsed }">
    <aside class="sidebar">
      <div class="sidebar__brand">
        <span class="sidebar__mark">CC</span>
        <span class="sidebar__brand-text">
          <strong>{{ t('nav.companyName') }}</strong>
          <small>{{ t('nav.subtitle') }}</small>
        </span>
      </div>

      <nav class="sidebar__nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="sidebar__link"
          :class="{ 'sidebar__link--active': $route.path === item.path }"
          :title="sidebarCollapsed ? item.label : undefined"
        >
          <span class="sidebar__icon" v-html="item.icon" aria-hidden="true" />
          <span class="sidebar__label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar__footer">
        <LanguageSwitcher />
        <ProfileMenu @show-profile-details="..." @show-tasks="..." />
        <button
          class="sidebar__collapse"
          @click="toggleSidebar"
          :aria-label="t('nav.collapseSidebar')"
        >
          <!-- chevron icon; rotates when collapsed -->
        </button>
      </div>
    </aside>

    <div class="app__content">
      <FilterBar />
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <!-- modals unchanged -->
  </div>
</template>
```

## Nav items

Six routes, matching `client/src/main.js` (order preserved). Labels come from i18n
exactly as today; `Reports` currently has a hardcoded literal — add `nav.reports` to
both locale files and use it.

| path         | i18n key              | icon (inline SVG, ~18px, stroke=currentColor) |
|--------------|-----------------------|-----------------------------------------------|
| `/`          | `nav.overview`        | grid / layout-dashboard                        |
| `/inventory` | `nav.inventory`       | package / box                                  |
| `/orders`    | `nav.orders`          | clipboard-list / shopping-cart                 |
| `/spending`  | `nav.finance`         | wallet / dollar-sign                           |
| `/demand`    | `nav.demandForecast`  | trending-up / line-chart                       |
| `/reports`   | `nav.reports` (new)   | bar-chart / file-text                          |

Build `navItems` as a `computed` in `<script setup>` so labels stay reactive to
locale. Keep icons as inline SVG strings (the repo uses no icon library — do not add
one). Heroicons "outline" or Lucide paths are fine as source geometry.

## Active state

Keep the current mechanism: exact `$route.path === item.path` comparison (not
`router-link-active`, which would mark `/` active on every route). Active styling:
`color: var(--text-primary); background: var(--accent-subtle);` plus a
`box-shadow: inset 3px 0 0 var(--accent)` left rail (replaces the old `::after`
underline).

## Collapse behavior

- `sidebarCollapsed` is a `ref(false)` in `<script setup>`, initialised from and
  written back to `localStorage` key `sidebar-collapsed` (wrap access in try/catch —
  private-mode browsers throw).
- Collapsed: `.app--sidebar-collapsed .sidebar { width: var(--sidebar-w-collapsed) }`,
  `.app--sidebar-collapsed .app__content { margin-left: var(--sidebar-w-collapsed) }`,
  and `.sidebar__label` / `.sidebar__brand-text` are hidden. Icons stay centered.
- Transition `width` / `margin-left` with `var(--transition)`.

## Responsive (below `--breakpoint-md`, 1024px)

Add the app's first `@media` query. Below the breakpoint:

- `.sidebar` becomes an off-canvas drawer: `transform: translateX(-100%)`, shown by
  a `mobileNavOpen` ref that adds `.sidebar--open` (`transform: translateX(0)`), with
  a full-screen `.sidebar__scrim` behind it.
- `.app__content` drops its `margin-left` (`margin-left: 0`).
- A slim top bar appears **inside `.app__content`, above `FilterBar`** containing a
  hamburger button (toggles `mobileNavOpen`) and the brand mark. Height
  `var(--topbar-h)`.
- Route change closes the drawer (`watch($route, () => mobileNavOpen.value = false)`).
- `FilterBar` on mobile: allow the `.filters-grid` to wrap (`flex-wrap: wrap`).

## Where the switchers go

`LanguageSwitcher` and `ProfileMenu` move from the top-right nav into
`.sidebar__footer` (stacked). Their internal dropdown positioning changes from
`right: 0` to `left: 0` (they now open from the left edge). When the sidebar is
collapsed, both render icon-only and their dropdowns open to the right of the rail
(`left: 100%`).

## FilterBar placement

`FilterBar` renders once, as the first child of `.app__content`, `position: sticky;
top: 0` within that scroll container. It keeps its four selects + reset button; only
the wrapper styling changes (tokens, `border-bottom: 1px solid var(--border)`,
`background: var(--bg-surface)`, `padding: var(--space-3) var(--content-pad)`).

## `main-content`

```css
.main-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max);
  margin: 0 auto;
  padding: var(--content-pad);
}
```
