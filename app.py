from flask import Flask, render_template, request, jsonify
from railway_simulation import (
    start_simulation_from_config,
    get_simulation_status,
    reset_simulation,
    get_trains_state,
    set_fire_alarm,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("main.html")


@app.route("/start", methods=["POST"])
def start():
    data = request.get_json() or {}
    start_simulation_from_config(data)
    return jsonify({"ok": True})


@app.route("/status", methods=["GET"])
def status():
    return jsonify(get_simulation_status())


@app.route("/reset", methods=["POST"])
def reset():
    reset_simulation()
    return jsonify({"ok": True})


@app.route("/trains", methods=["GET"])
def trains():
    return jsonify(get_trains_state())


@app.route("/fire_alarm", methods=["POST"])
def fire_alarm():
    data = request.get_json() or {}
    station = data.get("station")
    active = bool(data.get("active", True))
    set_fire_alarm(station, active)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, jsonify
from railway_simulation import (
    start_simulation_from_config,
    get_simulation_status,
    reset_simulation,
    get_trains_state,
    set_fire_alarm,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("main.html")


@app.route("/start", methods=["POST"])
def start():
    data = request.get_json() or {}
    start_simulation_from_config(data)
    return jsonify({"ok": True})


@app.route("/status", methods=["GET"])
def status():
    return jsonify(get_simulation_status())


@app.route("/reset", methods=["POST"])
def reset():
    reset_simulation()
    return jsonify({"ok": True})


@app.route("/trains", methods=["GET"])
def trains():
    return jsonify(get_trains_state())


@app.route("/fire_alarm", methods=["POST"])
def fire_alarm():
    data = request.get_json() or {}
    station = data.get("station")
    active = bool(data.get("active", True))
    set_fire_alarm(station, active)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)
