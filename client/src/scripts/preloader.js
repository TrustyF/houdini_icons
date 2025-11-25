// preload routes
import {createVNode, render} from "vue";

function chunkArray(array, chunkSize) {
  const chunks = [];
  for (let i = 0; i < array.length; i += chunkSize) {
    chunks.push(array.slice(i, i + chunkSize));
  }
  return chunks;
}

const runIdle = (fn) => {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(fn, {timeout: 50000});
  } else {
    setTimeout(fn, 50000);
  }
}

function runChunks(items, chunkSize, fn) {
  return new Promise(resolve => {
    let chunks = chunkArray(items, chunkSize)
    let i = 0;

    const processNextChunk = () => {
      if (i >= chunks.length) {
        resolve()
        return;
      }

      chunks[i].forEach(fn); // call your processing function on each item
      i++;
      runIdle(processNextChunk);
    };
    runIdle(processNextChunk);
  })
}

export async function preload(router) {

  await router.isReady()
  await new Promise(resolve => {
    if (document.readyState === 'complete') {
      resolve();
    } else {
      window.addEventListener('load', resolve, {once: true});
    }
  });
  await new Promise(requestAnimationFrame);
  await new Promise(resolve => setTimeout(resolve, 500));

  const preload_routes = () => {

    const routes = router.options.routes

    function load_route(route) {
      if (typeof route.component === 'function') route.component();
      if (route.components) Object.values(route.components).forEach((comp) => {
        if (typeof comp === 'function') comp()
      });
    }

    // load top-level routes then children
    runChunks(routes, 1, (route) => load_route(route))
      .then(() => {
        routes.forEach((r) => {
          const children = r.children
          if (children) runChunks(children, 2, (route) => load_route(route))
        })
      })
  }

  const preload_thumbnails = async () => {
    try {
      const res = await fetch('/manifest.json');
      const manifest = await res.json();

      //  2. Preload small images / thumbnails
      const atlasIcons = manifest['atlas'].map(f => `/atlas/${f}`);
      const helpImage = manifest['help'].map(f => `/help_images/${f}`);
      const allUrls = [...atlasIcons, ...helpImage];

      runChunks(allUrls, 1, (url) => {
        const img = new Image()
        img.src = url
      })

    } catch (e) {
      console.warn('Failed to preload manifest', e)
    }
  }

  runIdle(preload_routes)
  runIdle(preload_thumbnails)
}
