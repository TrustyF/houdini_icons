<script setup>
import {computed, inject} from "vue";
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

function add_to_clipboard() {
  let clip = `hicon:/SVGIcons.index?${props.data.category}_${props.data.name}.svg`
  navigator.clipboard.writeText(clip);

  alert_content.value = {
    title: 'Copied!',
    message: 'Icon was copied to clipboard'
  }
}

function download_svg(data) {
  let file = data.name
  let category = data.category
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


// Flip based on whether the space to the right of the click point can
// actually fit the modal's worst-case width (the same cap the CSS
// max-width enforces), rather than a fixed screen-percentage split — a
// fixed split can still pick "grow rightward" for a click near the
// middle of a narrow screen even though the modal needs more room than
// is actually left, pushing it past the viewport edge.
const modal_max_width = computed(() => Math.min(400, window.innerWidth - 24))

const screen_flip = computed(() => {
  const space_right = window.innerWidth - props.position.x
  return space_right < modal_max_width.value
})

const position_style = computed(() => {
  const margin = 13

  // Clamp the offset itself so the box — whose width is always <=
  // modal_max_width thanks to the CSS max-width cap — can never be
  // pushed past the *opposite* edge either, which a raw click-relative
  // offset doesn't guard against on narrow screens where the modal's
  // worst-case width leaves little to no slack either side.
  const min_offset = margin
  const max_offset = Math.max(margin, window.innerWidth - modal_max_width.value - margin)

  if (screen_flip.value) {
    const right = Math.min(Math.max(props.position['xf'] - margin, min_offset), max_offset)
    return `
  right:${right}px;
  top:${props.position['y'] - margin}px;
  `
  }

  const left = Math.min(Math.max(props.position['x'] - margin, min_offset), max_offset)
  return `
  left:${left}px;
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
         :title="data['name']"> {{ data['name'].replaceAll("_", ' ') }}
    </div>

    <div class="icon_category">{{ data['category'] }}</div>

    <div class="icon_path_box" @click="add_to_clipboard">
      <div class="bi-copy"/>
      <div>{{ `${data['category']}_${data['name']}.svg` }}
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
  max-width: min(400px, calc(100vw - 24px));

  padding: 20px;
  border: #262626 3px solid;
  border-radius: 8px;
  user-select: none;
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

</style>
