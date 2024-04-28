import enum
from tea.db import db_session, SugarBlend, TeaServing
from sqlalchemy import select

Action = enum.Enum('Action', [
    'set_sugar',
    'get_sugar',
    'add_cup',
    'get_suggestion',
    'list_cups',
    'update_cup',
])


def dispatch_action(action, data=None) -> dict:
    print(action, data)

    result = None
    match action:
        case Action.set_sugar:
            result = do_set_sugar(data)
        case Action.get_sugar:
            result = do_get_sugar(data)
        case Action.add_cup:
            result = do_add_cup(data)
        case Action.get_suggestion:
            result = do_get_suggestion(data)
        case Action.list_cups:
            result = do_list_cups(data)
        case Action.update_cup:
            result = do_update_cup(data)

    print(result)

    return dict(result=result)


def do_set_sugar(data) -> SugarBlend:
    with db_session() as session:
        blend = SugarBlend(**data)
        session.add(blend)
        session.commit()

        return blend


def do_get_sugar(data) -> dict:
    with db_session() as session:
        stmnt = select(SugarBlend).order_by(SugarBlend.created_at.asc())
        return session.scalars(stmnt).all()


def do_add_cup(data) -> dict:
    with db_session() as session:
        stmnt = select(SugarBlend).limit(
            1).order_by(SugarBlend.created_at.desc())
        blend_id = session.scalar(stmnt).id
        cup = TeaServing(blend=blend_id, **data)
        session.add(cup)
        session.commit()
        return cup


def do_list_cups(data) -> dict:
    with db_session() as session:
        stmnt = select(TeaServing).order_by(TeaServing.created_at.asc())
        return session.scalars(stmnt).all()


def do_update_cup(data) -> dict:
    return {}


def do_get_suggestion(data) -> dict:
    return {}
