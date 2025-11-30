"""Flask web application for PLC MicroScan Engine."""

from flask import Flask, jsonify, render_template, request
from typing import Optional

from plc_engine.program import Program
from web.state_adapter import (
    DemoKind,
    build_program_for_demo,
    serialize_state,
    toggle_bool,
)

app = Flask(__name__, template_folder="templates", static_folder="static")

# Global state (single-user assumption)
CURRENT_PROGRAM: Optional[Program] = None
CURRENT_DEMO: str = DemoKind.SEAL_IN

SCAN_DT_MS_DEFAULT = 100  # default scan time in milliseconds


def ensure_program() -> Program:
    """Ensure CURRENT_PROGRAM is initialized, lazily building if needed."""
    global CURRENT_PROGRAM
    if CURRENT_PROGRAM is None:
        CURRENT_PROGRAM = build_program_for_demo(CURRENT_DEMO)
    return CURRENT_PROGRAM


@app.route("/")
def index():
    """Render the main UI page."""
    return render_template("index.html", current_demo=CURRENT_DEMO)


@app.route("/api/select_demo", methods=["POST"])
def select_demo():
    """
    Switch to a different demo program.

    JSON body: {"demo": "seal_in"} or {"demo": "motor"}
    Returns: {"demo": str, "state": {...}}
    """
    global CURRENT_PROGRAM, CURRENT_DEMO

    data = request.get_json()
    demo = data.get("demo", DemoKind.SEAL_IN)

    CURRENT_DEMO = demo
    CURRENT_PROGRAM = build_program_for_demo(demo)

    return jsonify({
        "demo": CURRENT_DEMO,
        "state": serialize_state(CURRENT_PROGRAM)
    })


@app.route("/api/state", methods=["GET"])
def get_state():
    """
    Get the current program state.

    Returns: {"demo": str, "state": {...}}
    """
    program = ensure_program()
    return jsonify({
        "demo": CURRENT_DEMO,
        "state": serialize_state(program)
    })


@app.route("/api/toggle_bool", methods=["POST"])
def api_toggle_bool():
    """
    Toggle a boolean tag.

    JSON body: {"name": "<tagname>"}
    Returns: {"demo": str, "state": {...}}
    """
    program = ensure_program()
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Missing 'name' parameter"}), 400

    try:
        toggle_bool(program.tagdb, name)
    except KeyError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify({
        "demo": CURRENT_DEMO,
        "state": serialize_state(program)
    })


@app.route("/api/step", methods=["POST"])
def api_step():
    """
    Execute a single scan step.

    JSON body (optional): {"dt_ms": 100}
    Returns: {"demo": str, "state": {...}}
    """
    program = ensure_program()
    data = request.get_json() or {}
    dt_ms = data.get("dt_ms", SCAN_DT_MS_DEFAULT)

    program.scan(dt_ms)

    return jsonify({
        "demo": CURRENT_DEMO,
        "state": serialize_state(program)
    })


@app.route("/api/run", methods=["POST"])
def api_run():
    """
    Execute multiple scan steps.

    JSON body: {"steps": 50, "dt_ms": 100}
    Returns: {"demo": str, "state": {...}}
    """
    program = ensure_program()
    data = request.get_json() or {}
    steps = data.get("steps", 50)
    dt_ms = data.get("dt_ms", SCAN_DT_MS_DEFAULT)

    for _ in range(steps):
        program.scan(dt_ms)

    return jsonify({
        "demo": CURRENT_DEMO,
        "state": serialize_state(program)
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
