<script setup>
import data from "@/assets/database.json";
import {inject, onMounted, reactive, ref, watch} from "vue";
import Icon_container from "@/components/icon/icon_container.vue";

let search_timeout;
const filtered_data = reactive({ value : []})

const search = inject("search");
const searching = inject("searching");

let page = 1

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

function make_search(append=true) {

  // console.log(data)

  let new_data = data.sort((a, b) => a.id - b.id)

  if (search.value.length > 0){
    new_data = new_data.map((entry) => matchFields(entry, search.value))
    new_data = new_data.filter((entry) => hasMatch(entry))
    new_data.sort((a, b) => calc_weight(b) - calc_weight(a))
  }

  if (append){
    console.log('appending')
    Array.prototype.push.apply(filtered_data.value,new_data.slice(Math.max(0,page-1) * 50, page * 50))
  } else {
    page = 1
    filtered_data.value = new_data.slice(0,page * 50)
  }


  searching.value = search.value.length > 0
}

function paginate(){
  console.log('loading', page)
}

watch(search, (oldV, newV) => {
  // make_search()

  clearTimeout(search_timeout);
  search_timeout = setTimeout(() => {
    requestIdleCallback(() => {
      make_search(false)
    })
  }, 150); // Delay the operation

})

onMounted(() => {
  make_search()
})

</script>
<template>
  <button @click="page+=1;make_search()">paginate</button>
  <div class="icons_list">
    <transition-group name="list">

      <icon_container v-for="icon in filtered_data.value"
                      :key="icon['id']"
                      :data="icon"/>

    </transition-group>
  </div>
</template>
<script>
export default {
  name: 'icon_list'
}
</script>
<style scoped>

.icons_list {
  margin-top: 20px;
  /*outline: 1px solid red;*/
  display: flex;
  flex-flow: row wrap;
  justify-content: flex-start;
  /*align-items: flex-start;*/
  /*gap: 5px;*/
}

.list-move,
.list-enter-active,
.list-leave-active {
  transition: transform 500ms ease, opacity 200ms linear;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.list-leave-active {
  display: none;
  /*position: absolute;*/
}
</style>
