from flask import Flask, request, jsonify
from tea.db import db_session

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
    print(content)
    return jsonify({})

@app.post("/get_sugar")
def get_sugar():
    content = request.json
    print(content)
    return jsonify({})

@app.post("/add_cup")
def add_cupp():
    content = request.json
    print(content)
    return jsonify({})

@app.post("/get_suggestion")
def get_suggestion():
    content = request.json
    print(content)
    return jsonify({})

@app.post("/list_cups")
def list_cups():
    content = request.json
    print(content)
    return jsonify({})

@app.post("/update_cup")
def update_cup():
    content = request.json
    print(content)
    return jsonify({})

