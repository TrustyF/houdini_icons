<script setup>
import {computed, inject, ref} from "vue";
import Tag_list from "@/components/icon/tag_list.vue";
import {clickOutSide as vClickOutSide} from '@mahdikhashan/vue3-click-outside'
import Icon_image from "@/components/icon/Icon_image.vue";
import Icon_node_preview from "@/components/icon/Icon_node_preview.vue";

let props = defineProps({
  data: Object
});

let alert_content = inject('alert_content')

const searching = inject("searching");
const settings = inject("settings");

let icon_scale = computed(() => settings.icon_scale)
let icon_size = computed(() => `${120 * icon_scale.value}px`)
let image_size = computed(() => `${100 * icon_scale.value}px`)

let master_icon = ref()
let expanded = ref(false)

function close_expand() {
  if (expanded.value) expanded.value = false
}

function expand() {

  if (!expanded.value) {
    expanded.value = true
  } else {
    expanded.value = false
  }

}

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

</script>

<template>
  <div ref="master_icon" :class="`icon_container_wrapper ${expanded ? 'expanded':''}`"
       v-click-out-side="close_expand">

    <div class="icon_download" @click="download_svg(data)" v-show="expanded">
      <div class="bi-download"/>
    </div>

    <icon_image :icon_id="props.data.id"/>

    <div :class="`icon_name ${expanded ? 'full_name':''}`"
         v-show="!settings.icon_only && !expanded"
         :title="data['name']['name']"> {{ data['name']['name'].replaceAll("_", ' ') }}
    </div>

    <div class="icon_category"
         v-show="!settings.icon_only && !expanded">{{ data['category']['name'] }}
    </div>

    <div class="icon_path_box" @click="add_to_clipboard" v-show="expanded">
      <div class="bi-copy"/>
      <div v-show="!settings.icon_only || expanded">{{ `${data['category']['name']}_${data['name']['name']}.svg` }}
      </div>
    </div>

    <div :class="`tags ${expanded ? 'expanded':''}`" v-show="((searching && !settings.icon_only) || expanded) ">

      <tag_list :content="data['tags']" :expanded="expanded" @tag_search="close_expand"
                v-show="data['tags'] || expanded"
                title="Tags">
      </tag_list>

    </div>

    <div class="node_prev_list" v-show="expanded">
      <icon_node_preview class="node_prev" :icon_id="props.data.id" :bg_color="0"/>
      <icon_node_preview class="node_prev" :icon_id="props.data.id" :bg_color="1"/>
      <icon_node_preview class="node_prev" :icon_id="props.data.id" :bg_color="2"/>
    </div>

    <div class="click_zone" :style="`cursor: ${expanded ? 'auto':'pointer'} `" @click="expand"></div>

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
  to {
    opacity: 0
  }
}

.expanded {
  /*flex-grow: 10;*/
  width: 300px;
  max-width: 300px;
  background-color: #1f1f1f;
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
  padding: 8px;

  background-color: #2b2b2b;
  border-radius: 5px;
  color: #8d8d8d;

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
