<script setup>
import {inject, onMounted, watch, ref, computed} from "vue";
import {RouterLink} from "vue-router";

let props = defineProps({
  test: {
    type: String,
    default: null,
  },
});
let emits = defineEmits(["test"]);

</script>

<template>
  <nav>

    <div style="display: flex;flex-flow: row;gap: 3px;align-items: center;margin-right: 50px;">
      <img src="/favicon.ico" alt="home_icon" class="home_icon">
      <h1 style="font-size: 1em;line-height: 1em;text-transform: uppercase ">Houdini Icons</h1>
    </div>

    <RouterLink class="link" to="/">Home</RouterLink>
<!--    <RouterLink class="link" to="/report">report bug</RouterLink>-->
  </nav>
</template>

<style scoped>
nav {
  display: flex;
  flex-flow: row wrap;
  align-items: center;
  gap: 20px;

  margin: 20px 0 20px 0;
}
.home_icon {
  width: 30px;
  object-fit: contain;
}
.link{
  /*outline: 1px solid red;*/
  color: #969e9e;

  font-size: 1em;
  padding: 20px;
  margin: -13px -10px -10px -10px;
  /*text-decoration: none;*/
  font-weight: 800;
}
</style>
