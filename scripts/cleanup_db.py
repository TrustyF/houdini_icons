from pprint import pprint

from numpy.ma.core import shape

from db_loader import session, Session_maker
from sqlalchemy import func, select
from icon_model import Shape, Color, Icon, Tag, IconShapeAssoc


def cleanup_capitalized(model, assoc_model):
    raw_db = session.query(model.name, model.id).all()

    cleaned = []

    for i in raw_db:
        name = i[0]

        name.strip()
        name = name.lower()
        name = name.replace('_', ' ')

        cleaned.append((name, i[1]))

    print([x[0] for x in cleaned])

    for i in cleaned:

        target = session.query(model).filter_by(name=i[0]).one_or_none()

        if target:

            if target.id != i[1]:

                print(target.id, i[1])

                old_assoc = session.query(assoc_model).filter_by(shape_id=i[1]).all()

                for assoc in old_assoc:
                    print(assoc.icon, assoc.shape)

                    new_as = assoc_model(icon_id=assoc.icon.id, shape_id=target.id, weight=assoc.weight)
                    session.add(new_as)
                    session.delete(assoc)

                old_shape = session.query(model).filter_by(id=i[1]).one()
                print('deleting',old_shape)
                session.delete(old_shape)

            target.name = i[0]

    session.commit()
    session.close()


if __name__ == '__main__':
    cleanup_capitalized(Shape, IconShapeAssoc)
    # cleanup_capitalized(Color)
