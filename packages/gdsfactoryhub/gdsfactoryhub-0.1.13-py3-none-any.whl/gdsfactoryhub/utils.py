"""Utilities for interacting with the DoData API."""

import time
import uuid
from collections.abc import Iterable
from itertools import batched
from typing import Any

import pandas as pd
from tenacity import Retrying, stop_after_attempt, wait_exponential
from tqdm.auto import tqdm

from gdsfactoryhub import helpers
from gdsfactoryhub.api_client import ApiClient
from gdsfactoryhub.errors import DoDataError
from gdsfactoryhub.query_client import QueryClient
from gdsfactoryhub.schemas import Analysis, AnalysisExecutionRequest, DeviceData, Function


class AnalysisUtils:
    """Utility class for handling analyses."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client

    def wait_for_completion(
        self, pks: list[str | uuid.UUID], poll_interval: float = 1.0, query_batch_size: int = 100
    ) -> None:
        """Wait until all given analyses complete, showing a progress bar."""
        query_retry_policy = Retrying(
            stop=stop_after_attempt(5),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            reraise=True,
        )

        count = len(pks)

        with tqdm(total=count, desc="Waiting for analyses") as pbar:
            completed = set()

            while len(completed) < count:
                new_completed = set()

                for batch in batched(pks, query_batch_size):
                    for attempt in query_retry_policy:
                        with attempt:
                            rows = (
                                self._query_client.table("analyses")
                                .select("pk", "status")
                                .in_("pk", batch)
                                .execute()
                                .data
                            )
                    new_completed = new_completed.union({row["pk"] for row in rows if row["status"] != "RUNNING"})
                    time.sleep(0.1)

                delta = len(new_completed - completed)

                if delta > 0:
                    pbar.update(delta)
                    completed = new_completed
                time.sleep(poll_interval)

    def run_analyses_in_batches(
        self,
        analyses_requests: list[AnalysisExecutionRequest],
        max_batch_size: int = 100,
        poll_interval: float = 1.0,
        low_watermark: float = 0.2,
    ) -> list[str]:
        """Run analyses in controlled batches.

        Args:
            analyses_requests: List of AnalysisExecutionRequest objects.
            max_batch_size: Max number of requests per batch (default: 100).
            poll_interval: Time to wait between status checks (seconds).
            low_watermark: Fraction of max_batch_size at or below which to
                           launch the next batch (default: 0.2 = 20%).

        Returns:
            List of completed PKs

        """
        if not analyses_requests:
            return []
        total = len(analyses_requests)
        completed: set[str] = set()
        running: set[str] = set()

        batch_iter = iter(batched(analyses_requests, max_batch_size))
        next_batch = next(batch_iter)

        query_retry_policy = Retrying(
            stop=stop_after_attempt(5),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            reraise=True,
        )

        threshold = max(1, int(low_watermark * max_batch_size))

        with tqdm(total=total, desc="Analyses") as pbar:
            while len(completed) < total:
                for attempt in query_retry_policy:
                    with attempt:
                        # query statuses for running PKs
                        total_running_analysis = (  # for the whole organization
                            self._query_client.table("analyses")
                            .select("count()")
                            .eq("status", "RUNNING")
                            .single()
                            .execute()
                            .data["count"]
                        )
                        new_done = {
                            x["pk"]
                            for x in self._query_client.table("analyses")
                            .select("pk")
                            .not_.eq("status", "RUNNING")
                            .in_("pk", running)
                            .execute()
                            .data
                        }

                        if new_done:
                            completed |= new_done
                            running -= new_done
                            pbar.update(len(new_done))

                        # if total_running_analysis count <= threshold, load next batch
                        if next_batch and total_running_analysis <= threshold:
                            try:
                                result = self._api_client.start_multiple_analyses(analyses_requests=next_batch)
                                running |= {analysis["pk"] for analysis in result}
                                next_batch = next(batch_iter)
                            except StopIteration:
                                next_batch = None  # no more batches left

                        time.sleep(poll_interval)

        return list(completed)


class DeviceDataUtils:
    """Utility class for handling device data."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client

    def wait_for_plot_completion(
        self, pk: str | uuid.UUID, poll_interval: float = 1.0, *, verbose: bool = True
    ) -> None:
        """Wait until a device_data plot is completed."""
        first_check = True
        check_count = 0
        dot_frequency = 5  # Print dot every 5 checks
        while True:
            row = self._query_client.table("device_data").select("pk, plot_status").eq("pk", pk).single().execute().data
            if not row:
                msg = f"No device data found for pk: {pk}"
                raise DoDataError(msg)

            status = row.get("plot_status")
            if status != "RUNNING":
                if verbose:
                    print("\n✅ Plot completed")  # noqa: T201
                return

            if first_check:
                print("⏳ Still running", end="", flush=True)  # noqa: T201
                first_check = False
            else:
                check_count += 1
                if check_count % dot_frequency == 0:
                    print(".", end="", flush=True)  # noqa: T201
            time.sleep(poll_interval)

    def get_as_dataframe(self, pk: str | uuid.UUID) -> pd.DataFrame:
        """Fetch device data as a pandas DataFrame."""
        res = self._query_client.table("device_data").select("data_file").eq("pk", str(pk)).execute()

        if not res.data:
            msg = f"No device data found for pk: {pk}"
            raise DoDataError(msg)

        if not res.data[0]["data_file"]:
            msg = f"No data file found for device data with pk: {pk}"
            raise DoDataError(msg)

        device_data_file_content = self._api_client.download_file(res.data[0]["data_file"]["path"])

        return helpers.df_from_bytes(device_data_file_content)


class FunctionUtils:
    """Utility class for handling functions."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client

    def wait_for_test_completion(self, pk: str | uuid.UUID, poll_interval: float = 1.0) -> Function:
        """Wait until a function test is completed."""
        first_check = True
        check_count = 0
        dot_frequency = 5  # Print dot every 5 checks
        while True:
            row = self._query_client.table("functions").select("pk, status").eq("pk", pk).single().execute().data
            if not row:
                msg = f"No function found for pk: {pk}"
                raise DoDataError(msg)

            status = row.get("status")
            if status != "RUNNING":
                print("\n✅ Test completed")  # noqa: T201
                return Function.model_validate(self._query_client.functions().eq("pk", pk).single().execute().data)

            if first_check:
                print("⏳ Still running", end="", flush=True)  # noqa: T201
                first_check = False
            else:
                check_count += 1
                if check_count % dot_frequency == 0:
                    print(".", end="", flush=True)  # noqa: T201
            time.sleep(poll_interval)


class DieUtils:
    """Utility class for handling die data."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client
        self._device_data_utils: DeviceDataUtils = DeviceDataUtils(api_client, query_client)

    def get_device_data_objects(self, pk: str | uuid.UUID) -> list[tuple[DeviceData, pd.DataFrame]]:
        """Fetch device data objects for a given die."""
        res = self._query_client.device_data().eq("die_pk", str(pk)).execute()
        if not res.data:
            msg = f"No device data found for die: {pk}"
            raise DoDataError(msg)

        device_data_objects = []
        for device_data_dict in res.data:
            device_data = DeviceData.model_validate(device_data_dict)
            df = self._device_data_utils.get_as_dataframe(device_data.pk)
            device_data_objects.append((device_data, df))
        return device_data_objects


class WaferUtils:
    """Utility class for handling wafer data."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client

    def get_die_analyses(
        self, pk: str | uuid.UUID, filter_clauses: Iterable[tuple[str, str, Any]] = ()
    ) -> dict[tuple[float, float], list[Analysis]]:
        """Fetch analyses for all dies on a wafer."""
        base_query = self._query_client.analyses().not_.is_("die", None).eq("die.wafer.pk", str(pk))
        for column, operator, value in filter_clauses:
            base_query = base_query.filter(column, operator, value)
        res = base_query.execute()
        if not res.data:
            msg = f"No die analyses found for wafer: {pk}"
            raise DoDataError(msg)
        analyses_per_die: dict[tuple[float, float], list[Analysis]] = {}
        for data in res.data:
            analysis = Analysis.model_validate(data)
            die = analysis.die
            if die is not None:
                key = (die.x, die.y)
                if key not in analyses_per_die:
                    analyses_per_die[key] = []
                analyses_per_die[key].append(analysis)
        return analyses_per_die


class CommonUtils:
    """Utility class for common operations."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client

    def display_remote_image(self, file_path: str) -> None:
        """Display an image from a remote file path."""
        from IPython.display import Image, display

        file_bytes = self._api_client.download_file(file_path)
        display(Image(data=file_bytes))


class Utils:
    """Main utility class for accessing various utility functions."""

    def __init__(self, api_client: ApiClient, query_client: QueryClient) -> None:
        """Initialize with API and Query clients."""
        self._api_client = api_client
        self._query_client = query_client

    def function(self) -> FunctionUtils:
        """Return an instance of FunctionUtils."""
        return FunctionUtils(self._api_client, self._query_client)

    def analyses(self) -> AnalysisUtils:
        """Return an instance of AnalysisUtils."""
        return AnalysisUtils(self._api_client, self._query_client)

    def device_data(self) -> DeviceDataUtils:
        """Return an instance of DeviceDataUtils."""
        return DeviceDataUtils(self._api_client, self._query_client)

    def die(self) -> DieUtils:
        """Return an instance of DieUtils."""
        return DieUtils(self._api_client, self._query_client)

    def wafer(self) -> WaferUtils:
        """Return an instance of WaferUtils."""
        return WaferUtils(self._api_client, self._query_client)

    def common(self) -> CommonUtils:
        """Return an instance of CommonUtils."""
        return CommonUtils(self._api_client, self._query_client)
