"""Classic start/stop motor seal-in circuit example."""

from plc_engine.tags import TagDB
from plc_engine.timers import TimerEngine
from plc_engine.program import Program, Rung
from plc_engine.instructions import Instruction, OpCode
from plc_engine.runtime import Runtime


def build_program() -> Program:
    """
    Build a seal-in circuit program.

    Logical description:
        Inputs:
            StartPB (momentary NO)
            StopPB (normally closed)
        Internal / outputs:
            MotorRun
        Rung behavior:
            MotorRun = (StartPB OR MotorRun) AND StopPB
    """
    tagdb = TagDB()
    tagdb.ensure_bool("StartPB")
    tagdb.ensure_bool("StopPB").value = True  # NC stop, default pressed
    tagdb.ensure_bool("MotorRun")

    timer_engine = TimerEngine(tagdb)

    # Rung: (StartPB OR MotorRun) AND StopPB -> OTE MotorRun
    instructions = [
        Instruction(OpCode.XIC, "StartPB"),
        Instruction(OpCode.XIC, "MotorRun"),
        Instruction(OpCode.OR),
        Instruction(OpCode.XIC, "StopPB"),
        Instruction(OpCode.AND),
        Instruction(OpCode.OTE, "MotorRun"),
    ]

    rung = Rung(name="SealIn", instructions=instructions)
    program = Program(tagdb=tagdb, timer_engine=timer_engine)
    program.add_rung(rung)
    return program


if __name__ == "__main__":
    program = build_program()
    runtime = Runtime(program, target_scan_ms=100)

    # crude manual sim:
    db = program.tagdb
    db.set_bool_val("StartPB", True)
    runtime.run(max_scans=5)
    db.set_bool_val("StartPB", False)
    runtime.run(max_scans=5)
    db.set_bool_val("StopPB", False)  # stop pressed (NC opened)
    runtime.run(max_scans=5)

    print("MotorRun:", db.get_bool_val("MotorRun"))
