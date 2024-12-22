<script setup>
import {RouterLink, RouterView} from 'vue-router'
</script>

<template>
  <div class="wrapper">
    <RouterView/>
  </div>
</template>

<style scoped>
.wrapper {
  outline: 1px solid red;
  position: relative;

  margin: 0 0 0 0;
  max-width: 1080px;
  min-height: 80vh;
  /*overflow-x: clip;*/

  padding: 0 40px 0 40px;
}
</style>
