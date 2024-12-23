<script setup>
import {inject, onMounted, watch, ref, computed} from "vue";

let props = defineProps({
  test: {
    type: String,
    default: null,
  },
});
const search = inject("search");

</script>

<template>
  <input class="search_bar" type="search" placeholder="Search"
         @keydown.esc="search=''" @click="$event.target.select()"
         v-model="search">
  <h1 class="search_bar_clean bi-x-circle" @click="search=''"></h1>
</template>

<style scoped>
.search_bar {
  padding: 5px;
  border: 1px solid #4d4d4d;
  background-color: #282828;
  color: white;
  border-radius: 5px;

  box-shadow: 3px 3px 5px black;
}
.search_bar_clean {
  cursor: pointer;
  font-size: 0.8em;
  position: absolute;
  right: 0;
  padding: 5px 5px 5px 8px;
  z-index: 11;
}
</style>
