"""SSP Partner O implementation."""

from typing import Any

from src.partners.base import PartnerType
from src.partners.json_partner import JSONPartner


class SSPPartnerO(JSONPartner):
    """SSP Partner O - JSON API without auth."""

    name = "ssp-partner-o"
    partner_type = PartnerType.SSP
    currency = "usd"

    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        return [
            f"https://ssp-partner-o.example/reporting/dsp?start_date={start_date}&end_date={end_date}"
        ]

    def parse_json(self, data: dict[str, Any]) -> list[tuple[str, int, float]]:
        result = []
        for item in data.get("data", []):
            date_str = item["date"]
            imps = int(float(item["impressionCount"]))
            spent = float(item["spent"])
            result.append((date_str, imps, spent))
        return result
