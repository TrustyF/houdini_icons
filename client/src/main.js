import './assets/main.css'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import LazyComponent from 'v-lazy-component'

const app = createApp(App)

app.use(LazyComponent)
app.use(router)
app.mount('#app')
