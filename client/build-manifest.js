// build-manifest.js
import fs from 'fs';
import path from 'path';

const folders = [
  {name: 'atlas', path: './public/atlas/'},
  {name: 'help', path: './public/help_images/'},
];

const manifest = {};

function extractNumber(filename) {
  const match = filename.match(/\d+/);
  return match ? parseInt(match[0], 10) : 0;
}

folders.forEach(({name, path: folderPath}) => {
  const items = fs
    .readdirSync(folderPath)
    .filter(file => !file.startsWith('.'))
    .sort((a, b) => extractNumber(a) - extractNumber(b)); // numeric sort

  manifest[name] = items.map(file => `${file}`);
});

fs.writeFileSync(
  './public/manifest.json',
  JSON.stringify(manifest, null, 2)
);

console.log('Manifest generated!');
