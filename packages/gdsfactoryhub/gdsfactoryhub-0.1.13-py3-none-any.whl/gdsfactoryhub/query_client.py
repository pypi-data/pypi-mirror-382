"""Query Client for DoData."""

from typing import Any

from postgrest._sync.client import (
    SyncPostgrestClient,
)
from postgrest._sync.request_builder import (
    SyncRequestBuilder,
    SyncSelectRequestBuilder,
)
from postgrest.constants import (
    DEFAULT_POSTGREST_CLIENT_HEADERS,
)

from gdsfactoryhub import columns as c
from gdsfactoryhub.errors import DoDataError

_TableT = dict[str, Any]


class QueryClient:
    """Query Client for DoData."""

    def __init__(self, query_url: str, key: str, *, project_id: str = "") -> None:
        """Initialize the QueryClient."""
        if not query_url:
            msg = "query_url is required"
            raise DoDataError(msg)
        if not key:
            msg = "key is required"
            raise DoDataError(msg)

        self.project_id = project_id
        self.dodata_url = query_url
        self.key = key
        self._postgrest = None

    @property
    def postgrest(self) -> SyncPostgrestClient:
        """Get the PostgREST client."""
        if self._postgrest is None:
            self._postgrest = SyncPostgrestClient(
                self.dodata_url, headers={"api-key": self.key, **DEFAULT_POSTGREST_CLIENT_HEADERS}
            )

        return self._postgrest

    def table(self, table_name: str) -> SyncRequestBuilder[_TableT]:
        """Perform a table operation."""
        return self.postgrest.from_(table_name)

    def projects(self) -> SyncSelectRequestBuilder[dict]:
        """Get the projects table."""
        return self.table("projects").select(c.PROJECT_COLUMNS_FULL)

    def cells(self) -> SyncSelectRequestBuilder[dict]:
        """Get the cells table."""
        return self._eq_project_id(self.table("cells").select(c.CELL_COLUMNS_FULL), "project.project_id")

    def devices(self) -> SyncSelectRequestBuilder[dict]:
        """Get the devices table."""
        return self._eq_project_id(self.table("devices").select(c.DEVICE_COLUMNS_FULL), "cell.project.project_id")

    def wafers(self) -> SyncSelectRequestBuilder[dict]:
        """Get the wafers table."""
        return self._eq_project_id(self.table("wafers").select(c.WAFER_COLUMNS_FULL), "project.project_id")

    def dies(self) -> SyncSelectRequestBuilder[dict]:
        """Get the dies table."""
        return self._eq_project_id(self.table("dies").select(c.DIE_COLUMNS_FULL), "wafer.project.project_id")

    def device_data(self, *, with_die: bool | None = None) -> SyncSelectRequestBuilder[dict]:
        """Get the device data table."""
        q = self._eq_project_id(
            self.table("device_data").select(c.DEVICE_DATA_COLUMNS_FULL), "device.cell.project.project_id"
        )
        if with_die is None:
            return q
        if with_die:
            return q.not_.is_("die", "null")
        return q.is_("die", "null")

    def functions(self) -> SyncSelectRequestBuilder[dict]:
        """Get the functions table."""
        return self.table("functions").select(c.FUNCTION_COLUMNS_FULL)

    def analyses(self) -> SyncSelectRequestBuilder[dict]:
        """Get the analyses table."""
        return self.table("analyses").select(c.ANALYSIS_COLUMNS_FULL)

    def _eq_project_id(self, query: SyncSelectRequestBuilder, selector: str) -> SyncSelectRequestBuilder:
        """Filter the query by project_id."""
        if self.project_id:
            return query.eq(selector, self.project_id)
        return query


def create_query_client(query_url: str, key: str, *, project_id: str = "") -> QueryClient:
    """Create a QueryClient instance."""
    return QueryClient(query_url, key, project_id=project_id)
