<script setup>
import data from "@/assets/database.json";
import {defineAsyncComponent, inject, provide, onBeforeMount, onMounted, reactive, ref, watch, shallowRef} from "vue";
import Icon_container from "@/components/icon/Icon_container.vue";
import Virtual_list from "@/components/generic/virtual_list.vue";

let search_timeout;
const filtered_data = ref([])

const search = inject("search");

const list_height = ref(100)
const list_width = ref(100)

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

  filtered_data.value = [...new_data]
}

function check_list_size() {
  const windowHeight = window.innerHeight || document.documentElement.clientHeight;
  list_height.value = windowHeight - 120
  console.log(list_height.value)
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
  addEventListener("resize", check_list_size)
  check_list_size()
})

</script>
<template>
  <virtual_list
    :nodes="filtered_data"
    :rowHeight="200"
    :columnsPerRow="10"
    :viewportHeight="400"
  />

  <!--  <div class="icons_list" ref="icon_list_ref">-->

  <!--      <icon_container :data="icon"/>-->

  <!--  </div>-->

</template>
<style scoped>

.icons_list {
  /*content-visibility: auto;*/
  /*contain-intrinsic-size: 150px;*/

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
