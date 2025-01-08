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
            "name": {"name": self.name, "match": 0, "weight": 1},
            "image": self.image,
            "category": {"name": self.category, "match": 0, "weight": 1},
            "tags": sorted([x.to_dict() for x in self.tags], reverse=True, key=lambda x:
            (custom_tag_order[x['type']], x['weight']))
        }


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(255), nullable=False)

    icons = relationship("IconTagAssoc", back_populates='tag', cascade="all, delete-orphan")

    @validates('name')
    def val(self, key, value):
        return value.strip().lower().replace('_', '')

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
            'count': session.query(IconTagAssoc).filter_by(tag_id=self.tag_id).count(),
            'match': 0
        }

    def __repr__(self):
        return f"<IconTag(icon={self.icon_id},tag={self.tag_id})>"
