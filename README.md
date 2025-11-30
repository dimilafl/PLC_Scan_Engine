# PLC MicroScan Engine

A minimal PLC (Programmable Logic Controller) simulation engine for learning and testing ladder logic programs.

## What is PLC MicroScan Engine?

This is a small but realistic implementation of a PLC scan engine that executes ladder logic programs. It simulates the behavior of industrial PLCs used in automation and control systems.

## Core Concepts

### Scan Cycle

PLCs operate on a continuous scan cycle:
1. Read inputs
2. Execute program logic (evaluate all rungs in order)
3. Update outputs
4. Repeat

Each scan takes a fixed amount of time (e.g., 100ms). The engine simulates this by calling `program.scan(dt_ms)` repeatedly.

### TagDB (Tag Database)

The TagDB is the central storage for all PLC variables:
- **BoolTag**: Boolean values representing digital I/O or internal bits
- **TimerTag**: Timer values with preset (PRE), accumulated (ACC), enable (EN), done (DN), and timing (TT) bits

Tags must be created before use via `ensure_bool()` or `ensure_timer()`. Accessing non-existent tags raises `KeyError`.

### Instruction Set

Programs are built from a simple bytecode instruction set:

| OpCode | Description | Stack Effect |
|--------|-------------|--------------|
| XIC | Examine if closed (true when tag is true) | Push tag value |
| XIO | Examine if open (true when tag is false) | Push !tag value |
| AND | Logical AND | Pop 2, push a AND b |
| OR | Logical OR | Pop 2, push a OR b |
| NOT | Logical NOT | Pop 1, push !a |
| OTE | Output energize (write to tag) | Pop 1, write to tag |
| TON | Timer on delay | Pop 1 as enable, update timer |
| XIC_TIMER_DN | Examine timer done bit | Push timer.dn |

Instructions use a boolean stack for intermediate results. The stack must be balanced (no underflow).

### Timer Semantics (TON)

Timer On Delay (TON) behavior:

**When enable is FALSE:**
- EN = False, TT = False, DN = False, ACC = 0

**When enable is TRUE:**
- EN = True
- If not done:
  - TT = True (timing)
  - ACC += dt_ms (accumulate time)
  - When ACC >= PRE: DN = True, TT = False
- If done:
  - DN = True, TT = False

Timers only advance based on the `dt_ms` parameter passed to each scan, not wall-clock time.

## Project Structure

```
PLC_Scan_Engine/
  main.py                 # CLI entrypoint
  requirements.txt        # Python dependencies
  plc_engine/
    __init__.py
    tags.py               # Tag database (BoolTag, TimerTag, TagDB)
    instructions.py       # Instruction set and execution
    program.py            # Program structure (Rung, Program)
    runtime.py            # Runtime loop
    timers.py             # Timer engine (TON logic)
  examples/
    seal_in.py            # Classic start/stop seal-in circuit
    motor_start_with_permissives.py  # Motor with safety permissives and timer
  web/
    __init__.py
    app.py                # Flask web application
    state_adapter.py      # State serialization for web API
    templates/
      base.html           # Base HTML template
      index.html          # Main UI page
    static/
      css/
        style.css         # UI styling
      js/
        ui.js             # Client-side logic
  tests/
    test_timers.py        # Timer behavior tests
    test_seal_in.py       # Seal-in circuit tests
    test_motor_permissives.py  # Motor permissive tests
```

## Quickstart

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run Examples

```bash
# Run seal-in circuit demo
python main.py --demo seal_in

# Run motor with permissives demo
python main.py --demo motor
```

### Run Tests

```bash
pytest
```

## Web UI

The PLC MicroScan Engine includes a Flask-based web interface for interactive simulation and visualization.

### Features

- **Live Tag Visualization**: View all boolean and timer tags in real-time
- **Interactive Controls**: Toggle input bits with a single click
- **Scan Control**: Step through individual scans or run multiple scans at once
- **Demo Switching**: Switch between seal-in and motor permissive demos
- **Clean Interface**: Portfolio-ready UI with responsive design

### Running the Web UI

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Run the Flask app
python -m web.app

# Or using Flask CLI
FLASK_APP=web.app flask run
```

Then open your browser to: **http://localhost:5000/**

### Using the Web UI

1. **Select Demo**: Choose between "Seal-In" or "Motor + Permissives" from the dropdown
2. **View State**: The tables show current values of all boolean and timer tags
3. **Toggle Inputs**: Click "Toggle" buttons to change input tag values
4. **Step Execution**: Click "Step" to execute a single 100ms scan cycle
5. **Run Multiple Scans**: Click "Run 50 steps" to execute 50 scan cycles (5 seconds simulation time)
6. **Refresh**: Click "Refresh" to update the display with current values

### Understanding the Tables

**Boolean Tags Table:**
- **Name**: Tag identifier
- **Value**: Current state (TRUE/FALSE)
  - Green = TRUE (energized)
  - Gray = FALSE (de-energized)
- **Toggle**: Button to flip the tag value

**Timer Tags Table:**
- **Name**: Timer identifier
- **EN**: Enable bit (timer is running)
- **DN**: Done bit (timer has reached preset)
- **TT**: Timing bit (timer is actively timing)
- **ACC (ms)**: Accumulated time in milliseconds
- **PRE (ms)**: Preset time in milliseconds

### Demo Behaviors

**Seal-In Demo:**
1. Toggle `StartPB` to TRUE and step → `MotorRun` becomes TRUE
2. Toggle `StartPB` back to FALSE and step → `MotorRun` stays TRUE (sealed in)
3. Toggle `StopPB` to FALSE (NC contact opens) and step → `MotorRun` becomes FALSE

**Motor + Permissives Demo:**
1. Set all permissives (`StartCmd`, `EStopOK`, `Permissive1OK`, `Permissive2OK`) to TRUE
2. Click "Run 50 steps" to simulate 5 seconds
3. Watch the timer accumulate and `MotorRun` activate when timer completes
4. Toggle `EStopOK` to FALSE and step → `MotorRun` immediately stops

## Example: Seal-In Circuit

A classic motor start/stop circuit with seal-in logic:

**Logic:** `MotorRun = (StartPB OR MotorRun) AND StopPB`

- Press StartPB (momentary): Motor starts
- Release StartPB: Motor stays running (sealed in by MotorRun feedback)
- Press StopPB (NC contact opens): Motor stops

See `examples/seal_in.py` for implementation.

## Example: Motor with Permissives

A safety-oriented motor start with multiple permissives and timer delay:

**Inputs:**
- StartCmd
- EStopOK (E-Stop healthy)
- Permissive1OK, Permissive2OK

**Logic:**
1. EnableLogic = StartCmd AND EStopOK AND Permissive1OK AND Permissive2OK
2. TON MotorStartTON (5 second delay)
3. MotorRun = MotorStartTON.DN

Motor only runs if all permissives are true AND timer has completed.

See `examples/motor_start_with_permissives.py` for implementation.

## Development

### Adding New Instructions

1. Add opcode to `OpCode` enum in `instructions.py`
2. Implement handler in `execute_rung_bytecode()`
3. Update tests

### Creating Programs

Programs are built by:
1. Creating a TagDB and declaring all tags
2. Creating a TimerEngine
3. Building rungs from instructions
4. Adding rungs to a Program

See examples for patterns.

## License

MIT
