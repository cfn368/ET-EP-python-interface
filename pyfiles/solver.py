"""
solver.py
---------
Minimise EnergyPLAN TOTAL ANNUAL COSTS over a set of capacity variables
using Nelder-Mead optimisation.

All configuration lives in the notebook. Call configure() once per run,
then call run().
"""

from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from pyfiles.scenario_functions import build_params, format_value, load_energyplan_file
from pyfiles.ep_run import DEFAULT_EXE, INPUT_DIR

# =============================================================================
# MODULE-LEVEL STATE  —  set by configure()
# =============================================================================

def _short(name: str, width: int = 14) -> str:
    """Short display label: strip leading 'input_' and truncate."""
    s = name[6:] if name.startswith("input_") else name
    return s[:width]


_case              = None
_base_params       = None
_base_case_params  = None
_shock_case_params = None
_eval_count        = 0
_best_cost         = float("inf")
_best_x            = None

# config
_x0               = None   # dict: {param_name: initial_value}
_bounds           = {}     # dict: {param_name: (lo, hi)}
_ref_file         = None
_ep_exe           = None
_data_dir         = None
_import_limit_twh = 0.5
_import_penalty   = 1e9
_bounds_penalty   = 1e9


# ==================== ==================== ==================== ====================
# 1. set all configuration before running
def configure(
    case: str,
    base_params: dict,
    base_case_params: dict,
    shock_case_params: dict,
    *,
    x0: dict,
    ref_file: str | Path,
    bounds: dict | None = None,
    import_limit_twh: float = 0.5,
    import_penalty: float = 1e9,
    bounds_penalty: float = 1e9,
    ep_exe: str | Path | None = None,
    data_dir: str | Path | None = None,
) -> None:
    """
    Set all solver configuration before running.

    Parameters
    ----------
    case              : 'base' or 'shock'
    base_params       : general parameters (same for both cases)
    base_case_params  : base-case-specific parameters
    shock_case_params : shock-case-specific parameters
    x0                : dict of {param_name: initial_value} — variables to optimise
    ref_file          : path to reference EnergyPLAN .txt file
    bounds            : dict of {param_name: (lower, upper)}, None = no bound
    import_limit_twh  : electricity import constraint (TWh)
    import_penalty    : M EUR per TWh over the import limit
    bounds_penalty    : M EUR per MW of bounds violation
    ep_exe            : path to energyPLAN.exe (defaults to project root)
    data_dir          : directory for temporary input files (defaults to Data/)
    """
    global _case, _base_params, _base_case_params, _shock_case_params
    global _eval_count, _best_cost, _best_x
    global _x0, _bounds, _ref_file, _ep_exe, _data_dir
    global _import_limit_twh, _import_penalty, _bounds_penalty

    if case not in ("base", "shock"):
        raise ValueError(f"case must be 'base' or 'shock', got {case!r}")

    _case              = case
    _base_params       = base_params
    _base_case_params  = base_case_params.copy()
    _shock_case_params = shock_case_params.copy()
    _eval_count        = 0
    _best_cost         = float("inf")
    _best_x            = None

    _x0               = x0
    _bounds           = bounds or {}
    _ref_file         = Path(ref_file)
    _ep_exe           = Path(ep_exe) if ep_exe is not None else DEFAULT_EXE
    _data_dir         = Path(data_dir) if data_dir is not None else INPUT_DIR
    _import_limit_twh = import_limit_twh
    _import_penalty   = import_penalty
    _bounds_penalty   = bounds_penalty


# =============================================================================
# ASCII PARSING HELPERS
# =============================================================================

_NUM_RE = re.compile(r"""
    ^\s*[-+]?
    (?:
        (?:\d{1,3}(?:[.,]\d{3})+|\d+)(?:[.,]\d+)?
        |(?:[.,]\d+)
    )
    (?:e[-+]?\d+)?\s*$
""", re.IGNORECASE | re.VERBOSE)

_UNIT_RE = re.compile(r"\s*(MW|MWh|GWh|TWh|kW|EUR|MEUR|M\s*EUR)\s*$", re.IGNORECASE)


# ==================== ==================== ==================== ====================
# 2. parse a single token to a number or leave as string
def _to_number(x: str):
    s = x.strip()
    if s == "":
        return ""
    s_clean = re.sub(r"[%€]", "", s)
    s_clean = _UNIT_RE.sub("", s_clean).strip()
    s0 = s_clean.replace(" ", "")
    if not _NUM_RE.match(s0):
        return s
    if "," in s0 and "." in s0:
        s1 = s0.replace(".", "").replace(",", ".") if s0.rfind(",") > s0.rfind(".") else s0.replace(",", "")
    elif "," in s0 and "." not in s0:
        s1 = s0.replace(",", ".")
    else:
        s1 = s0.replace(",", "")
    try:
        return float(s1)
    except ValueError:
        return s


# ==================== ==================== ==================== ====================
# 3. split one ASCII line into fields
def _split_line(ln: str) -> list:
    if "\t" in ln:
        return ln.split("\t")
    if ";" in ln:
        return ln.split(";")
    return re.split(r"\s{2,}", ln.rstrip())


# ==================== ==================== ==================== ====================
# 4. parse full ASCII output file into a list of rows
def _parse_rows(ascii_path: Path) -> list[list]:
    try:
        text = ascii_path.read_text(encoding="cp1252")
    except UnicodeDecodeError:
        text = ascii_path.read_text(encoding="latin-1")
    rows = []
    for ln in text.splitlines():
        if ln.strip() == "":
            rows.append([""])
        else:
            parts = _split_line(ln)
            rows.append([_to_number(p) for p in parts])
    return rows


# ==================== ==================== ==================== ====================
# 5. return first float in a row starting from a given column
def _first_float(row: list, start_col: int = 1) -> float | None:
    for v in row[start_col:]:
        if isinstance(v, float):
            return v
    return None


# =============================================================================
# COST EXTRACTORS
# =============================================================================


# ==================== ==================== ==================== ====================
# 6. extract total annual costs from parsed ASCII rows
def get_total_annual_cost(rows: list[list]) -> float:
    for raw_idx in [54, 55, 61, 63, 65, 67]:
        if raw_idx >= len(rows):
            continue
        row = rows[raw_idx]
        label = str(row[0]).strip() if row else ""
        if "TOTAL" in label.upper():
            val = _first_float(row)
            if val is not None:
                return val
    for row in rows:
        if not row:
            continue
        label = str(row[0]).strip()
        if "TOTAL" in label.upper() and "ANNUAL" in label.upper():
            val = _first_float(row)
            if val is not None:
                return val
    raise ValueError(
        "Could not find TOTAL ANNUAL COSTS in ASCII output.\n"
        "Tip: add  print(rows[50:70])  in get_total_annual_cost() to inspect."
    )


# ==================== ==================== ==================== ====================
# 7. extract annual electricity imports (TWh) from ASCII output
def get_imports_twh(ascii_path: Path) -> float:
    try:
        text = ascii_path.read_text(encoding="cp1252")
    except UnicodeDecodeError:
        text = ascii_path.read_text(encoding="latin-1")

    lines = text.splitlines()
    if len(lines) < 85:
        print("  WARNING: ASCII output too short to find electricity imports.", flush=True)
        return 0.0

    h1     = lines[80].split("\t")
    h2     = lines[81].split("\t")
    annual = lines[84].split("\t")

    for i, (a, b) in enumerate(zip(h1, h2)):
        if f"{a.strip()}_{b.strip()}" == "Import_Electr." and i < len(annual):
            try:
                return float(annual[i].strip().replace(",", "."))
            except ValueError:
                pass

    print("  WARNING: 'Import_Electr.' column not found — constraint not enforced.", flush=True)
    return 0.0


# ==================== ==================== ==================== ====================
# 8. custom electricity import cost function
def I_price(import_twh: float) -> float:
    """Custom electricity import cost (M EUR)."""
    return import_twh * 1e6 * 74.7 * 1e-6   # = import_twh * 74.7


# ==================== ==================== ==================== ====================
# 9. extract EnergyPLAN's own import cost (M EUR) from parsed rows
def get_ep_import_cost_meur(rows: list[list]) -> float:
    for raw_idx in [54, 55]:
        if raw_idx >= len(rows):
            continue
        row = rows[raw_idx]
        if str(row[0]).strip() == "Import":
            val = _first_float(row)
            if val is not None:
                return val
    for row in rows[50:75]:
        if str(row[0]).strip() == "Import":
            val = _first_float(row)
            if val is not None:
                return val
    print("  WARNING: EnergyPLAN import cost row not found — no cost adjustment made.", flush=True)
    return 0.0


# =============================================================================
# OBJECTIVE FUNCTION
# =============================================================================


# ==================== ==================== ==================== ====================
# 10. objective function for Nelder-Mead optimisation
def objective(x: np.ndarray) -> float:
    global _eval_count, _best_cost, _best_x

    if _case is None:
        raise RuntimeError("Call solver.configure(...) before running the optimiser.")

    _eval_count += 1

    if any(v <= 0 for v in x):
        print(f"  [{_eval_count:3d}] penalty (non-positive value in x)", flush=True)
        return 1e12

    # 1. apply bounds penalty before running EnergyPLAN (cheap evaluation)
    bounds_penalty = 0.0
    bounds_tags: list[str] = []
    for name, val in zip(_x0.keys(), x):
        lo, hi = _bounds.get(name, (None, None))
        if lo is not None and val < lo:
            bounds_penalty += _bounds_penalty * (lo - val)
            bounds_tags.append(f"{_short(name)}<{lo:.0f}")
        if hi is not None and val > hi:
            bounds_penalty += _bounds_penalty * (val - hi)
            bounds_tags.append(f"{_short(name)}>{hi:.0f}")
    if bounds_penalty > 0:
        var_str = "  ".join(f"{_short(k)}={v:7.1f}" for k, v in zip(_x0.keys(), x))
        print(
            f"  [{_eval_count:3d}] {var_str}  → bounds violated: {', '.join(bounds_tags)}  penalty={bounds_penalty:.2e}",
            flush=True,
        )
        return bounds_penalty

    # 2. build parameter file and run EnergyPLAN
    params = build_params(_case, _base_params, _base_case_params, _shock_case_params)
    for name, val in zip(_x0.keys(), x):
        params[name] = val

    tmp_input = _data_dir / f"_solver_{_case}.txt"
    tmp_ascii = ROOT / "runs" / f"_solver_{_case}_ascii.txt"

    lines, value_idx = load_energyplan_file(_ref_file)
    for name, val in params.items():
        if name not in value_idx:
            raise KeyError(f"Parameter not found in EnergyPLAN file: {name!r}")
        lines[value_idx[name]] = format_value(val)

    with open(tmp_input, "w", encoding="utf-16") as f:
        f.writelines(lines)

    tmp_ascii.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    res = subprocess.run(
        [str(_ep_exe), "-i", str(tmp_input), "-ascii", str(tmp_ascii)],
        capture_output=True, text=True,
    )
    elapsed = time.perf_counter() - t0

    if res.returncode != 0 or not tmp_ascii.exists():
        print(f"  [{_eval_count:3d}] EnergyPLAN failed – returning penalty", flush=True)
        return 1e12

    # 3. parse output and extract cost
    rows = _parse_rows(tmp_ascii)
    try:
        cost = get_total_annual_cost(rows)
    except ValueError as e:
        print(f"  [{_eval_count:3d}] Parse error: {e}", flush=True)
        return 1e12

    # 4. apply import constraint penalty
    imports_twh = get_imports_twh(tmp_ascii)
    violation   = max(0.0, imports_twh - _import_limit_twh)
    penalised   = cost + _import_penalty * violation

    marker     = " *" if penalised < _best_cost else "  "
    import_tag = f"  [IMPORT {imports_twh:.2f} > {_import_limit_twh} TWh!]" if violation > 0 else ""
    var_str    = "  ".join(f"{_short(k)}={v:7.1f}" for k, v in zip(_x0.keys(), x))
    print(
        f"{marker}[{_eval_count:3d}] {var_str}  "
        f"→ cost={cost:8.2f} M EUR  imports={imports_twh:.3f} TWh  ({elapsed:.1f}s){import_tag}",
        flush=True,
    )

    if penalised < _best_cost:
        _best_cost = penalised
        _best_x    = x.copy()

    return penalised


# =============================================================================
# CONVENIENCE RUNNER
# =============================================================================


# ==================== ==================== ==================== ====================
# 11. run the Nelder-Mead optimisation
def run(max_evaluations: int = 500) -> dict:
    """
    Run the Nelder-Mead optimisation and return a results dict.

    Parameters
    ----------
    max_evaluations : maximum number of EnergyPLAN calls

    Returns
    -------
    dict with keys: 'best_cost', 'best_x', 'result'
    """
    if _case is None:
        raise RuntimeError("Call solver.configure(...) before solver.run().")

    _x0_arr = np.array(list(_x0.values()), dtype=float)

    print("=" * 70, flush=True)
    print(f"EnergyPLAN cost minimiser  (case='{_case}', {max_evaluations} max evals)", flush=True)
    print(f"  Choice vars ({len(_x0_arr)}): " + ",  ".join(f"{_short(k)}={v:.0f}" for k, v in _x0.items()), flush=True)
    print(f"  Import limit : {_import_limit_twh} TWh", flush=True)
    active_bounds = [(k, lo, hi) for k, (lo, hi) in _bounds.items() if lo is not None or hi is not None]
    for k, lo, hi in active_bounds:
        lo_s = f">= {lo}" if lo is not None else ""
        hi_s = f"<= {hi}" if hi is not None else ""
        print(f"  Bound: {k}  {lo_s}{' ' if lo_s and hi_s else ''}{hi_s}", flush=True)
    print("=" * 70, flush=True)

    result = minimize(
        objective,
        _x0_arr,
        method="Nelder-Mead",
        options={
            "maxfev"  : max_evaluations,
            "maxiter" : max_evaluations * 1000,
            "xatol"   : 1e-6,
            "fatol"   : 1e-6,
            "adaptive": True,
            "disp"    : False,
        },
    )

    best_x = _best_x if _best_x is not None else result.x

    print("\n" + "=" * 70, flush=True)
    print(f"Finished after {_eval_count} evaluations  (converged: {result.success})", flush=True)
    print(f"  Best cost : {_best_cost:.2f} M EUR", flush=True)
    print("  Best parameters:", flush=True)
    for name, val in zip(_x0.keys(), best_x):
        print(f"    {name:<35s} = {val:.1f}", flush=True)
    print("=" * 70, flush=True)

    return {"best_cost": _best_cost, "best_x": best_x, "result": result}


# =============================================================================
# __main__
# =============================================================================

if __name__ == "__main__":
    raise SystemExit(
        "solver.py is called from a notebook via configure() + run().\n"
        "See the docstring at the top of this file for usage."
    )
