<script setup>

</script>

<template>
  <nav>

    <div style="display: flex;flex-flow: row;gap: 3px;align-items: center;margin-right: 50px;">
      <img src="/favicon.ico" alt="home_icon" class="home_icon">
      <h1 style="font-size: 1em;line-height: 1em;text-transform: uppercase ">Houdini Icons</h1>
    </div>

    <!--    <RouterLink class="link" to="/">Home</RouterLink>-->
    <!--    <RouterLink class="link" to="/report">report bug</RouterLink>-->

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
  /*outline: 1px solid red;*/
  color: #969e9e;

  font-size: 1em;
  padding: 20px;
  margin: -13px -10px -10px -10px;
  /*text-decoration: none;*/
  font-weight: 800;
}

.external_links {
  position: absolute;
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
