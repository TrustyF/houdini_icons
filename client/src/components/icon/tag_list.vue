<script setup>
import {inject, onMounted, watch, ref, computed, onUpdated} from "vue";

let props = defineProps({
  content: Array, expanded: Boolean
});
let emits = defineEmits(["tag_search"]);
const search = inject("search");
const searching = inject("searching");
const tag_ref = ref()

const settings = inject("settings");

let icon_scale = computed(() => settings.icon_scale)

function add_to_search(tag) {
  search.value = `#${tag['type']} ${tag['name']}`
  emits('tag_search')
}


const filtered = computed(() => props['content'].filter((elem) => {
  if (props['expanded']) return true
  return elem['match'] === 1
}))

function get_color_from_type(type) {
  if (type === 'tag') return 'rgb(102,41,41)'
  if (type === 'shape') return 'rgb(102,95,41)'
  if (type === 'symbol') return 'rgb(41,97,102)'
  if (type === 'color') return 'rgb(86,41,102)'
}

</script>

<template>
  <div class="tag_list">
    <div v-for="tag in filtered" :key="tag['id']">
      <div ref="tag_ref" class="tag"
           :style="`background-color:${get_color_from_type(tag['type'])};border-color:${get_color_from_type(tag['type'])}`"
           @click="add_to_search(tag)">
        <h1>{{ `${tag['name']}` }}</h1>
      </div>
    </div>
  </div>
</template>

<style scoped>

.tag_list {
  display: flex;
  flex-flow: row wrap;
  justify-items: flex-start;
  gap: 2px;
  margin: 0;
  width: 100%;
  overflow: hidden;
}

.tag {
  color: #cccccc;
  cursor: pointer;
  position: relative;
  display: flex;
  flex-flow: row;
  gap: 5px;
  font-size: 0.7em;
  background-color: #282828;
  padding: 3px 6px 3px 6px;
  border-radius: 5px;
  /*border: 1px solid;*/
  /*width: 100%;*/
  /*overflow: hidden;*/
}

.tag:hover  {
  background-color: #2c3e50 !important;
}

h1 {
  /*width: 100%;*/
  font-size: inherit;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

</style>
