<template>
  <BaseModal
    :is-open="isOpen && !!inventoryItem"
    :title="t('modals.inventory.title')"
    size="md"
    @close="close"
  >
    <template v-if="inventoryItem">
      <div class="item-header">
        <div class="item-icon" :class="getStockIconClass()">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <rect x="8" y="12" width="32" height="28" rx="2" stroke="currentColor" stroke-width="2.5"/>
            <path d="M16 8V16M32 8V16M8 20H40" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M16 28H32M16 34H24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="item-title-section">
          <h4 class="item-name">{{ translateProductName(inventoryItem.name) }}</h4>
          <div class="item-sku">SKU: {{ inventoryItem.sku }}</div>
        </div>
        <span class="stock-badge" :class="getStockStatusClass()">
          {{ stockStatusLabel }}
        </span>
      </div>

      <div class="stock-summary">
        <div class="summary-card primary">
          <div class="summary-label">{{ t('modals.inventory.quantityOnHand') }}</div>
          <div class="summary-value">{{ inventoryItem.quantity_on_hand }} {{ t('modals.inventory.units') }}</div>
        </div>
        <div class="summary-card" :class="getSummaryCardClass()">
          <div class="summary-label">{{ t('modals.inventory.stockLevel') }}</div>
          <div class="summary-value">{{ stockPercentage }}%</div>
          <div class="summary-subtitle">{{ t('modals.inventory.vsReorderPoint') }}</div>
        </div>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <div class="info-label">{{ t('modals.inventory.category') }}</div>
          <div class="info-value">{{ inventoryItem.category }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.inventory.location') }}</div>
          <div class="info-value">{{ inventoryItem.location }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.inventory.reorderPoint') }}</div>
          <div class="info-value">{{ inventoryItem.reorder_point }} {{ t('modals.inventory.units') }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.inventory.unitsRemaining') }}</div>
          <div class="info-value">
            <span :style="{ color: inventoryItem.quantity_on_hand <= inventoryItem.reorder_point ? 'var(--color-danger-fg)' : 'var(--color-success-fg)' }">
              {{ inventoryItem.quantity_on_hand - inventoryItem.reorder_point }} {{ t('modals.inventory.units') }}
            </span>
          </div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.inventory.unitCost') }}</div>
          <div class="info-value">{{ currencySymbol }}{{ inventoryItem.unit_cost.toFixed(2) }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.inventory.totalValue') }}</div>
          <div class="info-value total-value">
            {{ currencySymbol }}{{ totalValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
          </div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.inventory.warehouse') }}</div>
          <div class="info-value">{{ translateWarehouse(inventoryItem.location) }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.inventory.status') }}</div>
          <div class="info-value">
            <span :class="['badge', getStockStatusClass()]">
              {{ stockStatusLabel }}
            </span>
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

const { t, currentCurrency, translateProductName, translateWarehouse } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '¥' : '$'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  inventoryItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const totalValue = computed(() => {
  if (!props.inventoryItem) return 0
  return props.inventoryItem.quantity_on_hand * props.inventoryItem.unit_cost
})

const stockPercentage = computed(() => {
  if (!props.inventoryItem || props.inventoryItem.reorder_point === 0) return 0
  return Math.round((props.inventoryItem.quantity_on_hand / props.inventoryItem.reorder_point) * 100)
})

const close = () => {
  emit('close')
}

const getStockStatus = () => {
  if (!props.inventoryItem) return 'Unknown'
  if (props.inventoryItem.quantity_on_hand <= props.inventoryItem.reorder_point) {
    return 'Low Stock'
  } else if (props.inventoryItem.quantity_on_hand <= props.inventoryItem.reorder_point * 1.5) {
    return 'Adequate'
  } else {
    return 'In Stock'
  }
}

const stockStatusLabel = computed(() => {
  const status = getStockStatus()
  if (status === 'Low Stock') return t('status.lowStock')
  if (status === 'Adequate') return t('status.adequate')
  if (status === 'In Stock') return t('status.inStock')
  return t('status.unknown')
})

const getStockStatusClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger'
  if (status === 'Adequate') return 'warning'
  return 'success'
}

const getStockIconClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger-icon'
  if (status === 'Adequate') return 'warning-icon'
  return 'success-icon'
}

const getSummaryCardClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger-card'
  if (status === 'Adequate') return 'warning-card'
  return 'success-card'
}
</script>

<style scoped>
.item-header {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--border);
  margin-bottom: var(--space-6);
}

.item-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-on-accent);
  flex-shrink: 0;
}

.item-icon.success-icon {
  background: var(--color-success-fg);
}

.item-icon.warning-icon {
  background: var(--color-warning-fg);
}

.item-icon.danger-icon {
  background: var(--color-danger-fg);
}

.item-title-section {
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

.stock-badge {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  flex-shrink: 0;
}

.stock-badge.success {
  background: var(--color-success-subtle);
  color: var(--color-success-fg);
}

.stock-badge.warning {
  background: var(--color-warning-subtle);
  color: var(--color-warning-fg);
}

.stock-badge.danger {
  background: var(--color-danger-subtle);
  color: var(--color-danger-fg);
}

.stock-summary {
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

.summary-card.primary {
  border-color: var(--accent-border);
  background: var(--accent-subtle);
}

.summary-card.success-card {
  border-color: var(--color-success-subtle);
  background: var(--color-success-subtle);
}

.summary-card.warning-card {
  border-color: var(--color-warning-subtle);
  background: var(--color-warning-subtle);
}

.summary-card.danger-card {
  border-color: var(--color-danger-subtle);
  background: var(--color-danger-subtle);
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

.summary-subtitle {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin-top: var(--space-1);
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

.info-value.total-value {
  font-size: var(--text-lg);
  color: var(--accent);
  font-weight: 700;
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
