"""Timer engine for PLC-like timer operations."""

from .tags import TagDB, TimerTag


class TimerEngine:
    """Handles TON (Timer On Delay) behavior in a PLC-like way."""

    def __init__(self, tagdb: TagDB):
        self.tagdb = tagdb

    def eval_ton(self, name: str, enable: bool, dt_ms: int) -> None:
        """
        PLC-like TON behavior:

        - If enable is False:
            EN = False, TT = False, DN = False, ACC = 0.
        - If enable is True:
            EN = True.
            If not DN:
                TT = True.
                ACC += dt_ms.
                If ACC >= PRE:
                    DN = True
                    TT = False.
            If DN:
                EN = True, DN = True, TT = False.
        """
        timer = self.tagdb.get_timer(name)

        if not enable:
            # Timer disabled: reset all
            timer.en = False
            timer.tt = False
            timer.dn = False
            timer.acc_ms = 0
        else:
            # Timer enabled
            timer.en = True

            if not timer.dn:
                # Not done yet: accumulate time
                timer.tt = True
                timer.acc_ms += dt_ms

                if timer.acc_ms >= timer.pre_ms:
                    # Reached preset: mark done
                    timer.dn = True
                    timer.tt = False
            # If already DN, keep EN=True, DN=True, TT=False (already set)
