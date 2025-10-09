# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "gdsfactoryhub==0.1.13",
#     "matplotlib",
#     "numpy",
# ]
# ///
"""Aggregate device analyses for a specific die."""

from typing import Any

import matplotlib.pyplot as plt
import numpy as np

import gdsfactoryhub as dd

client = dd.create_client_from_env()
api = client.api()
query = client.query()


def run(
    die_pkey: int,
    device_data_function_id: str,
    output_key: str,
    device_attributes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Aggregate device analyses for a specific die.

    Args:
        die_pkey (int): Primary key of the die to filter analyses.
        device_data_function_id (str): Function ID for device data.
        output_key (str): Key in the analysis output to aggregate.
        device_attributes (dict[str, Any], optional): Attributes to filter devices.

    """
    device_attributes = device_attributes or {}

    analyses = (
        query.analyses()
        .not_.is_("device_data", "null")
        .not_.is_("device_data.die", "null")
        .eq("function.function_id", device_data_function_id)
        .eq("device_data.die.pk", die_pkey)
        .execute()
        .data
    )
    filtered_analyses = [d for d in analyses if _filter_fn(d, **device_attributes)]

    data = {}
    for analysis in filtered_analyses:
        data[analysis["device_data"]["device"]["device_id"]] = analysis["output"][output_key]

    values = np.array(list(data.values()))
    ymin = max(int(np.min(values)), 0.0)
    ymax = round(np.max(values) + 0.5)
    plt.figure(figsize=(8, 4))
    plt.bar(list(data), list(data.values()))
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Value")
    plt.ylim(ymin, ymax)
    plt.title("RingDouble Values")

    return {
        "output": {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "median": float(np.median(values)),
        },
        "summary_plot": plt.gcf(),
        "die_pkey": die_pkey,
    }


def _filter_fn(analysis: dict, **attributes: dict[str, float]) -> bool:
    device_attributes = analysis["device_data"]["device"]["cell"]["attributes"]
    for k, v in attributes.items():
        if k not in device_attributes:
            return False
        if not np.isclose(device_attributes[k], v):  # type: ignore[reportArgumentType]
            return False
    return True
