<template>
  <div
    class="app"
    :class="{
      'app--sidebar-collapsed': sidebarCollapsed,
      'app--mobile-nav-open': mobileNavOpen
    }"
  >
    <aside
      id="app-sidebar"
      ref="sidebarRef"
      class="sidebar"
      :class="{ 'sidebar--open': mobileNavOpen }"
      :inert="isMobileViewport && !mobileNavOpen ? true : undefined"
      :role="isMobileViewport && mobileNavOpen ? 'dialog' : undefined"
      :aria-modal="isMobileViewport && mobileNavOpen ? 'true' : undefined"
    >
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
          <span
            class="sidebar__icon"
            v-html="item.icon"
            aria-hidden="true"
          ></span>
          <span class="sidebar__label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar__footer">
        <LanguageSwitcher />
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="showTasks = true"
        />
        <button
          class="sidebar__collapse"
          type="button"
          @click="toggleSidebar"
          :aria-label="t('nav.collapseSidebar')"
          :title="t('nav.collapseSidebar')"
        >
          <svg
            class="sidebar__collapse-icon"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m15 18-6-6 6-6" />
          </svg>
          <span class="sidebar__collapse-label">{{
            t('nav.collapseSidebar')
          }}</span>
        </button>
      </div>
    </aside>

    <div
      class="sidebar__scrim"
      v-if="mobileNavOpen"
      @click="mobileNavOpen = false"
    ></div>

    <div class="app__content">
      <div class="app__topbar">
        <button
          ref="hamburgerRef"
          class="app__hamburger"
          type="button"
          @click="mobileNavOpen = !mobileNavOpen"
          :aria-label="t('nav.openNav')"
          :aria-expanded="mobileNavOpen"
          aria-controls="app-sidebar"
        >
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <span class="app__topbar-mark">CC</span>
      </div>

      <FilterBar />
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

const route = useRoute()
const { currentUser } = useAuth()
const { t } = useI18n()

const showProfileDetails = ref(false)
const showTasks = ref(false)

const ICONS = {
  overview:
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>',
  inventory:
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>',
  orders:
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/></svg>',
  finance:
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg>',
  demand:
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
  reports:
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>'
}

const navItems = computed(() => [
  {
    path: '/',
    labelKey: 'nav.overview',
    label: t('nav.overview'),
    icon: ICONS.overview
  },
  {
    path: '/inventory',
    labelKey: 'nav.inventory',
    label: t('nav.inventory'),
    icon: ICONS.inventory
  },
  {
    path: '/orders',
    labelKey: 'nav.orders',
    label: t('nav.orders'),
    icon: ICONS.orders
  },
  {
    path: '/spending',
    labelKey: 'nav.finance',
    label: t('nav.finance'),
    icon: ICONS.finance
  },
  {
    path: '/demand',
    labelKey: 'nav.demandForecast',
    label: t('nav.demandForecast'),
    icon: ICONS.demand
  },
  {
    path: '/reports',
    labelKey: 'nav.reports',
    label: t('nav.reports'),
    icon: ICONS.reports
  }
])

const sidebarCollapsed = ref(false)
try {
  sidebarCollapsed.value = localStorage.getItem('sidebar-collapsed') === 'true'
} catch (err) {
  // localStorage unavailable (private mode) - keep default
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  try {
    localStorage.setItem(
      'sidebar-collapsed',
      sidebarCollapsed.value ? 'true' : 'false'
    )
  } catch (err) {
    // ignore write failures
  }
}

const mobileNavOpen = ref(false)
watch(
  () => route.path,
  () => {
    mobileNavOpen.value = false
  }
)

// Tasks are local-only demo state (no backend route exists). Seed from the mock
// currentUser and hold in a local ref so add/toggle/delete are reactive. Switching
// locale rebuilds currentUser, so re-seed (task edits reset with the language, as
// before). No /api/tasks calls — that route never existed and 404'd on every load.
const tasks = ref([...currentUser.value.tasks])
watch(currentUser, (user) => {
  tasks.value = [...user.tasks]
})

const addTask = (taskData) => {
  tasks.value.unshift({
    id: Date.now(),
    status: 'pending',
    ...taskData
  })
}

const deleteTask = (taskId) => {
  tasks.value = tasks.value.filter((t) => t.id !== taskId)
}

const toggleTask = (taskId) => {
  const task = tasks.value.find((t) => t.id === taskId)
  if (task) {
    task.status = task.status === 'pending' ? 'completed' : 'pending'
  }
}

// ---- Mobile nav drawer: viewport tracking + focus trap -------------------
const sidebarRef = ref(null)
const hamburgerRef = ref(null)
const isMobileViewport = ref(false)
let mobileMedia = null

const onMediaChange = (event) => {
  isMobileViewport.value = event.matches
}

const onDrawerKeydown = (event) => {
  if (!mobileNavOpen.value) return
  if (event.key === 'Escape') {
    mobileNavOpen.value = false
    return
  }
  if (event.key === 'Tab' && sidebarRef.value) {
    const focusable = Array.from(
      sidebarRef.value.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    ).filter((el) => el.offsetParent !== null)
    if (focusable.length === 0) return
    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    const active = document.activeElement
    if (event.shiftKey) {
      if (active === first || !sidebarRef.value.contains(active)) {
        event.preventDefault()
        last.focus()
      }
    } else if (active === last || !sidebarRef.value.contains(active)) {
      event.preventDefault()
      first.focus()
    }
  }
}

watch(mobileNavOpen, async (open) => {
  if (open) {
    document.addEventListener('keydown', onDrawerKeydown)
    await nextTick()
    const firstLink = sidebarRef.value?.querySelector('.sidebar__link')
    firstLink?.focus()
  } else {
    document.removeEventListener('keydown', onDrawerKeydown)
    if (isMobileViewport.value) {
      hamburgerRef.value?.focus()
    }
  }
})

onMounted(() => {
  mobileMedia = window.matchMedia('(max-width: 1024px)')
  isMobileViewport.value = mobileMedia.matches
  mobileMedia.addEventListener('change', onMediaChange)
})

onBeforeUnmount(() => {
  mobileMedia?.removeEventListener('change', onMediaChange)
  document.removeEventListener('keydown', onDrawerKeydown)
})
</script>

<style>
:root {
  /* ---- Font --------------------------------------------------------------- */
  --font-sans:
    'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, sans-serif;

  /* ---- Neutral ramp (warm gray — Tailwind "stone") ---------------------- */
  --color-neutral-50: #fafaf9;
  --color-neutral-100: #f5f5f4;
  --color-neutral-200: #e7e5e4;
  --color-neutral-300: #d6d3d1;
  --color-neutral-400: #a8a29e;
  --color-neutral-500: #78716c;
  --color-neutral-600: #57534e;
  --color-neutral-700: #44403c;
  --color-neutral-800: #292524;
  --color-neutral-900: #1c1917;
  --color-neutral-950: #0c0a09;

  /* ---- Accent (friendly periwinkle indigo) ----------------------------- */
  --color-accent-50: #eef0fb;
  --color-accent-100: #dfe3f7;
  --color-accent-200: #c4cbf0;
  --color-accent-300: #9fa9e4;
  --color-accent-400: #7b83d6;
  --color-accent-500: #5f66c9;
  --color-accent-600: #4d51b0;
  --color-accent-700: #40428f;

  /* ---- Semantic status (aligned to the existing green/blue/yellow/red) -- */
  --color-success-fg: #15803d;
  --color-success-subtle: #dcfce7;
  --color-warning-fg: #b45309;
  --color-warning-subtle: #fef3c7;
  --color-danger-fg: #b91c1c;
  --color-danger-subtle: #fee2e2;
  --color-info-fg: var(--color-accent-600);
  --color-info-subtle: var(--color-accent-50);

  /* ---- Semantic surfaces & text --------------------------------------- */
  --bg-app: var(--color-neutral-100);
  --bg-surface: #ffffff;
  --bg-muted: var(--color-neutral-50);
  --bg-sidebar: var(--color-neutral-50);
  --border: var(--color-neutral-200);
  --border-strong: var(--color-neutral-300);
  --text-primary: var(--color-neutral-900);
  --text-secondary: var(--color-neutral-500);
  --text-tertiary: var(--color-neutral-400);
  --text-on-accent: #ffffff;

  --accent: var(--color-accent-500);
  --accent-hover: var(--color-accent-600);
  --accent-subtle: var(--color-accent-50);
  --accent-border: var(--color-accent-200);

  /* ---- Spacing scale (4px base) -------------------------------------- */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-7: 2rem;
  --space-8: 2.5rem;
  --space-9: 3rem;
  --space-10: 4rem;
  --space-11: 5rem;
  --space-12: 6rem;

  /* ---- Radius (soft) ------------------------------------------------- */
  --radius-sm: 10px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;

  /* ---- Elevation (gentle, large-blur, low-opacity) ----------------- */
  --shadow-xs: 0 1px 2px rgba(12, 10, 9, 0.04), 0 1px 3px rgba(12, 10, 9, 0.06);
  --shadow-sm: 0 4px 12px rgba(12, 10, 9, 0.06);
  --shadow-md: 0 12px 32px rgba(12, 10, 9, 0.1);

  /* ---- Type scale -------------------------------------------------- */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 0.9375rem;
  --text-md: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.375rem;
  --text-2xl: 1.75rem;
  --text-3xl: 2.125rem;
  --leading-tight: 1.25;
  --leading-normal: 1.6;
  --tracking-tight: -0.01em;

  /* ---- Controls -------------------------------------------------- */
  --control-h: 40px;
  --control-h-sm: 32px;
  --focus-ring: 0 0 0 3px var(--color-accent-100);

  /* ---- Layout -------------------------------------------------- */
  --sidebar-w: 256px;
  --sidebar-w-collapsed: 68px;
  --topbar-h: 60px;
  --content-max: 1440px;
  --content-pad: var(--space-7);
  --breakpoint-md: 1024px;

  /* ---- Motion ------------------------------------------------ */
  --transition-fast: 120ms ease;
  --transition: 200ms ease;

  /* ---- Z-index ------------------------------------------------ */
  --z-filterbar: 20;
  --z-sidebar: 40;
  --z-drawer: 60;
  --z-dropdown: 80;
  --z-modal: 100;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  background: var(--bg-app);
  color: var(--text-primary);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ============================================================ */
/* App shell                                                    */
/* ============================================================ */

.app {
  display: flex;
  flex-direction: row;
  min-height: 100vh;
}

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  width: var(--sidebar-w);
  z-index: var(--z-sidebar);
  display: flex;
  flex-direction: column;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  transition:
    width var(--transition),
    transform var(--transition);
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-5);
  min-height: var(--topbar-h);
}

.sidebar__mark {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-sm);
  background: var(--accent);
  color: var(--text-on-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: var(--text-sm);
  letter-spacing: var(--tracking-tight);
}

.sidebar__brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
  line-height: var(--leading-tight);
}

.sidebar__brand-text strong {
  font-size: var(--text-md);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: var(--tracking-tight);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar__brand-text small {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar__nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-4) var(--space-3);
  overflow-y: auto;
}

.sidebar__link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-3);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: var(--text-sm);
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
}

.sidebar__link:hover {
  background: var(--color-neutral-100);
  color: var(--text-primary);
}

.sidebar__link--active {
  background: var(--accent-subtle);
  color: var(--text-primary);
  box-shadow: inset 3px 0 0 var(--accent);
}

.sidebar__icon {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
}

.sidebar__label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar__footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-3);
  border-top: 1px solid var(--border);
}

.sidebar__collapse {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-family: inherit;
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
}

.sidebar__collapse:hover {
  background: var(--color-neutral-100);
  color: var(--text-primary);
}

.sidebar__collapse-icon {
  flex-shrink: 0;
  transition: transform var(--transition);
}

.sidebar__scrim {
  display: none;
}

.app__content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  margin-left: var(--sidebar-w);
  transition: margin-left var(--transition);
}

.app__topbar {
  display: none;
}

/* ---- Collapsed sidebar ---------------------------------------- */

.app--sidebar-collapsed .sidebar {
  width: var(--sidebar-w-collapsed);
}

.app--sidebar-collapsed .app__content {
  margin-left: var(--sidebar-w-collapsed);
}

.app--sidebar-collapsed .sidebar__label,
.app--sidebar-collapsed .sidebar__brand-text,
.app--sidebar-collapsed .sidebar__collapse-label {
  display: none;
}

.app--sidebar-collapsed .sidebar__brand {
  justify-content: center;
  padding-left: var(--space-3);
  padding-right: var(--space-3);
}

.app--sidebar-collapsed .sidebar__link,
.app--sidebar-collapsed .sidebar__collapse {
  justify-content: center;
}

.app--sidebar-collapsed .sidebar__collapse-icon {
  transform: rotate(180deg);
}

/* ============================================================ */
/* Content column                                               */
/* ============================================================ */

.main-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max);
  margin: 0 auto;
  padding: var(--content-pad);
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-header h2 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-1);
  letter-spacing: var(--tracking-tight);
}

.page-header p {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

/* ============================================================ */
/* Shared primitives                                            */
/* ============================================================ */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--bg-surface);
  padding: var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
  transition:
    border-color var(--transition),
    box-shadow var(--transition);
}

.stat-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-sm);
}

.stat-label {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-2);
}

.stat-value {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: var(--tracking-tight);
}

.stat-card.warning .stat-value {
  color: var(--color-warning-fg);
}

.stat-card.success .stat-value {
  color: var(--color-success-fg);
}

.stat-card.danger .stat-value {
  color: var(--color-danger-fg);
}

.stat-card.info .stat-value {
  color: var(--color-info-fg);
}

.card {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: var(--space-6);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
  margin-bottom: var(--space-5);
  transition: box-shadow var(--transition);
}

.card:hover {
  box-shadow: var(--shadow-sm);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--border);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: var(--tracking-tight);
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--bg-muted);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

th {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: var(--space-2) var(--space-3);
  border-top: 1px solid var(--border);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

tbody tr {
  transition: background-color var(--transition-fast);
}

tbody tr:hover {
  background: var(--bg-muted);
}

.badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge.success {
  background: var(--color-success-subtle);
  color: var(--color-success-fg);
}

.badge.warning {
  background: var(--color-warning-subtle);
  color: var(--color-warning-fg);
}

.badge.danger {
  background: var(--color-danger-subtle);
  color: var(--color-danger-fg);
}

.badge.info {
  background: var(--color-info-subtle);
  color: var(--color-info-fg);
}

.badge.increasing {
  background: var(--color-success-subtle);
  color: var(--color-success-fg);
}

.badge.decreasing {
  background: var(--color-danger-subtle);
  color: var(--color-danger-fg);
}

.badge.stable {
  background: var(--accent-subtle);
  color: var(--color-accent-700);
}

.badge.high {
  background: var(--color-danger-subtle);
  color: var(--color-danger-fg);
}

.badge.medium {
  background: var(--color-warning-subtle);
  color: var(--color-warning-fg);
}

.badge.low {
  background: var(--color-info-subtle);
  color: var(--color-info-fg);
}

.loading {
  text-align: center;
  padding: var(--space-9);
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.error {
  background: var(--color-danger-subtle);
  border: 1px solid var(--color-danger-subtle);
  color: var(--color-danger-fg);
  padding: var(--space-4);
  border-radius: var(--radius-sm);
  margin: var(--space-4) 0;
  font-size: var(--text-sm);
}

/* ============================================================ */
/* Responsive — off-canvas drawer                               */
/* ============================================================ */

@media (max-width: 1024px) {
  .sidebar {
    transform: translateX(-100%);
    width: var(--sidebar-w);
    z-index: var(--z-drawer);
    box-shadow: var(--shadow-md);
  }

  .sidebar--open {
    transform: translateX(0);
  }

  .app--sidebar-collapsed .sidebar {
    width: var(--sidebar-w);
  }

  .app--sidebar-collapsed .sidebar__label,
  .app--sidebar-collapsed .sidebar__brand-text,
  .app--sidebar-collapsed .sidebar__collapse-label {
    display: initial;
  }

  .app--sidebar-collapsed .sidebar__link,
  .app--sidebar-collapsed .sidebar__collapse,
  .app--sidebar-collapsed .sidebar__brand {
    justify-content: flex-start;
  }

  .sidebar__scrim {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(12, 10, 9, 0.4);
    z-index: var(--z-sidebar);
  }

  .app__content,
  .app--sidebar-collapsed .app__content {
    margin-left: 0;
  }

  .app__topbar {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    height: var(--topbar-h);
    padding: 0 var(--space-4);
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: var(--z-filterbar);
  }

  .app__hamburger {
    display: flex;
    align-items: center;
    justify-content: center;
    width: var(--control-h);
    height: var(--control-h);
    background: none;
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    cursor: pointer;
  }

  .app__hamburger:hover {
    background: var(--bg-muted);
  }

  .app__topbar-mark {
    width: 32px;
    height: 32px;
    border-radius: var(--radius-sm);
    background: var(--accent);
    color: var(--text-on-accent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: var(--text-sm);
  }

  .sidebar--open + .sidebar__scrim,
  .app--mobile-nav-open .sidebar__scrim {
    display: block;
  }
}
</style>
