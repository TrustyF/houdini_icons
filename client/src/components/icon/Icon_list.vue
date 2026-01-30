<script setup>
import data from "@/assets/database.json";
import {defineAsyncComponent, inject, provide, onBeforeMount, onMounted, reactive, ref, watch, shallowRef} from "vue";
import Icon_container from "@/components/icon/Icon_container.vue";

let search_timeout;
const filtered_data = shallowRef([])

const search = inject("search");
const searching = inject("searching");
const icon_modal_vis = inject("icon_modal_vis");
const icon_list_ref = ref()

let ico_per_page = 51
let page = 1
let added_icons = 0

function make_match(item, search_text) {
  if (!search_text) return true

  if (item.name.toLowerCase().includes(search_text)) return true
  return item.tags?.some(t => t.name.toLowerCase().includes(search_text));
}


function make_search(append = true) {

  const search_text = search.value.trim().toLowerCase();
  let new_data = data

  new_data.filter(item => make_match(item, search_text))

  console.log(new_data)

  if (append) {
    let pushed = new_data.slice(Math.max(0, page - 1) * ico_per_page, page * ico_per_page)
    filtered_data.value = [...filtered_data.value, ...pushed]
    added_icons = pushed.length
  } else {
    page = 1
    filtered_data.value = [...new_data.slice(0, page * ico_per_page)]
    added_icons = ico_per_page
  }

  setTimeout(() => {
    searching.value = search.value.length > 0
    check_list_size()
  }, 5)
}

function check_list_size() {
  const padding = 2000

  if (!icon_list_ref.value) return

  const rect = icon_list_ref.value.getBoundingClientRect();
  const windowHeight = window.innerHeight || document.documentElement.clientHeight;

  // Check if the bottom of the element is within the visible viewport
  if (rect.bottom > -padding && rect.bottom <= windowHeight + padding && added_icons > 0) {
    page += 1
    make_search()
    setTimeout(() => check_list_size(), 500)
  }
}


watch(search, (oldV, newV) => {
  icon_modal_vis.value = false
  clearTimeout(search_timeout);
  search_timeout = setTimeout(() => {
    requestAnimationFrame(() => {
      make_search(false)
    })
  }, 500); // Delay the operation

})

onMounted(() => {
  make_search()
  addEventListener("scroll", check_list_size)
  check_list_size()
})

</script>
<template>


  <div class="icons_list" ref="icon_list_ref">

    <lazy-component class="icon_list_elem"
                    v-for="icon in filtered_data"
                    :key="icon['id']" :threshold="0.1" rootMargin="0px 0px 2000px 0px">
      <icon_container :data="icon"/>
    </lazy-component>

    <div :class="`list-spinner ${searching ? 'visible':''}`">
      <div class="spinner-border"></div>
    </div>

    <div class="empty" :class="`${filtered_data.length < 1 ? 'empty_vis' : ''}`">
      <h1>No results</h1>
    </div>

  </div>

</template>
<style scoped>

.icons_list {
  content-visibility: auto;
  contain-intrinsic-size: 150px;
  position: relative;

  margin-top: 20px;
  margin-bottom: 300px;
  /*outline: 1px solid red;*/

  display: flex;
  flex-flow: row wrap;
  justify-content: flex-start;
  align-items: flex-start;
  /*gap: 5px;*/
}

.icon_list_elem {

}

.list-spinner {
  display: flex;
  justify-content: center;
  width: 100%;

  visibility: hidden;
  opacity: 100;
  transition: 250ms opacity;
}

.empty {
  display: flex;
  justify-content: center;
  width: 100%;

  visibility: hidden;
  opacity: 0;
  transition: 250ms opacity;
  /*transition-delay: 500ms;*/
}

.empty_vis {
  transition-delay: 250ms;
  visibility: visible;
  opacity: 1;
}

.visible {
  transition-delay: 250ms;
  visibility: visible;
  opacity: 0;
}

</style>
