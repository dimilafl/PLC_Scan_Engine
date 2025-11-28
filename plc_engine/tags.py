"""Core tag model for PLC-style variables."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class BoolTag:
    """Boolean tag representing a digital I/O or internal bit."""
    name: str
    value: bool = False


@dataclass
class TimerTag:
    """Timer tag for PLC-style timing operations."""
    name: str
    pre_ms: int        # preset in ms
    acc_ms: int = 0    # accumulated in ms
    en: bool = False   # enable
    dn: bool = False   # done
    tt: bool = False   # timing


@dataclass
class TagDB:
    """Tag database managing all PLC tags."""
    bools: Dict[str, BoolTag] = field(default_factory=dict)
    timers: Dict[str, TimerTag] = field(default_factory=dict)

    def ensure_bool(self, name: str) -> BoolTag:
        """Create or retrieve a boolean tag."""
        if name not in self.bools:
            self.bools[name] = BoolTag(name=name)
        return self.bools[name]

    def ensure_timer(self, name: str, pre_ms: int) -> TimerTag:
        """Create or retrieve a timer tag with specified preset."""
        if name not in self.timers:
            self.timers[name] = TimerTag(name=name, pre_ms=pre_ms)
        return self.timers[name]

    def get_bool_val(self, name: str) -> bool:
        """Get boolean tag value. Raises KeyError if tag doesn't exist."""
        if name not in self.bools:
            raise KeyError(f"Boolean tag '{name}' does not exist")
        return self.bools[name].value

    def set_bool_val(self, name: str, val: bool) -> None:
        """Set boolean tag value. Raises KeyError if tag doesn't exist."""
        if name not in self.bools:
            raise KeyError(f"Boolean tag '{name}' does not exist")
        self.bools[name].value = val

    def get_timer(self, name: str) -> TimerTag:
        """Get timer tag. Raises KeyError if timer doesn't exist."""
        if name not in self.timers:
            raise KeyError(f"Timer tag '{name}' does not exist")
        return self.timers[name]
