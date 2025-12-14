"""XML partner base class."""

import logging
import xml.etree.ElementTree as ET
from abc import abstractmethod
from datetime import date
from xml.etree.ElementTree import Element

from aiohttp import ClientSession

from src.core.models import PartnerData, aggregate_partner_data
from src.partners.base import BasePartner, ResponseFormat

logger = logging.getLogger(__name__)


class XMLPartner(BasePartner):
    """Base class for partners that return XML data."""

    format: ResponseFormat = ResponseFormat.XML

    @abstractmethod
    def parse_xml(self, root: Element) -> list[tuple[str, int, float]]:
        """
        Parse XML response and extract data.

        Args:
            root: Root element of parsed XML

        Returns:
            List of tuples (date_string, impressions, revenue)
        """
        ...

    def parse_date(self, date_str: str) -> date:
        """Parse date string to date object. Override for custom formats."""
        from datetime import datetime

        for fmt in ["%Y-%m-%d", "%Y%m%d", "%d-%m-%Y"]:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date: {date_str}")

    async def fetch_data(
        self, session: ClientSession, start_date: date, end_date: date
    ) -> list[PartnerData]:
        """Fetch and parse XML data from partner API."""
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
                    text = await response.text()
                    root = ET.fromstring(text)

                parsed = self.parse_xml(root)
                for date_str, imps, spent in parsed:
                    parsed_date = self.parse_date(date_str)
                    all_data.append(self._create_partner_data(parsed_date, imps, spent))

            except Exception as e:
                logger.error(f"Error fetching {self.name} from {url}: {e}")

        return aggregate_partner_data(all_data)
