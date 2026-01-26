<script setup>
import {computed, inject, nextTick, ref} from "vue";
import Tag_list from "@/components/icon/tag_list.vue";
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

function close(e) {
  if (props.visibility === true) emits('close')
}


const screen_flip = computed(() => {
  if (window.innerWidth > 500) return props.position.x > window.innerWidth * 0.7
  else return props.position.x > window.innerWidth / 2
})

const position_style = computed(() => {
  const margin = 13
  if (screen_flip.value) return `
  right:${props.position['xf'] - margin}px;
  top:${props.position['y'] - margin}px;
  `
  return `
  left:${props.position['x'] - margin}px;
  top:${props.position['y'] - margin}px;
  `
})

</script>

<template>
  <div class="icon_modal_wrapper"
       v-show="props.visibility" v-if="props.data" v-click-outside="close"
       :style="position_style">

    <div class="sidebar" :style="screen_flip ? 'left:0;right:auto' : ''">

      <div class="bi-x sidebar_button" @click="close"/>
<!--      <div class="bi-download sidebar_button" @click="download_svg(data)"/>-->

    </div>

    <icon_image :style="screen_flip ? 'margin-left: auto;' : '' + 'cursor:pointer'"
                :icon_id="props.data.id" :scale_min="1" @click="close"/>

    <div class="icon_name full_name"
         :title="data['name']['name']"> {{ data['name']['name'].replaceAll("_", ' ') }}
    </div>

    <div class="icon_category">{{ data['category']['name'] }}</div>

    <div class="icon_path_box" @click="add_to_clipboard">
      <div class="bi-copy"/>
      <div>{{ `${data['category']['name']}_${data['name']['name']}.svg` }}
      </div>
    </div>

    <tag_list class="tags"
              :content="data['tags']"
              v-show="data['tags']"
              :expanded="true"
              title="Tags"/>

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

  width: auto;

  padding: 20px;
  border: #262626 3px solid;
  border-radius: 5px;
  user-select: none;
  /*background-color: #1f1f1f;*/
  background: linear-gradient(to bottom, #1f1f1f 25%, #1d2626 150%);
  box-shadow: rgba(0, 0, 0, 0.9) 0 0 30px, rgba(0, 0, 0, 0.8) 0 0 50px;
}

.sidebar {
  z-index: 10;
  cursor: pointer;
  position: absolute;
  right: 0;
  top: 0;
  display: flex;
  flex-flow: column;
  justify-content: center;
  align-items: center;
  /*gap: 5px;*/
}

.sidebar_button {
  position: relative;
  margin: 5px;
  padding: 10px;
  border-radius: 5px;
  color: #404040;
  font-size: 1.2em;
  line-height: 1;
}

.sidebar_button:hover {
  background-color: #2c3e50;
  color: #e6e6e6;
}

.icon_name {
  /*outline: 1px solid orange;*/
  color: white;
  font-size: 1em;
  /*text-align: center;*/

  align-items: center;
  vertical-align: center;
  padding: 3px 0 3px 0;
  /*margin: 3px;*/
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
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
  font-size: 0.8em;
  font-weight: 1000;
  line-height: 1;
  /*text-align: center;*/

  align-items: center;
  vertical-align: center;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.icon_path_box {
  z-index: 5;
  cursor: pointer;

  display: flex;
  flex-flow: row;
  justify-content: center;
  align-items: center;
  gap: 5px;

  margin: 20px 0 0 0;
  padding: 15px;
  width: 100%;

  background-color: #262626;
  outline: 2px solid #666666;
  border-radius: 5px;
  color: #e6e6e6;

  font-size: 0.9em;
  line-height: 1;
}

.icon_path_box:hover {
  background-color: #2c3e50;
  outline: 2px solid #486582;
}

.tags {
  /*width: 100%;*/
  max-width: 300px;
  z-index: 5;

  margin-top: 25px;
}

.node_prev_list {
  z-index: 5;
  display: flex;
  flex-flow: row wrap;
  gap: 5px;
  margin-top: 15px;
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
