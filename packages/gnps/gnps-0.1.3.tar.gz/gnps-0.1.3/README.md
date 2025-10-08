# GNPS project

The *GNPS* project (Generalized Numerical P Systems) aims to create a 
library for simulation of different variants of Numerical P Systems (NPS).

It contains:

* GNPS core (the core classes for NPS simulation)
* GNPS parser (parsers for different inputs)
* GNPS generator (generates outputs, i.e. Verilog, Amaranth and Lustre) *work in progress.*
* Utils (like the main runner)

## Input Files

- **System description**: YAML file describing the GNPS system (required as the first argument).
- **Input file**: Optional CSV file, each row representing input variable values for a simulation step. The header must match the input variable names defined in the YAML.
- **Output file**: Optional CSV file, each row representing output variable values for each step.

## Command Line Options

Run the simulator with:

    python -m gnps <gnps_file.yaml> [input.csv] [output.csv] [options]

Options:
- `-c`, `--compute_mode`   Run in continuous compute mode (no input variables allowed)
- `-s`, `--steps N`        Number of steps to run (default: 1)
- `--csv`                  Output in CSV format in continuous compute mode

- `gnps_file` (YAML): Required. GNPS system description.
- `input` (CSV): Optional. Input values per step (default: stdin).
- `output` (CSV): Optional. Output values per step (default: stdout).

## Modes

- **IO mode (default)**: Reads input variables from CSV for each step, writes output variables for each step.
- **Continuous compute mode**: Runs for a set number of steps without input variables, outputs results at each step (CSV or text).

## Example Input YAML

Below is an example of a GNPS system description in YAML format (from `test_math_functions.yaml`):

```yaml
description: "A test system"

cells:
  - id: 1
    contents:
      - x = 0, y = 0, E = 0, z = 0, u = 1
      # Comments can be added like this
    # input variables should be empty for continuous compute mode
    input: [u] 
    output: [x,y,z]

rules:
  - E > x | x + 3 -> x  # guarded rule
  - E + 1 -> E         # unguarded rule
  - 0*z + x + y -> z
  - (E > u || E > x || E > y) | u + x + y -> y                                   # step will be reset to 0
```


For more details, see the CHANGELOG.md and documentation in the docs/ folder.
