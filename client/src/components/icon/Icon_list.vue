<script setup>
import data from "@/assets/database.json";
import {defineAsyncComponent, inject, onMounted, reactive, ref, watch} from "vue";
import Icon_container from "@/components/icon/icon_container.vue";
import {RecycleScroller} from "vue-virtual-scroller"

let search_timeout;
const filtered_data = reactive({value: []})

const search = inject("search");
const searching = inject("searching");
const icon_list_ref = ref()

let ico_per_page = 50
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

function make_search(append = false) {

  // let new_data = data.sort((a, b) => a.id - b.id)
  let new_data = data

  if (search.value.length > 0) {
    new_data = new_data.map((entry) => matchFields(entry, search.value))
    new_data = new_data.filter((entry) => hasMatch(entry))
    new_data.sort((a, b) => calc_weight(b) - calc_weight(a))
  }

  if (append) {
    let pushed = new_data.slice(Math.max(0, page - 1) * ico_per_page, page * ico_per_page)
    filtered_data.value.push(...pushed)
    added_icons = pushed.length
  } else {
    page = 1
    filtered_data.value = new_data.slice(0, page * ico_per_page)
    console.log((filtered_data.value))
    added_icons = ico_per_page
  }


  searching.value = search.value.length > 0
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
    setTimeout(() => check_list_size(), 10)
  }
}

watch(search, (oldV, newV) => {

  clearTimeout(search_timeout);
  search_timeout = setTimeout(() => {
    requestIdleCallback(() => {
      make_search(false)
      check_list_size()
    })
  }, 150); // Delay the operation

})

onMounted(() => {
  // console.log(data)
  make_search()
  // new ResizeObserver(check_list_size).observe(icon_list_ref.value)
  // addEventListener("scroll", check_list_size)
  // check_list_size()
})

</script>
<template>
  <!--  <div class="icons_list" ref="icon_list_ref">-->
  <!--      <component :is="icon_cont" v-for="icon in filtered_data.value"-->
  <!--                      :key="icon['id']"-->
  <!--                      :data="icon"/>-->
  <!--  </div>-->

  <RecycleScroller
    class="icons_list"
    :items="filtered_data.value"
    :item_size="100"
    :key-field="'id'"
    v-slot="{icon}">

<!--    <Icon_container :data="icon"/>-->
    <div class="test">{{icon.id}}</div>

  </RecycleScroller>

</template>
<script>
export default {
  name: 'icon_list'
}
</script>
<style scoped>

.icons_list {
  margin-top: 20px;
  outline: 1px solid red;
  /*display: flex;*/
  /*flex-flow: row wrap;*/
  /*justify-content: flex-start;*/
  /*align-items: flex-start;*/
  /*gap: 5px;*/
  height: 100%;
}
.test {
  height: 100px;
}

</style>
