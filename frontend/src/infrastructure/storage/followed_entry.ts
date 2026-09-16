const key = 'mesa247-followed-entry-id'
export const followedEntryStorage = {
  get: (): number | null => { const value = Number.parseInt(localStorage.getItem(key) || '', 10); return Number.isFinite(value) ? value : null },
  set: (id: number) => localStorage.setItem(key, String(id)),
  clear: () => localStorage.removeItem(key),
}
