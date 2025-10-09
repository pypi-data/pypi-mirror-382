"""Dodata helpers module."""

import io
import json
import sys
import warnings
from collections.abc import Callable, Generator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, suppress
from functools import wraps
from importlib import import_module
from multiprocessing import cpu_count
from pathlib import Path
from types import ModuleType
from typing import TypeVar, cast

import httpx
import orjson
import pandas as pd
from tqdm import tqdm as _tqdm

from gdsfactoryhub.errors import DoDataError


@contextmanager
def suppress_api_error() -> Generator[None, None, None]:
    """Context manager to suppress DoDataError and print the error message."""
    try:
        yield
    except DoDataError as e:
        try:
            msg = json.loads(f"{e}")["detail"]
        except Exception:
            raise e  # noqa: B904
        sys.stderr.write(f"{msg}\n")


A = TypeVar("A")
B = TypeVar("B")


def parallel(f: Callable[[A], B], *, items: list[A], n_workers: int | None = None) -> list[B]:
    """Run a function in parallel over a list of items."""
    pb = tqdm(total=len(items))

    def _func(item: A) -> B:
        pb.update(1)
        return f(item)

    with ThreadPoolExecutor(n_workers or cpu_count()) as ex:
        r = ex.map(_func, items)

    return list(r)


def get_function_path(func: Callable) -> Path:
    """Get the file path of a function."""
    module_str = getattr(func, "__module__", "")
    if not module_str or module_str == "__main__":
        msg = f"The function {func} has no associated path."
        raise FileNotFoundError(msg)
    module = import_module(module_str)
    return get_module_path(module)


def get_module_path(module: ModuleType) -> Path:
    """Get the file path of a module."""
    path = getattr(module, "__file__", "")
    if not path:
        msg = f"The module {module} has no associated path."
        raise FileNotFoundError(msg)
    return Path(path).resolve()


class APIHttpxAuth(httpx.Auth):
    """HTTPX authentication class for API key."""

    def __init__(self, api_key: str) -> None:
        """Initialize the APIHttpxAuth with an API key."""
        self.api_key = api_key

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, None, None]:
        """Add the API key to the request headers."""
        request.headers["api-key"] = self.api_key
        yield request


@wraps(_tqdm)
def tqdm(*args, **kwargs):  # noqa: ANN002,ANN003,ANN201
    """Create a tqdm progress bar."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        from tqdm.autonotebook import tqdm
    return tqdm(*args, **kwargs)


def get_bytes(file_obj: str | Path | bytes | pd.DataFrame) -> bytes:
    """Get a file object for an HTTP request."""
    if isinstance(file_obj, pd.DataFrame):
        buf = io.BytesIO()
        cast(pd.DataFrame, file_obj).to_parquet(buf)
        file_obj = buf.getvalue()
    if isinstance(file_obj, str) and "\n" in file_obj:
        file_obj = file_obj.encode()
    if isinstance(file_obj, bytes):
        return file_obj
    return Path(file_obj).read_bytes()


def df_from_bytes(bts: bytes) -> pd.DataFrame:
    """Convert bytes to a DataFrame."""
    if isinstance(bts, str):
        bts = bts.encode()  # should not happen, but just in case

    # Try Parquet
    if bts.startswith(b"PAR1"):
        with suppress(Exception):
            return pd.read_parquet(io.BytesIO(bts))

    # Try JSON
    with suppress(Exception):
        return pd.DataFrame(**orjson.loads(bts))

    # Try CSV
    with suppress(Exception):
        df = pd.read_csv(io.BytesIO(bts))
        df = df.reset_index(drop=True)
        return df

    msg = "Could not convert bytes to DataFrame. Given bytes should be valid parquet, json or csv."
    raise TypeError(msg)
