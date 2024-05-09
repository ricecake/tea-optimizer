import enum
from tea.db import db_session, SugarBlend, TeaServing, TrialSuggestion
import tea.math

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert

from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction
from scipy.optimize import NonlinearConstraint
import numpy as np

Action = enum.Enum('Action', [
    'set_sugar',
    'get_sugar',
    'add_cup',
    'get_suggestion',
    'list_suggestions',
    'list_cups',
    'update_cup',
    'get_best_guess',
    'get_sugar_suggestion',
])

Strategy = enum.Enum('Strategy', [
    'Explorative', # kappa 10
    'Bold', # kappa 5
    'Neutral', #kappa 2.5
    'Timid', # kappa 1
    'Certain', #kappa 0.1
    'Contextual', # Vary kappa by number of previous trials
])

def dispatch_action(action, data=None) -> dict:
    result = None

    ACTION_EXECUTOR = {
        Action.set_sugar: do_set_sugar,
        Action.get_sugar: do_get_sugar,
        Action.add_cup: do_add_cup,
        Action.get_suggestion: do_get_suggestion,
        Action.list_cups: do_list_cups,
        Action.update_cup: do_update_cup,
        Action.get_best_guess: do_get_best_guess,
        Action.list_suggestions: do_list_suggestions,
        Action.get_sugar_suggestion: do_get_sugar_suggestion,
    }

    executor = ACTION_EXECUTOR.get(action)
    if executor:
        result = executor(data)

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

        optimizer, _ = get_optimizer(session, blend)

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

        optimizer, utility = get_optimizer(session, blend)

        mixture = optimizer.suggest(utility)
        suggestion = project_mixture_to_blend(mixture, blend)

        trial = TrialSuggestion(blend=blend.id, **suggestion)
        trial_dict = trial.as_dict()
        del trial_dict["created_at"]
        session.execute(insert(TrialSuggestion).values(
            trial_dict).on_conflict_do_nothing())
        session.commit()

        return suggestion


def do_get_sugar_suggestion(data):
    with db_session() as session:
        optimizer, utility = get_optimizer(session, strategy=Strategy.Certain)

        mixture = optimizer.suggest(utility)
        blend = blend_from_mixture(mixture)
        return blend.scaled_composition(200)


def do_list_suggestions(data) -> dict:
    with db_session() as session:
        stmnt = select(TrialSuggestion).order_by(
            TrialSuggestion.created_at.asc())
        return session.scalars(stmnt).all()


def get_optimizer(session, blend: SugarBlend = None, strategy: Strategy = Strategy.Contextual) -> tuple[BayesianOptimization, UtilityFunction]:
    def constraint_func(**kwargs):
        desired_blend = blend_from_mixture(kwargs)
        closest_blend = blend.nearest_blend(desired_blend)

        return closest_blend - desired_blend

    constraint = None
    if blend is not None:
        constraint = NonlinearConstraint(constraint_func, -np.inf, 0.1)

    optimizer = BayesianOptimization(
        f=None,
        constraint=constraint,
        pbounds={
            'water': (400, 500),
            'sugar': (0, 20),
            'vanillin': (0, 5), # 3?
            'ethyl_vanillin': (0, 2), # 1?
            'almond_milk': (0, 200),
        },
        verbose=0,
        random_state=1,
        allow_duplicate_points=True,
    )

    stmnt = select(TeaServing).where(TeaServing.quality != None)
    cups = session.scalars(stmnt).all()
    for cup in cups:
        get_brew_blend = select(SugarBlend).limit(
            1).order_by(SugarBlend.created_at.desc())
        brew_blend = session.scalar(get_brew_blend)

        scaled_blend = brew_blend.scaled_composition(cup.sugar)

        params = dict(
            water=cup.water,
            almond_milk=cup.almond_milk,
            sugar=scaled_blend.sugar,
            vanillin=scaled_blend.vanillin,
            ethyl_vanillin=scaled_blend.ethyl_vanillin,
        )

        constraint_value = None
        if blend is not None:
            constraint_value = constraint_func(**params)

        optimizer.register(
            params=params,
            target=cup.quality,
            constraint_value=constraint_value,
        )

    utility = get_utility_function(strategy, len(cups))

    return optimizer, utility


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

def get_utility_function(strategy: Strategy, cups: int) -> UtilityFunction:
# This needs to shift more towards exploitation as more cups are added.
# It should be moved into the get_optimizer() function, and use a sigmoid
# curve to transition between the exploration and exploitation values.
# as part of the suggestion table, it should track the value of kappa, 
# maybe with a name that represents what it does rather than the term itself.
# Maybe call it "exploration factor"?
# It ***Definitely*** needs to be very conservative when making the sugar blend,
# so it should be able to be overwritten or specified to be very conservative 
# or very explorative
    parameters = {
        Strategy.Explorative: { 'kappa': 10, 'xi': 0.0, 'kind': 'ucb' },
        Strategy.Bold: { 'kappa': 5, 'xi': 0.0, 'kind': 'ucb' },
        Strategy.Neutral: { 'kappa': 2.5, 'xi': 0.0, 'kind': 'ucb' },
        Strategy.Timid: { 'kappa': 1, 'xi': 0.0, 'kind': 'ucb' },
        Strategy.Certain: { 'kappa': 0.1, 'xi': 0.0, 'kind': 'ucb' },
        Strategy.Contextual: {
            'xi': 0.0,
            'kind': 'ucb',
            'kappa': tea.math.sigmoid_curve(
                cups,
                max_val=10,
                min_val=0.01,
                middle=15
            ),
        },
    }
    utility_params = parameters[strategy]

    print(f'Kappa: {utility_params.get("kappa")}')

    return UtilityFunction(**utility_params)