"""Tests for motor with permissives and timer."""

from examples.motor_start_with_permissives import build_program


def test_motor_fails_with_permissive_false():
    """
    Keep one permissive false: confirm that even after long time
    (many scans, enough to exceed PRE), MotorRun is False.
    """
    program = build_program()
    tagdb = program.tagdb

    # Set all except one permissive
    tagdb.set_bool_val("StartCmd", True)
    tagdb.set_bool_val("EStopOK", True)
    tagdb.set_bool_val("Permissive1OK", True)
    tagdb.set_bool_val("Permissive2OK", False)  # This one is False

    # Run for 60 scans (6 seconds at 100ms per scan - exceeds 5s timer)
    for _ in range(60):
        program.scan(dt_ms=100)

    # Motor should NOT run because permissive is false
    assert tagdb.get_bool_val("MotorRun") is False, \
        "MotorRun should be False when permissive is not met"

    timer = tagdb.get_timer("MotorStartTON")
    assert timer.dn is False, "Timer should not be done when permissive is false"


def test_motor_starts_with_all_permissives():
    """
    With all permissives true:
        After enough simulated time, MotorRun becomes True and stays True
        while StartCmd stays True.
    """
    program = build_program()
    tagdb = program.tagdb

    # Set all permissives and start command
    tagdb.set_bool_val("StartCmd", True)
    tagdb.set_bool_val("EStopOK", True)
    tagdb.set_bool_val("Permissive1OK", True)
    tagdb.set_bool_val("Permissive2OK", True)

    # Before timer expires, motor should be off
    for _ in range(40):  # 4 seconds
        program.scan(dt_ms=100)

    assert tagdb.get_bool_val("MotorRun") is False, \
        "MotorRun should be False before timer expires"

    # Run until timer expires (need at least 5 seconds total)
    for _ in range(20):  # Additional 2 seconds = 6 seconds total
        program.scan(dt_ms=100)

    # After timer expires, motor should run
    assert tagdb.get_bool_val("MotorRun") is True, \
        "MotorRun should be True after timer expires with all permissives"

    timer = tagdb.get_timer("MotorStartTON")
    assert timer.dn is True, "Timer should be done"

    # Motor should stay running
    for _ in range(10):
        program.scan(dt_ms=100)

    assert tagdb.get_bool_val("MotorRun") is True, \
        "MotorRun should stay True while StartCmd is True"


def test_motor_stops_when_estop_fails():
    """
    If EStopOK is set False mid-run, next scan forces MotorRun False.
    """
    program = build_program()
    tagdb = program.tagdb

    # Set all permissives and start command
    tagdb.set_bool_val("StartCmd", True)
    tagdb.set_bool_val("EStopOK", True)
    tagdb.set_bool_val("Permissive1OK", True)
    tagdb.set_bool_val("Permissive2OK", True)

    # Run until motor starts (6 seconds)
    for _ in range(60):
        program.scan(dt_ms=100)

    assert tagdb.get_bool_val("MotorRun") is True, "MotorRun should be running"

    # Trigger EStop failure
    tagdb.set_bool_val("EStopOK", False)
    program.scan(dt_ms=100)

    # Motor should stop immediately
    assert tagdb.get_bool_val("MotorRun") is False, \
        "MotorRun should be False when EStopOK becomes False"
