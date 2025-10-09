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


"""Calculates loss per component."""

from typing import Any

import numpy as np
from matplotlib import pyplot as plt

import gdsfactoryhub as dd

client = dd.create_client_from_env()
api = client.api()
query = client.query()


def run(die_pkey: int, yname: str = "output_power") -> dict[str, Any]:
    """Loss per component in cutback structures.

    Args:
        die_pkey: Primary key of the die to analyze.
        yname: Name of the column in the data file that contains the output power.

    """
    datas = query.device_data().not_.is_("die", "null").eq("die.pk", die_pkey).execute().data

    dfs = [api.download_df(d["data_file"]["path"]) for d in datas]
    num_comps = [d["device"]["cell"]["attributes"]["components"] for d in datas]
    powers = [df[yname].max() for df in dfs]

    a, b = np.polyfit(num_comps, powers, deg=1)
    x = np.arange(0, max(num_comps) + 99, 100)
    plt.scatter(num_comps, powers, color="C1")
    plt.plot(x, a * x + b, color="C0")
    plt.grid(visible=True)
    plt.xlim(x.min() - 30, x.max() + 30)
    plt.title(f"loss = {-a:.2e} dB/component")
    plt.xlabel("# components")
    plt.ylabel("Power [dBm]")
    plt.show()

    return {
        "output": {"component_loss": -a, "insertion_loss": -b},
        "summary_plot": plt.gcf(),
        "die_pkey": die_pkey,
    }
