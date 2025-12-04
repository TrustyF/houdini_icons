<script setup>
import {RouterView} from 'vue-router'
import {defineAsyncComponent, provide, reactive, ref} from "vue";
import Navbar from "@/components/generic/navbar.vue";
import data from "@/assets/database.json";
import Icon_modal from "@/components/icon/Icon_modal.vue";

let NotificationModal = defineAsyncComponent(() => import("@/components/generic/notificationModal.vue"))

let alert_content = ref({
  title: 'Test title',
  message: 'Test message'
})
provide('alert_content', alert_content)

const settings = reactive({
  icon_only: false,
  icon_scale: 1,
})
const search = ref("")
const searching = ref(false)

provide("settings", settings)
provide("search", search)
provide("searching", searching)

const icon_modal_pos = ref({'x': 0, 'y': 0})
const icon_modal_vis = ref(false)
const icon_modal_id = ref(1)

provide('icon_modal_pos', icon_modal_pos)
provide('icon_modal_vis', icon_modal_vis)
provide('icon_modal_id', icon_modal_id)

function icon_modal_close() {
  icon_modal_vis.value = false
}

</script>

<template>
  <img src="/atlas/atlas_0.webp" fetchpriority="high" style="display: none" alt=""/>
  <img src="/atlas/atlas_1.webp" fetchpriority="high" style="display: none" alt=""/>

  <icon_modal :position="icon_modal_pos"
              :visibility="icon_modal_vis"
              :data="data[icon_modal_id-1]"
              @close="icon_modal_close"
  />

  <div class="home_wrapper">
    <notification-modal/>
    <navbar/>
    <RouterView/>
  </div>
</template>

<style scoped>
.home_wrapper {
  position: relative;

  margin: 0;
  /*max-width: 1080px;*/
  min-height: 80vh;
}
</style>
