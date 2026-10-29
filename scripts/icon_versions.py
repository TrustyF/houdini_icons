"""Builds the versioned icon database from the per-version icons.zip copies.

Run from the scripts folder (db_loader opens assets/icon_db.db relative to it):

    python icon_versions.py

Every step is idempotent, so re-running after adding a new Houdini version
to VERSIONS (icon_model.py) only adds what's new.
"""
import os
import shutil
import sqlite3
import zipfile
import tempfile
import subprocess
from datetime import date
from collections import defaultdict, Counter

from db_loader import session
from icon_model import Icon, IconVersion, VERSIONS, VERSION_ORDER, ICONS_DIR
from icon_render import decode_svg, svg_hash, atlas_image, changed_fraction

main_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(main_dir, 'assets', 'icon_db.db')
HFS = r'C:\Program Files\Side Effects Software\Houdini 22.0.466'

# changed_fraction above this means a different drawing. Re-exports and
# touch-ups of the same artwork score < 0.017; restyles like H21's flat
# CHANNELS/auto_slope score from 0.0205 (calibrated on H19.5 -> H22)
SAME_DRAWING_THRESHOLD = 0.02

# The site's original (unversioned) icon set was built from Houdini 20.5
BASE_VERSION = '20.5'

# Files at the root of icons.zip up to H21 (canofworms, log) live in MISC/
# from H21/H22 on; filing them under MISC keeps each one a single icon
ROOT_CATEGORY = 'MISC'
# What the unversioned site called those root files (see merge_root_icons)
OLD_ROOT_CATEGORY = 'icons'


def migrate_schema():
    """Drops the old per-file `image` column and adds svg_hash and the
    pointer to each drawing's svg (source_version/source_path).

    SQLite can't drop a UNIQUE column in place, so the table is rebuilt.
    Ids are kept, so tags and atlas positions stay valid.
    """
    con = sqlite3.connect(DB_PATH)
    cols = [r[1] for r in con.execute('PRAGMA table_info(icon)')]
    if 'svg_hash' in cols:
        con.close()
        return

    backup = DB_PATH.replace('.db', f'_BAK_{date.today():%Y%m%d}_pre_versioning.db')
    shutil.copy(DB_PATH, backup)
    print(f'backed up database to {backup}')

    con.executescript('''
        PRAGMA foreign_keys=OFF;
        BEGIN;
        CREATE TABLE icon_new (
            id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(255),
            svg_hash VARCHAR(32),
            source_version VARCHAR(16),
            source_path VARCHAR(512),
            PRIMARY KEY (id)
        );
        INSERT INTO icon_new (id, name, category) SELECT id, name, category FROM icon;
        DROP TABLE icon;
        ALTER TABLE icon_new RENAME TO icon;
        COMMIT;
    ''')
    con.close()


def migrate_svg_to_source():
    """Replaces the stored svg text (113 MB, over GitHub's file size limit)
    with a pointer to it in the icons.zip of the first version using it.

    Each pointer is checked against the row's svg_hash before the svg
    column is dropped, so no drawing can end up pointing at the wrong file.
    """
    con = sqlite3.connect(DB_PATH)
    cols = [r[1] for r in con.execute('PRAGMA table_info(icon)')]
    if 'svg' not in cols:
        con.close()
        return

    backup = DB_PATH.replace('.db', f'_BAK_{date.today():%Y%m%d}_pre_svg_pointer.db')
    shutil.copy(DB_PATH, backup)
    print(f'backed up database to {backup}')

    sources = {v['key']: read_source(os.path.join(ICONS_DIR, v['source'])) for v in VERSIONS}
    hashes = {key: {k: svg_hash(svg) for k, (_, svg) in source.items()} for key, source in sources.items()}

    versions_of = defaultdict(list)
    for icon_id, version in con.execute('SELECT icon_id, version FROM icon_version'):
        versions_of[icon_id].append(version)

    pointers, missing = [], []
    for icon_id, category, name, h in con.execute('SELECT id, category, name, svg_hash FROM icon'):
        key = (category, name)
        found = next((v for v in sorted(versions_of[icon_id], key=VERSION_ORDER.get)
                      if hashes[v].get(key) == h), None)
        if found:
            pointers.append((found, sources[found][key][0], icon_id))
        else:
            missing.append(f'{icon_id} {category}/{name}')
    if missing:
        con.close()
        raise RuntimeError(f'{len(missing)} drawings not found in any of their versions: {missing[:10]}')

    con.executescript('''
        PRAGMA foreign_keys=OFF;
        BEGIN;
        CREATE TABLE icon_new (
            id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(255),
            svg_hash VARCHAR(32),
            source_version VARCHAR(16),
            source_path VARCHAR(512),
            PRIMARY KEY (id)
        );
        INSERT INTO icon_new (id, name, category, svg_hash) SELECT id, name, category, svg_hash FROM icon;
        DROP TABLE icon;
        ALTER TABLE icon_new RENAME TO icon;
        COMMIT;
    ''')
    con.executemany('UPDATE icon SET source_version = ?, source_path = ? WHERE id = ?', pointers)
    con.commit()
    con.execute('VACUUM')
    con.close()
    print(f'replaced stored svg with a zip pointer for {len(pointers)} drawings')


def migrate_tag_types():
    """Moves the tag/shape/color type from each word (tag) to each icon's
    use of it (icon_tag_assoc), so a word's first use no longer fixes its
    type everywhere. Existing links keep their word's old type."""
    con = sqlite3.connect(DB_PATH)
    cols = [r[1] for r in con.execute('PRAGMA table_info(icon_tag_assoc)')]
    if 'type' in cols:
        con.close()
        return

    backup = DB_PATH.replace('.db', f'_BAK_{date.today():%Y%m%d}_pre_tag_types.db')
    shutil.copy(DB_PATH, backup)
    print(f'backed up database to {backup}')

    con.executescript('''
        PRAGMA foreign_keys=OFF;
        BEGIN;
        CREATE TABLE icon_tag_assoc_new (
            icon_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            type VARCHAR(255) NOT NULL,
            weight FLOAT,
            PRIMARY KEY (icon_id, tag_id, type),
            FOREIGN KEY(icon_id) REFERENCES icon (id) ON DELETE CASCADE,
            FOREIGN KEY(tag_id) REFERENCES tag (id) ON DELETE CASCADE
        );
        INSERT INTO icon_tag_assoc_new (icon_id, tag_id, type, weight)
            SELECT a.icon_id, a.tag_id, t.type, a.weight FROM icon_tag_assoc a JOIN tag t ON t.id = a.tag_id;
        DROP TABLE icon_tag_assoc;
        ALTER TABLE icon_tag_assoc_new RENAME TO icon_tag_assoc;
        CREATE TABLE tag_new (
            id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            PRIMARY KEY (id),
            UNIQUE (name)
        );
        INSERT INTO tag_new (id, name) SELECT id, name FROM tag;
        DROP TABLE tag;
        ALTER TABLE tag_new RENAME TO tag;
        COMMIT;
    ''')
    con.close()


def merge_root_icons():
    """Moves the pre-versioning `icons/` rows (canofworms, log) to MISC/.

    Where an identical MISC/ drawing was already imported, its versions fold
    into the old row (which keeps its id, as the deployed site uses it) and
    the MISC/ row is deleted. Later ids then shift down to close the gap,
    since ids are atlas cells and must stay contiguous.
    """
    con = sqlite3.connect(DB_PATH)
    rows = con.execute('SELECT id, name, svg_hash FROM icon WHERE category = ?', (OLD_ROOT_CATEGORY,)).fetchall()
    if not rows:
        con.close()
        return

    backup = DB_PATH.replace('.db', f'_BAK_{date.today():%Y%m%d}_pre_root_merge.db')
    shutil.copy(DB_PATH, backup)
    print(f'backed up database to {backup}')

    deleted = []
    for icon_id, name, h in rows:
        twins = con.execute('SELECT id FROM icon WHERE category = ? AND name = ? AND svg_hash = ?',
                            (ROOT_CATEGORY, name, h)).fetchall()
        for (twin_id,) in twins:
            con.execute('INSERT OR IGNORE INTO icon_version (icon_id, version) '
                        'SELECT ?, version FROM icon_version WHERE icon_id = ?', (icon_id, twin_id))
            for table in ('icon_version', 'icon_tag_assoc'):
                con.execute(f'DELETE FROM {table} WHERE icon_id = ?', (twin_id,))
            con.execute('DELETE FROM icon WHERE id = ?', (twin_id,))
            deleted.append(twin_id)
        con.execute('UPDATE icon SET category = ? WHERE id = ?', (ROOT_CATEGORY, icon_id))
        print(f'{OLD_ROOT_CATEGORY}/{name} -> {ROOT_CATEGORY}/{name} (merged ids {[t for t, in twins]})')

    if deleted:
        # Ascending, so each id moves into a slot that's already free
        later = [r[0] for r in con.execute('SELECT id FROM icon WHERE id > ? ORDER BY id', (min(deleted),))]
        for old_id in later:
            new_id = old_id - sum(d < old_id for d in deleted)
            for table, column in (('icon', 'id'), ('icon_version', 'icon_id'), ('icon_tag_assoc', 'icon_id')):
                con.execute(f'UPDATE {table} SET {column} = ? WHERE {column} = ?', (new_id, old_id))
        print(f'renumbered {len(later)} later icons to close {len(deleted)} gaps; rebuild the atlas')
    con.commit()
    con.close()


def read_source(zip_path):
    """{(category, name): (path in the zip, svg)} for every SVG in an icons.zip."""
    icons = {}
    with zipfile.ZipFile(zip_path) as z:
        for path in z.namelist():
            if not path.lower().endswith('.svg'):
                continue
            category = os.path.basename(os.path.dirname(path)) or ROOT_CATEGORY
            name = os.path.splitext(os.path.basename(path))[0]
            icons[(category, name)] = (path, decode_svg(z.read(path)))
    return icons


def build_legacy_zip(hfs=HFS):
    """Writes H22_legacy_icons.zip from Houdini 22's SVGIcons.index.

    H22's icons.zip already has the new-skin drawings swapped in; the legacy
    skin's ones only live in the main index. Its entries are flat
    `CATEGORY_name.svg` files, so they're put back in icons.zip's folders:
    by category prefix when that names a file icons.zip has, else by
    identical content (CONVERTED/ and Pics/ don't follow the prefix rule),
    else by prefix alone for icons only the legacy skin has.
    """
    out_path = os.path.join(ICONS_DIR, 'H22_legacy_icons.zip')
    if os.path.exists(out_path):
        return

    with zipfile.ZipFile(os.path.join(ICONS_DIR, 'H22_icons.zip')) as z:
        svg_paths = [p for p in z.namelist() if p.lower().endswith('.svg')]
        path_by_hash = {svg_hash(decode_svg(z.read(p))): p for p in svg_paths}
        categories = sorted({os.path.dirname(p) for p in svg_paths if os.path.dirname(p)}, key=len, reverse=True)

    def zip_path(flat_name, svg):
        stem = os.path.splitext(flat_name)[0]
        by_prefix = next((f'{cat}/{stem[len(cat) + 1:]}.svg' for cat in categories
                          if stem.startswith(cat + '_')), None)
        if by_prefix in svg_paths:
            return by_prefix
        if svg_hash(svg) in path_by_hash:
            return path_by_hash[svg_hash(svg)]
        if by_prefix:
            return by_prefix
        print(f'no category for {flat_name}, keeping it at the root')
        return f'{stem}.svg'

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([os.path.join(hfs, 'bin', 'hidx.exe'), '-x', tmp,
                        os.path.join(hfs, 'houdini', 'config', 'Icons', 'SVGIcons.index')],
                       check=True, capture_output=True)

        # Sections.list maps hidx's escaped names (`_` doubled) to the originals
        originals = {}
        with open(os.path.join(tmp, 'Sections.list'), encoding='utf-8') as f:
            for line in f.read().splitlines()[1:]:
                parts = line.split('\t')
                originals[parts[0]] = parts[1] if len(parts) > 1 else parts[0].replace('__', '_')

        with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for escaped, original in sorted(originals.items()):
                if original.lower().endswith('.svg'):
                    with open(os.path.join(tmp, escaped), 'rb') as f:
                        data = f.read()
                    z.writestr(zip_path(original, decode_svg(data)), data)

    print(f'wrote {out_path}')


def fill_base_sources():
    """Points every pre-versioning row at its drawing in BASE_VERSION."""
    missing = session.query(Icon).filter(Icon.source_version.is_(None)).all()
    if not missing:
        return

    source = read_source(os.path.join(ICONS_DIR, f'H{BASE_VERSION}_icons.zip'))
    not_found = [i for i in missing if (i.category, i.name) not in source]
    if not_found:
        raise RuntimeError(f'{len(not_found)} icons not in H{BASE_VERSION}: {not_found[:10]}')

    for icon in missing:
        path, svg = source[(icon.category, icon.name)]
        icon.source_version, icon.source_path, icon.svg_hash = BASE_VERSION, path, svg_hash(svg)
    session.commit()
    print(f'pointed {len(missing)} existing icons at their H{BASE_VERSION} drawing')


def import_version(version):
    """Links every icon in a version's source to a matching drawing, adding
    a new row only where the drawing is new or visibly different."""
    source = read_source(os.path.join(ICONS_DIR, version['source']))

    existing = defaultdict(list)
    for icon in session.query(Icon).order_by(Icon.id).all():
        existing[(icon.category, icon.name)].append(icon)

    renders = {}

    def render(icon):
        if icon.id not in renders:
            renders[icon.id] = atlas_image(icon.svg)
        return renders[icon.id]

    stats = Counter()
    for (category, name), (path, svg) in sorted(source.items()):
        h = svg_hash(svg)
        candidates = existing[(category, name)]
        match = next((c for c in candidates if c.svg_hash == h), None)

        if not match and candidates:
            new_render = atlas_image(svg)
            match = next((c for c in candidates
                          if changed_fraction(render(c), new_render) <= SAME_DRAWING_THRESHOLD), None)

        if match:
            stats['unchanged'] += 1
        else:
            stats['redrawn' if candidates else 'new'] += 1
            match = Icon(name=name, category=category, svg_hash=h,
                         source_version=version['key'], source_path=path)
            session.add(match)
            candidates.append(match)

        if version['key'] not in {v.version for v in match.versions}:
            match.versions.append(IconVersion(version=version['key']))

    session.commit()
    print(f"{version['label']}: {len(source)} icons, {dict(stats)}")


def main():
    migrate_schema()
    migrate_tag_types()
    build_legacy_zip()
    migrate_svg_to_source()
    merge_root_icons()
    fill_base_sources()

    # Base version first so its drawings keep their original ids
    ordered = sorted(VERSIONS, key=lambda v: v['key'] != BASE_VERSION)
    for version in ordered:
        import_version(version)

    session.close()


if __name__ == '__main__':
    main()
