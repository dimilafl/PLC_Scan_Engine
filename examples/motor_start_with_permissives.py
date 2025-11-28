"""Motor start with permissives and TON delay example."""

from plc_engine.tags import TagDB
from plc_engine.timers import TimerEngine
from plc_engine.program import Program, Rung
from plc_engine.instructions import Instruction, OpCode
from plc_engine.runtime import Runtime


def build_program() -> Program:
    """
    Build a motor start program with permissives and timer delay.

    Logical description:
        Inputs:
            StartCmd
            EStopOK (true when E-Stop is healthy)
            Permissive1OK
            Permissive2OK
        Timer:
            MotorStartTON (PRE = 5000 ms, 5 seconds)
        Output:
            MotorRun
        Rungs:
            1. EnableLogic = StartCmd AND EStopOK AND Permissive1OK AND Permissive2OK
            2. TON MotorStartTON with rung-in EnableLogic
            3. MotorRun = MotorStartTON.DN
    """
    tagdb = TagDB()

    # Create input tags
    tagdb.ensure_bool("StartCmd")
    tagdb.ensure_bool("EStopOK")
    tagdb.ensure_bool("Permissive1OK")
    tagdb.ensure_bool("Permissive2OK")

    # Create internal tag for enable logic
    tagdb.ensure_bool("EnableLogic")

    # Create timer (5 second delay)
    tagdb.ensure_timer("MotorStartTON", pre_ms=5000)

    # Create output tag
    tagdb.ensure_bool("MotorRun")

    timer_engine = TimerEngine(tagdb)
    program = Program(tagdb=tagdb, timer_engine=timer_engine)

    # Rung 1: EnableLogic = StartCmd AND EStopOK AND Permissive1OK AND Permissive2OK
    rung1_instructions = [
        Instruction(OpCode.XIC, "StartCmd"),
        Instruction(OpCode.XIC, "EStopOK"),
        Instruction(OpCode.AND),
        Instruction(OpCode.XIC, "Permissive1OK"),
        Instruction(OpCode.AND),
        Instruction(OpCode.XIC, "Permissive2OK"),
        Instruction(OpCode.AND),
        Instruction(OpCode.OTE, "EnableLogic"),
    ]
    program.add_rung(Rung(name="EnableLogic", instructions=rung1_instructions))

    # Rung 2: TON MotorStartTON with EnableLogic
    rung2_instructions = [
        Instruction(OpCode.XIC, "EnableLogic"),
        Instruction(OpCode.TON, "MotorStartTON"),
    ]
    program.add_rung(Rung(name="StartTimer", instructions=rung2_instructions))

    # Rung 3: MotorRun = MotorStartTON.DN
    rung3_instructions = [
        Instruction(OpCode.XIC_TIMER_DN, "MotorStartTON"),
        Instruction(OpCode.OTE, "MotorRun"),
    ]
    program.add_rung(Rung(name="MotorOutput", instructions=rung3_instructions))

    return program


if __name__ == "__main__":
    program = build_program()
    runtime = Runtime(program, target_scan_ms=100)

    # Simulate with all permissives OK
    db = program.tagdb
    db.set_bool_val("StartCmd", True)
    db.set_bool_val("EStopOK", True)
    db.set_bool_val("Permissive1OK", True)
    db.set_bool_val("Permissive2OK", True)

    # Run for 60 scans (6 seconds at 100ms per scan)
    runtime.run(max_scans=60)

    print("MotorRun:", db.get_bool_val("MotorRun"))
    print("Timer ACC:", db.get_timer("MotorStartTON").acc_ms, "ms")
    print("Timer DN:", db.get_timer("MotorStartTON").dn)
