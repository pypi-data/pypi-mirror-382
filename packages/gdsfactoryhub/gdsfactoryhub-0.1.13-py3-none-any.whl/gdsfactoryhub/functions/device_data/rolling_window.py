# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "gdsfactoryhub==0.1.13",
#     "pandas",
#     "matplotlib",
#     "numpy",
# ]
# ///
"""Calculate the power envelope of a signal."""

from typing import Any, cast

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import gdsfactoryhub as dd


def run(
    device_data_pkey: str,
    xname: str,
    yname: str,
    x0: float | None = None,
    window: int | None = None,
    apply_times: int = 2,
    xlabel: str = "",
    ylabel: str = "",
) -> dict[str, Any]:
    """Calculate the power envelope of a signal.

    Args:
        device_data_pkey: the primary key of the data to work with
        xname: the x-column name
        yname: the y-column name
        x0: the x-value at which to store the metrics
        window: the window size of the convolution kernel
        apply_times: how many times the window is applied (more = smoother)
        xlabel: the x-label for the x-axis
        ylabel: the y-label for the y-axis

    """
    utils = dd.create_client_from_env().utils()
    data = utils.device_data().get_as_dataframe(device_data_pkey)

    if apply_times < 1:
        msg = "apply_times should be at least 1."
        raise ValueError(msg)

    if data is None:
        msg = f"Device data with pkey {device_data_pkey} not found."
        raise ValueError(msg)

    if xname not in data:
        msg = f"Device data with pkey {device_data_pkey} does not have a column named {xname!r}."
        raise ValueError(msg)

    if yname not in data:
        msg = f"Device data with pkey {device_data_pkey} does not have a column named {yname!r}."
        raise ValueError(msg)

    x = cast(pd.Series, data[xname])
    y = cast(pd.Series, data[yname])
    window = window or x.shape[0] // 10

    low = cast(pd.Series, y.rolling(window, center=True).min())
    mean = cast(pd.Series, y.rolling(window, center=True).mean())
    high = cast(pd.Series, y.rolling(window, center=True).max())

    for _ in range(1, apply_times):
        low = cast(pd.Series, low.rolling(window, center=True).mean())
        mean = cast(pd.Series, mean.rolling(window, center=True).mean())
        high = cast(pd.Series, high.rolling(window, center=True).mean())

    if x0 is not None:  # noqa: SIM108
        idx = int(np.argmin(np.abs(x - x0)))
    else:
        idx = int(np.argmax(high))

    plt.plot(x, y, label="signal", zorder=0)
    plt.plot(x, low, label="low", zorder=1)
    plt.plot(x, mean, label="mean", zorder=2)
    plt.plot(x, high, label="high", zorder=3)

    plt.xlabel(xlabel or xname)
    plt.ylabel(ylabel or yname)
    plt.grid(visible=True)
    plt.legend()
    plt.title(f"Envelope with Window Size {window}")

    return {
        "output": {
            xname: float(x[idx]),
            f"{yname}_low": float(low[idx]),
            f"{yname}_mean": float(mean[idx]),
            f"{yname}_high": float(high[idx]),
        },
        "summary_plot": plt.gcf(),
        "device_data_pkey": device_data_pkey,
    }
