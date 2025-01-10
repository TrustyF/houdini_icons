<script setup>
import data from "@/assets/database.json";
import {defineAsyncComponent, inject, provide, onBeforeMount, onMounted, reactive, ref, watch, shallowRef} from "vue";
import {log_event} from "@/scripts/log_events.js";
import Icon_container from "@/components/icon/icon_container.vue";

let search_timeout;
const filtered_data = shallowRef([])

const search = inject("search");
const searching = inject("searching");
const icon_list_ref = ref()

let ico_per_page = 51
let page = 1
let added_icons = 0

function matchFields(data, query) {
  // console.log('query', query)

  const dat = {...data}

  const matchesQuery = (value,type=null) => {
    if (typeof (value) !== "string" && query.length < 1) {
      return false;
    }

    // Check for strict matching prefix
    if (query.startsWith("#strict ")) {
      const strictQuery = query.slice(8);
      return value === strictQuery;
    }

    if (query.startsWith("#color ")) {
      const strictQuery = query.slice(7);
      return value === strictQuery && type === 'color';
    }

    if (query.startsWith("#tag ")) {
      const strictQuery = query.slice(5);
      return value === strictQuery && type === 'tag';
    }

    if (query.startsWith("#symbol ")) {
      const strictQuery = query.slice(8);
      return value === strictQuery && type === 'symbol';
    }

    return value.includes(query)
  }

  dat['name']['match'] = matchesQuery(dat['name']['name']) ? 1 : 0;
  dat['category']['match'] = matchesQuery(dat['category']['name']) ? 1 : 0;
  dat['tags'].forEach((elem) => elem['match'] = matchesQuery(elem['name'],elem['type']) ? 1 : 0)

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

  return total_weight
}

function make_search(append = true) {

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

  clearTimeout(search_timeout);
  search_timeout = setTimeout(() => {
    requestAnimationFrame(() => {
      make_search(false)
    })
    if (oldV !== newV && search.value.length > 0) log_event('search', 'int', search.value)
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

    <lazy-component v-for="icon in filtered_data" :key="icon['id']" :threshold="0.1" rootMargin="0px 0px 2000px 0px">
      <icon_container :data="icon"/>
    </lazy-component>

    <div :class="`list-spinner ${searching ? 'visible':''}`">
      <div class="spinner-border"></div>
    </div>

  </div>

</template>
<style scoped>

.icons_list {
  content-visibility: auto;
  contain-intrinsic-size: 150px;

  margin-top: 20px;
  margin-bottom: 300px;
  /*outline: 1px solid red;*/

  display: flex;
  flex-flow: row wrap;
  justify-content: flex-start;
  align-items: flex-start;
  /*gap: 5px;*/
}

.list-spinner {
  display: flex;
  justify-content: center;
  width: 100%;

  visibility: hidden;
  opacity: 100;
  transition: 250ms opacity;
}

.visible {
  transition-delay: 500ms;
  visibility: visible;
  opacity: 0;
}

</style>
