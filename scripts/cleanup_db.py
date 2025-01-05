from numpy.ma.core import shape

from db_loader import session, Session_maker
from sqlalchemy import func, select
from icon_model import Shape, Color, Icon, Tag, IconShapeAssoc


def cleanup_capitalized(model):

    subquery = (
        session.query(
            func.lower(model.name).label("lower_name"),
            func.min(model.id).label("min_id"),
            func.max(model.id).label("max_id"),
        )
        .group_by(func.lower(model.name))
        .subquery()
    )

    duplicates = (
        session.query(model)
        .join(subquery, func.lower(model.name) == subquery.c.lower_name)
        .filter(model.id != subquery.c.min_id)
        .all()
    )



if __name__ == '__main__':
    cleanup_capitalized(Shape)
    # cleanup_capitalized(Color)
