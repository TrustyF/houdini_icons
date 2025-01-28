<script setup>

import {inject, ref, watch} from "vue";

let alert_content = inject('alert_content')
let alert_timeout = null
let visible = ref(false)

watch(alert_content,(value, oldValue, onCleanup)=>{

  visible.value = true

  clearTimeout(alert_timeout)
  alert_timeout = setTimeout(()=>{
    visible.value = false
  },2000)

})

</script>

<template>
  <div :class="`notification_wrapper ${visible ? 'visible':''}`">
    <div class="bi-check-circle" style="font-size: 2em"/>
    <div class="alert_text_wrapper">
      <h1>{{ alert_content['title'] }}</h1>
      <h2>{{ alert_content['message'] }}</h2>
    </div>
  </div>
</template>

<style scoped>
.notification_wrapper {
  display: flex;
  flex-flow: row wrap;
  position: fixed;
  gap: 10px;

  justify-content: center;
  align-items: center;

  color: rgb(230, 230, 230);

  background-color: #1d2a36;
  /*width: 50vw;*/
  padding: 10px 20px 10px 20px;
  margin-bottom: 20px;
  border-radius: 10px;

  left: 50%;
  transform: translate(-50%) translate(0,20px);
  bottom: 0;
  z-index: 100;

  transition: 250ms ease-in-out;

  visibility: hidden;
  opacity: 0;
}
.visible {
  transform: translate(-50%) translate(0,0);
  visibility: visible;
  opacity: 1;
}

.alert_text_wrapper {
  display: flex;
  flex-flow: column;
  gap: 5px;
  font-size: 0.5em;
  line-height: 1;
}
.alert_text_wrapper h1 {
  font-weight: 1000;
}
.alert_text_wrapper h2 {
  color: rgb(179, 179, 179);
}
</style>
