# EnergyPLAN Python Framework

## About

This repository provides a lightweight Python framework for running and analysing [EnergyPLAN](https://www.energyplan.eu/) simulations programmatically. It wraps the EnergyPLAN Windows binary, parses its ASCII output into structured data, and exposes a clean API for scenario creation, cost analysis, time-series visualisation, and capacity optimisation.

The framework is designed as a skeleton — comprehensive enough to cover the full workflow, slim enough to be extended freely.

---

## Repository Structure

```
/
├── pyfiles/
│   ├── preamble.py             # Shared imports, plot colours, notebook initialisation
│   ├── scenario_functions.py   # load_energyplan_file, save_scenario, build_params
│   ├── ep_run.py               # Core runner: call EnergyPLAN, parse ASCII → parquet;
│   │                           #   load helpers (scalars, annual, monthly, hourly, investments)
│   ├── ep_costs.py             # Cost summary helpers: get_costs_all, detailed_get_costs_all
│   ├── ep_plot.py              # plot_monthly, plot_hourly — multi-scenario grid plots
│   ├── ep_to_excel.py          # Export parquet output to Excel
│   ├── solver.py               # Nelder-Mead cost minimiser over user-defined capacities
│   ├── input_variables.py      # Human-readable labels for all EnergyPLAN input parameters
│   └── output_variables.py     # Human-readable labels for all EnergyPLAN output columns
│
├── 1_create_scenario.ipynb     # Build input .txt files from a reference scenario
├── 2_get_output.ipynb          # Run scenarios, inspect costs, plot time-series
├── 3_optimiser.ipynb           # Minimise total system costs over capacity variables
│
├── runs/                       # Parquet output files written here
└── energyPLAN.exe              # EnergyPLAN binary (not tracked)
```

---

## Quickstart

### Dependencies

```
numpy
pandas
matplotlib
scipy
requests
pyarrow      # parquet support
```

Install with:
```bash
pip install numpy pandas matplotlib scipy requests pyarrow
```

### EnergyPLAN binary

Download EnergyPLAN from [energyplan.eu](https://energyplan.eu/download/). Unzip it, then **clone this repository into the EnergyPLAN folder** (the one containing `energyPLAN.exe`). The framework resolves all paths relative to the repository root, which must be the same directory as the binary.

### Running the notebooks

All notebooks begin with:
```python
from pyfiles.preamble import *
setup_notebook()
```

This imports the full library, sets plot styles, and enables autoreload.

**Recommended execution order:**

| Step | Notebook | Purpose |
|------|----------|---------|
| 1 | `1_create_scenario.ipynb` | Define parameters and write input files |
| 2 | `2_get_output.ipynb` | Run scenarios and visualise results |
| 3 | `3_optimiser.ipynb` | Find cost-minimising capacities *(optional)* |

---

## Workflow

### 1. Create scenarios

Scenarios are built by loading a reference `.txt` file and overriding specific parameters:

```python
ref_path = ep_run.INPUT_DIR / "reference.txt"

params = {
    'Input_el_demand_Twh'  : 311/10,
    'input_RES1_capacity'  : 5150,
    'input_nuclear_cap'    : 1000,
}

save_scenario(ref_path, ep_run.INPUT_DIR / "my_scenario.txt", params)
```

For base/shock pairs, define shared and case-specific dicts and loop:

```python
for case in ('base', 'shock'):
    params = build_params(case, base_params, base_case_params, shock_case_params)
    save_scenario(ref_path, ep_run.INPUT_DIR / f"my_{case}.txt", params)
```

Browse `pyfiles/input_variables.py` for all available parameter names.

### 2. Run and analyse

```python
# Run EnergyPLAN — saves five parquet files per scenario to /runs/
ep_run.run_scenarios(['my_base', 'my_shock'])

# Cost summary
ep_costs.get_costs_all(['my_base', 'my_shock'], names=['Base', 'Shock'])

# Detailed cost decomposition
ep_costs.detailed_get_costs_all(['my_base', 'my_shock'], names=['Base', 'Shock'])

# Time-series plots
ep_plot.plot_monthly(names=['my_base', 'my_shock'], variables=['Wind_Electr.', 'PV_Electr.'])
ep_plot.plot_hourly( names=['my_base', 'my_shock'], variables=['Nuclear_Electr.'])
```

Browse `pyfiles/output_variables.py` for all available output variable names.

### 3. Optimise

Minimise total annual costs over a set of capacity variables using Nelder-Mead:

```python
solver.configure(
    'base', base_params, base_case_params, shock_case_params,
    x0     = {'input_cap_pp2_el': 4500, 'input_cap_ELTtrans_el': 4000},
    bounds = {'input_cap_ELTtrans_el': (3200, None)},
    ref_file         = ref_path,
    import_limit_twh = 0.5,
)
result = solver.run(max_evaluations=1000)
```

---

## Output format

Each `run_energyplan()` call produces five parquet files in `/runs/`:

| File | Content | Shape |
|------|---------|-------|
| `*_scalars.parquet` | Summary KPIs (CO2, costs, fuel use, RES shares) | 1 row × metrics |
| `*_annual.parquet` | Annual production totals | 1 row × variables |
| `*_monthly.parquet` | Monthly averages | 12 rows × variables (MW) |
| `*_hourly.parquet` | Full hourly dispatch | 8760 rows × variables (MW) |
| `*_investments.parquet` | Investment cost breakdown per technology | N rows |

Load directly with:
```python
ep_run.load_scalars('my_scenario')
ep_run.load_monthly('my_scenario')
ep_run.load_hourly('my_scenario')
ep_run.load_investments('my_scenario')
ep_run.ann_T('my_scenario')   # annual, transposed (variables as rows)
```

---

## Data

Input files and distribution files are not tracked in this repository. EnergyPLAN ships with example data; additional files can be downloaded from the [EnergyPLAN website](https://energyplan.eu/) or built from national energy statistics.

Place scenario files in `energyPlan Data/Data/` and hourly distribution files in `energyPlan Data/Distributions/`.

---

Developed by [Linus Lindquist](https://github.com/cfn368) for [Erhvervslivets Tænketank](https://www.e-tank.dk) as part of Kernekraftprojektet.