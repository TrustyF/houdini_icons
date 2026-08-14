<script setup>
</script>

<template>
  <nav>
    <RouterLink to="/" class="link" active-class="link_active">
      <img src="/favicon.ico" alt="home_icon" class="home_icon">
      <h1>Houdini Icons</h1>
    </RouterLink>

    <RouterLink to="/help" class="link" active-class="link_active">
      <h2>
        <span class="help_text_full">How to use</span>
        <span class="help_text_short">Help</span>
      </h2>
    </RouterLink>

    <div class="external_links">
      <a class="github-button kofi-button" href="https://ko-fi.com/arthursirjacobs" target="_blank"
         rel="noopener noreferrer">
        <div class="bi-cup-hot-fill"/>
        <p>Ko-fi</p>
      </a>
<!--      <a class="github-button" href="https://github.com/TrustyF/houdini_icons" target="_blank"-->
<!--         rel="noopener noreferrer">-->
<!--        <div class="bi-github"/>-->
<!--      </a>-->
      <a class="github-button hide_on_mobile" href="https://github.com/TrustyF/houdini_icons/issues" target="_blank"
         rel="noopener noreferrer" title="Issue" aria-label="Issue">
        <div class="bi-exclamation-circle"/>
        <p>Issue</p>
      </a>
      <a class="github-button collapse_on_mobile" href="https://arthur-sirjacobs.art/" target="_blank"
         rel="noopener noreferrer" title="Arthur Sirjacobs" aria-label="Arthur Sirjacobs">
        <div class="bi-person-fill"/>
        <p>Arthur Sirjacobs</p>
      </a>
    </div>
  </nav>

</template>

<style scoped>
nav {
  display: flex;
  flex-flow: row wrap;
  align-items: center;
  column-gap: 30px;
  row-gap: 10px;

  margin: 20px 0 20px 0;
}

.home_icon {
  width: 30px;
  object-fit: contain;
}

.link {
  display: flex;
  flex-flow: row;
  gap: 3px;
  align-items: center;

  h1 {
    line-height: 1em;
    text-transform: uppercase;
    font-size: 1em;
  }

  h2 {
    line-height: 1.2em;
    font-size: 1.1em;
  }
}

.link_active {
  color: white;
}

.help_text_short {
  display: none;
}

@media (max-width: 480px) {
  .help_text_full {
    display: none;
  }

  .help_text_short {
    display: inline;
  }

  .github-button.collapse_on_mobile p {
    display: none;
  }

  .github-button.hide_on_mobile {
    display: none;
  }
}

.external_links {
  /*position: absolute;*/
  margin-left: auto;
  right: 0;
  top: 0;
  display: flex;
  flex-flow: row wrap;
  gap: 5px;
}

.github-button {
  display: flex;
  flex-flow: row;
  gap: 5px;
  line-height: 1;
  font-size: 0.9em;
  padding: 6px 8px 6px 8px;

  border: 1px solid #4d4d4d;
  background-color: #282828;
  color: #b3b3b3;

  z-index: 5;
  border-radius: 10px;
}

.github-button:hover {
  background-color: #333333;
}

.kofi-button {
  border-color: #5a3a1e;
  color: #ff9d5c;
}

.kofi-button:hover {
  background-color: #4a2e0f;
}
</style>
