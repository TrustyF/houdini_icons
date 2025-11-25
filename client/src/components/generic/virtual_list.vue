<script setup>
import {ref, computed} from 'vue'
import {useVirtualizer} from '@tanstack/vue-virtual'

const props = defineProps({
  nodes: {type: Array, required: true},
  rowHeight: {type: Number, default: 100},
  columnsPerRow: {type: Number, default: 4},
  viewportHeight: {type: Number, default: 400}
})

const viewport = ref(null)

const totalRows = computed(() =>
  Math.ceil(props.nodes.length / props.columnsPerRow)
)

const rowVirtualizer = useVirtualizer({
  count: 10000,
  getScrollElement: () => viewport.value,
  estimateSize: () => 35,
  overscan: 5
})

</script>

<template>
  <div ref="viewport" class="viewport">
    <div
      :style="{ height: totalHeight + 'px', width: '100%', position: 'relative' }"
    >
      <div
        v-for="virtualRow in virtualRows"
        :key="virtualRow.index"
        :style="{
          position: 'absolute',
          top: virtualRow.start + 'px',
          left: '0',
          display: 'flex',
          width: '100%'
        }"
        class="row"
      >
        <div
          v-for="colIndex in columnsPerRow"
          :key="colIndex"
          class="grid-item"
          v-show="nodes[virtualRow.index * columnsPerRow + (colIndex - 1)]"
        >
          {{ nodes[virtualRow.index * columnsPerRow + (colIndex - 1)].name }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.viewport {
  height: 400px; /* can pass via prop */
  overflow-y: auto;
  border: 1px solid #ccc;
}

.row {
  display: flex;
}

.grid-item {
  flex: 1;
  border: 1px solid #eee;
  box-sizing: border-box;
  height: 100px; /* same as rowHeight */
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
