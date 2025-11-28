"""Tests for seal-in circuit."""

from examples.seal_in import build_program


def test_seal_in_circuit():
    """
    Test the seal-in circuit behavior.

    Simulate:
        1. All inputs default, MotorRun must be False.
        2. Set StartPB=True, run one scan, MotorRun becomes True.
        3. Set StartPB=False, run scans, MotorRun stays True.
        4. Set StopPB=False, run one scan, MotorRun becomes False.
    """
    program = build_program()
    tagdb = program.tagdb

    # Step 1: Initial state - MotorRun should be False
    program.scan(dt_ms=100)
    assert tagdb.get_bool_val("MotorRun") is False, "MotorRun should start False"

    # Step 2: Press start button, MotorRun becomes True
    tagdb.set_bool_val("StartPB", True)
    program.scan(dt_ms=100)
    assert tagdb.get_bool_val("MotorRun") is True, "MotorRun should be True after StartPB"

    # Step 3: Release start button, MotorRun stays True (sealed in)
    tagdb.set_bool_val("StartPB", False)
    for _ in range(5):
        program.scan(dt_ms=100)
    assert tagdb.get_bool_val("MotorRun") is True, "MotorRun should stay True (sealed in)"

    # Step 4: Press stop button (NC opened), MotorRun becomes False
    tagdb.set_bool_val("StopPB", False)
    program.scan(dt_ms=100)
    assert tagdb.get_bool_val("MotorRun") is False, "MotorRun should be False after StopPB"
