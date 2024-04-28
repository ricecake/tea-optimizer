import enum
from tea.db import db_session, SugarBlend, TeaServing, TrialSuggestion
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert

from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction
from scipy.optimize import NonlinearConstraint
import numpy as np

utility = UtilityFunction(kind="ucb", kappa=10, xi=0.0)

Action = enum.Enum('Action', [
    'set_sugar',
    'get_sugar',
    'add_cup',
    'get_suggestion',
    'list_suggestions',
    'list_cups',
    'update_cup',
    'get_best_guess'
])


def dispatch_action(action, data=None) -> dict:
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
        case Action.list_suggestions:
            result = do_list_suggestions(data)

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
    with db_session() as session:
        get_blend = select(SugarBlend).limit(
            1).order_by(SugarBlend.created_at.desc())
        blend = session.scalar(get_blend)

        if not blend:
            return

        optimizer = get_optimizer(blend)

        stmnt = select(TeaServing).where(TeaServing.quality != None)
        for cup in session.scalars(stmnt):
            scaled_blend = blend.scaled_composition(cup.sugar)
            constraint = optimizer.constraint

            params = dict(
                water=cup.water,
                almond_milk=cup.almond_milk,
                sugar=scaled_blend.sugar,
                vanillin=scaled_blend.vanillin,
                ethyl_vanillin=scaled_blend.ethyl_vanillin,
            )

            optimizer.register(
                params=params,
                target=cup.quality,
                constraint_value=constraint.fun(**params)
            )

        max = optimizer.max

        if not max:
            return

        max["params"] = project_mixture_to_blend(max["params"], blend)

        return max


def do_get_suggestion(data) -> dict:
    with db_session() as session:
        get_blend = select(SugarBlend).limit(
            1).order_by(SugarBlend.created_at.desc())
        blend = session.scalar(get_blend)

        if not blend:
            return

        optimizer = get_optimizer(blend)

        stmnt = select(TeaServing).where(TeaServing.quality != None)
        for cup in session.scalars(stmnt):
            scaled_blend = blend.scaled_composition(cup.sugar)
            constraint = optimizer.constraint

            params = dict(
                water=cup.water,
                almond_milk=cup.almond_milk,
                sugar=scaled_blend.sugar,
                vanillin=scaled_blend.vanillin,
                ethyl_vanillin=scaled_blend.ethyl_vanillin,
            )

            optimizer.register(
                params=params,
                target=cup.quality,
                constraint_value=constraint.fun(**params)
            )

        mixture = optimizer.suggest(utility)
        suggestion = project_mixture_to_blend(mixture, blend)

        trial = TrialSuggestion(blend=blend.id, **suggestion)
        trial_dict = trial.as_dict()
        del trial_dict["created_at"]
        session.execute(insert(TrialSuggestion).values(trial_dict).on_conflict_do_nothing())
        session.commit()

        return suggestion

def do_list_suggestions(data) -> dict:
    with db_session() as session:
        stmnt = select(TrialSuggestion).order_by(TrialSuggestion.created_at.asc())
        return session.scalars(stmnt).all()


def get_optimizer(blend: SugarBlend) -> BayesianOptimization:
    def constraint_func(**kwargs):
        desired_blend = blend_from_mixture(kwargs)
        closest_blend = blend.nearest_blend(desired_blend)

        return closest_blend - desired_blend

    return BayesianOptimization(
        f=None,
        constraint=NonlinearConstraint(constraint_func, -np.inf, 0.1),
        pbounds={
            'water': (400, 500),
            'sugar': (0, 20),
            'vanillin': (0, 5),
            'ethyl_vanillin': (0, 2),
            'almond_milk': (0, 200),
        },
        verbose=0,
        random_state=1,
        allow_duplicate_points=True,
    )


def blend_from_mixture(mixture) -> SugarBlend:
    return SugarBlend(
        sugar=mixture["sugar"],
        vanillin=mixture["vanillin"],
        ethyl_vanillin=mixture["ethyl_vanillin"],
    )


def project_mixture_to_blend(mixture: dict, blend: SugarBlend) -> dict:
    desired_blend = blend_from_mixture(mixture)
    closest_blend = blend.nearest_blend(desired_blend)
    return dict(
        water=mixture["water"],
        almond_milk=mixture["almond_milk"],
        sugar=closest_blend.gross_weight,
    )
