<script setup>
import {ref, onBeforeMount, onMounted} from 'vue';
import {RecycleScroller} from 'vue-virtual-scroller';

const items = ref([]);

onBeforeMount(() => {
  for (let i = 0; i < 20000; i += 1) {
    items.value.push({id: `id-${i.toString()}`});
  }

  window.setInterval(() => {
    items.value.push({id: `id-${items.value.length.toString()}`});
  }, 1000);
});
</script>

<template>
  <recycle-scroller v-slot="{ item }"
                    class="scroller"
                    :items="items"
                    :item-size="48">
    <div>{{ item.id }}</div>
  </recycle-scroller>
</template>

<style scoped>
.scroller {
  outline: 1px solid red;
  /*width: 100vh;*/
  height: 100vh;
  /*scrollbar-gutter: stable;*/
  overflow-y: scroll;
}
</style>
