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

let url = `${curr_api}/session/add`

async function send_batch(events) {
  let geo = await geo_location
  console.log(geo)
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
        events.push(JSON.stringify(event));
      },
      blockClass: 'notification_wrapper'
    });

    sendInterval = setInterval(() => {
      if (events.length === 0) return;
      send_batch(events).then()
      console.log(events.length)
      events = [];
    }, 10000);
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
