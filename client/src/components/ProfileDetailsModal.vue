<template>
  <BaseModal
    :is-open="isOpen"
    :title="t('profileDetails.title')"
    size="md"
    @close="close"
  >
    <div class="profile-section">
      <div class="avatar-section">
        <div class="avatar-xl">
          {{ getInitials(currentUser.name) }}
        </div>
        <h4 class="profile-name">{{ currentUser.name }}</h4>
        <p class="profile-job-title">{{ currentUser.jobTitle }}</p>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.email') }}</div>
          <div class="info-value">{{ currentUser.email }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.department') }}</div>
          <div class="info-value">{{ currentUser.department }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.location') }}</div>
          <div class="info-value">{{ currentUser.location }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.phone') }}</div>
          <div class="info-value">{{ currentUser.phone }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.joinDate') }}</div>
          <div class="info-value">{{ formatDate(currentUser.joinDate) }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.employeeId') }}</div>
          <div class="info-value">CC-{{ currentUser.id.toString().padStart(5, '0') }}</div>
        </div>
      </div>
    </div>

    <template #footer>
      <button class="btn-secondary" @click="close">{{ t('profileDetails.close') }}</button>
    </template>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'
import { useAuth } from '../composables/useAuth'
import { useI18n } from '../composables/useI18n'

const { currentUser, getInitials } = useAuth()
const { t, currentLocale } = useI18n()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
  return date.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.profile-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-7);
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--border);
}

.avatar-xl {
  width: 96px;
  height: 96px;
  border-radius: var(--radius-full);
  background: var(--accent);
  color: var(--text-on-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: var(--text-3xl);
  letter-spacing: 0.025em;
  box-shadow: var(--shadow-sm);
}

.profile-name {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.profile-job-title {
  font-size: var(--text-md);
  color: var(--text-secondary);
  margin: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
