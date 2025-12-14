"""DSP Partner M implementation."""

from typing import Any

from src.partners.base import PartnerType
from src.partners.json_partner import JSONPartner


class DSPPartnerM(JSONPartner):
    """DSP Partner M (ID: 27) - JSON API with Bearer auth."""

    name = "dsp-partner-m"
    partner_type = PartnerType.DSP
    dsp_id = 27
    currency = "rub"

    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        return [
            f"https://dsp-partner-m.example/api/v2/statistics?date_from={start_date}&date_to={end_date}"
        ]

    def get_headers(self) -> dict[str, str] | None:
        return {"Authorization": f"Bearer {self.config.partner_m_dsp_access_token}"}

    def parse_json(self, data: dict[str, Any]) -> list[tuple[str, int, float]]:
        result = []
        for item in data.get("items", []):
            for row in item.get("rows", []):
                date_str = row["date"]
                imps = int(float(row["shows"]))
                spent = float(row["amount"])
                result.append((date_str, imps, spent))
        return result
