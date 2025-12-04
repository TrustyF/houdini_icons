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
  const sat = 45
  const lig = 20
  if (type === 'tag') return `hsl(0,${sat}%,${lig}%)`
  if (type === 'shape') return `hsl(107,${sat}%,${lig}%)`
  if (type === 'symbol') return `hsl(185,${sat}%,${lig}%)`
  if (type === 'color') return `hsl(284,${sat}%,${lig}%)`
}

</script>

<template>
  <div class="tag_list">
    <div v-for="tag in filtered" :key="tag['id']">
      <div ref="tag_ref" class="tag"
           :style="`background-color:${get_color_from_type(tag['type'])};`"
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
  justify-content: inherit;
  gap: 4px;
  margin: 0;
  width: 100%;
  overflow: hidden;
}

.tag {
  color: #d9d9d9;
  cursor: pointer;
  position: relative;
  display: flex;
  flex-flow: row;
  justify-content: center;
  align-items: center;
  gap: 5px;
  font-size: 0.8em;
  line-height: normal;
  background-color: #282828;
  padding: 3px 6px 3px 6px;
  border-radius: 5px;
  /*border: inset 2px;*/
  /*width: 100%;*/
  /*overflow: hidden;*/
}

.tag:hover {
  background-color: #2a4766 !important;
}

h1 {
  /*width: 100%;*/
  font-size: inherit;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  transform: translateY(-1px);
}

</style>
