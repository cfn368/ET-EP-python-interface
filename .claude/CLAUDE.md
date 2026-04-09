# EnergyPLAN Python Framework

## Project goal
Publishing a clean, general-purpose Python framework for running and analyzing [EnergyPLAN](https://www.energyplan.eu/) simulations. The published version is distilled from a larger private research project — the priority is simplicity, clarity, and ease of use for new users.

## What EnergyPLAN is
EnergyPLAN is a deterministic energy system simulation tool (Windows `.exe`). It takes a `.txt` input file, runs an hourly simulation for a full year (8760 hours), and writes an ASCII output file. The framework wraps that binary via Python.

## Project layout
```
/                         project root
  energyPLAN.exe          the EnergyPLAN binary (not tracked in git)
  energyPlan Data/
    Data/                 input scenario .txt files (UTF-16 encoded)
    Distributions/        hourly distribution files (demand, wind, solar, prices…)
    Cost/                 cost data files
  runs/                   output parquet files written here
  pyfiles/
    preamble.py           single import that re-exports all common deps + modules
    ep_run.py             core runner: runs exe, parses ASCII output → parquet
    ep_to_excel.py        optional Excel export helpers
    ep_costs.py           cost calculation helpers
    ep_plot.py            plotting helpers
    input_variables.py    human-readable labels for every EnergyPLAN input parameter
    output_variables.py   human-readable labels for every EnergyPLAN output column
  1_create_scenario.ipynb create/modify input .txt files from a reference scenario
  2_get_output.ipynb      run scenarios and load/analyse output
  3_solver.ipynb          optimisation / solver workflows
```

## Key design decisions

### Input files
- EnergyPLAN input files are plain `.txt` (UTF-16 encoded). They are modified by loading a reference file, overriding specific parameter values, and writing the result.
- Parameters are identified by their exact EnergyPLAN key names (documented in `input_variables.py`).
- Decimal values are expressed as fractions in code (e.g. `311/10`) so they stay readable.

### Output / parsing
- `ep_run.run_energyplan()` calls the binary, captures the ASCII output, and parses it into five parquet files per run:
  - `*_scalars.parquet` — summary KPIs (CO2, costs, fuel use…)
  - `*_annual.parquet`  — annual production totals (1 row × columns)
  - `*_monthly.parquet` — monthly averages (12 rows × columns, MW)
  - `*_hourly.parquet`  — full hourly dispatch (8760 rows × columns, MW)
  - `*_investments.parquet` — investment cost breakdown per technology
- Loading helpers: `ann_T()`, `load_scalars()`, `load_monthly()`, `load_hourly()`, `load_investments()`

### Column/variable naming
- Raw EnergyPLAN output uses terse internal names (`Electr._Demand`, `Wind_Electr.`, etc.).
- `output_variables.labels` maps these to human-readable strings.
- `input_variables.labels` does the same for input parameters.

## Style conventions
- Keep the public API minimal — ease of use over configurability.
- Notebook cells should read like a clear recipe: load reference → override params → run → analyse.
- Prefer explicit parameter dicts over positional arguments.
- Avoid breaking changes to `ep_run` public functions; downstream notebooks depend on them.