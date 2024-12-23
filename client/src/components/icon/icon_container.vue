<script setup>
import {inject, onMounted, watch, ref, computed, provide} from "vue";
import Tag_list from "@/components/icon/tag_list.vue";

let props = defineProps({
  data: {
    type: Object,
    default: null,
  },
});

let emits = defineEmits(["test"]);
const search = inject("search");
const searching = inject("searching");

const expanded = ref(false)
provide("expanded",expanded)

</script>

<template>
  <div class="icon_container_wrapper">
    <img class="icon_img" :src="`/src/assets/converted_icons/${data['image']}`" alt="">

    <div class="icon_name" :title="data['name']['name']">{{ data['name']['name'] }}</div>
    <div class="icon_category">{{ data['category']['name'] }}</div>

    <div class="tags" v-show="searching || expanded">
      <tag_list :icon_name="data['name']['name']" :content="data['tags']" v-show="data['tags'] || expanded" title="Tags"></tag_list>
      <tag_list :icon_name="data['name']['name']" :content="data['shapes']" v-show="data['shapes'] || expanded" title="Shapes"></tag_list>
      <tag_list :icon_name="data['name']['name']" :content="data['symbols']" v-show="data['symbols'] || expanded" title="Symbols"></tag_list>
      <tag_list :icon_name="data['name']['name']" :content="data['colors']" v-show="data['colors'] || expanded" title="Colors"></tag_list>
    </div>

    <div class="click_zone" @click="expanded = !expanded"></div>
  </div>
</template>

<style scoped>
.icon_container_wrapper {
  width: 120px;
  /*height: 250px;*/
  /*outline: 1px solid red;*/
  position: relative;
  display: flex;
  flex-flow: column nowrap;
  justify-items: flex-start;
  align-items: flex-start;

  background-color: #282828;
  padding: 10px;
  border-radius: 5px;
  user-select: none;
  cursor: pointer;
}
.icon_container_wrapper:hover {
  background-color: var(--vt-c-black-soft);
}
.icon_img {
  object-fit: cover;
  width: 100px;
  height: 100px;
  padding: 5px;
}

.icon_name {
  /*outline: 1px solid orange;*/
  color: white;
  font-size: 0.8em;
  /*text-align: center;*/

  align-items: center;
  vertical-align: center;
  padding: 3px 0 3px 0;
  /*margin: 3px;*/
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  width: 100%;
}

.icon_category {
  /*outline: 1px solid orange;*/
  color: rgba(84, 84, 84, 1);
  font-size: 0.6em;
  font-weight: 1000;
  line-height: 1;
  /*text-align: center;*/

  align-items: center;
  vertical-align: center;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  width: 100%;
}
.tags {
  width: 100%;
  z-index: 5;
  /*outline: 1px solid blue;*/
  max-height: 100px;
  overflow-y: scroll;
  display: flex;
  flex-flow: row wrap;

  justify-items: flex-start;
  align-items: flex-start;
  align-content: flex-start;
  justify-content: flex-start;

  gap: 3px;
  margin-top: 10px;
}
.click_zone {
  z-index: 3;
  /*outline: 1px solid red;*/
  width: 100%;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
}

</style>
