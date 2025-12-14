"""DSP Partner O implementation."""

from typing import Any

from src.partners.base import PartnerType
from src.partners.json_partner import JSONPartner


class DSPPartnerO(JSONPartner):
    """DSP Partner O (ID: 65) - JSON API with custom date format."""

    name = "dsp-partner-o"
    partner_type = PartnerType.DSP
    dsp_id = 65
    currency = "rub"

    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        return [
            f"https://dsp-partner-o.example/v1/reporting?start={start_date}&end={end_date}&group=day"
        ]

    def parse_json(self, data: dict[str, Any]) -> list[tuple[str, int, float]]:
        result = []
        for item in data.get("data", []):
            # Day format: "DD.MM.YYYY" -> convert to "YYYY-MM-DD"
            day = item["day"]
            date_str = f"{day[6:10]}-{day[3:5]}-{day[0:2]}"
            imps = int(float(item["impressions"]))
            spent = float(item["earnings"]) / 1000  # earnings in 1/1000
            result.append((date_str, imps, spent))
        return result
