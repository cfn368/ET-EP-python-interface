# pyfiles/ep_to_excel.py
"""
Collect EnergyPLAN parquet output for multiple scenarios into one Excel file.

Sheet layout
------------
scalars      : one row per scenario × named scalar metrics
annual       : one row per scenario × named annual production columns
monthly      : all scenarios stacked (first column = scenario name, second = month)
investments  : all scenarios stacked (first column = scenario name)

Hourly data is omitted — 8 760 rows × many columns per scenario is too large
for a practical spreadsheet.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

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

    # 2. annual — one row per scenario
    annual = pd.concat(
        [ann_T(name, out_dir=out_dir).rename(columns={name: name}) for name in out_names],
        axis=1,
    ).T
    annual.index.name = "scenario"

    # 3. monthly — stacked, scenario + month as first two columns
    monthly_frames = []
    for name in out_names:
        df = load_monthly(name, out_dir=out_dir).copy()
        df.insert(0, "scenario", name)
        df.index.name = "month"
        df = df.reset_index()
        monthly_frames.append(df)
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
        annual.to_excel(writer, sheet_name="annual")
        monthly.to_excel(writer, sheet_name="monthly", index=False)
        investments.to_excel(writer, sheet_name="investments", index=False)

    return excel_path