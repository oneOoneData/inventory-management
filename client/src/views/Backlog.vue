<template>
  <div class="backlog">
    <div class="page-header">
      <h2>Backlog Management</h2>
      <p>Track and resolve inventory shortages</p>
    </div>

    <div v-if="loading && initialLoad" class="loading">Loading backlog...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else :aria-busy="loading" :class="{ 'is-updating': loading }">
      <div v-if="loading" class="updating-indicator" role="status">
        Updating…
      </div>
      <div class="stats-grid">
        <div class="stat-card danger">
          <div class="stat-label">High Priority</div>
          <div class="stat-value">
            {{ getBacklogByPriority('high').length }}
          </div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">Medium Priority</div>
          <div class="stat-value">
            {{ getBacklogByPriority('medium').length }}
          </div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">Low Priority</div>
          <div class="stat-value">{{ getBacklogByPriority('low').length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Total Backlog Items</div>
          <div class="stat-value">{{ backlogItems.length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Backlog Items</h3>
        </div>
        <div
          v-if="backlogItems.length === 0"
          style="padding: 3rem; text-align: center"
        >
          <p style="font-size: 1.125rem; color: #10b981; font-weight: 600">
            ✓ No backlog items - all orders can be fulfilled!
          </p>
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>Order ID</th>
                <th>SKU</th>
                <th>Item Name</th>
                <th>Quantity Needed</th>
                <th>Quantity Available</th>
                <th>Shortage</th>
                <th>Days Delayed</th>
                <th>Priority</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in backlogItems" :key="item.id">
                <td>
                  <strong>{{ item.order_id }}</strong>
                </td>
                <td>
                  <strong>{{ item.item_sku }}</strong>
                </td>
                <td>{{ item.item_name }}</td>
                <td>{{ item.quantity_needed }}</td>
                <td>{{ item.quantity_available }}</td>
                <td>
                  <span class="badge danger">
                    {{ item.quantity_needed - item.quantity_available }} units
                    short
                  </span>
                </td>
                <td>
                  <span
                    :style="{
                      color: item.days_delayed > 7 ? '#ef4444' : '#f59e0b'
                    }"
                  >
                    {{ item.days_delayed }} days
                  </span>
                </td>
                <td>
                  <span :class="['badge', item.priority]">
                    {{ item.priority }}
                  </span>
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

export default {
  name: 'Backlog',
  setup() {
    const loading = ref(true)
    const initialLoad = ref(true)
    const error = ref(null)
    const allBacklogItems = ref([])
    const inventoryItems = ref([])

    // Use shared filters
    const { selectedLocation, selectedCategory, getCurrentFilters } =
      useFilters()

    // Filter backlog based on inventory filters
    const backlogItems = computed(() => {
      if (
        selectedLocation.value === 'all' &&
        selectedCategory.value === 'all'
      ) {
        return allBacklogItems.value
      }

      // Get SKUs of items that match the filters
      const validSkus = new Set(inventoryItems.value.map((item) => item.sku))
      return allBacklogItems.value.filter((b) => validSkus.has(b.item_sku))
    })

    // Guards against an earlier slow response overwriting a newer filtered one.
    let loadToken = 0

    const loadBacklog = async () => {
      const myToken = ++loadToken
      try {
        loading.value = true
        const filters = getCurrentFilters()

        const [backlogData, inventoryData] = await Promise.all([
          api.getBacklog(),
          api.getInventory({
            warehouse: filters.warehouse,
            category: filters.category
          })
        ])

        if (myToken !== loadToken) return

        allBacklogItems.value = backlogData
        inventoryItems.value = inventoryData
      } catch (err) {
        if (myToken !== loadToken) return
        error.value = 'Failed to load backlog: ' + err.message
        console.error(err)
      } finally {
        if (myToken === loadToken) {
          loading.value = false
          initialLoad.value = false
        }
      }
    }

    const getBacklogByPriority = (priority) => {
      return backlogItems.value.filter((item) => item.priority === priority)
    }

    // Watch for filter changes and reload data (debounced to coalesce rapid changes)
    watch(
      [selectedLocation, selectedCategory],
      debounce(() => {
        loadBacklog()
      }, 250)
    )

    onMounted(loadBacklog)

    return {
      loading,
      initialLoad,
      error,
      backlogItems,
      getBacklogByPriority
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
</style>
