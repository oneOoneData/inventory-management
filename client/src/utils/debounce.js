// Small debounce helper. Used to coalesce rapid filter-bar changes into a single
// data reload instead of firing a burst of requests (one per dropdown change).
export function debounce(fn, delay = 250) {
  let timer = null
  const debounced = (...args) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      timer = null
      fn(...args)
    }, delay)
  }
  debounced.cancel = () => {
    if (timer) clearTimeout(timer)
    timer = null
  }
  return debounced
}
