<script setup>
import {inject, onMounted, watch, ref, computed} from "vue";

let props = defineProps({
  content: {
    type: Array,
    default: null,
  },
  title: {
    type: String,
    default: null,
  },
});
let emits = defineEmits(["test"]);
const curr_api = inject("curr_api");

</script>

<template>
<!--  <div>{{content.length}}</div>-->
  <div class="tag_wrapper" v-if="content.length > 0">
    <h1 class="tag_heading">{{ title }}</h1>

    <div class="tag_list">
      <div class="tag" v-for="tag in content" :key="tag['name']+title">{{ tag['name'] }}</div>
    </div>

  </div>
</template>

<style scoped>
.tag_wrapper {
  display: flex;
  flex-flow: column;
  gap: 5px;
}

.tag_heading {
  font-size: 0.7em;
  text-decoration: underline 1px solid;
}

.tag_list {
  display: flex;
  flex-flow: row wrap;
  justify-items: flex-start;
  gap: 2px;
}

.tag {
  user-select: none;
  font-size: 0.7em;
  background-color: #181818;
  padding: 4px 7px 4px 7px;
  border-radius: 3px;
}


</style>
