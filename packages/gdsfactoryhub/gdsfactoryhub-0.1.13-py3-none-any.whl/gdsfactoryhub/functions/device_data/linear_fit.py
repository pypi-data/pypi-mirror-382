# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "gdsfactoryhub==0.1.13",
#     "matplotlib",
#     "pandas",
#     "numpy",
# ]
# ///


"""Fits a straight line."""

from typing import Any

import numpy as np
from matplotlib import pyplot as plt

import gdsfactoryhub as dd


def run(
    device_data_pkey: int,
    xname: str,
    yname: str,
    slopename: str = "",
    xlabel: str = "",
    ylabel: str = "",
) -> dict[str, Any]:
    """Fits a straight line through the data.

    Args:
        device_data_pkey: Primary key of the device data to use.
        xname: Name of the column to use for the x-axis.
        yname: Name of the column to use for the y-axis.
        slopename: Name of the slope to use in the output.
        xlabel: Label for the x-axis.
        ylabel: Label for the y-axis.

    """
    client = dd.create_client_from_env()
    api = client.api()
    query = client.query()

    data = query.device_data().eq("pk", device_data_pkey).limit(1).execute().data

    if not data:
        msg = f"Device data with pkey {device_data_pkey} not found."
        raise ValueError(msg)

    df = api.download_df(data[0]["data_file"]["path"])

    if xname not in df:
        msg = f"Device data with pkey {device_data_pkey} does not have a column named {xname!r}."
        raise ValueError(msg)

    if yname not in df:
        msg = f"Device data with pkey {device_data_pkey} does not have a column named {yname!r}."
        raise ValueError(msg)

    a, b = np.polyfit(df[xname].to_numpy(), df[yname].to_numpy(), deg=1)

    x = np.linspace(df[xname].to_numpy().min(), df[xname].to_numpy().max())
    plt.plot(df[xname].to_numpy(), df[yname].to_numpy(), label="measured")
    plt.plot(x, a * x + b, label=f"{slopename}: {a:.2e}")
    plt.xlabel(f"{xlabel or xname}")
    plt.ylabel(f"{ylabel or yname}")
    plt.title(f"{slopename.capitalize()} Plot")
    plt.grid(visible=True)
    plt.legend()

    return {
        "output": {
            slopename: float(a),
        },
        "summary_plot": plt.gcf(),
        "device_data_pkey": device_data_pkey,
    }
