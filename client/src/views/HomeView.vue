<script setup>
import data from '/src/assets/database.json'
import Icon_container from "@/components/icon/icon_container.vue";
import {computed, inject, provide, ref} from "vue";

const search = ref("")
provide("search", search)

function filterAndSort(data, searchTerm, minWeight = 0) {
  const filtered = [];

  data.forEach((entry) => {
    // console.log(entry)

    let matchWeights = [];
    // Match against tags, shapes, symbols, and colors
    ["tags", "shapes", "symbols", "colors"].forEach((field) => {
      if (entry[field]) {
        entry[field].forEach((item) => {
          if (item.name.toLowerCase().includes(searchTerm.toLowerCase()) && item.weight >= minWeight) {
            matchWeights.push(item.weight);
          }
        });
      }
    });

    // If there are matches, calculate total weight
    if (matchWeights.length > 0) {
      const totalWeight = matchWeights.reduce((sum, weight) => sum + weight, 0);
      filtered.push({entry, totalWeight});
    }
  });

  // Sort the filtered results by total weight in descending order
  filtered.sort((a, b) => b.totalWeight - a.totalWeight);

  // Extract the entries from the sorted list
  return filtered.map((item) => item.entry);
}

const filtered = computed(() => filterAndSort(data, search.value, 0.7))

</script>

<template>
  <main>
    <div class="search_bar">
      <input type="search" v-model="search">
    </div>

    <div class="icons_list">
      <icon_container v-for="icon in filtered"
                      :key="icon['id']"
                      :data="icon"/>
    </div>

  </main>
</template>

<style scoped>
.icons_list {
  outline: 1px solid red;
  display: flex;
  flex-flow: row wrap;

  /*justify-items: flex-start;*/
  /*align-items: flex-start;*/

  gap: 10px;
}
</style>
