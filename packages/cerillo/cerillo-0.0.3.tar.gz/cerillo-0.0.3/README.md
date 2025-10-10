# cerillo
# cerillo

Cerillo python API for control of Cerillo devices

[![PyPI - Version](https://img.shields.io/pypi/v/cerillo.svg)](https://pypi.org/project/cerillo)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cerillo.svg)](https://pypi.org/project/cerillo)

-----

## Table of Contents

- [cerillo](#cerillo)
- [cerillo](#cerillo-1)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [StratusReader](#stratusreader)
    - [RayoReader](#rayoreader)
    - [Basic experiment setup (CDCL ExperimentBuilder)](#basic-experiment-setup-cdcl-experimentbuilder)
  - [License](#license)

## Installation

`pip install cerillo`

## Usage

Below are concrete examples showing how to instantiate, connect, control, and disconnect `StratusReader` and `RayoReader`. These examples use the real public APIs implemented in `cerillo.base_plate_reader` and the reader modules.

### StratusReader

The `StratusReader` extends `CerilloBasePlateReader`. Key methods on the base class include `connect()`, `disconnect()`, and `read_absorbance(...)`.

Example (safe local test using simulation):

```python
from cerillo.stratus import StratusReader

# Create a reader. Use simulate=True for local testing without hardware.
reader = StratusReader(port="/dev/ttyUSB0", simulate=True)

# Connect (in simulation this will set up simulated device fields)
reader.connect()

# Print a quick summary populated by connect()/initialize()
print(reader)

# Read absorbance: wavelength (int), interval (seconds), duration (seconds)
# This method blocks and reads CDCL data until data transmission is received.
# The wavelength must be present on the device for it to work properly
try:
    data = reader.read_absorbance(wavelength=600, interval=60, duration=3600)
    print("Absorbance data:", data)
finally:
    # Always disconnect to clean up
    reader.disconnect()
```

Notes:
- Use `simulate=True` when developing without hardware. When `simulate=False` (default) the reader will open a serial port.
- `read_absorbance` uses the CDCL protocol and returns the parsed data transmission response when available.

### RayoReader

`RayoReader` also extends `CerilloBasePlateReader` and adds motor control utilities. The constructor accepts `has_motor` to enable motor operations and `simulate` for dry runs.

Example (motor commands + simulation):

```python
from cerillo.rayo import RayoReader, MotorStepCommand, MotorNamedCommand

# Create a Rayo reader. Enable simulate for dry-run and has_motor if device has a motor.
reader = RayoReader(port="/dev/ttyUSB0", has_motor=True, simulate=True)

# Connect (simulation will populate device info)
reader.connect()
print(reader)

# read absorbance
# The wavelength must be present on the device for this to work
data = reader.read_absorbance(wavelength=590)

# Move motor by a number of steps (positive/negative). If simulate=True this will print simulated responses.
step_cmd = MotorStepCommand(steps=100)
ok = reader.move_motor(step_cmd)
print("Motor step result:", ok)

# Use named commands for common operations: 'c' (close) and 'o' (open) are provided helpers.
close_ok = reader.close_lid()
open_ok = reader.open_lid()
print("Close lid result:", close_ok, "Open lid result:", open_ok)

# When done
reader.disconnect()
```

Notes:
- If `move_motor` is called on a reader constructed without `has_motor=True`, it will return False and print a helpful message.
- Motor commands are represented by `MotorStepCommand` (step count) and `MotorNamedCommand` (string commands). Both inherit the CDCL command base and are sent with `send_command` internally. `RayoReader::open_lid()` and `RayoReader::close_lid()` use the `MotorNamedCommand`.

### Basic experiment setup (CDCL ExperimentBuilder)

A minimal flow to create an experiment and start it with the reader:

```python
from cerillo.cdcl.experiment_builder import ExperimentBuilder
from cerillo.stratus import StratusReader

# Build an experiment configuration
builder = FullExperimentBuilder()
builder.experiment().set_name("example_experiment").set_interval(60).set_duration(3600)
builder.plate().set_manufacturer("corning")
# add plates, templates, etc. via builder API
# builder.set_interval(...)


# Create reader and start the experiment
reader = StratusReader(simulate=True)
reader.connect()
try:
    # Use start_experiment if you want the reader to send the builder messages and collect data
    data = reader.start_experiment(builder)
    print("Experiment data:", data)
finally:
    reader.disconnect()
```

## License

`cerillo` is distributed under the terms of the [GPLv3](https://spdx.org/licenses/GPL-3.0-or-later.html) license.

