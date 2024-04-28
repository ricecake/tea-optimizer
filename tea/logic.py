import enum
from tea.db import db_session, SugarBlend, TeaServing
from sqlalchemy import select

from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction

utility = UtilityFunction(kind="ucb", kappa=10, xi=0.0)

Action = enum.Enum('Action', [
    'set_sugar',
    'get_sugar',
    'add_cup',
    'get_suggestion',
    'list_cups',
    'update_cup',
    'get_best_guess'
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
        case Action.get_best_guess:
            result = do_get_best_guess(data)

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
    with db_session() as session:
        stmnt = select(TeaServing).where(
            TeaServing.id == data.get('id')).limit(1)

        cup = session.scalar(stmnt)
        cup.quality = data.get('quality')
        session.commit()

        return cup


def do_get_best_guess(data) -> dict:
    optimizer = get_optimizer(None)

    with db_session() as session:
        stmnt = select(TeaServing).where(TeaServing.quality != None)
        for cup in session.scalars(stmnt):
            optimizer.register(
                params=dict(
                    water=cup.water,
                    sugar=cup.sugar,
                    almond_milk=cup.almond_milk,
                ),
                target=cup.quality,
            )

        return optimizer.max


def do_get_suggestion(data) -> dict:
    optimizer = get_optimizer(None)

    with db_session() as session:
        stmnt = select(TeaServing).where(TeaServing.quality != None)
        for cup in session.scalars(stmnt):
            optimizer.register(
                params=dict(
                    water=cup.water,
                    sugar=cup.sugar,
                    almond_milk=cup.almond_milk,
                ),
                target=cup.quality,
            )

        return optimizer.suggest(utility)


def get_optimizer(blend: SugarBlend) -> BayesianOptimization:
    return BayesianOptimization(
        f=None,
        pbounds={
            'water': (400, 500),
            'sugar': (0, 20),
            'almond_milk': (0, 200),
        },
        verbose=2,
        random_state=1,
        allow_duplicate_points=True,
    )
