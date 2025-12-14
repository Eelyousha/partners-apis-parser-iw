"""SSP Partner S implementation."""

from typing import Any

from src.partners.base import PartnerType
from src.partners.json_partner import JSONPartner


class SSPPartnerS(JSONPartner):
    """SSP Partner S - JSON API with multiple campaigns."""

    name = "ssp-partner-s"
    partner_type = PartnerType.SSP
    currency = "usd"

    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        base = "https://ssp-partner-s.example/api/v1/dsp-report"
        return [
            f"{base}?campaign=display_eur&start={start_date}&end={end_date}",
            f"{base}?campaign=display_us&start={start_date}&end={end_date}",
            f"{base}?campaign=video_eur&start={start_date}&end={end_date}",
        ]

    def parse_json(self, data: dict[str, Any]) -> list[tuple[str, int, float]]:
        result = []
        for date_str, values in data.items():
            if isinstance(values, dict):
                imps = int(float(values.get("impressions", 0)))
                spent = float(values.get("revenue", 0))
                result.append((date_str, imps, spent))
        return result
