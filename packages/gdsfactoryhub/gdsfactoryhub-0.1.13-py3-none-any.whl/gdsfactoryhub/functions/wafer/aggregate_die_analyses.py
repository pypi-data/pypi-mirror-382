# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "gdsfactoryhub==0.1.13",
#     "numpy",
#     "matplotlib",
#     "pandas",
#     "pyarrow",
# ]
# ///
"""Aggregate die analyses into a wafer map."""

from hashlib import md5
from typing import Any

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import gdsfactoryhub as gfh


def run(  # noqa: PLR0915,C901
    wafer_pkey: str,
    die_function_id: str,
    output_key: str,
    min_output: float,
    max_output: float,
):
    """Aggregate die analyses into a wafer map.

    Args:
        wafer_pkey (str): The primary key of the wafer.
        die_function_id (str): The function ID of the die analyses to aggregate.
        output_key (str): The key in the output dictionary to aggregate.
        min_output (float | None, optional): Minimum output value to include. Defaults to None.
        max_output (float | None, optional): Maximum output value to include. Defaults to None.

    """
    utils = gfh.create_client_from_env().utils()
    analyses = dict(utils.wafer().get_die_analyses(pk=wafer_pkey))
    analyses = {
        (int(x), int(y)): [a for a in as_ if a.function.function_id == die_function_id]
        for (x, y), as_ in analyses.items()
    }
    analyses = {k: (None if not v else v[0]) for k, v in analyses.items()}

    die_xys = np.array(sorted({(int(x), int(y)) for x, y in analyses}))
    die_xs = np.unique(die_xys[:, 0])
    die_ys = np.unique(die_xys[:, 1])
    die_x_min, die_x_max = min(die_xs), max(die_xs) + 1
    die_y_min, die_y_max = min(die_ys), max(die_ys) + 1
    nx = die_x_max - die_x_min
    ny = die_y_max - die_y_min
    X, Y = np.mgrid[die_x_min:die_x_max, die_y_min:die_y_max]

    data = np.full((nx, ny), fill_value=np.nan)
    fails = np.full((nx, ny), fill_value=False)
    exists = np.full((nx, ny), fill_value=False)
    toolow = np.full((nx, ny), fill_value=False)
    toohigh = np.full((nx, ny), fill_value=False)

    def set_value(
        x: int,
        y: int,
        *,
        value: float = np.nan,
        failed_pipeline: bool | None = None,
    ) -> None:
        exists[x - die_x_min, y - die_y_min] = True
        data[x - die_x_min, y - die_y_min] = value
        if value < min_output:
            toolow[x - die_x_min, y - die_y_min] = True
        if value > max_output:
            toohigh[x - die_x_min, y - die_y_min] = True
        if failed_pipeline is not None:
            fails[x - die_x_min, y - die_y_min] = failed_pipeline

    for (x, y), analysis in analyses.items():
        if analysis is None or analysis.status != "COMPLETED":
            set_value(x, y, failed_pipeline=True)
            continue
        output = ((analysis or {}).output or {}).get(output_key, np.nan)
        if np.isnan(output):
            set_value(x, y, failed_pipeline=True)
            continue
        set_value(x, y, value=output)

    fig = plt.figure(figsize=(10, 4.5))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1], height_ratios=[0.9, 0.1], wspace=0.3)

    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])
    cax = fig.add_subplot(gs[1, :])  # dedicated colorbar axis

    # pass-fail wafermap
    ax0.pcolor(X, Y, np.ma.masked_less(~exists, 1), hatch="//", edgecolor="C7", facecolor="none", linewidth=0.0, label="no data")  # fmt: skip # noqa: E501
    ax0.pcolor(X, Y, toolow, cmap=cmap_into_color("blue", 0.8))
    ax0.plot([], [], "s", c=get_color("blue", 0.8), label=f"too low [<{min_output:.2f}]")
    ax0.pcolor(X, Y, toohigh, cmap=cmap_into_color("red", 0.8))
    ax0.plot([], [], "s", c=get_color("red", 0.8), label=f"too high [>{max_output:.2f}]")
    ax0.pcolor(
        X,
        Y,
        exists & (~toolow) & (~toohigh) & (~fails),
        cmap=cmap_into_color("#00ff00", 0.8),
    )
    ax0.plot([], [], "s", c=get_color("#00ff00", 0.8), label="good")
    ax0.pcolor(X, Y, fails, cmap=cmap_into_color("red", 0.2))
    ax0.plot([], [], "s", c=(1, 0, 0, 0.2), label="failed pipeline")

    # values wafermap
    _im = ax1.pcolormesh(X, Y, data, vmin=min_output, vmax=max_output)
    # fig.colorbar(im, cax=cax, label=output_key)
    ax1.pcolor(X, Y, np.ma.masked_less(~exists, 1), hatch="//", edgecolor="C7", facecolor="none", linewidth=0.0)  # fmt: skip # noqa: E501
    ax1.pcolor(X, Y, fails, cmap=cmap_into_color("red", 0.2))

    # ticks, grid, aspect, labels — keep both wafer plots identical

    for a in (ax0, ax1):
        for i in range(nx):
            for j in range(ny):
                value = data[i, j]
                if not np.isnan(value):
                    a.text(
                        i + die_x_min,
                        j + die_y_min,
                        f"{value:.2f}",
                        ha="center",
                        va="center",
                        color="black",
                        fontsize=8,
                    )

        a.set_xticks(die_xs)
        a.set_xticks(0.5 * (die_xs[1:] + die_xs[:-1]), minor=True)
        a.set_yticks(die_ys)
        a.set_yticks(0.5 * (die_ys[1:] + die_ys[:-1]), minor=True)
        a.grid(visible=True, which="minor", ls=":")
        a.set_aspect("equal", adjustable="box")
        a.set_xlabel("die x")
        a.set_ylabel("die y")

        plt.suptitle(f"{output_key}")

    # pos = cax.get_position()
    # cax.set_position((pos.x0, pos.y0 - 0.2, pos.width, pos.height))
    custom_colorbar(analyses, output_key, min_output, max_output, ax=cax)
    pos = cax.get_position()
    cax.set_position((pos.x0, pos.y0 - 0.17, pos.width, pos.height))
    fig.legend(ncol=5, bbox_to_anchor=(0.9, -0.2))

    return {
        "output": {f"mean_{output_key}": np.nanmean(data)},
        "summary_plot": plt.gcf(),
        "wafer_pkey": wafer_pkey,
    }


def cmap_into_color(
    color: Any,  # noqa: ANN401
    alpha: float | None = None,
) -> mcolors.LinearSegmentedColormap:
    """Create a colormap going from transparent into the color."""
    r, g, b, a = get_color(color, alpha)
    name = md5(np.array([r * 255, g * 255, b * 255, a * 255], dtype=np.uint8).tobytes()).hexdigest()[:8]
    return mcolors.LinearSegmentedColormap.from_list(name, [(0, 0, 0, 0), (r, g, b, a)])


def get_color(
    color: Any,  # noqa: ANN401
    alpha: float | None = None,
) -> tuple[float, float, float, float]:
    """Get RGBA values from a color."""
    r, g, b, a = mcolors.to_rgba(color)
    if alpha is not None:
        a = alpha
    return r, g, b, a


def custom_colorbar(  # noqa: PLR0915,C901
    analyses: dict[tuple[int, int], Any],
    output_key: str,
    too_low: float,
    too_high: float,
    ax: Any = None,  # noqa: ANN401
) -> None:
    """Create a custom colorbar for the wafer plot."""
    if ax is None:
        ax = plt.gca()
    plt.sca(ax)

    df_metric = pd.DataFrame(
        [{"die_x": x, "die_y": y, output_key: v.output.get(output_key, np.nan)} for (x, y), v in analyses.items()]
    )

    arr = df_metric[output_key].to_numpy()
    xy = df_metric[["die_x", "die_y"]].to_numpy()
    sorter = np.argsort(arr)
    arr = arr[sorter]
    xy = [(int(x), int(y)) for x, y in xy[sorter]]

    width = too_high - too_low
    dwidth = width / 20
    arr_too_low = arr < too_low
    arr_too_high = arr > too_high
    arr_too_low2 = too_low - np.arange(1, sum(arr_too_low) + 1)[::-1] * dwidth
    arr_too_high2 = too_high + np.arange(1, sum(arr_too_high) + 1) * dwidth
    arr2 = np.concatenate([arr_too_low2, arr[(too_low <= arr) & (arr <= too_high)], arr_too_high2])
    for x in arr2:
        if x < too_low:
            plt.axvline(x, color="blue")
        elif x <= too_high:
            plt.axvline(x, color="#00ff00")
        else:
            plt.axvline(x, color="red")

    def _append_str(s: str, sa: str) -> str:
        """Append a string with coordinates."""
        if not s:
            return sa
        ss = s.split("\n")
        if ss[-1].count(";") >= 2 or "LIMIT" in ss[-1]:
            ss.append(sa)
        else:
            ss[-1] = f"{ss[-1]}; {sa}"
        return "\n".join(ss)

    dw = dwidth / 3
    ticks1 = {}
    ticks2 = {}
    prev = -np.inf
    for v1, v2, (x, y) in zip(arr, arr2, xy, strict=False):
        v1 = float(v1)
        v2 = float(v2)
        if prev < too_low <= v2:
            ticks1[too_low] = f"{too_low:.2f}"
            ticks2[too_low] = "< LOWER LIMIT"
            prev = too_low
        elif prev <= too_high < v2:
            ticks1[too_high] = f"{too_high:.2f}"
            ticks2[too_high] = "< UPPER LIMIT"
            prev = too_high
        elif np.abs(prev - v2) < dw:
            ticks2[prev] = _append_str(ticks2[prev], f"{x:.0f},{y:.0f}")
            continue
        ticks1[v2] = _append_str(ticks1.get(v2, ""), f"{v1:.2f}")
        ticks2[v2] = _append_str(ticks2.get(v2, ""), f"{x:.0f},{y:.0f}")
        prev = v2

    plt.axvline(too_low, color="black")
    plt.axvline(too_high, color="black")
    plt.xticks(*zip(*list(ticks1.items()), strict=False), rotation=60)
    plt.xlim(
        min(float(np.min(arr2)), too_low) - dwidth,
        max(float(np.max(arr2)), too_high) + dwidth,
    )
    ylim = plt.ylim()
    X, Y = np.mgrid[too_low:too_high:100j, ylim[0] : 2 * ylim[-1] - ylim[-2]]
    Z = (X - too_low) / (too_high - too_low)
    plt.pcolormesh(X, Y, Z)
    plt.yticks([])
    plt.xlabel("note: outliers are evenly spaced in the colorbar!", fontsize=6)
    plt.twiny()
    plt.xticks(*zip(*list(ticks2.items()), strict=False), rotation=90, fontsize=6)
    plt.xlim(
        min(float(np.min(arr2)), too_low) - dwidth,
        max(float(np.max(arr2)), too_high) + dwidth,
    )
