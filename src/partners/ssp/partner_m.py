"""SSP Partner M implementation."""

from typing import Any

from src.partners.base import PartnerType
from src.partners.json_partner import JSONPartner


class SSPPartnerM(JSONPartner):
    """SSP Partner M - JSON API with Bearer token auth."""

    name = "ssp-partner-m"
    partner_type = PartnerType.SSP
    currency = "rub"

    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        return [
            f"https://ssp-partner-m.example/v2/statistics?date_from={start_date}&date_to={end_date}"
        ]

    def get_headers(self) -> dict[str, str] | None:
        return {"Authorization": f"Bearer {self.config.partner_m_ssp_access_token}"}

    def parse_json(self, data: dict[str, Any]) -> list[tuple[str, int, float]]:
        result = []
        for row in data.get("items", [{}])[0].get("rows", []):
            date_str = row["date"]
            imps = int(float(row["base"]["shows"]))
            spent = float(row["base"]["spent"])
            result.append((date_str, imps, spent))
        return result
