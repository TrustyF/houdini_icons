// build-database.js
// Strips fields unused by the client (icon "image", tag "id") and splits the
// result into content-hashed chunks under public/database/, fetched
// progressively at runtime instead of bundled into the JS or downloaded as
// one multi-MB blob. Hashed filenames also mean a stale browser cache can't
// serve mismatched data across builds the way one fixed /database.json could.
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const CHUNK_SIZE = 500;
const OUT_DIR = './public/database';

const raw = fs.readFileSync('./src/assets/database.json', 'utf-8');
const data = JSON.parse(raw);

const trimmed = data.map(({image, ...entry}) => ({
  ...entry,
  tags: entry.tags.map(({id, ...tag}) => tag),
}));

fs.rmSync(OUT_DIR, {recursive: true, force: true});
fs.mkdirSync(OUT_DIR, {recursive: true});

const chunks = [];
for (let i = 0; i < trimmed.length; i += CHUNK_SIZE) {
  const json = JSON.stringify(trimmed.slice(i, i + CHUNK_SIZE));
  const hash = crypto.createHash('md5').update(json).digest('hex').slice(0, 8);
  const filename = `chunk-${chunks.length}-${hash}.json`;
  fs.writeFileSync(path.join(OUT_DIR, filename), json);
  chunks.push(filename);
}

fs.writeFileSync(
  path.join(OUT_DIR, 'manifest.json'),
  JSON.stringify({chunks, total: trimmed.length})
);

console.log(`Database generated! ${trimmed.length} icons in ${chunks.length} chunks`);
