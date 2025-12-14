"""SSP SuperPartner implementation."""

from datetime import date, datetime
from typing import Any

from src.partners.base import PartnerType
from src.partners.json_partner import JSONPartner


class SSPSuperPartner(JSONPartner):
    """
    SSP SuperPartner - JSON API.

    API URL: https://superpartner.example/v1/api/report
    Parameters:
        - token: API token
        - start_date: Start date in YYYYMMDD format
        - end_date: End date in YYYYMMDD format
        - group: Grouping (e.g., "date")

    Response format:
    {
        "code": 0,
        "message": "success",
        "total_count": 1,
        "data": {
            "20250820": {
                "impression_count": 12345678,
                "click_count": 87654321,
                "cost": 100.500
            }
        }
    }
    """

    name = "superpartner"
    partner_type = PartnerType.SSP
    currency = "usd"

    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        # Convert from YYYY-MM-DD to YYYYMMDD format
        start = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y%m%d")
        end = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y%m%d")
        token = self.config.superpartner_token
        return [
            f"https://superpartner.example/v1/api/report?token={token}&start_date={start}&end_date={end}&group=date"
        ]

    def parse_json(self, data: dict[str, Any]) -> list[tuple[str, int, float]]:
        """Parse SuperPartner JSON response."""
        result = []

        # Check for success response
        if data.get("code") != 0:
            import logging

            logging.getLogger(__name__).warning(
                f"SuperPartner API returned non-zero code: {data.get('code')}, "
                f"message: {data.get('message')}"
            )
            return result

        # Parse data dictionary
        for date_str, values in data.get("data", {}).items():
            if isinstance(values, dict):
                imps = int(values.get("impression_count", 0))
                spent = float(values.get("cost", 0))
                result.append((date_str, imps, spent))

        return result

    def parse_date(self, date_str: str) -> date:
        """Parse SuperPartner date format (YYYYMMDD)."""
        return datetime.strptime(date_str, "%Y%m%d").date()
