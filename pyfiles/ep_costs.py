# pyfiles/ep_costs.py
"""
Cost summary helpers for EnergyPLAN output.
"""

from __future__ import annotations

import pandas as pd

from pyfiles.ep_run import load_scalars, _stem, DEFAULT_OUT_DIR


# ==================== ==================== ==================== ====================
def get_costs(name: str, *, out_dir=DEFAULT_OUT_DIR) -> pd.DataFrame:
    """
    Return cost summary for one run as a single-row DataFrame (M EUR).

    Parameters
    ----------
    name    : scenario stem (e.g. 'example_base')
    out_dir : directory containing the parquet files
    """
    s = load_scalars(name, out_dir=out_dir)
    row = {
        "Variable costs":          s.get("var_costs_MEUR"),
        "Fixed operation costs":   s.get("fixed_costs_MEUR"),
        "Annual Investment costs":  s.get("inv_costs_MEUR"),
        "TOTAL ANNUAL COSTS":      s.get("total_costs_MEUR"),
    }
    return pd.DataFrame([row], index=pd.Index([_stem(name)], name="Case (M EUR)"))


# ==================== ==================== ==================== ====================
def get_costs_all(names: list[str], *, out_dir=DEFAULT_OUT_DIR) -> pd.DataFrame:
    """
    Return cost summary for multiple runs as a multi-row DataFrame (M EUR).

    Parameters
    ----------
    names   : list of scenario stems
    out_dir : directory containing the parquet files
    """
    return pd.concat([get_costs(n, out_dir=out_dir) for n in names])