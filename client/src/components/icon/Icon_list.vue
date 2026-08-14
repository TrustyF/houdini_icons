<script setup>
import data from "@/assets/database.json";
import {inject, onMounted, ref, watch, shallowRef} from "vue";
import Icon_container from "@/components/icon/Icon_container.vue";

let search_timeout;
const filtered_data = shallowRef([])

const search = inject("search");
const searching = inject("searching");
const icon_modal_vis = inject("icon_modal_vis");
const icon_list_ref = ref()

let ico_per_page = 51
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
  if (!raw) return data

  const parsed = parse_query(raw)
  const results = []

  for (const entry of data) {
    const {matched, weight} = match_entry(entry, parsed)
    if (matched) results.push({entry, weight})
  }

  results.sort((a, b) => b.weight - a.weight)
  return results.map(({entry}) => entry)
}

// Cached full result for the current query, so pagination during
// infinite scroll just slices it instead of re-running the search.
let search_result = data

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

onMounted(() => {
  make_search()
  addEventListener("scroll", check_list_size)
  check_list_size()
})

</script>
<template>


  <div class="icons_list" ref="icon_list_ref">

    <lazy-component class="icon_list_elem"
                    v-for="icon in filtered_data"
                    :key="icon['id']" :threshold="0.1" rootMargin="0px 0px 2000px 0px">
      <icon_container :data="icon"/>
    </lazy-component>

    <div :class="`list-spinner ${searching ? 'visible':''}`">
      <div class="spinner-border"></div>
    </div>

    <div class="empty" :class="`${filtered_data.length < 1 ? 'empty_vis' : ''}`">
      <h1>No results</h1>
    </div>

  </div>

</template>
<style scoped>

.icons_list {
  content-visibility: auto;
  contain-intrinsic-size: 150px;
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

.icon_list_elem {

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
