<script setup>
import {RouterLink, RouterView} from 'vue-router'
import {onMounted} from "vue";
import {ping_user_leave} from "@/scripts/log_events.js";
import Navbar from "@/components/generic/navbar.vue";

onMounted(()=>{
  ping_user_leave()
  setInterval(() => ping_user_leave(), 5000)
})
</script>

<template>
  <div class="home_wrapper">
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
