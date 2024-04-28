from flask import Flask, request, jsonify
from tea.db import db_session, Base
import tea.logic as logic

from flask.json.provider import DefaultJSONProvider
from datetime import datetime


def datetime_to_string(obj):
    for key, value in obj.items():
        if isinstance(value, datetime):
            obj[key] = value.isoformat()

    return obj


class ModelProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, Base):
            return datetime_to_string(obj.as_dict())
        else:
            return super().default(obj)


app = Flask("TeaTime")
app.json = ModelProvider(app)


@app.teardown_appcontext
def teardown(exception=None):
    db_session.remove()


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.post("/set_sugar")
def set_sugar():
    content = request.json
    result = logic.dispatch_action(logic.Action.set_sugar, content)
    return jsonify(result)


@app.post("/get_sugar")
def get_sugar():
    result = logic.dispatch_action(logic.Action.get_sugar)
    return jsonify(result)


@app.post("/add_cup")
def add_cupp():
    content = request.json
    result = logic.dispatch_action(logic.Action.add_cup, content)
    return jsonify(result)


@app.post("/list_cups")
def list_cups():
    result = logic.dispatch_action(logic.Action.list_cups)
    return jsonify(result)


@app.post("/update_cup")
def update_cup():
    content = request.json
    result = logic.dispatch_action(logic.Action.update_cup, content)
    return jsonify(result)


@app.post("/get_suggestion")
def get_suggestion():
    result = logic.dispatch_action(logic.Action.get_suggestion)
    return jsonify(result)

@app.post("/get_best_guess")
def get_best_guess():
    result = logic.dispatch_action(logic.Action.get_best_guess)
    return jsonify(result)
