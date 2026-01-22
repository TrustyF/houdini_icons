<script setup>

</script>

<template>
  <nav>
    <RouterLink to="/" class="link" active-class="link_active">
      <img src="/favicon.ico" alt="home_icon" class="home_icon">
      <h1>Houdini Icons</h1>
    </RouterLink>

    <RouterLink to="/help" class="link" active-class="link_active">
      <h2>How to use</h2>
    </RouterLink>

    <div class="external_links">
      <a class="github-button" href="https://github.com/TrustyF/houdini_icons" target="_blank"
         rel="noopener noreferrer">
        <div class="bi-github"/>
        <p>GitHub</p>
      </a>
      <a class="github-button" href="https://github.com/TrustyF/houdini_icons/issues" target="_blank"
         rel="noopener noreferrer">
        <div class="bi-exclamation-circle"/>
        <p>Issue</p>
      </a>
    </div>
  </nav>

</template>

<style scoped>
nav {
  display: flex;
  flex-flow: row wrap;
  align-items: center;
  gap: 20px;

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
  margin-right: 50px;

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

.external_links {
  /*position: absolute;*/
  margin-left: auto;
  right: 0;
  top: 0;
  display: flex;
  flex-flow: row;
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
</style>
