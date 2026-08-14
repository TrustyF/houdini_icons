from sqlalchemy import Integer, String, Column, ForeignKey, Table, Float
from sqlalchemy.orm import relationship, validates
from db_loader import session, Base

custom_tag_order = {
    "tag": 4,
    "shape": 3,
    "symbol": 2,
    "color": 1,
}


class Icon(Base):
    __tablename__ = "icon"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    image = Column(String(255), nullable=False, unique=True)
    category = Column(String(255))

    tags = relationship("IconTagAssoc", back_populates='icon')

    def __repr__(self):
        return f"<Icon(name={self.name})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "category": self.category,
            "tags": sorted([x.to_dict() for x in self.tags], reverse=True, key=lambda x:
            (custom_tag_order[x['type']], x['weight']))
        }


# The tagger (GPT, in index_images.py) has no controlled vocabulary — it
# free-texts a name per tag, so it happily produces both spellings of the
# same concept across different icons (e.g. "grey" on one, "gray" on
# another) since neither collides with the other after basic
# strip/lower/underscore normalization. Collapsing known synonyms onto one
# canonical spelling here means every write path (index_images.py,
# cleanup_db.py, ad-hoc scripts) merges them into a single Tag row instead
# of silently fragmenting search/filtering.
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
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(255), nullable=False)

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
            'type': self.tag.type,
            'weight': self.weight,
        }

    def __repr__(self):
        return f"<IconTag(icon={self.icon_id},tag={self.tag_id})>"
