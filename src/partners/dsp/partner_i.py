"""DSP Partner I implementation."""

from typing import Any

from src.partners.base import PartnerType
from src.partners.json_partner import JSONPartner


class DSPPartnerI(JSONPartner):
    """DSP Partner I (ID: 71) - JSON API."""

    name = "dsp-partner-i"
    partner_type = PartnerType.DSP
    dsp_id = 71
    currency = "usd"

    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        # Partner I uses YYYYMMDD format
        from datetime import datetime

        start = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y%m%d")
        end = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y%m%d")
        return [f"https://dsp-partner-i.example/sspReport?start={start}&end={end}"]

    def parse_json(self, data: dict[str, Any]) -> list[tuple[str, int, float]]:
        result = []
        for item in data.get("data", []):
            date_str = item["date"]
            imps = int(float(item["imp"]))
            spent = float(item["revenue"])
            result.append((date_str, imps, spent))
        return result
