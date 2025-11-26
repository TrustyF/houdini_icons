<script setup>

import Icon_image from "@/components/icon/Icon_image.vue";
import {computed} from "vue";

let props = defineProps({icon_id: Number, bg_color: Number});

let bg_colors = [
  '#e6e6e6',
  '#4b831c',
  '#504191',
]
let bg_col = computed(() => bg_colors[props.bg_color])

</script>

<template>
  <div class="icon_node_prev_wrapper">
    <img class="node_img" src="/web_icons/node.webp" alt="node">
    <icon_image class="node_icon" :icon_id="icon_id" :scale_override="1"/>
    <div class="icon_node_prev_bg"/>
  </div>
</template>

<style scoped>
.icon_node_prev_wrapper {
  height: 50px;
  width: 155px;
  position: relative;
  display: flex;
  margin: -10px -35px -10px -35px;
  transform: scale(50%);
}

.node_img {
  z-index: 5;
  /*position: absolute;*/
  object-fit: contain;
  border-radius: 7px;
  image-rendering: high-quality;
}

.node_icon {
  z-index: 5;
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%) scale(35%);
}

.icon_node_prev_bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: v-bind(bg_col);
  clip-path: inset(2px 2px 2px 2px round 7px);
}
</style>
