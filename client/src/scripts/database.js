import {computed, ref, shallowRef, watch} from "vue";
import versions from "@/assets/versions.json";

export {versions};

// Not a Houdini version: shows every icon once, by its newest drawing
export const ALL_VERSIONS = 'all';

const VERSION_STORAGE_KEY = 'houdini_version';

// A visitor's picked version, if it's still one we serve. Storage can be
// unavailable (private windows, blocked site data), so it's best-effort.
function stored_version() {
  try {
    const key = localStorage.getItem(VERSION_STORAGE_KEY);
    return key === ALL_VERSIONS || versions.some((v) => v.key === key) ? key : null;
  } catch {
    return null;
  }
}

// One entry per drawing: an icon redrawn between Houdini versions appears
// once per drawing, each listing the versions (`versions`) that use it.
export const all_icons = shallowRef([]);

export const selected_version = ref(stored_version() ?? versions.at(-1).key);

watch(selected_version, (key) => {
  try {
    localStorage.setItem(VERSION_STORAGE_KEY, key);
  } catch {
    // Not remembered across visits, but the switch itself still works
  }
});

const version_rank = Object.fromEntries(versions.map((v, i) => [v.key, i]));

// "20.5", "22 (legacy UI)": the label without the repeated "Houdini"
const version_label = (key) => versions.find((v) => v.key === key).label.replace(/^Houdini /, '');

// Which versions use a drawing, as runs of consecutive versions: "21+" while
// the newest version still has it, otherwise "19.5 – 20.5 only" (removed or
// redrawn since).
export function version_span(keys) {
  return version_span_parts(keys).map(({text}) => text).join(', ');
}

// version_span's runs, each with the release it starts in (`release`, what
// a `#new` search for that run takes)
export function version_span_parts(keys) {
  const latest = versions.at(-1).key;
  return version_runs(keys).map((run) => {
    const [first, last] = [run[0], run.at(-1)];
    const release = release_of(first);
    // A run reaching the newest version from that release's legacy-UI set
    // means "new in that release", in both UIs: name the release, not the skin
    if (last === latest) return {text: `${version_label(release)}+`, release};
    const text = first === last ? `${version_label(first)} only` : `${version_label(first)} – ${version_label(last)} only`;
    return {text, release};
  });
}

// The releases a drawing appears in without being in the version before:
// added or redrawn there (a legacy-UI set counts as its release)
export function new_in(keys) {
  return new Set(version_runs(keys).map((run) => release_of(run[0])));
}

const release_of = (key) => key.replace(/-legacy$/, '');

function version_runs(keys) {
  const order = versions.map((v) => v.key);
  const used = new Set(keys);
  const runs = [];
  order.forEach((key, i) => {
    if (!used.has(key)) return;
    if (runs.length && used.has(order[i - 1])) runs.at(-1).push(key);
    else runs.push([key]);
  });
  return runs;
}

// The name Houdini knows the icon by, e.g. BUTTONS_folder (matches its icon
// index, checked against Houdini 22's): CATEGORY_name, except CONVERTED
// icons have no prefix and Pics use PICS_
export function icon_houdini_name({category, name}) {
  if (category === 'CONVERTED') return name;
  if (category === 'Pics') return `PICS_${name}`;
  return `${category}_${name}`;
}

export const version_list = (keys) => `Used in: ${keys.map((key) => `Houdini ${version_label(key)}`).join(', ')}`;

// Every icon once, by the drawing used in its newest version (so icons
// Houdini has since removed show their last drawing)
function newest_drawings(entries) {
  const newest = new Map();
  for (const entry of entries) {
    const key = `${entry.category}/${entry.name}`;
    const rank = Math.max(...entry.versions.map((v) => version_rank[v]));
    if (!newest.has(key) || rank > newest.get(key).rank) newest.set(key, {entry, rank});
  }
  const keep = new Set([...newest.values()].map(({entry}) => entry));
  return entries.filter((entry) => keep.has(entry));
}

// Each version uses at most one drawing per icon, so this is that version's icon set
export const icon_data = computed(() => {
  if (selected_version.value === ALL_VERSIONS) return newest_drawings(all_icons.value);
  return all_icons.value.filter((entry) => entry.versions.includes(selected_version.value));
});

// By id (= atlas cell), whatever version is selected
export const icon_by_id = computed(() => new Map(all_icons.value.map((entry) => [entry.id, entry])));

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
    if (typeof entry.words !== 'string') {
      throw new Error(`Invalid icon database entry at ${where}: 'words' must be a string, got ${JSON.stringify(entry.words)}`);
    }
    if (typeof entry.category !== 'string') {
      throw new Error(`Invalid icon database entry at ${where}: 'category' must be a string, got ${JSON.stringify(entry.category)}`);
    }
    if (!Array.isArray(entry.versions) || entry.versions.length < 1) {
      throw new Error(`Invalid icon database entry at ${where}: 'versions' must be a non-empty array, got ${JSON.stringify(entry.versions)}`);
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

  all_icons.value = validate_icon_entries(await fetch_json(`${import.meta.env.BASE_URL}database/${first}`), first);
  icon_data_ready.value = true;
  resolve_ready();

  for (const chunk of rest) {
    const items = validate_icon_entries(await fetch_json(`${import.meta.env.BASE_URL}database/${chunk}`), chunk);
    all_icons.value = [...all_icons.value, ...items];
  }
}

// Kicked off once, at first import, instead of blocking app mount on it.
load().catch((err) => console.error('Failed to load icon database', err));
