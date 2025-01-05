<script setup>
import {inject, onMounted, watch, ref, computed, provide, onUpdated} from "vue";
import Tag_list from "@/components/icon/tag_list.vue";
import {clickOutSide as vClickOutSide} from '@mahdikhashan/vue3-click-outside'

let props = defineProps({
  data: Object
});

let emits = defineEmits(["test"]);
const search = inject("search");
const searching = inject("searching");
const settings = inject("settings");

let icon_scale = computed(() => settings.icon_scale)
let icon_size = computed(() => `${120 * icon_scale.value}px`)
let image_size = computed(() => `${100 * icon_scale.value}px`)

let ico_atlas_pos = computed(() => {
  let id = props['data']['id'] - 1
  let atlas = Math.floor(id / 100) + 1

  let size = -100
  let y = Math.floor(id / 10) % 10
  let x = id % 10

  return `${(x * size) - 2.5}px ${(y * size) - 2.5}px`
})
let ico_atlas = computed(() => {
  let cus_id = String(Math.floor((props['data']['id'] - 1) / 100))
  let str_url = `/src/assets/atlas/atlas_${cus_id}.webp`
  let url = new URL(str_url, import.meta.url).href

  return `url(${url})`
})

let master_icon = ref()
const expanded = ref(false)
provide("expanded", expanded)

function close_expand() {
  if (expanded.value) expanded.value = false
}

function get_image(path) {
  const folder = 'houdini_icons'
  return `https://firebasestorage.googleapis.com/v0/b/vue-portfolio-7361b.appspot.com/o/${folder}%2F${path}?alt=media&token=34218f81-850f-42f4-bd7e-6c95e9eee724`
}

watch(searching, (oldV, newV) => {
  expanded.value = false
})

onUpdated(() => {
  console.log('component updated', props['data']['id'])
})

</script>

<template>
  <div ref="master_icon" :class="`icon_container_wrapper ${expanded ? 'expanded':''}`">

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
      <tag_list :content="data['shapes']"
                v-show="data['shapes'] || expanded"
                title="Shapes">
      </tag_list>
      <tag_list :content="data['symbols']"
                v-show="data['symbols'] || expanded"
                title="Symbols">
      </tag_list>
      <tag_list :content="data['colors']"
                v-show="data['colors'] || expanded"
                title="Colors">
      </tag_list>

    </div>

    <div class="click_zone" @click="expanded = !expanded" v-click-out-side="close_expand"></div>
  </div>
</template>

<style scoped>
.icon_container_wrapper {
  width: v-bind(icon_size);

  position: relative;
  display: flex;
  flex-flow: column wrap;
  justify-items: flex-start;
  align-items: flex-start;

  padding: calc(10px * v-bind(icon_scale));
  border-radius: 5px;
  user-select: none;
  cursor: pointer;
}

.icon_container_wrapper:hover {
  background-color: #1f1f1f;
}

.expanded {
  /*flex-grow: 10;*/
  width: 300px;
  background-color: #1f1f1f;
}

.icon_img {
  object-fit: contain;
  max-width: v-bind(icon_size);

  border: none;

  background-image: v-bind(ico_atlas);
  background-position: v-bind(ico_atlas_pos);
  background-repeat: no-repeat;

  width: 100px;
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
}

</style>
