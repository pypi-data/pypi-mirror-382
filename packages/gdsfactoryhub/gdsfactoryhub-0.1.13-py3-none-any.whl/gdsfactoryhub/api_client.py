"""API client for DoData SDK."""

import datetime
import io
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
from PIL import Image
from PIL.ImageFile import ImageFile

from gdsfactoryhub import helpers
from gdsfactoryhub.errors import DoDataError
from gdsfactoryhub.helpers import get_bytes
from gdsfactoryhub.schemas import (
    AnalysisExecutionRequest,
    DeviceDataType,
    ExtractionRule,
    FunctionRunResult,
    FunctionTargetModel,
    PlotSpec,
    Project,
)


class ApiClient:
    """API client for DoData SDK."""

    def __init__(self, api_url: str, key: str, *, project_id: str = "") -> None:
        """Initialize the API client."""
        if not api_url:
            msg = "api_url is required"
            raise DoDataError(msg)
        if not key:
            msg = "key is required"
            raise DoDataError(msg)

        self.api_url = api_url.rstrip("/")
        self.key = key
        self.project_id = project_id

    def _create_httpx_client(self) -> httpx.Client:
        return httpx.Client(
            timeout=httpx.Timeout(30.0, read=None), auth=helpers.APIHttpxAuth(self.key), follow_redirects=True
        )

    def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Response:  # noqa: ANN401
        url = f"{self.api_url}{endpoint}"

        with self._create_httpx_client() as client:
            response = client.request(method, url, **kwargs)
            self._raise_for_status(response)
            return response

    def _raise_for_status(self, response: httpx.Response) -> httpx.Response:
        if httpx.codes.is_error(response.status_code):
            raise DoDataError(response.text)
        return response

    def create_project(
        self,
        *,
        eda_layout_file: str | Path | bytes,
        description: str | None = None,
        extraction_rules: Iterable[ExtractionRule] = (),
        project_id: str = "",
    ) -> Project:
        """Create a new project with the given parameters."""
        response = self._make_request(
            "POST",
            "/api/sdk/create-project",
            params={
                "project_id": project_id or self.project_id,
                "description": description,
                "extraction_rules": json.dumps([rule.model_dump(mode="json") for rule in extraction_rules]),
            },
            files={
                # TODO: handle .oas as well.
                "eda_layout_file": ("layout.gds", get_bytes(eda_layout_file)),
            },
        )
        return Project.model_validate(response.json())

    def delete_project(self, *, project_id: str = "") -> None:
        """Delete a project by its ID."""
        self._make_request("DELETE", "/api/sdk/delete-project", params={"project_id": project_id or self.project_id})

    def upload_wafer_definitions(
        self,
        *,
        wafer_definitions_file: str | Path | bytes,
        project_id: str = "",
    ) -> str:
        """Upload wafer definitions for a project."""
        response = self._make_request(
            "PUT",
            "/api/sdk/upload-wafer-definitions",
            params={"project_id": project_id or self.project_id},
            files={
                "wafer_definitions_file": ("wafer_definitions.json", get_bytes(wafer_definitions_file)),
            },
        )
        return response.text

    def upload_design_manifest(
        self,
        *,
        design_attributes_file: str | Path | bytes,
        project_id: str = "",
    ) -> str:
        """Upload design attributes for a project."""
        response = self._make_request(
            "PUT",
            "/api/sdk/update-design-attributes",
            params={"project_id": project_id or self.project_id},
            files={
                "design_attributes_file": ("design_attributes.csv", get_bytes(design_attributes_file)),
            },
        )
        return response.text

    def download_design_manifest(
        self,
        *,
        file_path: str | Path | None = None,
        project_id: str = "",
    ) -> bytes:
        """Download design attributes for a project."""
        response = self._make_request(
            "GET",
            "/api/sdk/download-design-attributes",
            params={"project_id": project_id or self.project_id},
        )
        if file_path is not None:
            file_path = Path(file_path).resolve()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(response.content)
        return response.content

    def _add_device_data(
        self,
        *,
        device_id: str,
        data_file: str | Path | bytes | pd.DataFrame,
        data_type: DeviceDataType,
        plot_spec: PlotSpec | None = None,
        wafer_id: str | None = None,
        die_x: int | None = None,
        die_y: int | None = None,
        acquired_time: datetime.datetime | None = None,
        attributes: dict | None = None,
        project_id: str = "",
    ) -> dict[str, Any]:
        """Add device data to a project."""
        params = {"project_id": project_id or self.project_id, "device_id": device_id, "data_type": data_type}
        if plot_spec:
            params["plotting_settings"] = json.dumps(plot_spec.model_dump(mode="json", exclude_unset=True))
        if wafer_id is not None:
            params["wafer_id"] = wafer_id
        if die_x is not None:
            params["die_x"] = die_x
        if die_y is not None:
            params["die_y"] = die_y
        if acquired_time is not None:
            params["acquired_time"] = acquired_time
        if attributes is not None:
            params["attributes"] = json.dumps(attributes)

        response = self._make_request(
            "POST",
            "/api/sdk/add-device-data",
            params=params,
            files={
                "data_file": get_bytes(data_file),
            },
        )
        return response.json()

    def add_measurement(
        self,
        *,
        device_id: str,
        data_file: str | Path | bytes | pd.DataFrame,
        plot_spec: PlotSpec | None = None,
        wafer_id: str | None = None,
        die_x: int | None = None,
        die_y: int | None = None,
        acquired_time: datetime.datetime | None = None,
        attributes: dict | None = None,
        project_id: str = "",
    ) -> dict[str, Any]:
        """Add measurement data to a device."""
        return self._add_device_data(
            project_id=project_id,
            device_id=device_id,
            data_file=data_file,
            data_type=DeviceDataType.MEASUREMENT,
            plot_spec=plot_spec,
            wafer_id=wafer_id,
            die_x=die_x,
            die_y=die_y,
            acquired_time=acquired_time,
            attributes=attributes,
        )

    def add_simulation(
        self,
        *,
        device_id: str,
        data_file: str | Path | bytes | pd.DataFrame,
        plot_spec: PlotSpec | None = None,
        wafer_id: str | None = None,
        die_x: int | None = None,
        die_y: int | None = None,
        acquired_time: datetime.datetime | None = None,
        attributes: dict | None = None,
        project_id: str = "",
    ) -> dict[str, Any]:
        """Add simulation data to a device."""
        return self._add_device_data(
            project_id=project_id,
            device_id=device_id,
            data_file=data_file,
            data_type=DeviceDataType.SIMULATION,
            plot_spec=plot_spec,
            wafer_id=wafer_id,
            die_x=die_x,
            die_y=die_y,
            acquired_time=acquired_time,
            attributes=attributes,
        )

    def validate_function(
        self,
        *,
        function_id: str,  # noqa: ARG002
        target_model: FunctionTargetModel,  # noqa: ARG002
        test_target_model_pk: str,  # noqa: ARG002
        file: str | Path | bytes,  # noqa: ARG002
        test_kwargs: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> FunctionRunResult:
        """Validate a user function."""
        msg = "This function is deprecated. Use upload_function instead."
        raise DoDataError(msg)

    def upload_function(
        self,
        *,
        function_id: str,
        target_model: FunctionTargetModel,
        test_target_model_pk: str,
        file: str | Path | bytes,
        test_kwargs: dict[str, Any] | None = None,
    ) -> FunctionRunResult:
        """Upload a user function."""
        response = self._make_request(
            "POST",
            "/api/sdk/upload-function",
            params={
                "function_id": function_id,
                "target_model": target_model,
                "test_target_model_pk": test_target_model_pk,
                "test_kwargs": json.dumps(test_kwargs) if test_kwargs else None,
            },
            files={"file": helpers.get_bytes(file)},
        )

        return response.json()

    def delete_function(self, *, function_id: str = "") -> None:
        """Delete a function by its ID."""
        self._make_request("DELETE", "/api/sdk/delete-function", params={"function_id": function_id})

    def start_analysis(
        self,
        *,
        analysis_id: str,
        function_id: str,
        target_model: FunctionTargetModel,
        target_model_pk: str,
        kwargs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run an analysis."""
        response = self._make_request(
            "POST",
            "/api/sdk/run-analysis",
            params={
                "analysis_id": analysis_id,
                "function_id": function_id,
                "target_model": target_model,
                "target_model_pk": target_model_pk,
                "parameters": json.dumps(kwargs) if kwargs else None,
            },
        )

        return response.json()

    def start_multiple_analyses(self, *, analyses_requests: list[AnalysisExecutionRequest]) -> list[dict[str, Any]]:
        """Run an analysis."""
        response = self._make_request(
            "POST",
            "/api/sdk/run-multiple-analyses",
            content=json.dumps([r.model_dump(mode="json") for r in analyses_requests]),
        )

        return response.json()

    def download_file(self, path: str) -> bytes:
        """Download a file from the server."""
        response = self._make_request("GET", "/api/sdk/medias", params={"path": path})
        return response.content

    def download_df(self, path: str) -> pd.DataFrame:
        """Download a DataFrame from the server."""
        return helpers.df_from_bytes(self.download_file(path))

    def download_plot(self, path: str) -> ImageFile:
        """Download a plot image from the server."""
        return Image.open(io.BytesIO(self.download_file(path)))


def create_api_client(api_url: str, key: str, *, project_id: str = "") -> ApiClient:
    """Create an instance of the DoData API client."""
    return ApiClient(api_url, key, project_id=project_id)
