# pyfiles/preamble.py

# 1. third-party imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import MaxNLocator
import requests
import os

# 2. stdlib imports
import itertools
from pathlib import Path
from typing import Sequence

# 3. project module imports
import pyfiles.ep_run as ep_run
import pyfiles.ep_to_excel as ep_to_excel
import pyfiles.ep_costs as ep_costs
import pyfiles.ep_plot as ep_plot
from pyfiles.output_variables import labels


# ==================== ==================== ==================== ====================
# 1. enable IPython autoreload
def enable_autoreload(mode: int = 2) -> None:
    """Enable IPython autoreload (call from a notebook)."""
    ip = get_ipython()  # noqa: F821
    ip.run_line_magic("load_ext", "autoreload")
    ip.run_line_magic("autoreload", str(mode))


__all__ = [
    "np", "pd", "plt", "mcolors", "MaxNLocator", "requests",
    "itertools", "Path", "Sequence",
    "ep_run", "ep_to_excel", "ep_costs", "ep_plot", "labels", 'enable_autoreload', 'os'
]
