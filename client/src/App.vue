<script setup>
import {RouterView} from 'vue-router'
import {defineAsyncComponent, provide, ref} from "vue";
import Navbar from "@/components/generic/navbar.vue";

let NotificationModal = defineAsyncComponent(() => import("@/components/generic/notificationModal.vue"))

let alert_content = ref({
  title: 'Test title',
  message: 'Test message'
})
provide('alert_content', alert_content)

</script>

<template>
  <img src="/atlas/atlas_0.webp" fetchpriority="high" style="display: none" alt=""/>
  <img src="/atlas/atlas_1.webp" fetchpriority="high" style="display: none" alt=""/>
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
