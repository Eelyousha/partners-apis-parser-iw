"""Async data loader orchestrator."""

import asyncio
import logging
from datetime import date, timedelta

from aiohttp import ClientSession, ClientTimeout, TCPConnector

from src.config import Settings, get_settings
from src.core.loader import PartnerLoader
from src.core.models import PartnerData
from src.core.storage import ClickHouseStorage

logger = logging.getLogger(__name__)


class PartnerDataLoader:
    """Async orchestrator for loading data from all partners."""

    def __init__(
        self,
        config: Settings | None = None,
        storage: ClickHouseStorage | None = None,
        loader: PartnerLoader | None = None,
    ) -> None:
        """Initialize the data loader."""
        self.config = config or get_settings()
        self.storage = storage or ClickHouseStorage(config=self.config)
        self.loader = loader or PartnerLoader(config=self.config)

    async def _fetch_partner_data(
        self,
        session: ClientSession,
        partner_name: str,
        start_date: date,
        end_date: date,
    ) -> list[PartnerData]:
        """Fetch data from a single partner."""
        partner = self.loader.get_partner(partner_name)
        if partner is None:
            logger.error(f"Partner not found: {partner_name}")
            return []

        try:
            logger.info(f"Fetching data from {partner_name}")
            return await partner.fetch_data(session, start_date, end_date)
        except Exception as e:
            logger.error(f"Error fetching data from {partner_name}: {e}")
            return []

    async def load_all(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        insert_to_db: bool = True,
    ) -> list[PartnerData]:
        """
        Load data from all partners asynchronously.

        Args:
            start_date: Start date (default: yesterday)
            end_date: End date (default: yesterday)
            insert_to_db: Whether to insert data into ClickHouse

        Returns:
            List of all collected partner data
        """
        if start_date is None:
            start_date = date.today() - timedelta(days=1)
        if end_date is None:
            end_date = date.today() - timedelta(days=1)

        logger.info(f"Loading partner data from {start_date} to {end_date}")

        # Discover all partners
        partners = self.loader.discover_partners()
        logger.info(f"Found {len(partners)} partners to fetch")

        # Create aiohttp session with connection pooling
        timeout = ClientTimeout(total=300)
        connector = TCPConnector(limit=10, limit_per_host=2)

        async with ClientSession(timeout=timeout, connector=connector) as session:
            # Fetch data from all partners concurrently
            tasks = [
                self._fetch_partner_data(session, partner.name, start_date, end_date)
                for partner in partners
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect all data
        all_data: list[PartnerData] = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task failed with exception: {result}")
            elif isinstance(result, list):
                all_data.extend(result)

        logger.info(f"Collected {len(all_data)} records from all partners")

        # Insert to database
        if insert_to_db and all_data:
            rows_inserted = self.storage.insert(all_data)
            logger.info(f"Inserted {rows_inserted} rows into ClickHouse")

        return all_data

    async def load_partner(
        self,
        partner_name: str,
        start_date: date | None = None,
        end_date: date | None = None,
        insert_to_db: bool = True,
    ) -> list[PartnerData]:
        """Load data from a single partner."""
        if start_date is None:
            start_date = date.today() - timedelta(days=1)
        if end_date is None:
            end_date = date.today() - timedelta(days=1)

        timeout = ClientTimeout(total=60)
        async with ClientSession(timeout=timeout) as session:
            data = await self._fetch_partner_data(session, partner_name, start_date, end_date)

        if insert_to_db and data:
            self.storage.insert(data)

        return data


async def load_insert_data(
    start_date: str | None = None, end_date: str | None = None
) -> list[PartnerData]:
    """
    Main entry point for loading partner data.

    This function is called by the queue manager.
    """
    from datetime import datetime

    parsed_start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    parsed_end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    loader = PartnerDataLoader()
    return await loader.load_all(parsed_start, parsed_end)
