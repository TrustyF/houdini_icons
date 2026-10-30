import io
import os
import json
import time
import shutil
import hashlib
import base64
import logging
from datetime import date
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import anthropic
import numpy as np
from dotenv import load_dotenv
from PIL import Image
from db_loader import session
from icon_model import Tag, Icon, IconTagAssoc, VERSIONS, canonical_tag
from icon_render import render_svg, atlas_image, changed_fraction, ATLAS_CELL

log = logging.getLogger('custom')
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

load_dotenv()
CLIENT_DIR = 'C:/A_Mod/A_Projects/Webdev/houdini_icons/client'
DB_PATH = 'assets/icon_db.db'

claude = anthropic.Anthropic(max_retries=5)  # reads ANTHROPIC_API_KEY

# Sonnet 5.5 extracts the defining details better than Haiku 5.5. Sending
# several icons per request, tags without weights, 256px images and the
# Batch API (50% off) bring it to ~$3 for every drawing (vs ~$28 one by one)
TAG_MODEL = "claude-sonnet-5-5"
ICONS_PER_REQUEST = 8
IMAGE_SIZE = 256
TAG_COLORS = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "brown", "black", "white", "gray", "cyan"]
# The schema can't cap list lengths, so responses are trimmed to these
TAG_LIMITS = {"tags": 12, "shapes": 3, "colors": 3}
# Identical drawings share one entry, which lists up to this many of their names
NAMES_IN_PROMPT = 5

TAG_PROMPT = """You tag icons from the 3D software SideFX Houdini for a visual icon search engine.
People search by typing single words for what an icon looks like, not what it does.

Each image below is one icon; tag each separately, judging only its own image. Above each image are the
name(s) of the icon(s) that use it. Use the names to understand what the drawing depicts, and include up to 3 words
for that (e.g. timeline, terrain, buoy) when they fit what's visible. Don't just repeat words from the names:
the search already matches them.

- tags: 6-12 single lowercase words someone would type to find this icon: first what the icon shows as a whole
  (the main objects and what they form), then its overall style (glossy, flat, stacked, ...).
  Skip small details like highlights, shadows, tips, slits and dots unless they are what the icon is about.
  Include any signs drawn on it (arrow, plus, cross, check, question mark, ...).
  Write numbers as one tag in digits: "64", never "sixty" and "four".
  Fewer good tags beat a long list. Examples: pen, curve, handles, glossy.
  Split descriptions into separate words: "blue cap" becomes "cap", "control points" becomes "points" and "handles".
  Only use two words for a fixed term that means something else when split, like "question mark", "life ring" or "fountain pen".
  No colors in tags (they go in colors), nothing about the grey background, and never "icon", "symbol", "logo", "houdini" or "button".
- shapes: up to 3 single-word primitives (circle, square, triangle, line, curve, ...).
- colors: up to 3 colors of the icon itself. The grey background is not part of the icon.

List every field most relevant first: search ranks by that order.
Return one entry per image, with `image` set to its number."""

TAG_SCHEMA = {
    "type": "object",
    "properties": {"icons": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "image": {"type": "integer"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "shapes": {"type": "array", "items": {"type": "string"}},
            "colors": {"type": "array", "items": {"type": "string", "enum": TAG_COLORS}},
        },
        "required": ["image", "tags", "shapes", "colors"],
        "additionalProperties": False,
    }}},
    "required": ["icons"],
    "additionalProperties": False,
}


def encode_image(svg, size=IMAGE_SIZE):
    """PNG on mid-grey, so white and light icons stay visible."""
    img = render_svg(svg, size)
    flat = Image.new('RGB', img.size, (128, 128, 128))
    flat.paste(img, mask=img)
    buffer = io.BytesIO()
    flat.save(buffer, 'PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def icon_names(group, cap):
    """`A`, `B` and `C`: the first `cap` distinct names using one drawing."""
    names = list(dict.fromkeys(f'`{i.category}/{i.name}`' for i in sorted(group, key=lambda i: i.id)))[:cap]
    return names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]


def order_weight(index):
    """Relevance from list position: 1.0 for the first entry, then 0.1 less each, down to 0.3."""
    return round(max(0.3, 1 - 0.1 * index), 2)


def tag_request(items, model=TAG_MODEL):
    """Messages API params tagging several drawings, items being (svg, names) pairs.

    Plain strings rather than Icon rows, so building and sending requests
    never touches the shared (not thread-safe) session.
    """
    content = [{"type": "text", "text": TAG_PROMPT}]
    for k, (svg, names) in enumerate(items, 1):
        content.append({"type": "text", "text": f"Image {k}: {names}"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                    "data": encode_image(svg)}})
    return {
        "model": model,
        "max_tokens": 1000 + 300 * len(items),
        "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": TAG_SCHEMA}},
        "messages": [{"role": "user", "content": content}],
    }


def parse_tags(message, count):
    """[{kind: [[name, weight], ...]} or None] per image of a tag_request response."""
    if message.stop_reason != "end_turn":
        raise RuntimeError(f'stopped with {message.stop_reason}: {getattr(message, "stop_details", None)}')
    data = json.loads(next(b.text for b in message.content if b.type == "text"))
    by_image = {e["image"]: e for e in data["icons"]}
    return [weighted(clean_tags({kind: by_image[k][kind] for kind in TAG_LIMITS})) if k in by_image else None
            for k in range(1, count + 1)]


# Words the prompt rules out that still slip through now and then
BANNED_TAGS = {"icon", "icons", "symbol", "symbols", "logo", "logos", "houdini", "button", "buttons"}

# Tags added by hand, on every drawing of these icons, after the model's
# tags are cleaned (so a banned word like "houdini" can still be given on purpose)
MANUAL_TAGS = {
    "houdini": [
        # The Houdini logo itself
        ("MISC", "logo"), ("MISC", "logo_white"),
        ("DESKTOP", "application"), ("DESKTOP", "application2"), ("DESKTOP", "application_bigsur"),
        ("DESKTOP", "application_mac"), ("DESKTOP", "application_sierra"),
        # Icons with the logo as part of a larger picture
        ("ENGINE", "open_in_houdini"), ("TOP", "houdiniserver"), ("TOP", "houdiniserverstop"),
        ("COMMON", "houdinimaterialx"), ("DESKTOP", "hip"), ("DESKTOP", "hipnc"),
        ("SCENEGRAPH", "primtype_houdinifieldasset"), ("SCENEGRAPH", "selection_rule_houdini"),
    ],
}


def clean_tags(names):
    """Enforces the prompt rules the model occasionally breaks, on
    {kind: [name, ...]} in relevance order: drops banned words, and moves
    color words out of tags/shapes into colors (while there's room)."""
    colors = [canonical_tag(c) for c in names["colors"]]
    out = {}
    for kind in ("tags", "shapes"):
        out[kind] = []
        for name in names[kind]:
            word = canonical_tag(name)
            if word in BANNED_TAGS:
                continue
            if word in TAG_COLORS:
                if word not in colors and len(colors) < TAG_LIMITS["colors"]:
                    colors.append(word)
                continue
            out[kind].append(name)
    out["colors"] = colors
    return out


def weighted(names):
    """{kind: [[name, weight], ...]} from relevance-ordered names, trimmed to TAG_LIMITS."""
    return {kind: [[name, order_weight(n)] for n, name in enumerate(names[kind][:limit])]
            for kind, limit in TAG_LIMITS.items()}


def request_tags_now(items):
    """One immediate (non-batch) tag_request, for retries. Lets a safety
    decline re-run on Anthropic's recommended fallback model, which the
    Batch API doesn't support."""
    return parse_tags(claude.messages.create(
        **tag_request(items),
        extra_headers={"anthropic-beta": "server-side-fallback-2026-07-01"},
        extra_body={"fallbacks": "default"},
    ), len(items))


def request_tags_batched(chunks, poll_seconds=30):
    """Runs every chunk (a list of (svg, names)) through the Batch API.

    Returns one list per chunk, holding a tags dict or None (failed) per item.
    """
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    results = [[None] * len(c) for c in chunks]
    # Stay well under the 256 MB per-batch limit (each request is ~8 images)
    batch_ids = []
    for start in range(0, len(chunks), 200):
        batch = claude.messages.batches.create(requests=[
            Request(custom_id=f'chunk-{k}', params=MessageCreateParamsNonStreaming(**tag_request(chunks[k])))
            for k in range(start, min(start + 200, len(chunks)))])
        batch_ids.append(batch.id)
        log.info(f'submitted batch {batch.id} ({min(start + 200, len(chunks)) - start} requests)')

    for batch_id in batch_ids:
        while (batch := claude.messages.batches.retrieve(batch_id)).processing_status != "ended":
            log.info(f'{batch_id}: {batch.request_counts.processing} processing, {batch.request_counts.succeeded} done')
            time.sleep(poll_seconds)
        for result in claude.messages.batches.results(batch_id):
            k = int(result.custom_id.split('-')[1])
            if result.result.type != "succeeded":
                log.info(f'chunk {k} {result.result.type}')
                continue
            try:
                results[k] = parse_tags(result.result.message, len(chunks[k]))
            except Exception as e:
                log.info(f'chunk {k} unusable: {type(e).__name__}: {e}')
    return results


def is_blank(img):
    return not (np.asarray(img)[..., 3] > 32).any()


def identical_groups(icons):
    """Groups drawings that are the same artwork: identical svg, or renders
    that differ in at most ~9 pixels (re-exports, often under another name).
    Every icon is in exactly one group; most groups have one member.

    The pixel limit is near zero on purpose: icons like CONVERTED/CHILI_Ease
    and CHILI_Linear differ only by a thin curve, under 1% of the cell.
    """
    by_hash = defaultdict(list)
    for icon in icons:
        by_hash[icon.svg_hash].append(icon)
    hash_groups = list(by_hash.values())

    # Rows are read here: the session isn't thread-safe, only rendering runs in threads
    svgs = [g[0].svg for g in hash_groups]
    with ThreadPoolExecutor() as executor:
        images = list(executor.map(atlas_image, svgs))

    # A blank render would match every sparse icon, so those only group by svg
    groups = [g for g, img in zip(hash_groups, images) if is_blank(img)]
    hash_groups, images = zip(*[(g, img) for g, img in zip(hash_groups, images) if not is_blank(img)])

    # Only compare renders that share a coarse fingerprint, not every pair
    def fingerprint(img):
        a = np.asarray(img.resize((12, 12)), dtype=np.float32)
        luma = a[..., :3].mean(axis=2) * a[..., 3] / 255
        return tuple((luma // 32).astype(int).ravel()) + tuple((a[..., 3] // 64).astype(int).ravel())

    buckets = defaultdict(list)
    for group, img in zip(hash_groups, images):
        buckets[fingerprint(img)].append((group, img))

    for bucket in buckets.values():
        while bucket:
            (group, img), rest = bucket[0], bucket[1:]
            same = [r for r in rest if changed_fraction(img, r[1]) <= 0.001]
            groups.append(group + [icon for g, _ in same for icon in g])
            bucket = [r for r in rest if not any(r is s for s in same)]
    return groups


def set_tags(icon, tags):
    """Replaces an icon's tags with {kind: [[name, weight], ...]}."""
    session.query(IconTagAssoc).filter_by(icon_id=icon.id).delete()
    added = set()
    for kind, pairs in tags.items():
        for name, weight in pairs:
            name = canonical_tag(name)
            t = session.query(Tag).filter_by(name=name).one_or_none()
            if not t:
                t = Tag(name=name)
                session.add(t)
                session.flush()
            # Synonyms can collapse two entries of one kind onto the same word
            if (t.id, kind) not in added:
                session.add(IconTagAssoc(icon=icon, tag=t, type=kind[:-1], weight=weight))
                added.add((t.id, kind))


def current_tags(icon):
    return {kind: [[a.tag.name, a.weight] for a in icon.tags if a.type + 's' == kind] for kind in TAG_LIMITS}


def apply_manual_tags():
    """Gives every drawing of the icons in MANUAL_TAGS its hand-picked tags,
    as their most relevant tag (weight 1.0)."""
    added = 0
    for word, keys in MANUAL_TAGS.items():
        t = session.query(Tag).filter_by(name=word).one_or_none()
        if not t:
            t = Tag(name=word)
            session.add(t)
            session.flush()
        for category, name in keys:
            icons = session.query(Icon).filter_by(category=category, name=name).all()
            if not icons:
                log.info(f'manual tag "{word}": no icon {category}/{name}')
            for icon in icons:
                if not any(a.tag_id == t.id and a.type == 'tag' for a in icon.tags):
                    session.add(IconTagAssoc(icon=icon, tag=t, type='tag', weight=1.0))
                    added += 1
    session.commit()
    log.info(f'added {added} manual tags')


def clean_existing_tags():
    """Runs clean_tags over tags already in the database (no model calls)."""
    backup = DB_PATH.replace('.db', f'_BAK_{date.today():%Y%m%d}_pre_tag_cleanup.db')
    shutil.copy(DB_PATH, backup)
    log.info(f'backed up database to {backup}')

    changed = 0
    for icon in session.query(Icon).order_by(Icon.id).all():
        if not icon.tags:
            continue
        names = {kind: [name for name, _ in sorted(pairs, key=lambda p: -p[1])]
                 for kind, pairs in current_tags(icon).items()}
        cleaned = clean_tags(names)
        if cleaned != names:
            set_tags(icon, weighted(cleaned))
            changed += 1
    session.commit()

    orphans = session.query(Tag).filter(~Tag.icons.any()).all()
    for t in orphans:
        session.delete(t)
    session.commit()
    log.info(f'cleaned tags on {changed} drawings, {len(orphans)} unused words removed')
    apply_manual_tags()


def tag_icons(from_scratch=False, limit=None):
    """Tags every untagged drawing.

    With from_scratch, first deletes every tag (after backing up the
    database), so nothing from earlier tagging runs carries over.
    Identical drawings are tagged once and share the result; otherwise a
    drawing identical to one that already has tags copies them.
    With limit, sends at most that many drawings to the model, spread
    evenly over the set; run again without it to tag the rest.

    Drawings go out ICONS_PER_REQUEST at a time through the Batch API, which
    usually finishes within an hour. Anything that fails or is declined there
    is retried once, one drawing per request, outside the batch.
    """
    if from_scratch:
        backup = DB_PATH.replace('.db', f'_BAK_{date.today():%Y%m%d}_pre_retag.db')
        shutil.copy(DB_PATH, backup)
        log.info(f'backed up database to {backup}')
        session.query(IconTagAssoc).delete()
        session.query(Tag).delete()
        session.commit()
        session.expire_all()

    icons = session.query(Icon).order_by(Icon.id).all()
    targets = {i.id for i in icons if not i.tags}

    requests, copied, blank = [], 0, []
    for group in identical_groups(icons):
        todo = sorted((i for i in group if i.id in targets), key=lambda i: i.id)
        if not todo:
            continue
        # Nothing for the model to see (e.g. MISC/empty, or an SVG resvg can't draw)
        if is_blank(atlas_image(todo[0].svg)):
            blank += todo
            continue
        tagged = [i for i in group if i.id not in targets]
        if tagged:
            tags = current_tags(min(tagged, key=lambda i: i.id))
            for icon in todo:
                set_tags(icon, tags)
            copied += len(todo)
        else:
            requests.append(todo)
    session.commit()
    requests.sort(key=lambda g: g[0].id)
    if limit is not None and len(requests) > limit:
        step = len(requests) / limit
        requests = [requests[int(k * step)] for k in range(limit)]
        log.info(f'limited to {limit} drawings')
    shared = sum(len(g) - 1 for g in requests)
    log.info(f'{len(targets)} untagged drawings: {len(requests)} sent to the model (+{shared} identical drawings sharing '
             f'their result), {copied} copied from already-tagged identical drawings, {len(blank)} skipped as blank '
             f'renders {[f"{i.category}/{i.name}" for i in blank]}')

    items = [(group[0].svg, icon_names(group, NAMES_IN_PROMPT)) for group in requests]
    chunks = [list(range(k, min(k + ICONS_PER_REQUEST, len(items)))) for k in range(0, len(items), ICONS_PER_REQUEST)]
    results = [None] * len(items)
    for chunk, chunk_results in zip(chunks, request_tags_batched([[items[k] for k in c] for c in chunks])):
        for k, tags in zip(chunk, chunk_results):
            results[k] = tags

    def retry(k):
        try:
            return k, request_tags_now([items[k]])[0]
        except Exception as e:
            log.info(f'retry of {items[k][1]} failed: {type(e).__name__}: {e}')
            return k, None

    missing = [k for k, tags in enumerate(results) if tags is None]
    if missing:
        log.info(f'retrying {len(missing)} drawings one at a time')
        with ThreadPoolExecutor(max_workers=8) as executor:
            for k, tags in executor.map(retry, missing):
                results[k] = tags

    # DB writes stay on this thread: the session isn't thread-safe
    failed = 0
    for group, tags in zip(requests, results):
        if tags is None:
            failed += 1
            continue
        for icon in group:
            set_tags(icon, tags)
    session.commit()

    orphans = session.query(Tag).filter(~Tag.icons.any()).all()
    for t in orphans:
        session.delete(t)
    session.commit()
    log.info(f'done: {len(requests) - failed} tagged, {failed} failed, {len(orphans)} unused tags removed')
    apply_manual_tags()


def dump_json():
    print('dumping json')
    all_icons = [x.to_dict() for x in session.query(Icon).order_by(Icon.id).all()]

    with open(f'{CLIENT_DIR}/src/assets/database.json', 'w') as outfile:
        json.dump(all_icons, outfile)

    with open(f'{CLIENT_DIR}/src/assets/versions.json', 'w') as outfile:
        json.dump([{"key": v["key"], "label": v["label"]} for v in VERSIONS], outfile, indent=1)


def make_atlas():
    print('making atlas')
    output_path = f'{CLIENT_DIR}/public/atlas'

    icons = session.query(Icon).order_by(Icon.id).all()
    # The client finds a cell from the id alone, so ids must have no gaps
    assert [i.id for i in icons] == list(range(1, len(icons) + 1)), 'icon ids are not contiguous'

    # Rows are read here: the session isn't thread-safe, only rendering runs in threads
    svgs = [icon.svg for icon in icons]
    with ThreadPoolExecutor() as executor:
        images = list(executor.map(atlas_image, svgs))

    chunk_images = [images[i:i + 100] for i in range(0, len(images), 100)]
    page_files = []

    for (arr_index, img_arr) in enumerate(chunk_images):

        grid_size = (10, 10)
        cell_size = (100, 100)
        padding = 5

        cols, rows = grid_size
        cell_width, cell_height = cell_size
        atlas_width = cols * cell_width
        atlas_height = rows * cell_height

        # Create a blank atlas
        atlas = Image.new('RGBA', (atlas_width, atlas_height), (0, 0, 0, 0))  # Transparent background

        for idx, img in enumerate(img_arr):
            # Calculate grid position
            col = idx % cols
            row = idx // cols

            # Paste the image onto the atlas (already fitted to ATLAS_CELL)
            atlas.paste(img, ((col * cell_width) + padding, (row * cell_height) + padding))

        # Lossy WebP subsamples color at any quality, so 100 bought nothing
        # visible over 80 while being ~75% larger (21.6 MB vs 12.3 MB in total)
        buffer = io.BytesIO()
        atlas.save(buffer, "WebP", quality=80, method=6)
        data = buffer.getvalue()

        # Content-hashed name: a page whose cells change gets a new URL, so
        # browsers can cache pages indefinitely without ever showing stale ones
        name = f'atlas_{arr_index}-{hashlib.md5(data).hexdigest()[:8]}.webp'
        with open(f'{output_path}/{name}', 'wb') as f:
            f.write(data)
        page_files.append(name)

    for old in os.listdir(output_path):
        if old.startswith('atlas_') and old not in page_files:
            os.remove(f'{output_path}/{old}')

    # The client maps a page number to its file through this list
    with open(f'{CLIENT_DIR}/src/assets/atlas.json', 'w') as outfile:
        json.dump(page_files, outfile, indent=1)

    print(f'{len(chunk_images)} atlas pages for {len(images)} icons ({ATLAS_CELL}px cells)')


if __name__ == '__main__':
    # tag_icons()
    dump_json()
    # make_atlas()
