<script setup>
import {inject, onMounted, watch, ref, computed} from "vue";

let props = defineProps({
  test: {
    type: String,
    default: null,
  },
});
const search = inject("search");
const searching = inject("searching");

</script>

<template>
  <input class="search_bar" type="search" placeholder="Search"
         @keydown.esc="search=''"
         v-model="search">
  <h1 class="search_bar_clean bi-x-circle" @click="search=''"></h1>
  <div :class="`spinner-border loader ${searching ? 'visible' : ''}`"></div>
</template>

<style scoped>
.search_bar {
  padding: 5px;
  border: 1px solid #4d4d4d;
  background-color: #282828;
  color: white;
  z-index: 5;
  border-radius: 5px;

  box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.25);
}

.loader {
  position: absolute;
  right: -35px;
  margin-top: -2px;
  z-index: 0;
  visibility: hidden;
  opacity: 100;
  transition: 250ms opacity;
}
.visible {
  transition-delay: 500ms;
  visibility: visible;
  opacity: 0;
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
