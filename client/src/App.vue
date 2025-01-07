<script setup>
import {RouterLink, RouterView} from 'vue-router'
import {onMounted} from "vue";
import {ping_user_leave} from "@/scripts/log_events.js";

onMounted(()=>{
  ping_user_leave()
  setInterval(() => ping_user_leave(), 5000)
})
</script>

<template>
  <div class="wrapper">
    <RouterView/>
  </div>
</template>

<style scoped>
.wrapper {
  /*outline: 1px solid red;*/
  position: relative;

  margin: 0 0 0 0;
  /*max-width: 1080px;*/
  min-height: 80vh;
  /*overflow-x: clip;*/

  /*padding: 0 40px 0 40px;*/
}
</style>
