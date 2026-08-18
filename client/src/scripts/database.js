import {shallowRef} from "vue";

export const icon_data = shallowRef([]);
export const icon_data_ready = shallowRef(false);

async function fetch_json(url) {
  const res = await fetch(url);
  return res.json();
}

// Validates the shape the rest of the app assumes (Icon_list.vue,
// Icon_container.vue, Icon_modal.vue all access these fields directly).
// A schema drift here should throw loudly instead of shipping `undefined`
// into templates and clipboard/download paths silently.
function validate_icon_entries(items, source) {
  items.forEach((entry, i) => {
    const where = `${source}[${i}]`;

    if (typeof entry !== 'object' || entry === null) {
      throw new Error(`Invalid icon database entry at ${where}: expected object, got ${typeof entry}`);
    }
    if (typeof entry.name !== 'string') {
      throw new Error(`Invalid icon database entry at ${where}: 'name' must be a string, got ${JSON.stringify(entry.name)}`);
    }
    if (typeof entry.category !== 'string') {
      throw new Error(`Invalid icon database entry at ${where}: 'category' must be a string, got ${JSON.stringify(entry.category)}`);
    }
    if (!Array.isArray(entry.tags)) {
      throw new Error(`Invalid icon database entry at ${where}: 'tags' must be an array, got ${JSON.stringify(entry.tags)}`);
    }
    entry.tags.forEach((tag, j) => {
      if (typeof tag.name !== 'string' || typeof tag.type !== 'string') {
        throw new Error(`Invalid tag at ${where}.tags[${j}]: ${JSON.stringify(tag)}`);
      }
    });
  });

  return items;
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

  icon_data.value = validate_icon_entries(await fetch_json(`${import.meta.env.BASE_URL}database/${first}`), first);
  icon_data_ready.value = true;
  resolve_ready();

  for (const chunk of rest) {
    const items = validate_icon_entries(await fetch_json(`${import.meta.env.BASE_URL}database/${chunk}`), chunk);
    icon_data.value = [...icon_data.value, ...items];
  }
}

// Kicked off once, at first import, instead of blocking app mount on it.
load().catch((err) => console.error('Failed to load icon database', err));
