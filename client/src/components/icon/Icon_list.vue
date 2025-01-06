<script setup>
import data from "@/assets/database.json";
import {defineAsyncComponent, inject, provide, onBeforeMount, onMounted, reactive, ref, watch, shallowRef} from "vue";

const icon_container = defineAsyncComponent(() => import( "@/components/icon/icon_container.vue"))

let search_timeout;
const filtered_data = shallowRef([])

const search = inject("search");
const searching = inject("searching");
const icon_list_ref = ref()

let ico_per_page = 26
let page = 1
let added_icons = 0

function matchFields(data, query) {
  // console.log('query', query)

  const dat = {...data}

  const matchesQuery = (value) => {
    if (typeof (value) !== "string" && query.length < 1) {
      return false;
    }

    // Check for strict matching prefix
    if (query.startsWith("#strict ")) {
      const strictQuery = query.slice(8); // Remove "#strict " prefix
      return value === strictQuery;      // Strict equality check
    }

    // Default behavior: substring matching
    return value.includes(query)
  }

  dat['name']['match'] = matchesQuery(dat['name']['name']) ? 1 : 0;
  dat['category']['match'] = matchesQuery(dat['category']['name']) ? 1 : 0;

  dat['tags'].forEach((elem) => {
    elem['match'] = matchesQuery(elem['name']) ? 1 : 0;
  })
  dat['shapes'].forEach((elem) => {
    elem['match'] = matchesQuery(elem['name']) ? 1 : 0;
  })
  dat['symbols'].forEach((elem) => {
    elem['match'] = matchesQuery(elem['name']) ? 1 : 0;
  })
  dat['colors'].forEach((elem) => {
    elem['match'] = matchesQuery(elem['name']) ? 1 : 0;
  })

  return data;
}

function hasMatch(data) {
  if (Array.isArray(data)) {
    return data.some(hasMatch); // Check if any element in the array has a match
  } else if (typeof data === 'object' && data !== null) {
    if (data['match'] === 1) {
      return true; // Found a match
    }
    return Object.values(data).some(hasMatch); // Check all properties of the object
  }
  return false; // Base case: not an object or array
}

function calc_weight(entry) {
  let total_weight = 0

  total_weight += entry['name']['match'] ? 1 : 0
  total_weight += entry['category']['match'] ? 1 : 0

  total_weight += entry['tags'].reduce((sum, att) => att['match'] ? sum + att['weight'] : sum, 0)
  total_weight += entry['shapes'].reduce((sum, att) => att['match'] ? sum + att['weight'] : sum, 0)
  total_weight += entry['symbols'].reduce((sum, att) => att['match'] ? sum + att['weight'] : sum, 0)
  total_weight += entry['colors'].reduce((sum, att) => att['match'] ? sum + att['weight'] : sum, 0)

  return total_weight
}

async function make_search(append = true) {

  let new_data = data

  if (search.value.length > 0) {
    new_data = new_data.map((entry) => matchFields(entry, search.value))
    new_data = new_data.filter((entry) => hasMatch(entry))
    new_data.sort((a, b) => calc_weight(b) - calc_weight(a))
  }

  if (append) {
    let pushed = new_data.slice(Math.max(0, page - 1) * ico_per_page, page * ico_per_page)
    filtered_data.value = [...filtered_data.value, ...pushed]
    added_icons = pushed.length
  } else {
    page = 1
    filtered_data.value = [...new_data.slice(0, page * ico_per_page)]
    added_icons = ico_per_page
  }

  setTimeout(() => {
    searching.value = search.value.length > 0
  }, 5)
}

function resize_callback() {
  searching.value = false
  check_list_size()
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

  clearTimeout(search_timeout);
  search_timeout = setTimeout(() => {
    requestAnimationFrame(() => {
      make_search(false)
    })
  }, 150); // Delay the operation

})


onMounted(() => {
  // console.log(data)
  make_search()
  new ResizeObserver(resize_callback).observe(icon_list_ref.value)
  addEventListener("scroll", check_list_size)
  check_list_size()
})

</script>
<template>

  <div class="icons_list" ref="icon_list_ref">

    <lazy-component v-for="icon in filtered_data" :key="icon['id']" :threshold="0.1" rootMargin="0px 0px 2000px 0px">
      <component :is="icon_container"
                 :data="icon"/>
    </lazy-component>

  </div>

</template>
<style scoped>

.icons_list {
  content-visibility: auto;
  contain-intrinsic-size: 150px;

  margin-top: 20px;
  /*outline: 1px solid red;*/

  display: flex;
  flex-flow: row wrap;
  justify-content: flex-start;
  align-items: flex-start;
  /*gap: 5px;*/
  /*height: 100%;*/
}

</style>
