<script setup>
import {computed, inject} from "vue";

let props = defineProps({
  icon_id: Number, scale_override: Number, scale_min: Number
});

const settings = inject("settings");

// Only the two single-instance callers (modal, node preview) pass an
// override/min, so only they pay for reading the reactive settings object.
// The big list never sets this, so it just inherits --icon-scale from its
// ancestor via plain CSS instead of recomputing per mounted icon.
let icon_scale_style = computed(() => {
  if (props.scale_override) return {'--icon-scale': props.scale_override}
  if (props.scale_min) return {'--icon-scale': Math.max(props.scale_min, settings.icon_scale)}
  return undefined
})

// Position within the atlas depends only on icon_id (static per instance);
// the scale factor itself is applied in CSS via var(--icon-scale) so this
// never needs to recompute when the global scale changes.
let ico_atlas_pos_x = computed(() => {
  let id = props['icon_id'] - 1
  let x = id % 10
  return -(x * 100 + 2.5)
})
let ico_atlas_pos_y = computed(() => {
  let id = props['icon_id'] - 1
  let y = Math.floor(id / 10) % 10
  return -(y * 100 + 2.5)
})

let ico_atlas = computed(() => {
  let id = props['icon_id'] - 1

  let cus_id = Math.floor(id / 100)
  let str_url = `/atlas/atlas_${cus_id}.webp`

  return `url(${str_url})`
})
</script>

<template>
  <div class="icon_img" :style="icon_scale_style"/>
</template>

<style scoped>

.icon_img {
  max-width: calc(120px * var(--icon-scale, 1) * var(--icon-density, 1));
  background-size: calc(1000px * var(--icon-scale, 1) * var(--icon-density, 1));
  background-image: v-bind(ico_atlas);
  background-position: calc(v-bind(ico_atlas_pos_x) * 1px * var(--icon-scale, 1) * var(--icon-density, 1)) calc(v-bind(ico_atlas_pos_y) * 1px * var(--icon-scale, 1) * var(--icon-density, 1));
  background-repeat: no-repeat;
  width: calc(100px * var(--icon-scale, 1) * var(--icon-density, 1));
  aspect-ratio: 1;
}

</style>
