"""Base partner class and enums."""

from abc import ABC, abstractmethod
from datetime import date
from enum import Enum

from aiohttp import ClientSession

from src.config import Settings, get_settings
from src.core.models import PartnerData


class PartnerType(str, Enum):
    """Type of partner."""

    SSP = "ssp"
    DSP = "dsp"


class ResponseFormat(str, Enum):
    """Response format from partner API."""

    JSON = "json"
    XML = "xml"
    TXT = "txt"


class BasePartner(ABC):
    """Abstract base class for all partners."""

    name: str = ""
    partner_type: PartnerType = PartnerType.SSP
    dsp_id: int = 0
    currency: str = "usd"

    def __init__(self, config: Settings | None = None) -> None:
        """Initialize partner with configuration."""
        self.config = config or get_settings()

    def get_headers(self) -> dict[str, str] | None:
        """Get HTTP headers for API request. Override in subclass if needed."""
        return None

    @abstractmethod
    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        """Get list of URLs to fetch data from."""
        ...

    @abstractmethod
    async def fetch_data(
        self, session: ClientSession, start_date: date, end_date: date
    ) -> list[PartnerData]:
        """Fetch and parse data from partner API."""
        ...

    def _create_partner_data(self, parsed_date: date, imps: int, spent: float) -> PartnerData:
        """Create PartnerData instance based on partner type."""
        if self.partner_type == PartnerType.SSP:
            return PartnerData(
                date=parsed_date,
                ssp=self.name,
                imps=imps,
                spent=spent,
                currency=self.currency,
            )
        else:
            return PartnerData(
                date=parsed_date,
                dsp_id=self.dsp_id,
                imps=imps,
                spent=spent,
                currency=self.currency,
            )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, type={self.partner_type.value})>"
