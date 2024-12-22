<script setup>
import data from '/src/assets/database.json'
import Icon_container from "@/components/icon/icon_container.vue";
import {computed, ref} from "vue";

const search = ref("")
const s_regex = computed(() => new RegExp(search.value, 'i'))

const filtered_list = computed(() => {
  // console.log(data)
  return data.filter(item => {
    return (
      s_regex.value.test(item['name']) ||
      item['tags'].some(tag => s_regex.value.test(tag['name'])) ||
      item['shapes'].some(shape => s_regex.value.test(shape['name'])) ||
      item['symbols'].some(symbol => s_regex.value.test(symbol['name'])) ||
      item['colors'].some(color => s_regex.value.test(color['name']))
    );
  })
})


</script>

<template>
  <main>
    <div class="search_bar">
      <input type="search" v-model="search">
    </div>

    <div class="icons_list">
      <icon_container v-for="icon in filtered_list"
                      :key="icon.id"
                      :data="icon"
                      :search_term="search"/>
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
