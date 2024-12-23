<script setup>
import data from '/src/assets/database.json'
import Icon_container from "@/components/icon/icon_container.vue";
import {computed, provide, ref} from "vue";
import Search_bar from "@/components/generic/search_bar.vue";

const search = ref("")
provide("search", search)

console.log(data)

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
    if (data['match'] === 1 && data['weight'] > 0.6) {
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

const updatedData = computed(() => data.map((entry) => matchFields(entry, search.value)))
const filteredData = computed(() => updatedData.value.filter((entry) => {
  return search.value.length > 0 ? hasMatch(entry) : true
}).sort((a, b) => calc_weight(b) - calc_weight(a)))

</script>

<template>
  <div class="home_wrapper">

    <div class="search_area">
      <search_bar/>
    </div>

    <div class="icons_list">
      <icon_container v-for="icon in filteredData"
                      :key="icon['id']"
                      :data="icon"/>
    </div>

  </div>
</template>

<style scoped>
.home_wrapper {
  position: relative;

}
.search_area {
  position: fixed;
  top: 13px;
  left: auto;
  right: auto;

  display: flex;
  gap: 10px;
  z-index: 10;
}

.icons_list {
  margin-top: 20px;
  /*outline: 1px solid red;*/
  display: flex;
  flex-flow: row wrap;

  justify-content: center;
  /*align-items: flex-start;*/

  gap: 5px;
}
</style>
