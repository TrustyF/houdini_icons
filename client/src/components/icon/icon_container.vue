<script setup>
import {inject, onMounted, watch, ref, computed} from "vue";
import Tag_list from "@/components/icon/tag_list.vue";

let props = defineProps({
  data: {
    type: Object,
    default: null,
  },
});

let emits = defineEmits(["test"]);
const curr_api = inject("curr_api");
const search = inject("search");

const s_regex = computed(() => new RegExp(search, 'i'))

const matched_tags = computed(() =>  props['data']['tags'].filter(item => s_regex.value.test(item['name'])))
const matched_shapes = computed(() =>  props['data']['shapes'].filter(item => s_regex.value.test(item['name'])))
const matched_symbols = computed(() =>  props['data']['symbols'].filter(item => s_regex.value.test(item['name'])))
const matched_colors = computed(() =>  props['data']['colors'].filter(item => s_regex.value.test(item['name'])))

</script>

<template>
  <div class="icon_container_wrapper">
    <img class="icon_img" :src="`/src/assets/converted_icons/${data['image']}`" alt="">

    <div class="icon_name">{{ data['name'] }}</div>

    <div class="tags">
      <tag_list :content="matched_tags" title="Tags"></tag_list>
      <tag_list :content="matched_shapes" title="Shapes"></tag_list>
      <tag_list :content="matched_symbols" title="Symbols"></tag_list>
      <tag_list :content="matched_colors" title="Colors"></tag_list>
    </div>
  </div>
</template>

<style scoped>
.icon_container_wrapper {
  width: 120px;
  /*height: 250px;*/
  /*outline: 1px solid red;*/

  display: flex;
  flex-flow: column nowrap;
  justify-items: flex-start;
  align-items: flex-start;

  background-color: #282828;
  padding: 10px;

}

.icon_img {
  object-fit: cover;
  width: 100px;
  padding: 5px;
}

.icon_name {
  /*outline: 1px solid orange;*/
  color: white;
  font-size: 0.9em;
  /*text-align: center;*/

  align-items: center;
  vertical-align: center;
  padding: 0 0 3px 0;
  margin: 3px;
  white-space: wrap;
  line-break: anywhere;
}
.tags {
  /*width: 100%;*/
  max-height: 100px;
  overflow-y: scroll;
}

</style>
