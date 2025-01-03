from numpy.ma.core import shape

from db_loader import session, Session_maker
from sqlalchemy import func, select
from icon_model import Shape,Color,Icon,Tag,IconShapeAssoc

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

    # print(duplicates[0].icons[0].icon)

    for shp in duplicates:
        print(shp)
        # new_shape = subquery
        #
        # for icon in shp.icons:


    # assoc = IconShapeAssoc(icon=icon, shape=s, weight=shape[1])
    #
    # duplicate_ids = [d.id for d in duplicates]
    # session.query(Shape).filter(Shape.id.in_(duplicate_ids)).delete(synchronize_session=False)
    #
    # session.commit()


if __name__ == '__main__':
    cleanup_capitalized(Shape)
    # cleanup_capitalized(Color)