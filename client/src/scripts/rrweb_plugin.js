import {record} from "rrweb";
import {axios} from "@bundled-es-modules/axios";
import {geo_location, get_session_seed} from "@/scripts/session.js";

let stopRecording = null;
let events = [];
let sendInterval = null;
let geo = null;
let flushOnHide = null;
let visibilityHandler = null;

let server_url = 'https://analytics.arthursirjacobs.com'
let project = 'houdini_icons'

let url = `${server_url}/api/session/add`

async function send_batch(batch) {
  let params = {
    source: project,
    sid: get_session_seed(),
    geo: geo,
    events: batch
  }

  await axios.post(url, params).catch(() => {
    // failed to send, requeue the raw (unpacked) batch for the next flush
    events = batch.concat(events);
  })
}

export default {
  start() {
    if (stopRecording) return;

    geo_location.then(g => geo = g);

    stopRecording = record({
      emit(event) {
        // keep the hot input path cheap; compression happens once per flush, not per event
        events.push(event);
      },
      blockClass: 'notification_wrapper',
      sampling: {
        mousemove: 50,
        mouseInteraction: true,
        scroll: 150,
        input: 'last'
      },
      slimDOMOptions: 'all'
    });

    sendInterval = setInterval(() => {
      if (events.length === 0) return;
      let batch = events;
      events = [];
      send_batch(batch).then()
    }, 10000);

    flushOnHide = () => {
      if (events.length === 0) return;
      let params = {
        source: project,
        sid: get_session_seed(),
        geo: geo,
        events: events
      }
      navigator.sendBeacon(url, new Blob([JSON.stringify(params)], {type: 'application/json'}));
      events = [];
    }
    visibilityHandler = () => {
      if (document.visibilityState === 'hidden') flushOnHide();
    }
    document.addEventListener('visibilitychange', visibilityHandler);
    window.addEventListener('pagehide', flushOnHide);
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
    if (flushOnHide) {
      document.removeEventListener('visibilitychange', visibilityHandler);
      window.removeEventListener('pagehide', flushOnHide);
      flushOnHide = null;
      visibilityHandler = null;
    }
    events = [];
  },
};
