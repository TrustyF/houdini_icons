<script setup>
import {defineAsyncComponent, onMounted, provide, reactive, ref, watch} from "vue";

const search_bar = defineAsyncComponent(() => import("@/components/generic/search_bar.vue"))
const settings_bar = defineAsyncComponent(() => import("@/components/generic/settings_bar.vue"))
const icon_list = defineAsyncComponent(() => import("@/components/icon/Icon_list.vue"))

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
