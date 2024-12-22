from sqlalchemy import Integer, String, Column, ForeignKey, Table, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

icon_tag_association = Table(
    'icon_tag_assoc', Base.metadata,
    Column('icon_id', Integer, ForeignKey('icon.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True),
    Column('weight', Float)

)
icon_shape_association = Table(
    'icon_shape_assoc', Base.metadata,
    Column('icon_id', Integer, ForeignKey('icon.id'), primary_key=True),
    Column('shape_id', Integer, ForeignKey('shape.id'), primary_key=True),
    Column('weight', Float)

)
icon_color_association = Table(
    'icon_color_assoc', Base.metadata,
    Column('icon_id', Integer, ForeignKey('icon.id'), primary_key=True),
    Column('color_id', Integer, ForeignKey('color.id'), primary_key=True),
    Column('weight', Float)
)


class Icon(Base):
    __tablename__ = "icon"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    image = Column(String(255), nullable=False)
    category = Column(String(255))

    tags = relationship('Tag', secondary=icon_tag_association, back_populates='icons')
    shapes = relationship('Shape', secondary=icon_shape_association, back_populates='icons')
    colors = relationship('Color', secondary=icon_color_association, back_populates='icons')

    def __repr__(self):
        return f"<Icon(name={self.name},tags={self.tags},shapes={self.shapes},colors={self.colors})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "category": self.category,
            "tags": [x.to_dict() for x in self.tags],
            "shapes": [x.to_dict() for x in self.shapes],
            "colors": [x.to_dict() for x in self.colors],
        }


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    icons = relationship('Icon', secondary=icon_tag_association, back_populates='tags')

    def __repr__(self):
        return f"<Tag(name={self.name})>"

    def to_dict(self):
        return self.name


class Shape(Base):
    __tablename__ = "shape"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    icons = relationship('Icon', secondary=icon_shape_association, back_populates='shapes')

    def __repr__(self):
        return f"<Shape(name={self.name})>"

    def to_dict(self):
        return self.name


class Color(Base):
    __tablename__ = "color"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    icons = relationship('Icon', secondary=icon_color_association, back_populates='colors')

    def __repr__(self):
        return f"<Color(name={self.name})>"

    def to_dict(self):
        return self.name


class IconTagAssoc(Base):
    __tablename__ = "icon_tag_assoc"
    icon_id = Column(Integer, ForeignKey('icon.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    weight = Column(Float)

    icon = relationship('Icon',back_populates="tags")
    tag = relationship('Tag',back_populates="icons")
