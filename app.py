"""Flask server for Trading Bot Wars."""

from flask import Flask, jsonify, render_template
from engine import GameEngine

app = Flask(__name__)
game_engine = GameEngine()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/new_game", methods=["POST"])
def new_game():
    global game_engine
    game_engine = GameEngine()
    return jsonify({"status": "ok"})


@app.route("/api/tick", methods=["POST"])
def tick():
    global game_engine
    if game_engine is None:
        game_engine = GameEngine()
    state = game_engine.tick()
    return jsonify(state)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
