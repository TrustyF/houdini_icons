<script setup>
import {inject} from "vue";

const settings = inject("settings");

</script>

<template>
  <span class="setting_group">
    <label for="icon_toggle" class="label">Icon only</label>
    <input id="icon_toggle" type="checkbox" v-model="settings.icon_only">
  </span>

  <span class="setting_group">
    <label for="icon_size" class="label">Icon size</label>
    <!--        <input id="icon_size" type="number" min="0.1" max="2" step="0.1" v-model="settings.icon_scale">-->
    <input id="icon_size" type="range" min="0.3" max="2" step="0.1" v-model.number="settings.icon_scale">
  </span>
</template>

<style scoped>
.setting_group {
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  gap: 10px;
}

.label {
  /*height: 20px;*/
  /*overflow: hidden;*/
  white-space: wrap;
}

/* Custom checkbox and slider skins so both match the app's dark
   chrome/accent palette instead of the browser's default OS controls. */

#icon_toggle {
  appearance: none;
  -webkit-appearance: none;
  margin: 0;
  width: 16px;
  height: 16px;
  flex-shrink: 0;

  border: 1px solid #4d4d4d;
  border-radius: 4px;
  background-color: #1f1f1f;
  cursor: pointer;
  position: relative;

  transition: background-color 150ms, border-color 150ms;
}

#icon_toggle:hover {
  border-color: #666666;
}

#icon_toggle:checked {
  background-color: #2c3e50;
  border-color: #486582;
}

#icon_toggle:checked::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 2px;
  width: 3px;
  height: 7px;
  border: solid #e6e6e6;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

#icon_size {
  appearance: none;
  -webkit-appearance: none;
  width: 100px;
  height: 4px;
  margin: 0;

  border: 1px solid #4d4d4d;
  border-radius: 2px;
  background-color: #1f1f1f;
  cursor: pointer;
  outline: none;
}

#icon_size::-webkit-slider-runnable-track {
  height: 4px;
  border-radius: 2px;
  background: transparent;
}

#icon_size::-moz-range-track {
  height: 4px;
  border-radius: 2px;
  background: transparent;
  border: none;
}

#icon_size::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  margin-top: -6px;

  border-radius: 50%;
  background-color: #486582;
  border: 1px solid #6a93b8;
  cursor: pointer;

  transition: background-color 150ms;
}

#icon_size::-moz-range-thumb {
  width: 14px;
  height: 14px;

  border-radius: 50%;
  background-color: #486582;
  border: 1px solid #6a93b8;
  cursor: pointer;

  transition: background-color 150ms;
}

#icon_size:hover::-webkit-slider-thumb,
#icon_size:hover::-moz-range-thumb {
  background-color: #5a7a9c;
}
</style>
