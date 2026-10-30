import os
import zipfile
import threading

from sqlalchemy import Integer, String, Column, ForeignKey, Table, Float
from sqlalchemy.orm import relationship, validates
from db_loader import session, Base
from icon_render import decode_svg

# The per-version icons.zip copies (gitignored: SideFX's artwork)
ICONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'icons')

custom_tag_order = {
    "tag": 3,
    "shape": 2,
    "color": 1,
}

# Oldest first. Each key is one icon set the site can show; Houdini 22 has
# two because its new UI skin replaces ~300 UI icons that the legacy skin
# still draws the old way. `source` is the icons.zip copy in houdini_icons/icons.
VERSIONS = [
    {"key": "19.5", "label": "Houdini 19.5", "source": "H19.5_icons.zip"},
    {"key": "20", "label": "Houdini 20", "source": "H20_icons.zip"},
    {"key": "20.5", "label": "Houdini 20.5", "source": "H20.5_icons.zip"},
    {"key": "21", "label": "Houdini 21", "source": "H21_icons.zip"},
    {"key": "22-legacy", "label": "Houdini 22 (legacy UI)", "source": "H22_legacy_icons.zip"},
    {"key": "22", "label": "Houdini 22", "source": "H22_icons.zip"},
]
VERSION_ORDER = {v["key"]: i for i, v in enumerate(VERSIONS)}
VERSION_SOURCES = {v["key"]: v["source"] for v in VERSIONS}

_zips = {}
_zip_lock = threading.Lock()


def load_svg(version, path):
    """The svg at `path` in a version's icons.zip. Safe to call from threads."""
    with _zip_lock:
        if version not in _zips:
            _zips[version] = zipfile.ZipFile(os.path.join(ICONS_DIR, VERSION_SOURCES[version]))
        data = _zips[version].read(path)
    return decode_svg(data)


class Icon(Base):
    """One drawing of a Houdini icon.

    An icon redrawn between versions gets one row per drawing, all sharing
    the same category/name; `versions` says which icon sets use each one.
    The id doubles as the atlas position (cell id - 1), so ids stay
    contiguous and are never reused.

    The drawing itself isn't stored: `source_version`/`source_path` point at
    it in that version's icons.zip (see ICONS_DIR), and `svg` loads it.
    """
    __tablename__ = "icon"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(255))
    svg_hash = Column(String(32))
    source_version = Column(String(16))
    source_path = Column(String(512))

    tags = relationship("IconTagAssoc", back_populates='icon')
    versions = relationship("IconVersion", back_populates='icon', cascade="all, delete-orphan")

    @property
    def svg(self):
        return load_svg(self.source_version, self.source_path)

    def __repr__(self):
        return f"<Icon({self.id},{self.category}/{self.name})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "versions": sorted([x.version for x in self.versions], key=VERSION_ORDER.get),
            # Types no longer produced (e.g. pre-Claude "symbol" tags) sort last
            "tags": sorted([x.to_dict() for x in self.tags], reverse=True, key=lambda x:
            (custom_tag_order.get(x['type'], 0), x['weight']))
        }


class IconVersion(Base):
    __tablename__ = "icon_version"
    icon_id = Column(Integer, ForeignKey('icon.id', ondelete="CASCADE"), primary_key=True)
    version = Column(String(16), primary_key=True)

    icon = relationship('Icon', back_populates="versions")

    def __repr__(self):
        return f"<IconVersion(icon={self.icon_id},{self.version})>"


# The tagger (Claude, in index_images.py) has no controlled vocabulary for
# tags and shapes — it free-texts a name per entry, so it can produce both
# spellings of the same concept across different icons (e.g. "grey" on one,
# "gray" on another) since neither collides with the other after basic
# strip/lower/underscore normalization. Collapsing known synonyms onto one
# canonical spelling here means every write path (index_images.py, ad-hoc
# scripts) merges them into a single Tag row instead of silently
# fragmenting search/filtering.
TAG_SYNONYMS = {
    'grey': 'gray',
    'doughnut': 'donut',
    'push pin': 'pushpin',
    'userinterface': 'user interface',
    'user-interface': 'user interface',
    'pixelart': 'pixel art',
    'videogame': 'video game',
    'roundedrectangle': 'rounded rectangle',
    'rounded-rectangle': 'rounded rectangle',
    'semi-circle': 'semicircle',
    'curly brace': 'curlybrace',
    'lightblue': 'light blue',
    'light-blue': 'light blue',
    'lightgreen': 'light green',
    'darkgreen': 'dark green',
    'darkblue': 'dark blue',
    'dark-blue': 'dark blue',
}


class Tag(Base):
    """A word. Whether it's a tag, shape or color depends on the icon, so
    the type lives on IconTagAssoc."""
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

    icons = relationship("IconTagAssoc", back_populates='tag', cascade="all, delete-orphan")

    @validates('name')
    def val(self, key, value):
        value = value.strip().lower().replace('_', '')
        return TAG_SYNONYMS.get(value, value)

    def __repr__(self):
        return f"<Tag({self.id},{self.name})>"

    def to_dict(self):
        return self.name,


class IconTagAssoc(Base):
    __tablename__ = "icon_tag_assoc"
    icon_id = Column(Integer, ForeignKey('icon.id', ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id', ondelete="CASCADE"), primary_key=True)
    # tag / shape / color; part of the key, so one word can be both a tag and a shape of an icon
    type = Column(String(255), primary_key=True)
    weight = Column(Float)

    icon = relationship('Icon', back_populates="tags")
    tag = relationship('Tag', back_populates="icons")

    @validates('weight')
    def val(self, key, value):

        value = float(value)

        if value > 1:
            return value / 10
        else:
            return value

    def to_dict(self):
        return {
            'id': self.tag.id,
            'name': self.tag.name,
            'type': self.type,
            'weight': self.weight,
        }

    def __repr__(self):
        return f"<IconTag(icon={self.icon_id},tag={self.tag_id},{self.type})>"
