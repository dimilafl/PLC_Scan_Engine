"""Instruction set for PLC rung logic execution."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from .tags import TagDB
from .timers import TimerEngine


class OpCode(Enum):
    """Operation codes for PLC instructions."""
    XIC = auto()   # examine if closed (true when tag is true)
    XIO = auto()   # examine if open (true when tag is false)
    AND = auto()
    OR = auto()
    NOT = auto()
    OTE = auto()   # output energize
    TON = auto()   # timer on delay
    XIC_TIMER_DN = auto()  # examine timer DN bit


@dataclass
class Instruction:
    """Single PLC instruction with opcode and optional operand."""
    opcode: OpCode
    operand: str | None = None  # tag name or timer name


def execute_rung_bytecode(
    tagdb: TagDB,
    timer_engine: TimerEngine,
    instructions: List[Instruction],
    dt_ms: int,
) -> None:
    """
    Execute one rung for a single scan.
    Uses a boolean stack for intermediate results.
    Side effects:
      - Writes to coil tags via OTE.
      - Updates timers via TON using timer_engine.
    """
    stack: List[bool] = []

    for instr in instructions:
        if instr.opcode == OpCode.XIC:
            # Examine if closed: push tag value
            if instr.operand is None:
                raise ValueError("XIC instruction requires an operand")
            value = tagdb.get_bool_val(instr.operand)
            stack.append(value)

        elif instr.opcode == OpCode.XIO:
            # Examine if open: push NOT tag value
            if instr.operand is None:
                raise ValueError("XIO instruction requires an operand")
            value = tagdb.get_bool_val(instr.operand)
            stack.append(not value)

        elif instr.opcode == OpCode.AND:
            # Pop 2, push (a AND b)
            if len(stack) < 2:
                raise ValueError("Stack underflow: AND requires 2 operands")
            b = stack.pop()
            a = stack.pop()
            stack.append(a and b)

        elif instr.opcode == OpCode.OR:
            # Pop 2, push (a OR b)
            if len(stack) < 2:
                raise ValueError("Stack underflow: OR requires 2 operands")
            b = stack.pop()
            a = stack.pop()
            stack.append(a or b)

        elif instr.opcode == OpCode.NOT:
            # Pop 1, push (NOT a)
            if len(stack) < 1:
                raise ValueError("Stack underflow: NOT requires 1 operand")
            a = stack.pop()
            stack.append(not a)

        elif instr.opcode == OpCode.OTE:
            # Output energize: pop 1, write to tag
            if len(stack) < 1:
                raise ValueError("Stack underflow: OTE requires 1 operand")
            if instr.operand is None:
                raise ValueError("OTE instruction requires an operand")
            value = stack.pop()
            tagdb.set_bool_val(instr.operand, value)

        elif instr.opcode == OpCode.TON:
            # Timer on delay: pop 1 as enable, update timer
            if len(stack) < 1:
                raise ValueError("Stack underflow: TON requires 1 operand")
            if instr.operand is None:
                raise ValueError("TON instruction requires an operand")
            enable = stack.pop()
            timer_engine.eval_ton(instr.operand, enable, dt_ms)

        elif instr.opcode == OpCode.XIC_TIMER_DN:
            # Examine timer DN bit: push timer.dn value
            if instr.operand is None:
                raise ValueError("XIC_TIMER_DN instruction requires an operand")
            timer = tagdb.get_timer(instr.operand)
            stack.append(timer.dn)

        else:
            raise ValueError(f"Unknown opcode: {instr.opcode}")
