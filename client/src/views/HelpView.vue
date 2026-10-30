<script setup>
import {onMounted} from "vue";
import Icon_image from "@/components/icon/Icon_image.vue";

// Houdini icons beside each question, by id (= atlas cell, never reused)
const ICONS = {
  use: 5001,         // BUTTONS/paste
  missing: 1600,     // MISC/faq
  search: 1938,      // PANETYPES/dashbox
  no_results: 1040,  // DIALOG/warning
  location: 552,     // COMMON/archive
}

// Smooth jump to a question, without the router treating the hash as a navigation
function scroll_to(id) {
  document.getElementById(id)?.scrollIntoView({behavior: 'smooth'})
  history.replaceState(history.state, '', `#${id}`)
}

// A shared link like /help#search opens on that question
onMounted(() => {
  if (location.hash) document.getElementById(location.hash.slice(1))?.scrollIntoView()
})
</script>

<template>
  <div class="help_wrapper">

    <header class="intro">
      <h1>FAQ</h1>
    </header>

    <nav class="toc">
      <ul>
        <li><a href="#missing" @click.prevent="scroll_to('missing')">
          <icon_image :icon_id="ICONS.missing" :scale_override="0.22"/>I can't find an icon, or it's missing in my Houdini</a></li>
        <li><a href="#search" @click.prevent="scroll_to('search')">
          <icon_image :icon_id="ICONS.search" :scale_override="0.22"/>What can I search for?</a></li>
        <li><a href="#no-results" @click.prevent="scroll_to('no-results')">
          <icon_image :icon_id="ICONS.no_results" :scale_override="0.22"/>My search returns nothing, or odd results</a></li>
        <li><a href="#location" @click.prevent="scroll_to('location')">
          <icon_image :icon_id="ICONS.location" :scale_override="0.22"/>Where are the icons located?</a></li>
      </ul>
    </nav>

    <section>
      <div class="faq_item" id="use">
        <h2>
          <icon_image :icon_id="ICONS.use" :scale_override="0.36"/>How do I use the icons?</h2>
        <div class="faq_body">
          <p>Click an icon to expand it, then click its name to copy it. Paste it into the <strong>Icon</strong> field
            of your HDA's Type Properties.</p>
          <p class="hint">Either the full path or just the file name works.</p>
          <img src="/help_images/img_1.webp" alt="Copying an icon name into an HDA's icon field" class="image_block">
        </div>
      </div>

      <div class="faq_item" id="missing">
        <h2>
          <icon_image :icon_id="ICONS.missing" :scale_override="0.36"/>I can't find an icon, or it's missing in my Houdini</h2>
        <div class="faq_body">
          <p>Not every icon exists in every version of Houdini. SideFX adds, removes and redraws icons between
            releases, so an icon you find here may be missing or look different in the version you use.</p>

          <p>Use the <strong>Houdini</strong> dropdown in the settings bar to only show the icons of your version.
            <strong>All</strong> shows every icon ever shipped, each in its newest drawing.</p>

          <p>To check a single icon, expand it and look at the label at the bottom of the card:</p>

          <div class="version_demo">
            <div class="demo_card">
              <div class="demo_row"/>
              <div class="demo_row short"/>
              <div class="demo_label">Available in Houdini 21+</div>
            </div>
            <div class="demo_callout">the version label</div>
          </div>

          <p class="hint">Hover the label to see the full list of versions.</p>
        </div>
      </div>

      <div class="faq_item" id="search">
        <h2>
          <icon_image :icon_id="ICONS.search" :scale_override="0.36"/>What can I search for?</h2>
        <div class="faq_body">
          <p>Start a search with one of these prefixes to match one thing exactly:</p>
          <dl class="prefix_list">
            <dt><code>#tag arrow</code></dt>
            <dd>Icons with exactly that tag: what the icon shows or its style.</dd>
            <dt><code>#shape circle</code></dt>
            <dd>Icons built from that basic shape (circle, square, triangle, line, curve, ...).</dd>
            <dt><code>#color red</code></dt>
            <dd>Icons in that color: red, orange, yellow, green, blue, purple, pink, brown, black, white, gray or
              cyan.</dd>
            <dt><code>#strict arrow</code></dt>
            <dd>Icons whose name, category, tag, shape or color is exactly that word.</dd>
            <dt><code>#category sop</code></dt>
            <dd>Every icon of a category (<code>sop</code>, <code>cop</code>, <code>buttons</code>, ...).
              <code>cop</code> doesn't include COP2.</dd>
            <dt><code>#new 21</code></dt>
            <dd>Every icon added or redrawn in that Houdini version (<code>22</code> covers both of its UI skins). It
              ignores the <strong>Houdini</strong> dropdown, so it can show icons your version doesn't have: check
              the label at the bottom of each card.</dd>
          </dl>
          <p class="hint">Click an icon to expand it, then click any of its tags, its category or a version in its
            label to run that search.</p>
        </div>
      </div>

      <div class="faq_item" id="no-results">
        <h2>
          <icon_image :icon_id="ICONS.no_results" :scale_override="0.36"/>My search returns nothing, or odd results</h2>
        <div class="faq_body">
          <p>Try a single, simple word, and drop any <code>#</code> prefix, since those only match exactly. If that still finds nothing, set the <strong>Houdini</strong>
            dropdown to <strong>All</strong>: the icon may not exist in the version you picked.</p>
          <p>Most tags are generated automatically, so some will be missing or a bit off. If you spot a wrong tag or
            a search that should have found something, please
            <a href="https://github.com/TrustyF/houdini_icons/issues" target="_blank" rel="noopener noreferrer">report
              it on GitHub</a>.</p>
        </div>
      </div>

      <div class="faq_item" id="location">
        <h2>
          <icon_image :icon_id="ICONS.location" :scale_override="0.36"/>Where are the icons located?</h2>
        <div class="faq_body">
          <p>Houdini keeps its icons in a single <code>icons.zip</code>, inside <code>houdini/config/Icons</code> of
            the install folder (<code>$HFS</code>). With a default install, that's:</p>
          <dl class="path_list">
            <dt>Windows</dt>
            <dd><code>C:\Program Files\Side Effects Software\Houdini 21.0.xxx\houdini\config\Icons\icons.zip</code></dd>
            <dt>macOS</dt>
            <dd><code>/Applications/Houdini/Houdini21.0.xxx/Frameworks/Houdini.framework/Versions/Current/Resources/houdini/config/Icons/icons.zip</code></dd>
            <dt>Linux</dt>
            <dd><code>/opt/hfs21.0.xxx/houdini/config/Icons/icons.zip</code></dd>
          </dl>
          <p class="hint">Replace <code>21.0.xxx</code> with your installed version.</p>
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
.help_wrapper {
  display: flex;
  flex-flow: column;
  gap: 20px;
  max-width: 760px;
  margin: 50px auto 150px auto;
  padding: 0 16px;
  color: #e6edf3;
  line-height: 1.65;
}

h1 {
  font-size: 2.2em;
  font-weight: 700;
}

section p {
  margin-bottom: 14px;
  max-width: 65ch;
}

strong {
  color: white;
  font-weight: 600;
}

.hint {
  color: #9a9a9a;
  font-size: 0.9em;
}

code {
  font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
  font-size: 0.9em;
  padding: 2px 8px;
  border-radius: 4px;
  background-color: #151515;
  border: 1px solid #333333;
  color: #e6e6e6;
  font-weight: 400;
  white-space: nowrap;
}

.image_block {
  display: block;
  margin: 22px 0 0 0;
  width: 100%;
  aspect-ratio: 16/9;
  object-fit: cover;
  border-radius: 8px;
}

/* A stripped-down expanded card, pointing at the real card's version label */
.version_demo {
  display: flex;
  flex-flow: row wrap;
  align-items: flex-end;
  gap: 12px 16px;
  margin: 14px 0 18px 0;
}

.demo_card {
  display: flex;
  flex-flow: column;
  gap: 8px;
  width: 240px;
  padding: 14px;
  border-radius: 8px;
  background-color: #151515;
  border: 1px solid #333333;
}

.demo_row {
  height: 10px;
  border-radius: 4px;
  background-color: #2e2e2e;
}

.demo_row.short {
  width: 60%;
}

/* Same look as .version_note in Icon_modal.vue, highlighted */
.demo_label {
  margin-top: 4px;
  padding: 2px 6px;
  align-self: flex-start;
  color: #808080;
  font-size: 0.75em;
  line-height: 1.2;
  border-radius: 4px;
  outline: 2px solid #6a93b8;
  outline-offset: 2px;
}

.path_list {
  display: flex;
  flex-flow: column;
  gap: 4px;
  margin: 4px 0 12px 0;
}

.path_list dt {
  margin-top: 8px;
  color: #b3b3b3;
  font-size: 0.85em;
}

/* Paths are long: let them wrap anywhere instead of overflowing the panel */
.path_list code {
  display: block;
  padding: 6px 10px;
  white-space: normal;
  overflow-wrap: anywhere;
  user-select: all;
}

/* Search prefixes: the prefix, then what it matches */
.prefix_list {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 10px 16px;
  margin: 4px 0 18px 0;
}

.prefix_list dd {
  margin: 0;
}

@media (max-width: 520px) {
  .prefix_list {
    grid-template-columns: 1fr;
    gap: 4px;
  }

  .prefix_list dd {
    margin-bottom: 8px;
  }
}

/* Every question at a glance, linking down to its answer */
.toc ul {
  display: flex;
  flex-flow: column;
  gap: 6px;
  padding: 16px 20px;
  list-style: none;
  border-radius: 8px;
  background-color: #151515;
  border: 1px solid #333333;
}

.toc a {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6a93b8;
  text-decoration: none;
}

.toc a:hover {
  text-decoration: underline;
}

.faq_item {
  scroll-margin-top: 20px;
}

/* Long questions wrap on phones; the icon keeps its size */
.toc a > .icon_img,
.faq_item h2 > .icon_img {
  flex-shrink: 0;
}

/* FAQ: every question listed open, split by a hairline */
.faq_item + .faq_item {
  border-top: 1px solid #2a2a2a;
}

.faq_item h2 {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 32px 0 14px 0;
  color: white;
  font-size: 1.2em;
  font-weight: 700;
  line-height: 1.35;
}

/* Answers sit a step dimmer than their question, so the questions stand out */
/* The wrapper's gap already spaces the first question from the title */
.faq_item:first-child h2 {
  padding-top: 0;
}

.faq_body {
  padding: 0 0 32px 0;
  color: #c2c8ce;
}

.faq_body a {
  color: #6a93b8;
}

.demo_callout {
  color: #6a93b8;
  font-size: 0.9em;
  padding-bottom: 8px;
}

.demo_callout::before {
  content: '← ';
}

/* The callout wraps under the card on narrow screens, so point up instead */
@media (max-width: 520px) {
  .demo_callout::before {
    content: '↑ ';
  }
}
</style>
