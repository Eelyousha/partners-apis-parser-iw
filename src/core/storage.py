"""ClickHouse storage for partner data."""

import logging
from typing import Any

from clickhouse_driver import Client

from src.config import Settings, get_settings
from src.core.models import PartnerData

logger = logging.getLogger(__name__)


class ClickHouseStorage:
    """ClickHouse client wrapper for partner data storage."""

    def __init__(
        self,
        config: Settings | None = None,
        table: str = "partner_data",
        database: str = "dbname",
    ) -> None:
        """Initialize ClickHouse storage."""
        self.config = config or get_settings()
        self.table = table
        self.database = database
        self._client: Client | None = None

    @property
    def client(self) -> Client:
        """Get or create ClickHouse client."""
        if self._client is None:
            self._client = Client(
                host=self.config.clickhouse_host,
                user=self.config.clickhouse_user,
                password=self.config.clickhouse_password,
            )
        return self._client

    def insert(self, data: list[PartnerData]) -> int:
        """
        Insert partner data into ClickHouse.

        Returns:
            Number of rows inserted
        """
        if not data:
            logger.warning("No data to insert")
            return 0

        query = f"INSERT INTO {self.database}.{self.table} (*) VALUES"
        rows = [item.to_dict() for item in data]

        logger.info(f"Inserting {len(rows)} rows into {self.database}.{self.table}")
        self.client.execute(query, rows)
        return len(rows)

    def query(self, sql: str) -> list[tuple[Any, ...]]:
        """Execute a query and return results."""
        result = self.client.execute(sql)
        return result  # type: ignore[no-any-return]

    def close(self) -> None:
        """Close the client connection."""
        if self._client is not None:
            self._client.disconnect()
            self._client = None
