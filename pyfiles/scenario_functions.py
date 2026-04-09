# pyfiles/scenario_functions.py

from pathlib import Path


# ==================== ==================== ==================== ====================
# 1. load EnergyPLAN parameter file
def load_energyplan_file(path):
    """Load EnergyPLAN .txt and return (lines, value_index_by_name).

    Parameter names are mapped WITHOUT the trailing '=' so that
    'Input_el_demand_Twh' matches a line 'Input_el_demand_Twh='.
    """
    # 1. read UTF-16 encoded file
    with open(path, encoding="utf-16") as f:
        lines = f.readlines()

    # 2. build name -> line-index map (strip trailing '=' from keys)
    value_idx = {}
    for i in range(0, len(lines) - 1, 2):
        raw_name = lines[i].strip()   # e.g. 'Input_el_demand_Twh='
        key = raw_name.rstrip("=")    # e.g. 'Input_el_demand_Twh'
        value_idx[key] = i + 1

    return lines, value_idx


# ==================== ==================== ==================== ====================
# 2. format a parameter value for writing to EnergyPLAN file
def format_value(v):
    """Format a new value for EnergyPLAN (plain number string, terminated with newline)."""
    if isinstance(v, (int, float)):
        s = f"{v}"
    else:
        s = str(v)

    if not s.endswith("\n"):
        s = s + "\n"
    return s


# ==================== ==================== ==================== ====================
# 3. build combined parameter dict for a given case
def build_params(case: str, base_params, base_case_params, shock_case_params):
    """Return merged parameter dict for the requested case ('base' or 'shock')."""
    params = base_params.copy()

    if case == "base":
        params.update(base_case_params)
    elif case == "shock":
        params.update(shock_case_params)
    else:
        raise ValueError(f"Unknown case: {case!r}")

    return params


# ==================== ==================== ==================== ====================
# 4. save a scenario to disk
def save_scenario(ref_path, out_path, params):
    """Apply *params* on top of *ref_path* and write the result to *out_path*.

    Parameters
    ----------
    ref_path : path to the reference EnergyPLAN .txt file
    out_path : destination path for the new scenario file
    params   : dict of {parameter_name: new_value}
    """
    lines, value_idx = load_energyplan_file(ref_path)

    for name, new_val in params.items():
        if name not in value_idx:
            raise KeyError(f"Parameter not found in reference file: {name!r}")
        lines[value_idx[name]] = format_value(new_val)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-16") as f:
        f.writelines(lines)

    print(f"Written: {out_path}")