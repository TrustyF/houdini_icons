<script setup>
import {defineAsyncComponent, onMounted, provide, reactive, ref, watch} from "vue";

const search_bar = defineAsyncComponent(() => import("@/components/generic/search_bar.vue"))
const settings_bar = defineAsyncComponent(() => import("@/components/generic/settings_bar.vue"))
const icon_list = defineAsyncComponent(() => import("@/components/icon/Icon_list.vue"))

const settings_open = ref(false)

</script>

<template>
  <div class="home_wrapper">

    <div class="settings_header">
      <div class="search_area">
        <search_bar/>
        <div class="gear_toggle bi-gear-fill" :class="{gear_active: settings_open}"
             @click="settings_open = !settings_open"
             title="Settings" aria-label="Toggle settings"></div>
      </div>

      <div class="settings_area" v-show="settings_open" v-click-outside="() => settings_open = false">
        <settings_bar/>
      </div>
    </div>

    <icon_list/>

  </div>
</template>

<style scoped>
.home_wrapper {
  /*outline: 1px solid red;*/
  position: relative;

}

.settings_header {
  position: sticky;
  display: flex;
  flex-flow: row wrap;
  justify-content: space-between;
  top: 15px;
  z-index: 20;
  gap: 10px;
}

.search_area {
  position: sticky;
  /*top: 13px;*/
  left: auto;
  right: auto;

  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 10;
}

.gear_toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  cursor: pointer;

  border: 1px solid #4d4d4d;
  background-color: #282828;
  border-radius: 5px;
  color: #b3b3b3;
  font-size: 1em;

  box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.25);
}

.gear_toggle:hover {
  background-color: #333333;
}

.gear_active {
  background-color: #2c3e50;
  border-color: #486582;
  color: #e6e6e6;
}

/* Only phones need the settings collapsed behind a toggle — on desktop
   there's always room to just show the panel, so skip the extra click. */
@media (min-width: 481px) {
  .gear_toggle {
    display: none;
  }

  .settings_area {
    display: flex !important;
  }
}

.settings_area {
  position: sticky;

  display: flex;
  flex-flow: row wrap;
  align-items: center;
  gap: 10px;
  top: 13px;
  right: 20px;
  z-index: 10;
  padding: 5px;
  border: 1px solid #4d4d4d;
  background-color: #282828;
  border-radius: 5px;

  font-size: 0.9em;
  line-height: 1.3em;
  min-height: 30px;
}

</style>
