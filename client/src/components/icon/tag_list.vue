<script setup>
import {inject, onMounted, watch, ref, computed} from "vue";

let props = defineProps({
  content: Array,
  title: String
});
let emits = defineEmits(["test"]);
const search = inject("search");
const searching = inject("searching");

const settings = inject("settings");

let icon_scale = computed(() => settings.icon_scale)

const expanded = inject("expanded");

const filtered = ref([])

function compute() {
  return props['content'].filter((elem) => elem['match'] === 1)
}

function expand() {
  return props['content']
}

watch(searching, (oldV, newV) => {
  filtered.value = compute()
})
watch(expanded, (oldV, newV) => {
  if (oldV) {
    filtered.value = expand()
  } else {
    filtered.value = compute()
  }
})

onMounted(() => {
  filtered.value = compute()
})

</script>

<template>
  <div class="tag_list" v-if="filtered.length > 0">
<!--    <p style="font-size: 0.7em;padding: 3px">{{title}}</p>-->
    <div v-for="tag in filtered" :key="tag['id']">
      <div class="tag" @click="search=tag['name'];expanded = false">
        <h1>{{ `${tag['name']}` }}</h1>
        <h1 class="tag_count">{{ `${tag['count']}` }}</h1>
<!--        <h1 class="tag_count">{{ `${tag['weight']}` }}</h1>-->
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
}

.tag {
  position: relative;
  display: flex;
  gap: 5px;
  font-size: 0.7em;
  background-color: #282828;
  padding: 2px 5px 2px 5px;
  border-radius: 5px;
}
.tag:hover{
  background-color: #2c3e50;
}
h1 {
  font-size: inherit;
}

</style>
