<script setup>
import {computed, inject, defineProps} from "vue";

let props = defineProps({
  icon_id: Number, scale_override: Number, scale_min: Number
});

const settings = inject("settings");

let icon_scale = computed(() => {
  if (props.scale_override) return props.scale_override
  if (props.scale_min) return Math.max(props.scale_min, settings.icon_scale)
  return settings.icon_scale
})
let icon_size = computed(() => `${120 * icon_scale.value}px`)
let image_size = computed(() => `${100 * icon_scale.value}px`)

let ico_atlas_pos = computed(() => {
  let id = props['icon_id'] - 1

  let size = -100 * icon_scale.value
  let padding = 2.5 * icon_scale.value
  let y = Math.floor(id / 10) % 10
  let x = id % 10

  return `${(x * size) - padding}px ${(y * size) - padding}px`
})

let ico_atlas = computed(() => {
  let id = props['icon_id'] - 1

  let cus_id = Math.floor(id / 100)
  let str_url = `/atlas/atlas_${cus_id}.webp`

  return `url(${str_url})`
})
</script>

<template>
  <div class="icon_img"/>
</template>

<style scoped>

.icon_img {
  max-width: v-bind(icon_size);
  background-size: calc(1000px * v-bind(icon_scale));
  background-image: v-bind(ico_atlas);
  background-position: v-bind(ico_atlas_pos);
  background-repeat: no-repeat;
  width: calc(100px * v-bind(icon_scale));
  aspect-ratio: 1;
}

</style>
