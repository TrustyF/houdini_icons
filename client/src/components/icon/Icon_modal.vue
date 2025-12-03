<script setup>
import {computed, inject, ref} from "vue";
import Tag_list from "@/components/icon/tag_list.vue";
import {clickOutSide as vClickOutSide} from '@mahdikhashan/vue3-click-outside'
import Icon_image from "@/components/icon/Icon_image.vue";
import Icon_node_preview from "@/components/icon/Icon_node_preview.vue";

let props = defineProps({
  position: Object,
  visibility: Boolean,
  data: Object,
});

let emits = defineEmits(['close'])

let alert_content = inject('alert_content')

const searching = inject("searching");
const settings = inject("settings");

let icon_scale = computed(() => settings.icon_scale)
let icon_size = computed(() => `${120 * icon_scale.value}px`)
let image_size = computed(() => `${100 * icon_scale.value}px`)

function add_to_clipboard() {
  let clip = `hicon:/SVGIcons.index?${props['data']['category']['name']}_${props['data']['name']['name']}.svg`
  navigator.clipboard.writeText(clip);

  alert_content.value = {
    title: 'Copied!',
    message: 'Icon was copied to clipboard'
  }
}

function download_svg(data) {
  let file = data['name']['name']
  let category = data['category']['name']
  let path

  if (category.length < 1 || category === 'icons') path = `/icons/${file}.svg`
  else path = `/icons/${category}/${file}.svg`

  const a = document.createElement("a");
  a.href = path;
  a.download = file;
  a.style.display = "none";
  document.body.appendChild(a);
  a.dispatchEvent(new MouseEvent("click", {
    bubbles: false,
    cancelable: true,
    composed: false
  }));
  document.body.removeChild(a);
}

function close() {
  if (props.visibility === true) emits('close')
}

</script>

<template>
  <div class="icon_modal_wrapper" v-show="props.visibility"
       :style="`left:${position['x']};top:${position['y']};`">

    <div class="icon_download" @click="download_svg(data)">
      <div class="bi-download"/>
    </div>

    <icon_image :icon_id="props.data.id" @click="close"/>

    <div class="icon_name full_name"
         :title="data['name']['name']"> {{ data['name']['name'].replaceAll("_", ' ') }}
    </div>

    <div class="icon_category">{{ data['category']['name'] }}</div>

    <div class="icon_path_box" @click="add_to_clipboard">
      <div class="bi-copy"/>
      <div>{{ `${data['category']['name']}_${data['name']['name']}.svg` }}
      </div>
    </div>

    <div class="tags">
      <tag_list :content="data['tags']"
                v-if="data['tags'].length > 0"
                title="Tags">
      </tag_list>
    </div>

    <div class="node_prev_list">
      <icon_node_preview class="node_prev" :icon_id="props.data.id" :bg_color="0"/>
      <icon_node_preview class="node_prev" :icon_id="props.data.id" :bg_color="1"/>
      <icon_node_preview class="node_prev" :icon_id="props.data.id" :bg_color="2"/>
    </div>
  </div>
</template>

<style scoped>
.icon_modal_wrapper {
  position: absolute;
  z-index: 100;
  display: flex;
  flex-flow: column wrap;
  justify-items: flex-start;
  align-items: flex-start;

  padding: calc(10px * v-bind(icon_scale));
  border-radius: 5px;
  user-select: none;
  background-color: #1f1f1f;
  box-shadow: black 2px 2px 10px;
}

.icon_download {
  z-index: 10;
  cursor: pointer;
  position: absolute;
  right: 0;
  top: 0;

  display: flex;
  flex-flow: row;
  justify-content: center;
  align-items: center;
  gap: 5px;

  margin: 5px;
  padding: 10px;

  /*background-color: #1a1a1a;*/
  border-radius: 5px;
  color: #404040;

  font-size: 1.2em;
  line-height: 1;
}

.icon_download:hover {
  background-color: #2c3e50;
  color: #e6e6e6;
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

.icon_path_box {
  z-index: 5;
  cursor: pointer;

  display: flex;
  flex-flow: row;
  justify-content: center;
  align-items: center;
  gap: 5px;

  margin: 7px 0 0 0;
  padding: 9px;

  background-color: #333333;
  border-radius: 5px;
  color: #e6e6e6;

  font-size: 0.8em;
  line-height: 1;
}

.icon_path_box:hover {
  background-color: #2c3e50;
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

.node_prev_list {
  z-index: 5;
  display: flex;
  flex-flow: row nowrap;

  gap: 5px;
  margin-top: 10px;
}

.click_zone {
  z-index: 3;
  /*outline: 1px solid red;*/
  /*background-color: red;*/
  width: 100%;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
}

</style>
