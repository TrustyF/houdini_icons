"""Collapses tags that are spelling variants of each other onto one name.

    python tag_synonyms.py propose   # adds the variants found in the database to tag_synonyms.json
    python tag_synonyms.py merge     # rewrites the database onto the canonical names
    python tag_synonyms.py related   # asks Claude for related-word groups, added to tag_related.json

`propose` finds two kinds of variants among the tags in use:
  - plurals of a tag that also exists singular, onto the more used form ("arrows" -> "arrow", "stripe" -> "stripes")
  - spacing/hyphen spellings ("low-poly", "lowpoly" -> "low poly"), onto the most used one
It only adds entries, so hand-written ones in the file win. Review what it
added with `git diff`; to reject a pair for good, map the word to itself
("glasses": "glasses") or to the right word ("axes": "axis") and re-run.

Shade words ("teal", "light blue") are mapped by hand onto the TAG_COLORS
palette in index_images.py, so the tagger's color list stays the only one.

`related` groups words that aren't the same tag but that a search for one
should also show ("rope", "wire", "cable"). The database keeps them apart;
the client's search matches a group's other words at a lower weight. Groups
already in the file are kept, so hand edits survive re-runs.

Run both after every tagging run: the tagger can coin new variants.
"""
import os
import re
import sys
import json
import shutil
import sqlite3
from datetime import date
from collections import defaultdict

from icon_model import SYNONYMS_PATH

DB_PATH = 'assets/icon_db.db'
RELATED_PATH = os.path.join(os.path.dirname(SYNONYMS_PATH), 'tag_related.json')

RELATED_MODEL = "claude-opus-5-5"
RELATED_PROMPT = """Below is the tag vocabulary of a visual search engine for the icons of the 3D software SideFX
Houdini, one tag per line with the number of icons using it. People search by typing one word for what an icon
looks like.

Group words that someone searching for one would also want to see icons for, because they depict the same kind
of thing: e.g. rope, wire, cable, cord, string, thread; or person, figure, human, character, silhouette.

- Only group near-synonyms and things drawn alike. Never group opposites (plus/minus, left/right, open/close,
  up/down) or siblings of one category that look different (circle/square/triangle, cube/sphere, numbers,
  letters, colors, animals of different species).
- Skip colors entirely, and skip words too generic to help (shape, object, line, icon).
- 2 to 8 words per group, every word copied exactly from the list. A word may appear in several groups.
- Leave a word out rather than force it into a weak group. Most words belong in no group.

Groups already decided (don't repeat or change them, but you may add new groups that reuse their words):
{existing}

Vocabulary:
{vocabulary}"""

RELATED_SCHEMA = {
    "type": "object",
    "properties": {"groups": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}},
    "required": ["groups"],
    "additionalProperties": False,
}


def squash(name):
    """The name with spaces and hyphens between letters removed: one key for "low poly", "low-poly", "lowpoly"."""
    return re.sub(r'(?<=[a-z])[\s-]+(?=[a-z])', '', name)


def singulars(name):
    """The singular forms `name` could be the plural of, most likely first (only its last word is inflected)."""
    head, _, last = name.rpartition(' ')
    prefix = head + ' ' if head else ''
    forms = []
    if last.endswith('s') and not re.search(r'(ss|us|is)$', last):
        forms.append(last[:-1])
    if last.endswith('ies'):
        forms.append(last[:-3] + 'y')
    if last.endswith('ves'):
        forms += [last[:-3] + 'f', last[:-3] + 'fe']
    # "boxes", "branches" but not "panes" or "tubes", whose singular just drops the s
    if re.search(r'(s|x|z|ch|sh)es$', last):
        forms.append(last[:-2])
    return [prefix + f for f in forms]


def load_synonyms():
    with open(SYNONYMS_PATH) as f:
        return json.load(f)


def resolve(synonyms, name):
    """Follows variant -> canonical links to the end, so chains like "pushpins" -> "push pin" -> "pushpin" land once."""
    seen = set()
    while name in synonyms and synonyms[name] != name and name not in seen:
        seen.add(name)
        name = synonyms[name]
    return name


def tag_counts(con):
    return dict(con.execute(
        'SELECT t.name, count(*) FROM tag t JOIN icon_tag_assoc a ON a.tag_id = t.id GROUP BY t.id'))


def propose():
    synonyms = load_synonyms()
    con = sqlite3.connect(DB_PATH)
    counts = tag_counts(con)
    con.close()

    by_key = defaultdict(list)
    for name in counts:
        by_key[squash(name)].append(name)

    # Words the file already has a say on, as a variant or as a canonical spelling
    decided = set(synonyms) | set(synonyms.values())
    found = {}

    # Spacing variants: the most used spelling wins
    for names in by_key.values():
        free = [n for n in names if n not in decided]
        if len(names) > 1 and free:
            canonical = max(names, key=lambda n: (n in decided, counts[n], ' ' in n))
            for name in free:
                if name != canonical:
                    found[name] = canonical

    # Plurals: whichever of singular/plural is more used wins ("arrows" ->
    # "arrow", but "stripe" -> "stripes"); ties and hand-decided singulars keep the singular
    for name in counts:
        if name in decided:
            continue
        for form in singulars(name):
            if squash(form) in by_key:
                group = by_key[squash(form)]
                single = max(group, key=lambda n: counts[n])
                if counts[name] > sum(counts[n] for n in group) and not decided & set(group):
                    for n in group:
                        found[n] = name
                else:
                    found[name] = found.get(single, single)
                break

    added = {k: v for k, v in found.items() if k not in synonyms}
    synonyms.update(added)
    synonyms = {k: resolve(synonyms, v) for k, v in synonyms.items()}
    with open(SYNONYMS_PATH, 'w') as f:
        json.dump(dict(sorted(synonyms.items())), f, indent=1)
        f.write('\n')

    for name in sorted(added, key=lambda n: synonyms[n]):
        print(f'{name} ({counts[name]}) -> {synonyms[name]} ({counts.get(synonyms[name], 0)})')
    print(f'{len(added)} variants added to {SYNONYMS_PATH}')


def merge():
    """Moves every icon's use of a variant onto its canonical tag (keeping
    the higher weight when an icon has both) and deletes the variant."""
    synonyms = load_synonyms()
    backup = DB_PATH.replace('.db', f'_BAK_{date.today():%Y%m%d}_pre_tag_merge.db')
    shutil.copy(DB_PATH, backup)
    print(f'backed up database to {backup}')

    con = sqlite3.connect(DB_PATH)
    tag_ids = dict(con.execute('SELECT name, id FROM tag'))
    merged = renamed = 0

    with con:
        for variant in synonyms:
            canonical = resolve(synonyms, variant)
            if variant == canonical or variant not in tag_ids:
                continue
            vid = tag_ids.pop(variant)
            if canonical not in tag_ids:
                con.execute('UPDATE tag SET name = ? WHERE id = ?', (canonical, vid))
                tag_ids[canonical] = vid
                renamed += 1
                continue

            cid = tag_ids[canonical]
            for icon_id, kind, weight in con.execute(
                    'SELECT icon_id, type, weight FROM icon_tag_assoc WHERE tag_id = ?', (vid,)).fetchall():
                row = con.execute('SELECT weight FROM icon_tag_assoc WHERE icon_id = ? AND tag_id = ? AND type = ?',
                                  (icon_id, cid, kind)).fetchone()
                if row:
                    con.execute('UPDATE icon_tag_assoc SET weight = ? WHERE icon_id = ? AND tag_id = ? AND type = ?',
                                (max(row[0], weight), icon_id, cid, kind))
                    con.execute('DELETE FROM icon_tag_assoc WHERE icon_id = ? AND tag_id = ? AND type = ?',
                                (icon_id, vid, kind))
                else:
                    con.execute('UPDATE icon_tag_assoc SET tag_id = ? WHERE icon_id = ? AND tag_id = ? AND type = ?',
                                (cid, icon_id, vid, kind))
            con.execute('DELETE FROM tag WHERE id = ?', (vid,))
            merged += 1

    print(f'{merged} variants merged, {renamed} renamed; {len(tag_counts(con))} tags left')
    con.close()

    # A shade merged onto a palette color ("teal" -> "cyan") is still a
    # tag-typed row; this moves it into the icon's colors (or drops it)
    from index_images import clean_existing_tags
    clean_existing_tags()


def load_related():
    if not os.path.exists(RELATED_PATH):
        return []
    with open(RELATED_PATH) as f:
        return json.load(f)


def related():
    import anthropic
    from dotenv import load_dotenv
    load_dotenv()

    synonyms = load_synonyms()
    con = sqlite3.connect(DB_PATH)
    counts = tag_counts(con)
    con.close()
    existing = load_related()

    prompt = RELATED_PROMPT.format(
        existing='\n'.join(', '.join(g) for g in existing) or '(none)',
        vocabulary='\n'.join(f'{n} ({c})' for n, c in sorted(counts.items())))
    # One long answer: streamed so the request can't hit an HTTP timeout
    with anthropic.Anthropic().messages.stream(
            model=RELATED_MODEL,
            max_tokens=64000,
            output_config={"effort": "high", "format": {"type": "json_schema", "schema": RELATED_SCHEMA}},
            messages=[{"role": "user", "content": prompt}],
            # Re-runs a safety-declined request on Anthropic's recommended model instead of failing
            extra_headers={"anthropic-beta": "server-side-fallback-2026-07-01"},
            extra_body={"fallbacks": "default"},
    ) as stream:
        message = stream.get_final_message()
    if message.stop_reason != "end_turn":
        raise RuntimeError(f'stopped with {message.stop_reason}: {getattr(message, "stop_details", None)}')
    proposed = json.loads(next(b.text for b in message.content if b.type == "text"))["groups"]

    # Only words in use, under their canonical spelling; a group inside an existing one adds nothing
    known = [set(g) for g in existing]
    added = []
    for group in proposed:
        words = list(dict.fromkeys(resolve(synonyms, w.strip().lower()) for w in group))
        words = [w for w in words if w in counts]
        if len(words) < 2 or any(set(words) <= k for k in known):
            continue
        known.append(set(words))
        added.append(sorted(words, key=lambda w: -counts[w]))

    with open(RELATED_PATH, 'w') as f:
        json.dump(sorted(existing + added), f, indent=1)
        f.write('\n')

    for group in added:
        print(', '.join(f'{w} ({counts[w]})' for w in group))
    print(f'{len(added)} groups added to {RELATED_PATH} '
          f'({message.usage.input_tokens} in / {message.usage.output_tokens} out tokens)')


if __name__ == '__main__':
    {'propose': propose, 'merge': merge, 'related': related}[sys.argv[1]]()
