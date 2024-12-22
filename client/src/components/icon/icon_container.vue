<script setup>
import {inject, onMounted, watch, ref, computed} from "vue";
import {tag} from "postcss-selector-parser";

let props = defineProps({
  data: {
    type: Object,
    default: null,
  },
  search_term: {
    type: String,
    default: "",
  },
});

let emits = defineEmits(["test"]);
const curr_api = inject("curr_api");

const tags = computed(() => [...props['data']['tags']].concat(props['data']['shapes'], props['data']['colors']))
const search = computed(() => props['search_term'])
const s_regex = computed(() => new RegExp(search.value, 'i'))

const matched_tags = computed(() => {
  return tags.value.filter(item => s_regex.value.test(item))
})

</script>

<template>
  <div class="icon_container_wrapper">
    <img class="icon_img" :src="`/src/assets/converted_icons/${data['image']}`" alt="">
    <div class="icon_name">{{ data['name'] }}</div>
    <div class="icon_name" v-show="search_term">{{ matched_tags }}</div>
  </div>
</template>

<style scoped>
.icon_container_wrapper {
  width: 100px;
  height: 100px;
  /*outline: 1px solid red;*/

  display: flex;
  flex-flow: column;

  background-color: #282828;

}

.icon_img {
  object-fit: contain;
  height: 100%;
  padding: 5px;
}

.icon_name {
  /*outline: 1px solid orange;*/
  text-align: center;
  align-items: center;
  vertical-align: center;
  padding: 0 0 3px 0;
  margin: 3px;
}
</style>
