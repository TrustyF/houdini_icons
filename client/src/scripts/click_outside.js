// Centralized ignore list here:
const GLOBAL_IGNORE_SELECTORS = [
  '.settings_header',
  '.no-close-area',
  '[data-ignore-outside]',
]

export const clickOutside = {
  beforeMount(el, binding) {
    // Handler passed from component
    const handler = typeof binding.value === 'function'
      ? binding.value
      : binding.value.handler

    // Merge local + global ignore selectors
    const localIgnore =
      typeof binding.value === 'object' && binding.value.ignore
        ? binding.value.ignore
        : []

    el.__ignoreSelectors__ = [...GLOBAL_IGNORE_SELECTORS, ...localIgnore]
    el.__handler__ = handler

    el.__pointerDown__ = false

    el.__onPointerDown__ = event => {
      if (isIgnored(event, el)) return
      if (!el.contains(event.target)) {
        el.__pointerDown__ = true
      }
    }

    el.__onClick__ = event => {
      if (!el.__pointerDown__) return
      if (isIgnored(event, el)) return
      if (!el.contains(event.target)) {
        el.__handler__(event)
      }
      el.__pointerDown__ = false
    }

    document.addEventListener('pointerdown', el.__onPointerDown__, true)
    document.addEventListener('click', el.__onClick__, true)
  },

  unmounted(el) {
    document.removeEventListener('pointerdown', el.__onPointerDown__, true)
    document.removeEventListener('click', el.__onClick__, true)
    delete el.__ignoreSelectors__
    delete el.__handler__
    delete el.__onPointerDown__
    delete el.__onClick__
  },
}

function isIgnored(event, el) {
  return (el.__ignoreSelectors__ || []).some(sel => {
    try {
      return event.target.closest(sel)
    } catch {
      return false
    }
  })
}
