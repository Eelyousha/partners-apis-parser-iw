"""JSON partner base class."""

import logging
from abc import abstractmethod
from datetime import date
from typing import Any

from aiohttp import ClientSession

from src.core.models import PartnerData, aggregate_partner_data
from src.partners.base import BasePartner, ResponseFormat

logger = logging.getLogger(__name__)


class JSONPartner(BasePartner):
    """Base class for partners that return JSON data."""

    format: ResponseFormat = ResponseFormat.JSON

    @abstractmethod
    def parse_json(self, data: dict[str, Any]) -> list[tuple[str, int, float]]:
        """
        Parse JSON response and extract data.

        Returns:
            List of tuples (date_string, impressions, revenue)
        """
        ...

    def parse_date(self, date_str: str) -> date:
        """Parse date string to date object. Override for custom formats."""
        from datetime import datetime

        # Try common formats
        for fmt in ["%Y-%m-%d", "%Y%m%d", "%d-%m-%Y", "%d.%m.%Y"]:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date: {date_str}")

    async def fetch_data(
        self, session: ClientSession, start_date: date, end_date: date
    ) -> list[PartnerData]:
        """Fetch and parse JSON data from partner API."""
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        urls = self.get_urls(start_str, end_str)
        headers = self.get_headers()

        all_data: list[PartnerData] = []

        for url in urls:
            try:
                logger.info(f"Fetching {self.name}: {url}")
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    json_data = await response.json()

                parsed = self.parse_json(json_data)
                for date_str, imps, spent in parsed:
                    parsed_date = self.parse_date(date_str)
                    all_data.append(self._create_partner_data(parsed_date, imps, spent))

            except Exception as e:
                logger.error(f"Error fetching {self.name} from {url}: {e}")

        return aggregate_partner_data(all_data)
