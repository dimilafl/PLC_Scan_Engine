"""Tests for timer functionality."""

from plc_engine.tags import TagDB
from plc_engine.timers import TimerEngine
from plc_engine.program import Program, Rung
from plc_engine.instructions import Instruction, OpCode


def test_ton_reaches_done():
    """
    Case 1: TON reaches DN after enough scans.

    Create TagDB with TimerTag("T1", pre_ms=1000).
    Wire a minimal program: one rung with XIC ENBIT -> TON T1.
    Simulate 10 scans at dt_ms = 100 with ENBIT = True.
    Assert:
        After total 1000 ms, DN == True, TT == False, ACC >= PRE.
    """
    tagdb = TagDB()
    tagdb.ensure_bool("ENBIT").value = True
    tagdb.ensure_timer("T1", pre_ms=1000)

    timer_engine = TimerEngine(tagdb)
    program = Program(tagdb=tagdb, timer_engine=timer_engine)

    # Rung: XIC ENBIT -> TON T1
    instructions = [
        Instruction(OpCode.XIC, "ENBIT"),
        Instruction(OpCode.TON, "T1"),
    ]
    program.add_rung(Rung(name="TimerTest", instructions=instructions))

    # Simulate 10 scans at 100ms each = 1000ms total
    for _ in range(10):
        program.scan(dt_ms=100)

    timer = tagdb.get_timer("T1")
    assert timer.dn is True, "Timer should be done after 1000ms"
    assert timer.tt is False, "Timer should not be timing when done"
    assert timer.acc_ms >= timer.pre_ms, "Accumulated time should be >= preset"
    assert timer.en is True, "Timer should be enabled"


def test_ton_resets_when_disabled():
    """
    Case 2: Timer resets when enable goes false.

    Enable for some scans, check ACC > 0.
    Then set enable false, scan once.
    Assert ACC == 0, DN == False, TT == False.
    """
    tagdb = TagDB()
    tagdb.ensure_bool("ENBIT").value = True
    tagdb.ensure_timer("T1", pre_ms=1000)

    timer_engine = TimerEngine(tagdb)
    program = Program(tagdb=tagdb, timer_engine=timer_engine)

    # Rung: XIC ENBIT -> TON T1
    instructions = [
        Instruction(OpCode.XIC, "ENBIT"),
        Instruction(OpCode.TON, "T1"),
    ]
    program.add_rung(Rung(name="TimerTest", instructions=instructions))

    # Run 5 scans at 100ms each = 500ms
    for _ in range(5):
        program.scan(dt_ms=100)

    timer = tagdb.get_timer("T1")
    assert timer.acc_ms > 0, "Timer should have accumulated time"
    assert timer.dn is False, "Timer should not be done yet"
    assert timer.tt is True, "Timer should be timing"

    # Disable the timer
    tagdb.set_bool_val("ENBIT", False)
    program.scan(dt_ms=100)

    # Check reset
    assert timer.acc_ms == 0, "Accumulated time should reset to 0"
    assert timer.dn is False, "DN should be False"
    assert timer.tt is False, "TT should be False"
    assert timer.en is False, "EN should be False"
