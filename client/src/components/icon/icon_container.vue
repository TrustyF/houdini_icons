<script setup>
import {inject, onMounted, watch, ref, computed, provide, onUpdated} from "vue";
import Tag_list from "@/components/icon/tag_list.vue";
import {clickOutSide as vClickOutSide} from '@mahdikhashan/vue3-click-outside'
import {log_event} from "@/scripts/log_events.js";

let props = defineProps({
  data: Object
});

const searching = inject("searching");
const settings = inject("settings");

let icon_scale = computed(() => settings.icon_scale)
let icon_size = computed(() => `${120 * icon_scale.value}px`)
let image_size = computed(() => `${100 * icon_scale.value}px`)

let ico_atlas_pos = computed(() => {
  let id = props['data']['id'] - 1

  let size = -100 * icon_scale.value
  let padding = 2.5 * icon_scale.value
  let y = Math.floor(id / 10) % 10
  let x = id % 10

  return `${(x * size) - padding}px ${(y * size) - padding}px`
})
let ico_atlas = computed(() => {
  let id = props['data']['id'] - 1

  let cus_id = Math.floor(id / 100)
  let str_url = `/atlas/atlas_${cus_id}.webp`
  // let url = new URL(str_url, import.meta.url).href
  return `url(${str_url})`
})

let master_icon = ref()
let expanded = ref(false)
provide("expanded", expanded)

function close_expand() {
  if (expanded.value) expanded.value = false
}

function expand(){

  if (!expanded.value) {
    expanded.value = true
    log_event('expanded', 'int', props['data']['image'])
  } else {
    expanded.value = false
  }

}

</script>

<template>
  <div ref="master_icon" :class="`icon_container_wrapper ${expanded ? 'expanded':''}`">

<!--    <div class="spinner-cont">-->
<!--      <div class="spinner-border"></div>-->
<!--    </div>-->

    <div class="icon_img"/>

    <div :class="`icon_name ${expanded ? 'full_name':''}`"
         v-show="!settings.icon_only || expanded"
         :title="data['name']['name']"> {{ data['name']['name'].replaceAll("_", ' ') }}
    </div>

    <div class="icon_category"
         v-show="!settings.icon_only || expanded">{{ data['category']['name'] }}
    </div>

    <div :class="`tags ${expanded ? 'expanded':''}`" v-show="((searching && !settings.icon_only) || expanded) ">

      <tag_list :content="data['tags']"
                v-show="data['tags'] || expanded"
                title="Tags">
      </tag_list>

    </div>

    <div class="click_zone" @click="expand" v-click-out-side="close_expand"></div>
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
.spinner-cont {
  position: absolute;
  width: 100%;
  height: 100%;

  z-index: -1;

  opacity: 100;
  animation: fade 1s forwards;
}

@keyframes fade {
  to {opacity: 0}
}
.expanded {
  /*flex-grow: 10;*/
  width: 300px;
  max-width:300px;
  background-color: #1f1f1f;
}

.icon_img {
  max-width: v-bind(icon_size);

  background-size: calc(1000px * v-bind(icon_scale));
  background-image: v-bind(ico_atlas);
  background-position: v-bind(ico_atlas_pos);
  background-repeat: no-repeat;


  width: calc(100px * v-bind(icon_scale));
  aspect-ratio: 1;
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
  /*outline: 1px solid red;*/
  width: 100%;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
  cursor: pointer;
}

</style>
