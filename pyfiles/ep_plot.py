# pyfiles/ep_plot.py
"""
Visualisation helpers for EnergyPLAN output.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from pyfiles.ep_run import load_monthly, load_hourly, DEFAULT_OUT_DIR
from pyfiles.output_variables import labels as _labels
from pyfiles.preamble import colors as _COLORS


_LINESTYLES = ["-", "--", "-.", ":"]


# ==================== ==================== ==================== ====================
def plot_monthly(
    names: list[str],
    variables: list[str],
    *,
    inp_names: list[str] | None = None,
    out_dir: str | Path = DEFAULT_OUT_DIR,
    savepath: str | Path | None = None,
    dpi: int = 300,
    show: bool = True,
    close: bool = False,
) -> tuple[plt.Figure, np.ndarray]:
    """
    Multi-panel monthly grid plot — 3 columns, as many rows as needed.

    One subplot per variable, one line per scenario.

    Parameters
    ----------
    names     : scenario stems to load and compare
    variables : list of column names to plot (one panel each)
    inp_names : display names for the legend (defaults to `names`)
    out_dir   : directory containing the parquet files
    savepath  : optional path to save the figure (.png / .pdf)
    dpi       : resolution when saving a raster image
    show      : call plt.show() after plotting
    close     : close the figure after saving/showing
    """
    legend_names = inp_names if inp_names is not None else names

    # 1. load monthly data for each scenario
    dfs = {name: load_monthly(name, out_dir=out_dir) for name in names}

    # 2. drop variables missing in any scenario
    missing = [v for v in variables if not all(v in df.columns for df in dfs.values())]
    if missing:
        print(f"Warning: skipping variables missing in at least one scenario: {missing}")
    variables = [v for v in variables if v not in missing]
    if not variables:
        raise ValueError("No valid variables to plot.")

    # 3. grid layout — always 3 columns
    ncols = 3
    nrows = math.ceil(len(variables) / ncols)
    n_slots = nrows * ncols

    # 4. colours — one per scenario, cycling through global COLORS
    colors = [_COLORS[i % len(_COLORS)] for i in range(len(names))]

    # 5. build figure
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12, 3.5 * nrows), sharex=True)
    axes = np.array(axes).reshape(-1)

    x = np.arange(1, 13)
    handles, labels = [], []

    for k, var in enumerate(variables):
        ax = axes[k]
        for j, (name, legend_name) in enumerate(zip(names, legend_names)):
            df = dfs[name]
            y = df[var].values / 1000        # MW → GW  (or MWh → GWh)
            line, = ax.plot(
                x, y,
                linewidth=2,
                linestyle=_LINESTYLES[j % len(_LINESTYLES)],
                color=colors[j],
                label=legend_name,
            )
            if legend_name not in labels:
                handles.append(line)
                labels.append(legend_name)

        ax.set_title(_labels.get(var, var))
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=3))

        if k % ncols == 0:
            ax.set_ylabel("Monthly avg. (GW / GWh)")

    # 6. x-axis ticks — numbered months, label on bottom row only
    bottom_row_start = (nrows - 1) * ncols
    for k, ax in enumerate(axes[:len(variables)]):
        ax.set_xticks(x)
        ax.set_xticklabels(x)
        if k >= bottom_row_start:
            ax.set_xlabel("Month")

    # 7. hide unused subplot slots
    for k in range(len(variables), n_slots):
        fig.delaxes(axes[k])

    # 8. legend always below the figure
    fig.legend(
        handles, labels,
        loc="lower center",
        ncol=min(len(labels), 4),
        bbox_to_anchor=(0.5, 0.0),
        frameon=True,
    )

    plt.tight_layout(rect=(0, 0.04, 1, 1))

    # 9. save
    if savepath is not None:
        savepath = Path(savepath)
        savepath.parent.mkdir(parents=True, exist_ok=True)
        skw = {"bbox_inches": "tight"}
        if savepath.suffix.lower() not in (".pdf", ".svg"):
            skw["dpi"] = dpi
        fig.savefig(savepath, **skw)

    if show:
        plt.show()
    if close:
        plt.close(fig)

    return fig, axes


# ==================== ==================== ==================== ====================
def plot_hourly(
    names: list[str],
    variables: list[str],
    *,
    inp_names: list[str] | None = None,
    out_dir: str | Path = DEFAULT_OUT_DIR,
    savepath: str | Path | None = None,
    dpi: int = 300,
    show: bool = True,
    close: bool = False,
) -> list[plt.Figure]:
    """
    One figure per variable, each showing hourly time-series for all scenarios.

    Parameters
    ----------
    names     : scenario stems to load and compare
    variables : list of column names to plot (one figure each)
    inp_names : display names for the legend (defaults to `names`)
    out_dir   : directory containing the parquet files
    savepath  : directory to save figures; files named <var>.png (or .pdf etc.)
    dpi       : resolution when saving a raster image
    show      : call plt.show() after each figure
    close     : close each figure after saving/showing
    """
    legend_names = inp_names if inp_names is not None else names

    # 1. load hourly data for each scenario
    dfs = {name: load_hourly(name, out_dir=out_dir) for name in names}

    # 2. drop variables missing in any scenario
    missing = [v for v in variables if not all(v in df.columns for df in dfs.values())]
    if missing:
        print(f"Warning: skipping variables missing in at least one scenario: {missing}")
    variables = [v for v in variables if v not in missing]
    if not variables:
        raise ValueError("No valid variables to plot.")

    # 3. colours — one per scenario, cycling through global COLORS
    colors = [_COLORS[i % len(_COLORS)] for i in range(len(names))]

    figs = []

    for var in variables:
        fig, ax = plt.subplots(figsize=(12, 5))

        for j, (name, legend_name) in enumerate(zip(names, legend_names)):
            df = dfs[name]
            ax.plot(
                df["hour"].values,
                df[var].values / 1000,
                linewidth=0.8,
                linestyle=_LINESTYLES[j % len(_LINESTYLES)],
                color=colors[j],
                label=legend_name,
                alpha=0.85,
            )

        ax.set_title(_labels.get(var, var))
        ax.set_xlabel("Hour")
        ax.set_ylabel("Hourly (GW / GWh)")
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=3))
        fig.legend(
            loc="lower center",
            ncol=min(len(names), 4),
            bbox_to_anchor=(0.5, 0.0),
            frameon=True,
        )
        plt.tight_layout(rect=(0, 0.06, 1, 1))

        if savepath is not None:
            p = Path(savepath) / f"{var}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            skw = {"bbox_inches": "tight"}
            if p.suffix.lower() not in (".pdf", ".svg"):
                skw["dpi"] = dpi
            fig.savefig(p, **skw)

        if show:
            plt.show()
        if close:
            plt.close(fig)

        figs.append(fig)

    return figs