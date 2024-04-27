from flask import Flask, request, jsonify
from tea.db import db_session
import tea.logic as logic

app = Flask("TeaTime")

@app.teardown_appcontext
def teardown(exception=None):
    db_session.remove()

@app.get("/")
def index():
    return app.send_static_file("index.html")

@app.post("/set_sugar")
def set_sugar():
    content = request.json
    result = logic.dispatch_action(db_session, logic.Action.set_sugar, content)
    return jsonify(result)

@app.post("/get_sugar")
def get_sugar():
    content = request.json
    result = logic.dispatch_action(db_session, logic.Action.get_sugar, content)
    return jsonify(result)

@app.post("/add_cup")
def add_cupp():
    content = request.json
    result = logic.dispatch_action(db_session, logic.Action.add_cup, content)
    return jsonify(result)

@app.post("/get_suggestion")
def get_suggestion():
    content = request.json
    result = logic.dispatch_action(db_session, logic.Action.get_suggestion, content)
    return jsonify(result)

@app.post("/list_cups")
def list_cups():
    content = request.json
    result = logic.dispatch_action(db_session, logic.Action.list_cups, content)
    return jsonify(result)

@app.post("/update_cup")
def update_cup():
    content = request.json
    result = logic.dispatch_action(db_session, logic.Action.update_cup, content)
    return jsonify(result)

