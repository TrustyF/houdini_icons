import './assets/main.css'
import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import LazyComponent from 'v-lazy-component'
import rrweb_plugin from './scripts/rrweb_plugin'
import {preload} from "@/scripts/preloader.js";
import {clickOutside} from "@/scripts/click_outside.js";

const app = createApp(App)

app.directive('click-outside', clickOutside)
app.use(LazyComponent)
app.use(router)
app.mount('#app')

rrweb_plugin.start()
preload(router).then()
