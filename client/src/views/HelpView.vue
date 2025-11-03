<script setup>

</script>

<template>
  <div class="info_wrapper">

    <div class="text_wrapper">
      <div class="text_block">
        <h1>Using icons</h1>
        <p>Copy the given icon name to the "icon" field of your HDA. Either the full path or just the file name should work.</p>
        <img src="/help_images/img_1.jpg" alt="" class="image_block">

      </div>

    </div>
  </div>
</template>

<style scoped>
.info_wrapper {
  display: flex;
  flex-flow: column;

  justify-items: center;
  justify-content: center;
  align-items: center;
  margin: 50px 0 0 0;
  /*padding: 0;*/
  position: relative;
  color: white;
}

.text_wrapper {
  display: flex;
  flex-flow: column;
  gap: 70px;
  max-width: 1000px;
  /*width: 70%;*/
}

.text_block {
  /*font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";*/
  font-size: 1em;
  line-height: 1.5;
  word-wrap: break-word;
  font-weight: 400;
}

h1 {
  font-size: 1.5em;
  font-weight: 700;
  margin-bottom: 5px;
}

p {
  font-size: 16px;
  color: #e6edf3;
}

.image_block {
  /*outline: 1px solid red;*/
  /*height: 200px;*/
  margin: 15px 0 15px 0;
  width: 100%;
  object-fit: cover;
  /*border: 2px solid rgba(69, 69, 69, 0.5);*/
  /*height: 350px;*/
  border-radius: 8px;
}

</style>
