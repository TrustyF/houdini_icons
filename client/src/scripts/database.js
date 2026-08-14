import {shallowRef} from "vue";

export const icon_data = shallowRef([]);
export const icon_data_ready = shallowRef(false);

async function fetch_json(url) {
  const res = await fetch(url);
  return res.json();
}

let resolve_ready;
// Resolves once the first chunk has landed, so callers (the icon list,
// the modal) can render immediately instead of waiting on the whole dataset.
export const icon_data_promise = new Promise((resolve) => {
  resolve_ready = resolve;
});

async function load() {
  const manifest = await fetch_json(`${import.meta.env.BASE_URL}database/manifest.json`);
  const [first, ...rest] = manifest.chunks;

  icon_data.value = await fetch_json(`${import.meta.env.BASE_URL}database/${first}`);
  icon_data_ready.value = true;
  resolve_ready();

  for (const chunk of rest) {
    const items = await fetch_json(`${import.meta.env.BASE_URL}database/${chunk}`);
    icon_data.value = [...icon_data.value, ...items];
  }
}

// Kicked off once, at first import, instead of blocking app mount on it.
load().catch((err) => console.error('Failed to load icon database', err));
