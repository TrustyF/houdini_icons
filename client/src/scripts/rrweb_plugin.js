import {record} from "rrweb";
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

// browsers cap keepalive bodies at 64KB (shared across in-flight requests),
// anything bigger has to go as a plain fetch
const KEEPALIVE_MAX_BYTES = 60000;

function payload(batch) {
  return {
    source: project,
    sid: get_session_seed(),
    geo: geo,
    events: batch
  }
}

// sent as text/plain, a CORS-safelisted type, so these cross-origin posts need
// no preflight - a beacon can never pass one (it always sends credentials,
// which the server doesn't allow). The server's req.json() ignores the type.
// fetch rather than axios for keepalive, which XHR doesn't support
async function send_batch(batch) {
  let body = JSON.stringify(payload(batch));
  let ok = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'text/plain'},
    body: body,
    // lets a flush started as the tab hides survive the page closing
    keepalive: body.length < KEEPALIVE_MAX_BYTES
  }).then(res => res.ok).catch(() => false);

  // failed to send, requeue the raw (unpacked) batch for the next flush
  if (!ok) events = batch.concat(events);
}

function flush() {
  if (events.length === 0) return;
  let batch = events;
  events = [];
  send_batch(batch).then()
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
        input: true
      },
      slimDOMOptions: 'all'
    });

    sendInterval = setInterval(flush, 10000);

    // last chance as the page unloads, when a fetch could be cancelled
    flushOnHide = () => {
      if (events.length === 0) return;
      let queued = navigator.sendBeacon(url, new Blob([JSON.stringify(payload(events))], {type: 'text/plain'}));
      // false = over the beacon size quota, keep the events in case the page survives
      if (queued) events = [];
    }
    // the page is still alive when merely hidden (tab/app switch, screen lock),
    // so a normal send that requeues on failure beats a fire-and-forget beacon
    visibilityHandler = () => {
      if (document.visibilityState === 'hidden') flush();
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
    // send what's buffered rather than dropping it
    flush();
  },
};
