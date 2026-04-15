# pyfiles/ep_to_excel.py
"""
Collect EnergyPLAN parquet output for multiple scenarios into one Excel file.

Sheet layout
------------
scalars      : one row per scenario × named scalar metrics
annual       : one row per variable — columns: model_name, label, then one per scenario
monthly      : one row per (scenario, month, variable) — columns: scenario, month,
               model_name, label, value
investments  : all scenarios stacked (first column = scenario name)

Hourly data is omitted — 8 760 rows × many columns per scenario is too large
for a practical spreadsheet.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from pyfiles import output_variables
from pyfiles.ep_run import (
    DEFAULT_OUT_DIR,
    load_scalars,
    ann_T,
    load_monthly,
    load_investments,
)


# ==================== ==================== ==================== ====================
def to_excel(
    out_names: list[str],
    excel_path: str | Path,
    *,
    out_dir: str | Path = DEFAULT_OUT_DIR,
) -> Path:
    """
    Collect parquet output for *out_names* into a single Excel workbook.

    Parameters
    ----------
    out_names  : scenario stems (as passed to run_scenarios)
    excel_path : destination .xlsx file path
    out_dir    : directory containing the parquet files

    Returns
    -------
    Path to the written Excel file
    """
    excel_path = Path(excel_path)

    # 1. scalars — one row per scenario
    scalars = pd.DataFrame(
        {name: load_scalars(name, out_dir=out_dir) for name in out_names}
    ).T
    scalars.index.name = "scenario"

    # 2. annual — variables as rows: [model_name, label, scenario_1, scenario_2, ...]
    annual_data = pd.concat(
        [ann_T(name, out_dir=out_dir) for name in out_names],
        axis=1,
    )   # shape: (n_vars, n_scenarios)
    annual_data.columns = out_names
    annual_data.index.name = "model_name"
    annual_data = annual_data.reset_index()
    annual_data.insert(1, "label", annual_data["model_name"].map(output_variables.labels))

    # 3. monthly — long format: [scenario, month, model_name, label, value]
    monthly_frames = []
    for name in out_names:
        df = load_monthly(name, out_dir=out_dir)   # shape: (12, n_vars), index = month names
        df.index.name = "month"
        long = df.reset_index().melt(id_vars="month", var_name="model_name", value_name="value")
        long.insert(0, "scenario", name)
        long["label"] = long["model_name"].map(output_variables.labels)
        # reorder columns
        long = long[["scenario", "month", "model_name", "label", "value"]]
        monthly_frames.append(long)
    monthly = pd.concat(monthly_frames, ignore_index=True)

    # 4. investments — stacked, scenario as first column
    inv_frames = []
    for name in out_names:
        df = load_investments(name, out_dir=out_dir).copy()
        df.insert(0, "scenario", name)
        inv_frames.append(df)
    investments = pd.concat(inv_frames, ignore_index=True)

    # 5. write to Excel
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        scalars.to_excel(writer, sheet_name="scalars")
        annual_data.to_excel(writer, sheet_name="annual", index=False)
        monthly.to_excel(writer, sheet_name="monthly", index=False)
        investments.to_excel(writer, sheet_name="investments", index=False)

    return excel_path