"""Defines the data models for the application, including device data, wafers, dies, cells, and projects."""

import base64
import datetime
import uuid
from enum import StrEnum
from typing import Annotated, Any, Optional

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt


class ExtractionRule(BaseModel):
    """Defines a rule for filtering cells."""

    cell_name: str | None = None  # Exact cell name to target (None/empty means all top cells)
    min_depth: NonNegativeInt = 0
    max_depth: PositiveInt | None = None  # None means no max limit (process all depths)
    include_patterns: list[str] = []  # List of regex patterns to explicitly include
    exclude_patterns: list[str] = []  # List of regex patterns to explicitly exclude


class MatplotlibPlotSpec(BaseModel):
    """Matplotlib plot specification for device data visualization."""

    x_col: str
    y_col: str | list[str]
    x_name: str
    y_name: str
    x_units: str | None = None
    y_units: str | None = None
    grouping: dict[str, int] = Field(default_factory=dict)
    sort_by: dict[str, bool] = Field(default_factory=dict)
    x_log_axis: bool = False
    y_log_axis: bool = False
    x_limits: tuple[float, float] | None = None
    y_limits: tuple[float, float] | None = None
    scatter: bool = False


# any plot spec. (right now only matplotlib is supported)
type PlotSpec = MatplotlibPlotSpec | MatplotlibPlotSpec  # noqa: PYI016


class DeviceDataType(StrEnum):
    """Device data types."""

    MEASUREMENT = "measurement"
    SIMULATION = "simulation"
    IMAGE = "image"


class FileInfo(BaseModel):
    """File Info."""

    filename: str
    content_type: str
    path: str


class Project(BaseModel):
    """Project model."""

    pk: uuid.UUID
    project_id: str
    description: str
    eda_layout_file: FileInfo
    extraction_rules: list[ExtractionRule] | None = None
    created_at: datetime.datetime


class Cell(BaseModel):
    """Cell model."""

    pk: uuid.UUID
    cell_id: str
    project: Project
    attributes: dict[str, Any]
    created_at: datetime.datetime


class Device(BaseModel):
    """Device model."""

    pk: uuid.UUID
    x: float | None = None
    y: float | None = None
    cell: Cell
    angle: float | None = None
    parent: Optional["Device"] = None
    device_id: str
    created_at: datetime.datetime


class Wafer(BaseModel):
    """Wafer model."""

    pk: uuid.UUID
    lot_id: Any
    wafer_id: str
    attributes: Any
    created_at: datetime.datetime
    description: Any
    project: Project


class Die(BaseModel):
    """Die model."""

    pk: uuid.UUID
    x: int
    y: int
    wafer: Wafer
    created_at: datetime.datetime


class DeviceData(BaseModel):
    """Device data model."""

    pk: uuid.UUID
    data_file: FileInfo | None = None
    attributes: dict[str, Any] | None = None
    acquired_time: datetime.datetime | None = None
    plotting_settings: dict[str, Any] | None = None
    data_type: DeviceDataType
    plot_thumbnail: FileInfo | None = None
    plot_status: Any
    created_at: datetime.datetime
    die: Die | None = None
    device: Device

    @property
    def wafer(self) -> Wafer | None:
        """Return the wafer associated with this device data."""
        return self.die.wafer if self.die else None

    @property
    def cell(self) -> Cell:
        """Return the cell associated with this device data."""
        return self.device.cell

    @property
    def project(self) -> Project:
        """Return the project associated with this device data."""
        return self.cell.project


class FunctionTargetModel(StrEnum):
    """Target models for functions."""

    DEVICE_DATA = "device_data"
    DIE = "die"
    WAFER = "wafer"


class FunctionRunStatus(StrEnum):
    """Status of a function run."""

    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    RUNNING = "RUNNING"


class FunctionRunResult(BaseModel):
    """Result of a function run."""

    status: FunctionRunStatus
    stdout: str | None = None
    error: str | None = None
    return_value: dict[str, Any] | None = None
    parameters: dict[str, Any] | None = None

    def is_successful(self) -> bool:
        """Check if the function run was successful."""
        return self.status == FunctionRunStatus.COMPLETED

    def output(self) -> str | None:
        """Return the output of the function run."""
        return self.return_value.get("output") if self.return_value else None

    def summary_plot(self) -> None:
        """Display the summary plot of the function run."""
        from IPython.display import Image, display

        r = self.return_value or {}
        display(Image(data=base64.b64decode(r["summary_plot"])))


class Function(BaseModel):
    """Function model."""

    pk: uuid.UUID
    function_id: str
    version: int
    target_model: str
    content: str
    status: FunctionRunStatus | None
    function_execution_result: FunctionRunResult | None
    created_at: datetime.datetime

    def is_test_successful(self) -> bool:
        """Check if the function run was successful."""
        if self.status is FunctionRunStatus.RUNNING:
            msg = "Function is still running."
            raise ValueError(msg)
        return self.status == FunctionRunStatus.COMPLETED


class Analysis(BaseModel):
    """Analysis model."""

    pk: uuid.UUID
    analysis_id: str
    output: dict[str, Any] | None = None
    parameters: dict[str, Any] | None = None
    summary_plot: FileInfo | None = None
    status: FunctionRunStatus | None
    failed_function_result: FunctionRunResult | None
    die: Die | None = None
    device_data: DeviceData | None = None
    wafer: Wafer | None = None
    function: Function
    created_at: datetime.datetime


class AnalysisExecutionRequest(BaseModel):
    """Analysis execution request model."""

    analysis_id: Annotated[str, MinLen(3), MaxLen(255)]
    function_id: str
    target_model: FunctionTargetModel
    target_model_pk: uuid.UUID
    kwargs: dict[str, Any] | None = Field(None, serialization_alias="parameters")

    model_config = ConfigDict(serialize_by_alias=True)
