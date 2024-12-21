from sqlalchemy import Integer, String, Column, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

icon_tag_association = Table(
    'icon_tag', Base.metadata,
    Column('icon_id', Integer, ForeignKey('icon.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True)
)


class Icon(Base):
    __tablename__ = "icon"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    tags = relationship('Tag', secondary=icon_tag_association, back_populates='icons')

    def __repr__(self):
        return f"<Icon(name={self.name})>"


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    icons = relationship('Icon', secondary=icon_tag_association, back_populates='tags')

    def __repr__(self):
        return f"<Tag(name={self.name})>"
