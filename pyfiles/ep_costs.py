# pyfiles/ep_costs.py
"""
Cost summary helpers for EnergyPLAN output.
"""

from __future__ import annotations

import pandas as pd

from pyfiles.ep_run import load_scalars, _stem, DEFAULT_OUT_DIR


# ==================== ==================== ==================== ====================
def get_costs(name: str, *, display_name: str | None = None, out_dir=DEFAULT_OUT_DIR) -> pd.DataFrame:
    """
    Return cost summary for one run as a single-row DataFrame (M EUR).

    Parameters
    ----------
    name         : scenario stem (e.g. 'example_base')
    display_name : label for the index row; defaults to the file stem
    out_dir      : directory containing the parquet files
    """
    s = load_scalars(name, out_dir=out_dir)
    row = {
        "Variable costs":          s.get("var_costs_MEUR"),
        "Fixed operation costs":   s.get("fixed_costs_MEUR"),
        "Annual Investment costs": s.get("inv_costs_MEUR"),
        "TOTAL ANNUAL COSTS":      s.get("total_costs_MEUR"),
    }
    label = display_name if display_name is not None else _stem(name)
    return pd.DataFrame([row], index=pd.Index([label], name="Case (M EUR)"))


# ==================== ==================== ==================== ====================
def get_costs_all(
    files: list[str],
    *,
    names: list[str] | None = None,
    out_dir=DEFAULT_OUT_DIR,
) -> pd.DataFrame:
    """
    Return cost summary for multiple runs as a multi-row DataFrame (M EUR).
    Electricity exchange is shown separately from variable costs.

    Parameters
    ----------
    files   : list of scenario stems (used to locate parquet files)
    names   : display labels for the index; defaults to file stems
    out_dir : directory containing the parquet files
    """
    rows = []
    for n in files:
        s = load_scalars(n, out_dir=out_dir)
        rows.append({
            "Variable costs":           s.get("var_costs_MEUR"),
            "Fixed operation costs":    s.get("fixed_costs_MEUR"),
            "Annual Investment costs":  s.get("inv_costs_MEUR"),
            "TOTAL ANNUAL COSTS":       s.get("total_costs_MEUR"),
        })
    idx = names if names is not None else [_stem(n) for n in files]
    return pd.DataFrame(rows, index=pd.Index(idx, name="Case (M EUR)"))


# ==================== ==================== ==================== ====================
def detailed_get_costs(
    name: str,
    *,
    display_name: str | None = None,
    out_dir=DEFAULT_OUT_DIR,
) -> pd.DataFrame:
    """
    Return fully decomposed cost summary for one run (M EUR).
    Variable costs are replaced by their three components:

        Variable costs = Marginal operation costs
                       + Ngas exchange
                       + Fuel ex. Ngas exchange

    Parameters
    ----------
    name         : scenario stem (e.g. 'example_base')
    display_name : label for the index row; defaults to the file stem
    out_dir      : directory containing the parquet files
    """
    s = load_scalars(name, out_dir=out_dir)
    row = {
        "Marginal operation costs": s.get("var_marginal_MEUR"),
        "Ngas exchange":            s.get("ngas_exchange_MEUR"),
        "Fuel ex. Ngas exchange":   s.get("fuel_ex_ngas_MEUR"),
        "Electricity exchange":     s.get("elec_exchange_MEUR"),
        "Fixed operation costs":    s.get("fixed_costs_MEUR"),
        "Annual Investment costs":  s.get("inv_costs_MEUR"),
        "TOTAL ANNUAL COSTS":       s.get("total_costs_MEUR"),
   
    }
    label = display_name if display_name is not None else _stem(name)
    return pd.DataFrame([row], index=pd.Index([label], name="Case (M EUR)"))


# ==================== ==================== ==================== ====================
def detailed_get_costs_all(
    files: list[str],
    *,
    names: list[str] | None = None,
    out_dir=DEFAULT_OUT_DIR,
) -> pd.DataFrame:
    """
    Return fully decomposed cost summary for multiple runs (M EUR).

    Parameters
    ----------
    files   : list of scenario stems (used to locate parquet files)
    names   : display labels for the index; defaults to file stems
    out_dir : directory containing the parquet files
    """
    rows = []
    for n in files:
        s = load_scalars(n, out_dir=out_dir)
        rows.append({
            "Marginal operation costs": s.get("var_marginal_MEUR"),
            "Ngas exchange":            s.get("ngas_exchange_MEUR"),
            "Fuel ex. Ngas exchange":   s.get("fuel_ex_ngas_MEUR"),
            "Electricity exchange":     s.get("elec_exchange_MEUR"),
            "Fixed operation costs":    s.get("fixed_costs_MEUR"),
            "Annual Investment costs":  s.get("inv_costs_MEUR"),
            "TOTAL ANNUAL COSTS":       s.get("total_costs_MEUR"),
        })
    idx = names if names is not None else [_stem(n) for n in files]
    return pd.DataFrame(rows, index=pd.Index(idx, name="Case (M EUR)"))
