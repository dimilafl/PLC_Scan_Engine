"""State adapter for serializing PLC program state to JSON."""

from typing import Any, Dict, List

from plc_engine.tags import TagDB
from plc_engine.program import Program
from examples.seal_in import build_program as build_seal_in
from examples.motor_start_with_permissives import build_program as build_motor


class DemoKind:
    """Demo program identifiers."""
    SEAL_IN = "seal_in"
    MOTOR = "motor"


def build_program_for_demo(kind: str) -> Program:
    """Build a PLC program for the specified demo kind."""
    if kind == DemoKind.MOTOR:
        return build_motor()
    return build_seal_in()  # default


def serialize_state(program: Program) -> Dict[str, Any]:
    """
    Serialize the current program state to a JSON-compatible dictionary.

    Returns:
        Dictionary with 'bools' and 'timers' lists.
    """
    tagdb: TagDB = program.tagdb

    bools: List[Dict[str, Any]] = []
    for name, tag in sorted(tagdb.bools.items()):
        bools.append({"name": name, "value": tag.value})

    timers: List[Dict[str, Any]] = []
    for name, t in sorted(tagdb.timers.items()):
        timers.append(
            {
                "name": name,
                "pre_ms": t.pre_ms,
                "acc_ms": t.acc_ms,
                "en": t.en,
                "dn": t.dn,
                "tt": t.tt,
            }
        )

    return {
        "bools": bools,
        "timers": timers,
    }


def set_bool(tagdb: TagDB, name: str, value: bool) -> None:
    """Set a boolean tag value."""
    tagdb.set_bool_val(name, value)


def toggle_bool(tagdb: TagDB, name: str) -> None:
    """Toggle a boolean tag value."""
    current = tagdb.get_bool_val(name)
    tagdb.set_bool_val(name, not current)
