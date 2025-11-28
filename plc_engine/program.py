"""PLC program structure with rungs."""

from dataclasses import dataclass, field
from typing import List

from .instructions import Instruction, execute_rung_bytecode
from .tags import TagDB
from .timers import TimerEngine


@dataclass
class Rung:
    """A single rung of ladder logic."""
    name: str
    instructions: List[Instruction]


@dataclass
class Program:
    """Complete PLC program with tag database and rungs."""
    tagdb: TagDB
    timer_engine: TimerEngine
    rungs: List[Rung] = field(default_factory=list)

    def add_rung(self, rung: Rung) -> None:
        """Add a rung to the program."""
        self.rungs.append(rung)

    def scan(self, dt_ms: int) -> None:
        """
        Execute one full PLC scan: evaluate all rungs in order,
        using a consistent dt_ms for timer integration.
        """
        for rung in self.rungs:
            execute_rung_bytecode(
                self.tagdb,
                self.timer_engine,
                rung.instructions,
                dt_ms
            )
