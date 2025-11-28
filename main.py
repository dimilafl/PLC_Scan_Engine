"""Main entrypoint for PLC MicroScan Engine demos."""

import argparse
from examples.seal_in import build_program as build_seal_in
from examples.motor_start_with_permissives import build_program as build_motor
from plc_engine.runtime import Runtime


def main():
    parser = argparse.ArgumentParser(description="PLC MicroScan Engine Demo")
    parser.add_argument("--demo", choices=["seal_in", "motor"], default="seal_in",
                        help="Choose which demo to run")
    args = parser.parse_args()

    if args.demo == "seal_in":
        program = build_seal_in()
    else:
        program = build_motor()

    runtime = Runtime(program, target_scan_ms=100)
    runtime.run(max_scans=50)

    # Dump all boolean tags for inspection
    print("\n=== Boolean Tags ===")
    for name, tag in program.tagdb.bools.items():
        print(f"{name}: {tag.value}")

    # Dump all timer tags for inspection
    print("\n=== Timer Tags ===")
    for name, timer in program.tagdb.timers.items():
        print(f"{name}: EN={timer.en}, DN={timer.dn}, TT={timer.tt}, "
              f"ACC={timer.acc_ms}ms, PRE={timer.pre_ms}ms")


if __name__ == "__main__":
    main()
