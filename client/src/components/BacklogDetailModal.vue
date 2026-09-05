<template>
  <BaseModal
    :is-open="isOpen && !!backlogItem"
    :title="t('modals.backlog.title')"
    size="md"
    @close="close"
  >
    <template v-if="backlogItem">
      <div class="shortage-header">
        <div class="shortage-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <path d="M24 8L24 28M24 34L24 36" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
            <circle cx="24" cy="24" r="18" stroke="currentColor" stroke-width="3"/>
          </svg>
        </div>
        <div class="shortage-title-section">
          <h4 class="item-name">{{ translateProductName(backlogItem.item_name) }}</h4>
          <div class="item-sku">SKU: {{ backlogItem.item_sku }}</div>
        </div>
        <span class="priority-badge" :class="backlogItem.priority">
          {{ t('modals.backlog.priorityBadge', { priority: translatePriority(backlogItem.priority) }) }}
        </span>
      </div>

      <div class="shortage-summary">
        <div class="summary-card danger">
          <div class="summary-label">{{ t('modals.backlog.shortageAmount') }}</div>
          <div class="summary-value">{{ shortage }} {{ t('modals.backlog.units') }}</div>
        </div>
        <div class="summary-card warning">
          <div class="summary-label">{{ t('modals.backlog.daysDelayed') }}</div>
          <div class="summary-value">{{ backlogItem.days_delayed }} {{ t('modals.backlog.days') }}</div>
        </div>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <div class="info-label">{{ t('modals.backlog.orderId') }}</div>
          <div class="info-value order-id">{{ backlogItem.order_id }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.backlog.itemSku') }}</div>
          <div class="info-value sku">{{ backlogItem.item_sku }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.backlog.quantityNeeded') }}</div>
          <div class="info-value">{{ backlogItem.quantity_needed }} {{ t('modals.backlog.units') }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.backlog.quantityAvailable') }}</div>
          <div class="info-value">{{ backlogItem.quantity_available }} {{ t('modals.backlog.units') }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.backlog.expectedDate') }}</div>
          <div class="info-value">{{ formatDate(backlogItem.expected_date) }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.backlog.status') }}</div>
          <div class="info-value">
            <span class="badge danger">{{ t('modals.backlog.backordered') }}</span>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <button class="btn-secondary" @click="close">{{ t('common.close') }}</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import BaseModal from './BaseModal.vue'
import { useI18n } from '../composables/useI18n'

const { t, translateProductName } = useI18n()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  backlogItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return props.backlogItem.quantity_needed - props.backlogItem.quantity_available
})

const close = () => {
  emit('close')
}

const translatePriority = (priority) => {
  const key = `priority.${priority}`
  const translated = t(key)
  return translated === key ? priority : translated
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.shortage-header {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--border);
  margin-bottom: var(--space-6);
}

.shortage-icon {
  width: 64px;
  height: 64px;
  background: var(--color-danger-fg);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-on-accent);
  flex-shrink: 0;
}

.shortage-title-section {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.item-sku {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-family: 'Monaco', 'Courier New', monospace;
}

.priority-badge {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  flex-shrink: 0;
}

.priority-badge.high {
  background: var(--color-danger-subtle);
  color: var(--color-danger-fg);
}

.priority-badge.medium {
  background: var(--color-warning-subtle);
  color: var(--color-warning-fg);
}

.priority-badge.low {
  background: var(--accent-subtle);
  color: var(--color-accent-700);
}

.shortage-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-7);
}

.summary-card {
  padding: var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid;
}

.summary-card.danger {
  border-color: var(--color-danger-subtle);
  background: var(--color-danger-subtle);
}

.summary-card.warning {
  border-color: var(--color-warning-subtle);
  background: var(--color-warning-subtle);
}

.summary-label {
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.summary-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
}

.summary-card.danger .summary-value {
  color: var(--color-danger-fg);
}

.summary-card.warning .summary-value {
  color: var(--color-warning-fg);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-6);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.info-label {
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.info-value {
  font-size: var(--text-base);
  color: var(--text-primary);
  font-weight: 500;
}

.info-value.order-id,
.info-value.sku {
  font-family: 'Monaco', 'Courier New', monospace;
  color: var(--accent);
}

.btn-secondary {
  padding: var(--space-2) var(--space-5);
  background: var(--bg-muted);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-weight: 500;
  font-size: var(--text-sm);
  color: var(--text-primary);
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast);
  font-family: inherit;
}

.btn-secondary:hover {
  background: var(--border);
  border-color: var(--border-strong);
}
</style>
