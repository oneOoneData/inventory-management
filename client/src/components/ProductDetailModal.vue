<template>
  <BaseModal
    :is-open="isOpen && !!product"
    :title="t('modals.product.title')"
    size="md"
    @close="close"
  >
    <template v-if="product">
      <div class="product-header">
        <div class="product-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <rect x="8" y="12" width="32" height="28" rx="2" stroke="currentColor" stroke-width="2.5"/>
            <path d="M16 8V16M32 8V16M8 20H40" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="product-title-section">
          <h4 class="product-name">{{ product.name }}</h4>
          <div class="product-sku">SKU: {{ product.sku }}</div>
        </div>
        <span class="stock-badge" :class="getStockBadgeClass(product.stockLevel)">
          {{ product.stockLevel }}
        </span>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <div class="info-label">{{ t('modals.product.category') }}</div>
          <div class="info-value">{{ product.category }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.product.warehouse') }}</div>
          <div class="info-value">{{ product.warehouse }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.product.unitsOrdered') }}</div>
          <div class="info-value">{{ product.unitsOrdered }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.product.totalRevenue') }}</div>
          <div class="info-value">{{ currencySymbol }}{{ product.revenue.toLocaleString() }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.product.currentStock') }}</div>
          <div class="info-value">{{ product.quantityOnHand }} {{ t('modals.product.units') }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.product.reorderPoint') }}</div>
          <div class="info-value">{{ product.reorderPoint }} {{ t('modals.product.units') }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.product.firstOrderDate') }}</div>
          <div class="info-value">{{ formatDate(product.firstOrderDate) }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('modals.product.stockStatus') }}</div>
          <div class="info-value">
            <span :class="['badge', getStockBadgeClass(product.stockLevel)]">
              {{ product.stockLevel }}
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

const { t, currentCurrency } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '¥' : '$'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
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

const getStockBadgeClass = (stockLevel) => {
  if (stockLevel === 'In Stock') return 'success'
  if (stockLevel === 'Low Stock') return 'warning'
  if (stockLevel === 'Out of Stock') return 'danger'
  return 'info'
}
</script>

<style scoped>
.product-header {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--border);
  margin-bottom: var(--space-7);
}

.product-icon {
  width: 64px;
  height: 64px;
  background: var(--accent);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-on-accent);
  flex-shrink: 0;
}

.product-title-section {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.product-sku {
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
