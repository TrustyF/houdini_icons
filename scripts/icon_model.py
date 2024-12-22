from sqlalchemy import Integer, String, Column, ForeignKey, Table, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Icon(Base):
    __tablename__ = "icon"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    image = Column(String(255), nullable=False,unique=True)
    category = Column(String(255))

    tags = relationship("IconTagAssoc", back_populates='icon')
    shapes = relationship("IconShapeAssoc", back_populates='icon')
    symbols = relationship("IconSymbolAssoc", back_populates='icon')
    colors = relationship("IconColorAssoc", back_populates='icon')

    def __repr__(self):
        return f"<Icon(name={self.name},tags={self.tags},shapes={self.shapes},colors={self.colors})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "category": self.category,
            "tags": sorted([x.to_dict() for x in self.tags], reverse=True, key=lambda x: x['weight']),
            "shapes": sorted([x.to_dict() for x in self.shapes], reverse=True, key=lambda x: x['weight']),
            "symbols": sorted([x.to_dict() for x in self.symbols], reverse=True, key=lambda x: x['weight']),
            "colors": sorted([x.to_dict() for x in self.colors], reverse=True, key=lambda x: x['weight']),
        }


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    icons = relationship("IconTagAssoc", back_populates='tag')

    def __repr__(self):
        return f"<Tag(name={self.name})>"

    def to_dict(self):
        return self.name


class Shape(Base):
    __tablename__ = "shape"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    icons = relationship("IconShapeAssoc", back_populates='shape')

    def __repr__(self):
        return f"<Shape(name={self.name})>"

    def to_dict(self):
        return self.name

class Symbol(Base):
    __tablename__ = "symbol"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    icons = relationship("IconSymbolAssoc", back_populates='symbol')

    def __repr__(self):
        return f"<Symbol(name={self.name})>"

    def to_dict(self):
        return self.name

class Color(Base):
    __tablename__ = "color"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    icons = relationship("IconColorAssoc", back_populates='color')

    def __repr__(self):
        return f"<Color(name={self.name})>"

    def to_dict(self):
        return self.name


class IconTagAssoc(Base):
    __tablename__ = "icon_tag_assoc"
    icon_id = Column(Integer, ForeignKey('icon.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    weight = Column(Float)

    icon = relationship('Icon', back_populates="tags")
    tag = relationship('Tag', back_populates="icons")

    def to_dict(self):
        return {
            'name': self.tag.to_dict(),
            'weight': self.weight
        }


class IconShapeAssoc(Base):
    __tablename__ = "icon_shape_assoc"
    icon_id = Column(Integer, ForeignKey('icon.id'), primary_key=True)
    shape_id = Column(Integer, ForeignKey('shape.id'), primary_key=True)
    weight = Column(Float)

    icon = relationship('Icon', back_populates="shapes")
    shape = relationship('Shape', back_populates="icons")

    def to_dict(self):
        return {
            'name': self.shape.to_dict(),
            'weight': self.weight
        }
class IconSymbolAssoc(Base):
    __tablename__ = "icon_symbol_assoc"
    icon_id = Column(Integer, ForeignKey('icon.id'), primary_key=True)
    symbol_id = Column(Integer, ForeignKey('symbol.id'), primary_key=True)
    weight = Column(Float)

    icon = relationship('Icon', back_populates="symbols")
    symbol = relationship('Symbol', back_populates="icons")

    def to_dict(self):
        return {
            'name': self.symbol.to_dict(),
            'weight': self.weight
        }

class IconColorAssoc(Base):
    __tablename__ = "icon_color_assoc"
    icon_id = Column(Integer, ForeignKey('icon.id'), primary_key=True)
    color_id = Column(Integer, ForeignKey('color.id'), primary_key=True)
    weight = Column(Float)

    icon = relationship('Icon', back_populates="colors")
    color = relationship('Color', back_populates="icons")

    def to_dict(self):
        return {
            'name': self.color.to_dict(),
            'weight': self.weight
        }
