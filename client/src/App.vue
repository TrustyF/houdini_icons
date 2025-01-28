<script setup>
import {RouterLink, RouterView} from 'vue-router'
import {onMounted, provide, ref} from "vue";
import {ping_user_leave} from "@/scripts/log_events.js";
import Navbar from "@/components/generic/navbar.vue";
import NotificationModal from "@/components/generic/notificationModal.vue";

let alert_content = ref({
  title: 'Test title',
  message: 'Test message'
})
provide('alert_content', alert_content)

onMounted(() => {
  ping_user_leave()
  setInterval(() => ping_user_leave(), 5000)
})
</script>

<template>
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
