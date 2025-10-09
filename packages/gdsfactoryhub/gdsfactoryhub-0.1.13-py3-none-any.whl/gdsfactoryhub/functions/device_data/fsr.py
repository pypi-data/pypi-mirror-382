# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "gdsfactoryhub==0.1.13",
#     "matplotlib",
#     "numpy",
#     "orjson",
#     "pandas",
#     "scipy",
# ]
# ///
"""Free spectral range (FSR) analysis."""

from typing import Literal

import numpy as np
from matplotlib import pyplot as plt
from scipy import signal

import gdsfactoryhub as dd


def run(
    device_data_pkey: int,
    xname: str = "wavelength",
    yname: str = "power",
    peaks_direction: Literal["up", "down"] = "down",
    peaks_prominence: float | None = None,
    filter_cutoff: float = 0.05,
    filter_deg: int = 4,
):
    """Calculate the free spectral range (FSR) from device data.

    Args:
        device_data_pkey (int): Primary key of the device data.
        xname (str): Name of the x-axis column in the device data.
        yname (str): Name of the y-axis column in the device data.
        peaks_direction (Literal["up", "down"]): Direction of peaks to find.
        peaks_prominence (float | None): Prominence of peaks to find.
        filter_cutoff (float): Cutoff frequency for baseline removal filter.
        filter_deg (int): Degree of the polynomial for baseline removal.

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
        msg = f"Device data with pkey {device_data_pkey} does not have xname {xname!r}."
        raise ValueError(msg)

    if yname not in df:
        msg = f"Device data with pkey {device_data_pkey} does not have yname {yname!r}."
        raise ValueError(msg)

    x = df[xname].to_numpy()
    y_raw = df[yname].to_numpy()
    y = _remove_baseline(x, y_raw, filter_cutoff=filter_cutoff, filter_deg=filter_deg)

    if peaks_direction == "up":
        peaks, _ = signal.find_peaks(y, prominence=peaks_prominence)
    elif peaks_direction == "down":
        peaks, _ = signal.find_peaks(-y, prominence=peaks_prominence)
    else:
        msg = f"Invalid peaks_direction {peaks_direction!r}. Choose 'up' or 'down'."
        raise ValueError(msg)

    if not peaks.any():
        msg = f"No peaks found for device data with pkey {device_data_pkey}"
        raise ValueError(msg)

    if len(peaks) < 2:
        msg = f"Only one peak found for device data with pkey {device_data_pkey}"
        raise ValueError(msg)

    peak_frequencies = x[peaks]
    fsr = np.diff(peak_frequencies)
    fsr_mean = float(np.mean(fsr))
    fsr_std = float(np.std(fsr))

    plt.plot(x, y_raw, label="spectrum")
    plt.plot(x[peaks], y_raw[peaks], ls="none", marker="x", color="red", label="peaks")
    plt.xlabel(f"{xname}")
    plt.ylabel(f"{yname}")
    plt.title(f"FSR: {fsr_mean:.2e} ± {fsr_std:.2e} nm")
    plt.legend()

    return {
        "output": {
            "fsr_mean": fsr_mean,
            "fsr_std": fsr_std,
            "peaks": [float(xx) for xx in x[peaks]],
            "fsr": [float(f) for f in fsr],
        },
        "summary_plot": plt.gcf(),
        "device_data_pkey": device_data_pkey,
    }


def _filter_signal(x: np.ndarray, y: np.ndarray, cutoff: float = 0.05, order: int = 4) -> np.ndarray:
    step = (x[1:] - x[:-1]).mean()
    fs = 1 / step
    filt = signal.butter(order, cutoff / (0.5 * fs), btype="low")
    if filt is None:
        msg = "Filter coefficients are None, check the cutoff frequency and order."
        raise RuntimeError(msg)
    yf = signal.filtfilt(filt[0], filt[1], y)
    return yf


def _remove_baseline(x: np.ndarray, y: np.ndarray, *, filter_cutoff: float = 0.05, filter_deg: int = 4) -> np.ndarray:
    yf = _filter_signal(x, y, cutoff=filter_cutoff, order=filter_deg)
    yb = y - yf
    return yb
