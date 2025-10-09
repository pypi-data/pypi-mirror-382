"""DoDataClient module for creating and managing DoData API and Query clients."""

import os

import dotenv

from gdsfactoryhub.api_client import ApiClient, create_api_client
from gdsfactoryhub.query_client import QueryClient, create_query_client
from gdsfactoryhub.utils import Utils


class GDSFactoryHubClient:
    """A client for interacting with DoData API and Query services."""

    def __init__(self, api_url: str, query_url: str, key: str, *, project_id: str = "") -> None:
        """Initialize the DoDataClient with API and Query URLs and a key."""
        self._api_client: ApiClient = create_api_client(api_url, key, project_id=project_id)
        self._query_client: QueryClient = create_query_client(query_url, key, project_id=project_id)
        self._utils: Utils = Utils(self._api_client, self._query_client)

    def query(self) -> QueryClient:
        """Return the QueryClient instance."""
        return self._query_client

    def api(self) -> ApiClient:
        """Return the ApiClient instance."""
        return self._api_client

    def utils(self) -> Utils:
        """Return the Utils instance."""
        return self._utils


def create_client_from_env(*, project_id: str = "") -> GDSFactoryHubClient:
    """Create a DoDataClient instance using URLs from environment variables.

    Environment variables:
        GDSFACTORY_HUB_API_URL: URL for the API client
        GDSFACTORY_HUB_QUERY_URL: URL for the query client
        GDSFACTORY_HUB_KEY: Key for both the api client and query client
    """
    dotenv.load_dotenv()
    api_url = os.getenv("GDSFACTORY_HUB_API_URL")
    query_url = os.getenv("GDSFACTORY_HUB_QUERY_URL")
    key = os.getenv("GDSFACTORY_HUB_KEY")

    if not api_url:
        msg = "GDSFACTORY_HUB_API_URL environment variable is not set"
        raise ValueError(msg)
    if not query_url:
        msg = "GDSFACTORY_HUB_QUERY_URL environment variable is not set"
        raise ValueError(msg)
    if not key:
        msg = "GDSFACTORY_HUB_KEY environment variable is not set"
        raise ValueError(msg)

    return create_client(api_url, query_url, key, project_id=project_id)


def create_client(api_url: str, query_url: str, key: str, *, project_id: str = "") -> GDSFactoryHubClient:
    """Create a DoDataClient instance with the provided API and Query URLs and key."""
    return GDSFactoryHubClient(api_url, query_url, key, project_id=project_id)
