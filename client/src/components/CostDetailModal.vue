<template>
  <BaseModal
    :is-open="isOpen && !!costData"
    :title="costData ? t('modals.cost.title', { month: costData.month }) : ''"
    size="md"
    @close="close"
  >
    <template v-if="costData">
      <div class="cost-summary">
        <div class="summary-card total">
          <div class="summary-label">{{ t('modals.cost.totalCosts') }}</div>
          <div class="summary-value">{{ currencySymbol }}{{ totalCosts.toLocaleString() }}</div>
        </div>
      </div>

      <div class="cost-breakdown">
        <div class="cost-item procurement">
          <div class="cost-header">
            <div class="cost-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <rect x="4" y="6" width="16" height="14" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M8 6V4M16 6V4M4 10H20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="cost-info">
              <div class="cost-name">{{ t('modals.cost.procurement') }}</div>
              <div class="cost-amount">{{ currencySymbol }}{{ costData.procurement.toLocaleString() }}</div>
            </div>
          </div>
          <div class="cost-percentage">{{ getProcurementPercentage() }}{{ t('modals.cost.ofTotal') }}</div>
        </div>

        <div class="cost-item operational">
          <div class="cost-header">
            <div class="cost-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2"/>
                <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="cost-info">
              <div class="cost-name">{{ t('modals.cost.operational') }}</div>
              <div class="cost-amount">{{ currencySymbol }}{{ costData.operational.toLocaleString() }}</div>
            </div>
          </div>
          <div class="cost-percentage">{{ getOperationalPercentage() }}{{ t('modals.cost.ofTotal') }}</div>
        </div>

        <div class="cost-item labor">
          <div class="cost-header">
            <div class="cost-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="2"/>
                <path d="M6 20C6 16.6863 8.68629 14 12 14C15.3137 14 18 16.6863 18 20" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="cost-info">
              <div class="cost-name">{{ t('modals.cost.labor') }}</div>
              <div class="cost-amount">{{ currencySymbol }}{{ costData.labor.toLocaleString() }}</div>
            </div>
          </div>
          <div class="cost-percentage">{{ getLaborPercentage() }}{{ t('modals.cost.ofTotal') }}</div>
        </div>

        <div class="cost-item overhead">
          <div class="cost-header">
            <div class="cost-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M3 12L5 10M5 10L12 3L19 10M5 10V20C5 20.5523 5.44772 21 6 21H9M19 10L21 12M19 10V20C19 20.5523 18.5523 21 18 21H15M9 21C9 21 9 18 9 16C9 14 10 14 12 14C14 14 15 14 15 16C15 18 15 21 15 21M9 21H15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="cost-info">
              <div class="cost-name">{{ t('modals.cost.overhead') }}</div>
              <div class="cost-amount">{{ currencySymbol }}{{ costData.overhead.toLocaleString() }}</div>
            </div>
          </div>
          <div class="cost-percentage">{{ getOverheadPercentage() }}{{ t('modals.cost.ofTotal') }}</div>
        </div>
      </div>
    </template>

    <template #footer>
      <button class="btn-secondary" @click="close">{{ t('modals.cost.close') }}</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import BaseModal from './BaseModal.vue'
import { useI18n } from '../composables/useI18n'

const { t, currentCurrency } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '¥' : '$'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  costData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const totalCosts = computed(() => {
  if (!props.costData) return 0
  return props.costData.procurement + props.costData.operational +
         props.costData.labor + props.costData.overhead
})

const getProcurementPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.procurement / totalCosts.value) * 100).toFixed(1)
}

const getOperationalPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.operational / totalCosts.value) * 100).toFixed(1)
}

const getLaborPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.labor / totalCosts.value) * 100).toFixed(1)
}

const getOverheadPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.overhead / totalCosts.value) * 100).toFixed(1)
}

const close = () => {
  emit('close')
}
</script>

<style scoped>
.cost-summary {
  margin-bottom: var(--space-7);
}

.summary-card {
  padding: var(--space-6);
  border-radius: var(--radius-md);
  text-align: center;
}

.summary-card.total {
  background: var(--accent);
  color: var(--text-on-accent);
}

.summary-label {
  font-size: var(--text-sm);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.9;
  margin-bottom: var(--space-2);
}

.summary-value {
  font-size: var(--text-3xl);
  font-weight: 700;
}

.cost-breakdown {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.cost-item {
  padding: var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid;
}

.cost-item.procurement {
  border-color: var(--accent-border);
  background: var(--accent-subtle);
}

.cost-item.operational {
  border-color: var(--border-strong);
  background: var(--bg-muted);
}

.cost-item.labor {
  border-color: var(--color-success-subtle);
  background: var(--color-success-subtle);
}

.cost-item.overhead {
  border-color: var(--color-warning-subtle);
  background: var(--color-warning-subtle);
}

.cost-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-2);
}

.cost-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--text-on-accent);
}

.cost-item.procurement .cost-icon {
  background: var(--accent);
}

.cost-item.operational .cost-icon {
  background: var(--text-secondary);
}

.cost-item.labor .cost-icon {
  background: var(--color-success-fg);
}

.cost-item.overhead .cost-icon {
  background: var(--color-warning-fg);
}

.cost-info {
  flex: 1;
}

.cost-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: var(--text-md);
  margin-bottom: var(--space-1);
}

.cost-amount {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--text-primary);
}

.cost-percentage {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: 500;
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
