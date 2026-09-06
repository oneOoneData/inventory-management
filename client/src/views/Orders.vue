<template>
  <div class="orders">
    <div class="page-header">
      <h2>{{ t('orders.title') }}</h2>
      <p>{{ t('orders.description') }}</p>
    </div>

    <div v-if="loading && initialLoad" class="loading">
      {{ t('common.loading') }}
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else :aria-busy="loading" :class="{ 'is-updating': loading }">
      <div v-if="loading" class="updating-indicator" role="status">
        {{ t('common.updating') }}
      </div>
      <div class="stats-grid">
        <div class="stat-card success">
          <div class="stat-label">{{ t('status.delivered') }}</div>
          <div class="stat-value">
            {{ getOrdersByStatus('Delivered').length }}
          </div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('status.shipped') }}</div>
          <div class="stat-value">
            {{ getOrdersByStatus('Shipped').length }}
          </div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('status.processing') }}</div>
          <div class="stat-value">
            {{ getOrdersByStatus('Processing').length }}
          </div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">{{ t('status.backordered') }}</div>
          <div class="stat-value">
            {{ getOrdersByStatus('Backordered').length }}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            {{ t('orders.allOrders') }} ({{ orders.length }})
          </h3>
        </div>
        <div class="table-container">
          <table class="orders-table">
            <thead>
              <tr>
                <th class="col-order-number">
                  {{ t('orders.table.orderNumber') }}
                </th>
                <th class="col-customer">{{ t('orders.table.customer') }}</th>
                <th class="col-items">{{ t('orders.table.items') }}</th>
                <th class="col-status">{{ t('orders.table.status') }}</th>
                <th class="col-date">{{ t('orders.table.orderDate') }}</th>
                <th class="col-date">
                  {{ t('orders.table.expectedDelivery') }}
                </th>
                <th class="col-value">{{ t('orders.table.totalValue') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in orders" :key="order.id">
                <td class="col-order-number">
                  <strong>{{ order.order_number }}</strong>
                </td>
                <td class="col-customer">
                  {{ translateCustomerName(order.customer) }}
                </td>
                <td class="col-items">
                  <details class="items-details">
                    <summary class="items-summary">
                      {{
                        t('orders.itemsCount', { count: order.items.length })
                      }}
                    </summary>
                    <div class="items-dropdown">
                      <div
                        v-for="(item, idx) in order.items"
                        :key="idx"
                        class="item-entry"
                      >
                        <span class="item-name">{{
                          translateProductName(item.name)
                        }}</span>
                        <span class="item-meta"
                          >{{ t('orders.quantity') }}: {{ item.quantity }} @
                          {{ currencySymbol }}{{ item.unit_price }}</span
                        >
                      </div>
                    </div>
                  </details>
                </td>
                <td class="col-status">
                  <span :class="['badge', getOrderStatusClass(order.status)]">
                    {{ t(`status.${order.status.toLowerCase()}`) }}
                  </span>
                </td>
                <td class="col-date">{{ formatDate(order.order_date) }}</td>
                <td class="col-date">
                  {{ formatDate(order.expected_delivery) }}
                </td>
                <td class="col-value">
                  <strong
                    >{{ currencySymbol
                    }}{{ order.total_value.toLocaleString() }}</strong
                  >
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { debounce } from '../utils/debounce'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Orders',
  setup() {
    const { t, currentCurrency, translateProductName, translateCustomerName } =
      useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })
    const loading = ref(true)
    const initialLoad = ref(true)
    const error = ref(null)
    const orders = ref([])

    // Use shared filters
    const {
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      getCurrentFilters
    } = useFilters()

    // Guards against an earlier slow response overwriting a newer filtered one.
    let loadToken = 0

    const loadOrders = async () => {
      const myToken = ++loadToken
      try {
        loading.value = true
        const filters = getCurrentFilters()
        const fetchedOrders = await api.getOrders(filters)
        if (myToken !== loadToken) return

        // Sort orders by order_date (earliest first)
        orders.value = fetchedOrders.sort((a, b) => {
          const dateA = new Date(a.order_date)
          const dateB = new Date(b.order_date)
          return dateA - dateB
        })
      } catch (err) {
        if (myToken !== loadToken) return
        error.value = 'Failed to load orders: ' + err.message
        console.error(err)
      } finally {
        if (myToken === loadToken) {
          loading.value = false
          initialLoad.value = false
        }
      }
    }

    // Watch for filter changes and reload data (debounced to coalesce rapid changes)
    watch(
      [selectedPeriod, selectedLocation, selectedCategory, selectedStatus],
      debounce(() => {
        loadOrders()
      }, 250)
    )

    const getOrdersByStatus = (status) => {
      return orders.value.filter((order) => order.status === status)
    }

    const getOrderStatusClass = (status) => {
      const statusMap = {
        Delivered: 'success',
        Shipped: 'info',
        Processing: 'warning',
        Backordered: 'danger'
      }
      return statusMap[status] || 'info'
    }

    const formatDate = (dateString) => {
      const { currentLocale } = useI18n()
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return new Date(dateString).toLocaleDateString(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(loadOrders)

    return {
      t,
      loading,
      initialLoad,
      error,
      orders,
      getOrdersByStatus,
      getOrderStatusClass,
      formatDate,
      currencySymbol,
      translateProductName,
      translateCustomerName
    }
  }
}
</script>

<style scoped>
/* Refetch-in-progress: keep the last data visible but dim it and show a hint. */
.is-updating {
  opacity: 0.6;
  transition: opacity var(--transition);
  pointer-events: none;
}

.updating-indicator {
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-3);
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-muted);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  text-align: center;
}

/* Fixed table layout to prevent column shifting */
.orders-table {
  table-layout: fixed;
  width: 100%;
}

/* Column widths */
.col-order-number {
  width: 130px;
}

.col-customer {
  width: 180px;
}

.col-items {
  width: 200px;
}

.col-status {
  width: 130px;
}

.col-date {
  width: 140px;
}

.col-value {
  width: 120px;
}

/* Items details styling */
.items-details {
  position: relative;
}

.items-summary {
  cursor: pointer;
  color: var(--accent);
  font-weight: 500;
  list-style: none;
  user-select: none;
  display: inline-block;
}

.items-summary::-webkit-details-marker {
  display: none;
}

.items-summary::before {
  content: '▶';
  display: inline-block;
  margin-right: var(--space-1);
  font-size: var(--text-xs);
  transition: transform var(--transition);
}

.items-details[open] .items-summary::before {
  transform: rotate(90deg);
}

.items-summary:hover {
  color: var(--accent-hover);
  text-decoration: underline;
}

/* Dropdown container */
.items-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: var(--space-2);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  padding: var(--space-3);
  z-index: var(--z-dropdown);
  min-width: 300px;
  max-width: 400px;
}

.item-entry {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-2);
  border-bottom: 1px solid var(--border);
}

.item-entry:last-child {
  border-bottom: none;
}

.item-name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.item-meta {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}
</style>
