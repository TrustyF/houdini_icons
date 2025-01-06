<script setup>
import {onMounted, provide, reactive, ref, watch} from "vue";
import Search_bar from "@/components/generic/search_bar.vue";
import Icon_list from "@/components/icon/Icon_list.vue";

const search = ref("")
const searching = ref(false)

const settings = reactive({
  icon_only: false,
  icon_scale: 1,
})

provide("search", search)
provide("searching", searching)
provide("settings", settings)

// console.log(data)

</script>

<template>
  <div class="home_wrapper">

    <div class="settings_header">
      <div class="search_area">
        <search_bar/>
      </div>

      <div class="settings_area">
        <label for="icon_toggle" class="label">Icon only</label>
        <input id="icon_toggle" type="checkbox" v-model="settings.icon_only">

        <label for="icon_size" class="label">Icon size</label>
        <!--        <input id="icon_size" type="number" min="0.1" max="2" step="0.1" v-model="settings.icon_scale">-->
        <input id="icon_size" type="range" min="0.3" max="2" step="0.1" v-model="settings.icon_scale">
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

.label {
  /*height: 20px;*/
  /*overflow: hidden;*/
  white-space: wrap;
}

.search_area {
  position: sticky;
  /*top: 13px;*/
  left: auto;
  right: auto;

  display: flex;
  gap: 10px;
  z-index: 10;
}

.settings_area {
  position: sticky;

  display: flex;
  flex-flow: row wrap;
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
  height: 30px;
}

</style>
