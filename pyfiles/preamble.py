# pyfiles/preamble.py

# 1. third-party imports
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import MaxNLocator
import requests
import os

# 2. stdlib imports
import itertools
from pathlib import Path
from typing import Sequence

# 3. global plot colours (used by all plotting functions, in order)
colors = ['crimson', 'k', '#00B8D9']

# 4. project module imports
import pyfiles.ep_run as ep_run
import pyfiles.solver as solver
import pyfiles.ep_to_excel as ep_to_excel
import pyfiles.ep_costs as ep_costs
from pyfiles.ep_costs import get_costs, get_costs_all, detailed_get_costs, detailed_get_costs_all
import pyfiles.ep_plot as ep_plot
from pyfiles.output_variables import labels
from pyfiles.scenario_functions import (
    load_energyplan_file,
    format_value,
    build_params,
    save_scenario,
)


# ==================== ==================== ==================== ====================
# 1. enable IPython autoreload
def enable_autoreload(mode: int = 2) -> None:
    """Enable IPython autoreload (call from a notebook)."""
    ip = get_ipython()  # noqa: F821
    ip.run_line_magic("load_ext", "autoreload")
    ip.run_line_magic("autoreload", str(mode))


# ==================== ==================== ==================== ====================
# 2. matplotlib style
def set_aej(**kwargs):
    """Set matplotlib style for AEJ-style figures."""
    mpl.rcParams.update({
        "font.family": "serif",
        # "font.size": 15,

        "axes.linewidth": 1.0,
        "lines.linewidth": 1.2,
        "legend.frameon": False,

        "xtick.direction": "out",
        "ytick.direction": "out",

        "axes.spines.top": True,
        "axes.spines.right": True,

        # legend
        "legend.frameon": True,
        "legend.fancybox": True,
        "legend.borderaxespad": 0.4,
        "legend.handlelength": 2.0,
        "legend.handletextpad": 0.6,
        "legend.labelspacing": 0.35,

        "savefig.bbox": "tight",
        "savefig.dpi": 300,
    })


# ==================== ==================== ==================== ====================
# 3. setup notebook environment
def setup_notebook(*, autoreload: int = 2, aej: bool = True, **aej_kwargs) -> None:
    """
    One call in a notebook to get the usual environment:
      - autoreload
      - matplotlib style
    """
    enable_autoreload(autoreload)
    if aej:
        set_aej(**aej_kwargs)


__all__ = [
    "np", "pd", "mpl", "plt", "mcolors", "MaxNLocator", "requests",
    "itertools", "Path", "Sequence",
    "ep_run", "ep_to_excel", "ep_costs", "ep_plot", "labels", "os", "solver",
    "enable_autoreload", "set_aej", "setup_notebook",
    "get_costs", "get_costs_all", "detailed_get_costs", "detailed_get_costs_all",
    "colors",
    "load_energyplan_file", "format_value", "build_params", "save_scenario",
]
