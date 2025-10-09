# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "gdsfactoryhub==0.1.13",
#     "matplotlib",
#     "orjson",
#     "pandas",
#     "numpy",
# ]
# ///


"""Calculates propagation loss from cutback measurement."""

from typing import Any

import numpy as np
from matplotlib import pyplot as plt

import gdsfactoryhub as dd

client = dd.create_client_from_env()
api = client.api()
query = client.query()


def run(
    die_pkey: int,
    yname: str = "output_power",
    xlabel: str = "",
    ylabel: str = "",
    device_attributes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Propagation loss in dB/cm.

    Args:
        die_pkey: The primary key of the die.
        yname: The name of the column in the device data to use for power.
        xlabel: Label for the x-axis (optional).
        ylabel: Label for the y-axis (optional).
        device_attributes: Attributes to filter device data (optional).

    """
    device_attributes = device_attributes or {}
    datas = query.device_data().not_.is_("die", "null").eq("die.pk", die_pkey).execute().data
    filtered_datas = [d for d in datas if _filter_fn(d, **device_attributes)]
    dfs = [api.download_df(d["data_file"]["path"]) for d in filtered_datas]

    if not dfs:
        msg = f"No device data found with die_pkey {die_pkey} and attributes {device_attributes}."
        raise ValueError(msg)

    powers = []
    lengths_um = []

    for device_data, df in zip(filtered_datas, dfs, strict=True):
        _attributes = device_data["device"]["cell"]["attributes"]
        lengths_um.append(_attributes.get("length_um"))
        power = df[yname].max()
        powers.append(power)

    p = np.polyfit(lengths_um, powers, 1)
    propagation_loss = -p[0] * 1e4
    Ls = np.linspace(np.min(lengths_um), np.max(lengths_um))

    plt.scatter(lengths_um, powers, marker="o", color="C1")
    plt.plot(Ls, np.polyval(p, Ls), label="fit", color="C0")

    plt.xlabel(xlabel or "Length [um]")
    plt.ylabel(ylabel or "Power")
    plt.grid(visible=True)
    plt.title(f"Propagation loss: {propagation_loss:.2e} dB/cm ")

    return {
        "output": {"propagation_loss": propagation_loss, "insertion_loss": -p[1]},
        "summary_plot": plt.gcf(),
        "die_pkey": die_pkey,
    }


def _filter_fn(device_data: dict[str, Any], **attributes: dict[str, float]) -> bool:
    device_attributes = device_data["device"]["cell"]["attributes"]
    for k, v in attributes.items():
        if k not in device_attributes:
            return False
        if not np.isclose(device_attributes[k], v):  # type: ignore[reportArgumentType]
            return False
    return True
