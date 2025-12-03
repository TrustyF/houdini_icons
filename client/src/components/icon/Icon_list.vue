<script setup>
import data from "@/assets/database.json";
import {defineAsyncComponent, inject, provide, onBeforeMount, onMounted, reactive, ref, watch, shallowRef} from "vue";
import Icon_container from "@/components/icon/Icon_container.vue";
import Icon_modal from "@/components/icon/Icon_modal.vue";

let search_timeout;
const filtered_data = shallowRef([])

const search = inject("search");
const searching = inject("searching");
const icon_list_ref = ref()

let ico_per_page = 51
let page = 1
let added_icons = 0

const icon_modal_pos = ref({'x': 0, 'y': 0})
const icon_modal_vis = ref(false)
const icon_modal_id = ref(1)

function matchFields(data, query) {
  // console.log('query', query)

  const dat = {...data}

  const matchesQuery = (value, type = null) => {
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
  dat['tags'].forEach((elem) => elem['match'] = matchesQuery(elem['name'], elem['type']) ? 1 : 0)

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
    new_data = new_data.map((entry) => matchFields(entry, String(search.value).toLowerCase()))
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

function icon_select_callback(event) {
  const parent = icon_list_ref.value.getBoundingClientRect()
  icon_modal_pos.value = {
    'x': (event.position.x - parent.left) + 'px',
    'y': (event.position.y - parent.top) + 'px',
  }
  icon_modal_id.value = event.icon_id
  icon_modal_vis.value = true
}

function icon_modal_close(){
  icon_modal_vis.value = false
}

watch(search, (oldV, newV) => {

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

    <icon_modal v-if="filtered_data.length > 0"
                :position="icon_modal_pos"
                :visibility="icon_modal_vis"
                :data="filtered_data[icon_modal_id-1]"
                @close="icon_modal_close"
    />

    <lazy-component class="icon_list_elem"
                    v-for="icon in filtered_data"
                    :key="icon['id']" :threshold="0.1" rootMargin="0px 0px 2000px 0px">
      <icon_container :data="icon" @selected="icon_select_callback"/>
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
