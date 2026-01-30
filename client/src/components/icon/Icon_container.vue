<script setup>
import {computed, inject, ref} from "vue";
import Icon_image from "@/components/icon/Icon_image.vue";
import Tag_list from "@/components/icon/tag_list.vue";

let props = defineProps({
  data: Object
});

const settings = inject("settings");

const icon_modal_pos = inject("icon_modal_pos");
const icon_modal_vis = inject("icon_modal_vis");
const icon_modal_id = inject("icon_modal_id");

let icon_scale = computed(() => settings.icon_scale)
let icon_size = computed(() => `${120 * icon_scale.value}px`)
let image_size = computed(() => `${100 * icon_scale.value}px`)

let master_icon = ref()

function icon_select_callback(event) {
  const rect = master_icon.value.getBoundingClientRect();
  icon_modal_pos.value = {
    'x': (rect.left + window.scrollX),
    'y': (rect.top + window.scrollY),
    'xf': ((window.innerWidth - rect.right) + window.scrollX),
  }
  icon_modal_id.value = props.data.id
  icon_modal_vis.value = true
}

</script>

<template>
  <div ref="master_icon" class="icon_container_wrapper">

    <icon_image :icon_id="props.data.id"/>

    <div class="icon_name"
         v-show="!settings.icon_only"
         :title="data['name']"> {{ data['name'].replaceAll("_", ' ') }}
    </div>

    <div class="icon_category"
         v-show="!settings.icon_only">{{ data['category'] }}
    </div>

    <!--    <div class="tags">-->
    <!--      <tag_list :content="data['tags']" v-show="data['tags']" title="Tags"/>-->
    <!--    </div>-->

    <div class="click_zone" @click="icon_select_callback"></div>

  </div>
</template>

<style scoped>
.icon_container_wrapper {
  max-width: v-bind(icon_size);

  position: relative;
  display: flex;
  flex-flow: column wrap;
  justify-items: flex-start;
  align-items: flex-start;

  padding: calc(10px * v-bind(icon_scale));
  border-radius: 5px;
  user-select: none;
}

.icon_container_wrapper:hover {
  background-color: #1f1f1f;
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

.full_name {
  word-break: break-word;
  white-space: wrap;
  text-overflow: unset;
  overflow: unset;
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
  /*max-height: 100px;*/
  /*overflow-y: scroll;*/
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
  cursor: pointer;
  /*background-color: red;*/
  width: 100%;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
}

</style>
