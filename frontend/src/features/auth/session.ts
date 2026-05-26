import { computed, ref } from 'vue'

export type CurrentOwner = {
  owner_id: string
  name: string
  login_id: string
}

const currentOwner = ref<CurrentOwner | null>(null)

export function useCurrentOwner() {
  return computed(() => currentOwner.value)
}

export function getCurrentOwner(): CurrentOwner | null {
  return currentOwner.value
}

export function setCurrentOwner(owner: CurrentOwner): void {
  currentOwner.value = owner
}

export function clearCurrentOwner(): void {
  currentOwner.value = null
}
