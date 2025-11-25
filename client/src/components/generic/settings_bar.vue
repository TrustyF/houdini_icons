<script setup>
import {inject, onMounted, watch, ref, computed} from "vue";

let props = defineProps({
  test: {
    type: String,
    default: null,
  },
});
const settings = inject("settings");

</script>

<template>
  <label for="icon_toggle" class="label">Icon only</label>
  <input id="icon_toggle" type="checkbox" v-model="settings.icon_only">

  <label for="icon_size" class="label">Icon size</label>
  <!--        <input id="icon_size" type="number" min="0.1" max="2" step="0.1" v-model="settings.icon_scale">-->
  <input id="icon_size" type="range" min="0.3" max="2" step="0.1" v-model="settings.icon_scale">
</template>

<style scoped>
.label {
  /*height: 20px;*/
  /*overflow: hidden;*/
  white-space: wrap;
}
</style>
