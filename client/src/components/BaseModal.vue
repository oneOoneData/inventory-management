<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <div
          ref="containerRef"
          class="modal-container"
          :class="`modal-container--${size}`"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="title ? titleId : undefined"
          :aria-label="title ? undefined : 'Dialog'"
        >
          <header class="modal-header">
            <h2 :id="titleId" class="modal-title">{{ title }}</h2>
            <button
              ref="closeButtonRef"
              class="modal-close"
              type="button"
              aria-label="Close"
              @click="$emit('close')"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path
                  d="M15 5L5 15M5 5L15 15"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                />
              </svg>
            </button>
          </header>

          <div class="modal-body">
            <slot />
          </div>

          <footer v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'

// Vue 3.4 has no useId(); a module-level counter gives each modal instance a
// stable unique id so the dialog can be wired to its title via aria-labelledby.
let modalIdCounter = 0
const titleId = `modal-title-${++modalIdCounter}`

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md'
  }
})

const emit = defineEmits(['close'])

const containerRef = ref(null)
const closeButtonRef = ref(null)
// The element that had focus before the modal opened, so we can restore it.
let previouslyFocused = null

const FOCUSABLE_SELECTOR = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])'
].join(',')

const getFocusable = () => {
  if (!containerRef.value) return []
  return Array.from(
    containerRef.value.querySelectorAll(FOCUSABLE_SELECTOR)
  ).filter((el) => el.offsetParent !== null || el === document.activeElement)
}

const onKeydown = (event) => {
  if (event.key === 'Escape') {
    emit('close')
    return
  }
  if (event.key === 'Tab') {
    const focusable = getFocusable()
    if (focusable.length === 0) {
      event.preventDefault()
      return
    }
    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    const active = document.activeElement
    if (event.shiftKey) {
      if (active === first || !containerRef.value.contains(active)) {
        event.preventDefault()
        last.focus()
      }
    } else if (active === last || !containerRef.value.contains(active)) {
      event.preventDefault()
      first.focus()
    }
  }
}

const activate = async () => {
  if (typeof document === 'undefined') return
  previouslyFocused =
    document.activeElement instanceof HTMLElement
      ? document.activeElement
      : null
  document.addEventListener('keydown', onKeydown)
  document.body.style.overflow = 'hidden'
  await nextTick()
  closeButtonRef.value?.focus()
}

const deactivate = () => {
  if (typeof document === 'undefined') return
  document.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
  if (previouslyFocused && typeof previouslyFocused.focus === 'function') {
    previouslyFocused.focus()
  }
  previouslyFocused = null
}

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      activate()
    } else {
      deactivate()
    }
  },
  { immediate: true }
)

onBeforeUnmount(deactivate)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(12, 10, 9, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--space-4);
}

.modal-container {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  max-height: 90vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.modal-container--sm {
  max-width: 420px;
}

.modal-container--md {
  max-width: 600px;
}

.modal-container--lg {
  max-width: 860px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--border);
}

.modal-title {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: var(--tracking-tight);
}

.modal-close {
  flex-shrink: 0;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: var(--space-2);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
}

.modal-close:hover {
  background: var(--bg-muted);
  color: var(--text-primary);
}

.modal-body {
  overflow-y: auto;
  padding: var(--space-6);
}

.modal-footer {
  padding: var(--space-5) var(--space-6);
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

/* Transition — fade + scale */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 180ms ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 180ms ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.96);
}
</style>
