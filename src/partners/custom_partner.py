"""Custom partner base class for non-standard protocols."""

from abc import abstractmethod
from datetime import date

from aiohttp import ClientSession

from src.core.models import PartnerData
from src.partners.base import BasePartner


class CustomPartner(BasePartner):
    """
    Base class for partners with non-standard protocols (XMLRPC, SOAP, etc.).

    Subclasses must implement the full fetch_data method.
    """

    def get_urls(self, start_date: str, end_date: str) -> list[str]:  # noqa: ARG002
        """Not used for custom partners, but required by base class."""
        return []

    @abstractmethod
    async def fetch_data(
        self, session: ClientSession, start_date: date, end_date: date
    ) -> list[PartnerData]:
        """
        Fetch data using custom protocol.

        Must be fully implemented by subclass.
        """
        ...
