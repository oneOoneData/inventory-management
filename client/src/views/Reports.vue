<template>
  <div class="reports">
    <div class="page-header">
      <h2>{{ t('reports.title') }}</h2>
      <p>{{ t('reports.subtitle') }}</p>
    </div>

    <div v-if="loading && initialLoad" class="loading">
      {{ t('reports.loading') }}
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else :aria-busy="loading" :class="{ 'is-updating': loading }">
      <div v-if="loading" class="updating-indicator" role="status">
        {{ t('common.updating') }}
      </div>

      <div v-if="isEmpty" class="card">
        <p class="no-data">{{ t('reports.noDataForFilters') }}</p>
      </div>

      <template v-else>
        <!-- Quarterly Performance -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">{{ t('reports.quarterlyPerformance') }}</h3>
          </div>
          <div v-if="quarterlyData.length === 0" class="no-data">
            {{ t('reports.noDataForFilters') }}
          </div>
          <div v-else class="table-container">
            <table class="reports-table">
              <thead>
                <tr>
                  <th>{{ t('reports.table.quarter') }}</th>
                  <th>{{ t('reports.table.totalOrders') }}</th>
                  <th>{{ t('reports.table.totalRevenue') }}</th>
                  <th>{{ t('reports.table.avgOrderValue') }}</th>
                  <th>{{ t('reports.table.fulfillmentRate') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="q in quarterlyData" :key="q.quarter">
                  <td>
                    <strong>{{ q.quarter }}</strong>
                  </td>
                  <td>{{ q.total_orders.toLocaleString(numberLocale) }}</td>
                  <td>{{ money(q.total_revenue) }}</td>
                  <td>{{ money(q.avg_order_value) }}</td>
                  <td>
                    <span :class="getFulfillmentClass(q.fulfillment_rate)">
                      {{ q.fulfillment_rate }}%
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Monthly Trends Chart -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">{{ t('reports.monthlyRevenueTrend') }}</h3>
          </div>
          <div v-if="monthlyData.length === 0" class="no-data">
            {{ t('reports.noDataForFilters') }}
          </div>
          <div
            v-else
            class="chart-container"
            role="img"
            :aria-label="monthlyChartLabel"
          >
            <div class="bar-chart">
              <div
                v-for="month in monthlyData"
                :key="month.month"
                class="bar-wrapper"
              >
                <div class="bar-container">
                  <div
                    class="bar"
                    :style="{ height: getBarHeight(month.revenue) + 'px' }"
                    :title="money(month.revenue)"
                  ></div>
                </div>
                <div class="bar-label">{{ formatMonth(month.month) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Month-over-Month Comparison -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">{{ t('reports.momAnalysis') }}</h3>
          </div>
          <div v-if="monthlyData.length === 0" class="no-data">
            {{ t('reports.noDataForFilters') }}
          </div>
          <div v-else class="table-container">
            <table class="reports-table">
              <thead>
                <tr>
                  <th>{{ t('reports.table.month') }}</th>
                  <th>{{ t('reports.table.orders') }}</th>
                  <th>{{ t('reports.table.revenue') }}</th>
                  <th>{{ t('reports.table.change') }}</th>
                  <th>{{ t('reports.table.growthRate') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(month, index) in monthlyData" :key="month.month">
                  <td>
                    <strong>{{ formatMonth(month.month) }}</strong>
                  </td>
                  <td>{{ month.order_count.toLocaleString(numberLocale) }}</td>
                  <td>{{ money(month.revenue) }}</td>
                  <td>
                    <span
                      v-if="index > 0"
                      :class="
                        getChangeClass(
                          month.revenue,
                          monthlyData[index - 1].revenue
                        )
                      "
                    >
                      {{
                        getChangeValue(
                          month.revenue,
                          monthlyData[index - 1].revenue
                        )
                      }}
                    </span>
                    <span v-else>-</span>
                  </td>
                  <td>
                    <span
                      v-if="index > 0"
                      :class="
                        getChangeClass(
                          month.revenue,
                          monthlyData[index - 1].revenue
                        )
                      "
                    >
                      {{
                        getGrowthRate(
                          month.revenue,
                          monthlyData[index - 1].revenue
                        )
                      }}
                    </span>
                    <span v-else>-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Summary Stats -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">
              {{ t('reports.stats.totalRevenueYTD') }}
            </div>
            <div class="stat-value">{{ money(totalRevenue) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">
              {{ t('reports.stats.avgMonthlyRevenue') }}
            </div>
            <div class="stat-value">{{ money(avgMonthlyRevenue) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">
              {{ t('reports.stats.totalOrdersYTD') }}
            </div>
            <div class="stat-value">
              {{ totalOrders.toLocaleString(numberLocale) }}
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-label">{{ t('reports.stats.bestQuarter') }}</div>
            <div class="stat-value">{{ bestQuarter }}</div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '../api'
import { debounce } from '../utils/debounce'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { formatCurrency } from '../utils/currency'

const MONTH_KEYS = [
  'jan',
  'feb',
  'mar',
  'apr',
  'may',
  'jun',
  'jul',
  'aug',
  'sep',
  'oct',
  'nov',
  'dec'
]

export default {
  name: 'Reports',
  setup() {
    const { t, currentCurrency, currentLocale } = useI18n()
    const {
      getCurrentFilters,
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus
    } = useFilters()

    const loading = ref(true)
    const initialLoad = ref(true)
    const error = ref(null)
    const quarterlyData = ref([])
    const monthlyData = ref([])

    const numberLocale = computed(() =>
      currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
    )
    const money = (value) => formatCurrency(value || 0, currentCurrency.value)

    const isEmpty = computed(
      () => quarterlyData.value.length === 0 && monthlyData.value.length === 0
    )

    // Summary stats derived from the loaded data (never hand-recalculated on assignment).
    const totalRevenue = computed(() =>
      monthlyData.value.reduce((sum, m) => sum + (m.revenue || 0), 0)
    )
    const avgMonthlyRevenue = computed(() =>
      monthlyData.value.length > 0
        ? totalRevenue.value / monthlyData.value.length
        : 0
    )
    const totalOrders = computed(() =>
      monthlyData.value.reduce((sum, m) => sum + (m.order_count || 0), 0)
    )
    const bestQuarter = computed(() => {
      let best = ''
      let bestRevenue = -Infinity
      for (const q of quarterlyData.value) {
        if (q.total_revenue > bestRevenue) {
          bestRevenue = q.total_revenue
          best = q.quarter
        }
      }
      return best || t('common.notAvailable')
    })

    // Chart scale computed once instead of re-reducing on every getBarHeight call.
    const maxMonthlyRevenue = computed(() =>
      monthlyData.value.reduce((max, m) => Math.max(max, m.revenue || 0), 0)
    )

    const monthlyChartLabel = computed(() => {
      if (monthlyData.value.length === 0)
        return t('reports.monthlyRevenueTrend')
      const first = formatMonth(monthlyData.value[0].month)
      const last = formatMonth(
        monthlyData.value[monthlyData.value.length - 1].month
      )
      return `${t('reports.monthlyRevenueChartLabel')}, ${first}–${last}`
    })

    // Guards against an earlier slow response overwriting a newer filtered one.
    let loadToken = 0

    const loadData = async () => {
      const myToken = ++loadToken
      try {
        loading.value = true
        error.value = null
        const filters = getCurrentFilters()

        const [quarterly, monthly] = await Promise.all([
          api.getQuarterlyReports(filters),
          api.getMonthlyTrends(filters)
        ])

        if (myToken !== loadToken) return

        quarterlyData.value = quarterly
        monthlyData.value = monthly
      } catch (err) {
        if (myToken !== loadToken) return
        error.value = t('reports.loadError')
        console.error(err)
      } finally {
        if (myToken === loadToken) {
          loading.value = false
          initialLoad.value = false
        }
      }
    }

    function formatMonth(monthStr) {
      if (!monthStr || typeof monthStr !== 'string') return monthStr || ''
      const [year, month] = monthStr.split('-')
      const idx = parseInt(month, 10) - 1
      if (Number.isNaN(idx) || idx < 0 || idx > 11) return monthStr
      return `${t(`months.${MONTH_KEYS[idx]}`)} ${year}`
    }

    const getBarHeight = (revenue) => {
      if (maxMonthlyRevenue.value === 0) return 0
      return (revenue / maxMonthlyRevenue.value) * 200
    }

    const getFulfillmentClass = (rate) => {
      if (rate >= 90) return 'badge success'
      if (rate >= 75) return 'badge warning'
      return 'badge danger'
    }

    const getChangeValue = (current, previous) => {
      const change = current - previous
      const sign = change > 0 ? '+' : change < 0 ? '-' : ''
      return sign + money(Math.abs(change))
    }

    const getChangeClass = (current, previous) => {
      const change = current - previous
      if (change > 0) return 'positive-change'
      if (change < 0) return 'negative-change'
      return ''
    }

    const getGrowthRate = (current, previous) => {
      if (previous === 0) return t('common.notAvailable')
      const rate = ((current - previous) / previous) * 100
      const sign = rate > 0 ? '+' : ''
      return `${sign}${rate.toFixed(1)}%`
    }

    watch(
      [selectedPeriod, selectedLocation, selectedCategory, selectedStatus],
      debounce(() => {
        loadData()
      }, 250)
    )

    onMounted(loadData)

    return {
      t,
      loading,
      initialLoad,
      error,
      quarterlyData,
      monthlyData,
      isEmpty,
      numberLocale,
      money,
      totalRevenue,
      avgMonthlyRevenue,
      totalOrders,
      bestQuarter,
      monthlyChartLabel,
      formatMonth,
      getBarHeight,
      getFulfillmentClass,
      getChangeValue,
      getChangeClass,
      getGrowthRate
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

.no-data {
  padding: var(--space-7);
  text-align: center;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.chart-container {
  padding: var(--space-7) var(--space-4);
  min-height: 300px;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 250px;
  gap: var(--space-2);
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 80px;
}

.bar-container {
  height: 200px;
  display: flex;
  align-items: flex-end;
  width: 100%;
}

.bar {
  width: 100%;
  background: var(--accent);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: background var(--transition);
  cursor: pointer;
}

.bar:hover {
  background: var(--accent-hover);
}

.bar-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  text-align: center;
  transform: rotate(-45deg);
  white-space: nowrap;
  margin-top: var(--space-6);
}

.positive-change {
  color: var(--color-success-fg);
  font-weight: 600;
}

.negative-change {
  color: var(--color-danger-fg);
  font-weight: 600;
}
</style>
