import {pack, record} from "rrweb";
import {axios} from "@bundled-es-modules/axios";
import {geo_location, get_session_seed} from "@/scripts/session.js";

let stopRecording = null;
let events = [];
let sendInterval = null;

let local_url = 'http://127.0.0.1:5000'
let server_url = 'https://analytics-trustyfox.pythonanywhere.com'
let curr_api = server_url
let project = 'houdini_icons'

let url = `${curr_api}/event/add`

async function send_batch(events) {
  let geo = await geo_location
  let sid = get_session_seed()
  let params = {
    source: project,
    sid: sid,
    geo: geo,
    events: events
  }

  axios.post(url, params).catch((e) => {
    console.log(e)
  })

}

export default {
  start() {
    if (stopRecording) return;

    stopRecording = record({
      emit(event) {
        // if ([2,3].includes(event.type)) {
          events.push(JSON.stringify(event));
        // }
      },
      inlineStylesheet: false,
      slimDOMOptions: 'all',
      sampling: {
        mousemove: 100,
        mouseInteraction: false,
        scroll: 150,
        input: 'last',
      },
    });

    sendInterval = setInterval(() => {
      if (events.length === 0) return;
      send_batch(events)
      console.log(events.length)
      events = [];
    }, 2500);
  },

  stop() {
    if (stopRecording) {
      stopRecording();
      stopRecording = null;
    }
    if (sendInterval) {
      clearInterval(sendInterval);
      sendInterval = null;
    }
    events = [];
  },
};
