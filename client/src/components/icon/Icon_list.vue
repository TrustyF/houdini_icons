<script setup>
import {icon_data, icon_data_ready, icon_data_promise} from "@/scripts/database.js";
import {inject, onMounted, ref, watch, shallowRef, computed} from "vue";
import Icon_container from "@/components/icon/Icon_container.vue";

let search_timeout;
const filtered_data = shallowRef([])

const search = inject("search");
const searching = inject("searching");
const icon_modal_vis = inject("icon_modal_vis");
const icon_list_ref = ref()
const settings = inject("settings");

// Rendering cost estimate for content-visibility below, so the skipped
// placeholder roughly matches an actual icon_container at the current scale.
const icon_scale = computed(() => settings.icon_scale)
const icon_intrinsic_width = computed(() => `${Math.max(50, Math.round(120 * icon_scale.value))}px`)
const icon_intrinsic_height = computed(() => `${Math.max(60, Math.round(153 * icon_scale.value))}px`)

// Smaller phones mount fewer icons per batch, so infinite scroll stays
// light on weaker devices instead of force-mounting a desktop-sized page.
let ico_per_page = window.innerWidth <= 480 ? 12 : 51
let page = 1
let added_icons = 0

const STRICT_PREFIXES = [
  {prefix: '#strict ', type: null},
  {prefix: '#color ', type: 'color'},
  {prefix: '#tag ', type: 'tag'},
  {prefix: '#symbol ', type: 'symbol'},
  {prefix: '#shape ', type: 'shape'},
]

// Prefix is parsed once per search instead of once per field per entry.
function parse_query(raw) {
  const query = raw.trim().toLowerCase()

  for (const {prefix, type} of STRICT_PREFIXES) {
    if (query.startsWith(prefix)) {
      return {term: query.slice(prefix.length), type, exact: true}
    }
  }

  return {term: query, type: null, exact: false}
}

function matchesQuery(value, type, parsed) {
  if (typeof value !== "string") return false
  if (parsed.exact) return value === parsed.term && (parsed.type === null || type === parsed.type)
  return value.includes(parsed.term)
}

// Single pass per entry: matching and weighting happen together so sorting
// afterwards only compares pre-computed numbers instead of recomputing them.
function match_entry(entry, parsed) {
  let matched = matchesQuery(entry['name'], null, parsed)
  let weight = matched ? 1 : 0

  if (matchesQuery(entry['category'], null, parsed)) {
    matched = true
    weight += 1
  }

  for (const tag of entry['tags']) {
    if (matchesQuery(tag['name'], tag['type'], parsed)) {
      matched = true
      weight += tag['weight']
    }
  }

  return {matched, weight}
}

function run_search(raw) {
  if (!raw) return icon_data.value

  const parsed = parse_query(raw)
  const results = []

  for (const entry of icon_data.value) {
    const {matched, weight} = match_entry(entry, parsed)
    if (matched) results.push({entry, weight})
  }

  results.sort((a, b) => b.weight - a.weight)
  return results.map(({entry}) => entry)
}

// Cached full result for the current query, so pagination during
// infinite scroll just slices it instead of re-running the search.
let search_result = icon_data.value

function make_search(append = true) {

  if (!append) {
    search_result = run_search(String(search.value).trim().toLowerCase())
    page = 1
  }

  let pushed = search_result.slice(Math.max(0, page - 1) * ico_per_page, page * ico_per_page)
  filtered_data.value = append ? [...filtered_data.value, ...pushed] : pushed
  added_icons = pushed.length

  setTimeout(() => {
    searching.value = search.value.length > 0
    check_list_size()
  }, 5)
}

function check_list_size() {
  const padding = 2000

  if (!icon_list_ref.value) return

  const rect = icon_list_ref.value.getBoundingClientRect();
  const windowHeight = window.innerHeight || document.documentElement.clientHeight;

  // Check if the bottom of the element is within the visible viewport
  if (rect.bottom > -padding && rect.bottom <= windowHeight + padding && added_icons > 0) {
    page += 1
    make_search()
    setTimeout(() => check_list_size(), 500)
  }
}

// getBoundingClientRect() above forces a synchronous layout; scroll fires far
// more often than a frame renders, so cap it to once per animation frame
// instead of running that layout read on every single scroll event.
let scroll_ticking = false

function on_scroll() {
  if (scroll_ticking) return
  scroll_ticking = true
  requestAnimationFrame(() => {
    check_list_size()
    scroll_ticking = false
  })
}


// Chunks keep arriving in the background after the first one unblocks the
// UI. Keep the cached result set and the currently-visible page in sync as
// they land, so newly-loaded matches show up without requiring a scroll or
// a re-search.
watch(icon_data, () => {
  search_result = run_search(String(search.value).trim().toLowerCase())
  filtered_data.value = search_result.slice(0, page * ico_per_page)
})

watch(search, (oldV, newV) => {
  icon_modal_vis.value = false

  // Scroll back to the top now, while the old (taller) list is still
  // rendered, so the shorter result set never has to yank the scroll
  // position down when it replaces it a moment later.
  window.scrollTo({top: 0, behavior: 'smooth'})

  clearTimeout(search_timeout);
  search_timeout = setTimeout(() => {
    requestAnimationFrame(() => {
      make_search(false)
    })
  }, 500); // Delay the operation

})

onMounted(async () => {
  await icon_data_promise
  make_search()
  addEventListener("scroll", on_scroll)
  check_list_size()
})

</script>
<template>


  <div class="icons_list"
       ref="icon_list_ref"
       :class="{icon_only: settings.icon_only}"
       :style="{'--icon-scale': icon_scale}">

    <lazy-component class="icon_list_elem"
                    v-for="(icon, index) in filtered_data"
                    :key="icon['id']"
                    :is-intersected="index < ico_per_page"
                    :threshold="0.1" rootMargin="0px 0px 2000px 0px">
      <icon_container :data="icon"/>
    </lazy-component>

    <div :class="`list-spinner ${(searching || !icon_data_ready) ? 'visible':''}`">
      <div class="spinner-border"></div>
    </div>

    <div class="empty" :class="`${(icon_data_ready && filtered_data.length < 1) ? 'empty_vis' : ''}`">
      <h1>No results</h1>
    </div>

  </div>

</template>
<style scoped>

.icons_list {
  position: relative;

  margin-top: 20px;
  margin-bottom: 300px;
  /*outline: 1px solid red;*/

  display: flex;
  flex-flow: row wrap;
  justify-content: flex-start;
  align-items: flex-start;
  /*gap: 5px;*/
}

@media (max-width: 480px) {
  .icons_list {
    justify-content: center;
  }
}

/* Hiding the name/category via a single ancestor class + CSS descendant
   selector (instead of a v-show inside every icon_container instance) means
   toggling "icon only" is one Vue update instead of one per mounted icon. */
.icons_list.icon_only :deep(.icon_name),
.icons_list.icon_only :deep(.icon_category) {
  display: none;
}

.icon_list_elem {
  /* Skip layout/style/paint for icons scrolled off-screen, same benefit
     v-lazy-component gave us, but synchronous (CSS, not an
     IntersectionObserver callback) so there's no delayed pop-in. */
  content-visibility: auto;
  contain-intrinsic-size: auto v-bind(icon_intrinsic_width) auto v-bind(icon_intrinsic_height);

  /* Plain CSS animation instead of <transition-group>: it plays whenever an
     element is newly inserted (i.e. only genuinely new icons, since v-for's
     :key reuses DOM nodes for ones that already existed), with none of
     TransitionGroup's per-update getBoundingClientRect cost across every
     loaded item. */
  /*animation: icon-fade-in 100ms ease;*/
}

@keyframes icon-fade-in {
  from {
    opacity: 0;
  }
}

.list-spinner {
  display: flex;
  justify-content: center;
  width: 100%;

  visibility: hidden;
  opacity: 100;
  transition: 250ms opacity;
}

.empty {
  display: flex;
  justify-content: center;
  width: 100%;

  visibility: hidden;
  opacity: 0;
  transition: 250ms opacity;
  /*transition-delay: 500ms;*/
}

.empty_vis {
  transition-delay: 250ms;
  visibility: visible;
  opacity: 1;
}

.visible {
  transition-delay: 250ms;
  visibility: visible;
  opacity: 0;
}

</style>
