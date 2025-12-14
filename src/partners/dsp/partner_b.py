"""DSP Partner B implementation."""

from typing import Any

from aiohttp import ClientSession

from src.core.models import PartnerData, aggregate_partner_data
from src.partners.base import PartnerType
from src.partners.json_partner import JSONPartner


class DSPPartnerB(JSONPartner):
    """DSP Partner B (ID: 35) - JSON API with dynamic token auth."""

    name = "dsp-partner-b"
    partner_type = PartnerType.DSP
    dsp_id = 35
    currency = "rub"

    _cached_token: str | None = None

    async def _get_auth_token(self, session: ClientSession) -> str:
        """Get authentication token from Partner B API."""
        if self._cached_token:
            return self._cached_token

        auth_url = "https://dsp-partner-b.example/token"
        data = {
            "login": self.config.partner_b_dsp_login,
            "password": self.config.partner_b_dsp_password,
        }

        async with session.post(auth_url, data=data) as response:
            response.raise_for_status()
            json_data = await response.json()
            self._cached_token = json_data["data"]
            return self._cached_token

    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        user_id = self.config.partner_b_dsp_user_id
        return [
            f"https://dsp-partner-b.example/users/{user_id}/sites/chart?start_date={start_date}&end_date={end_date}"
        ]

    def parse_json(self, data: dict[str, Any]) -> list[tuple[str, int, float]]:
        result = []
        total_data = data.get("data", {}).get("total", {})
        dates = total_data.get("date", [])
        count_imps = total_data.get("count_imps", {})
        total_pub_payable = total_data.get("total_pub_payable", {})

        for date_str in dates:
            imps = int(float(count_imps.get(date_str, 0)))
            spent = float(total_pub_payable.get(date_str, 0))
            result.append((date_str, imps, spent))

        return result

    async def fetch_data(self, session: ClientSession, start_date, end_date):
        """Override to handle dynamic token."""
        import logging

        token = await self._get_auth_token(session)
        headers = {"Authorization": f"Token {token}"}

        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        urls = self.get_urls(start_str, end_str)

        all_data: list[PartnerData] = []

        for url in urls:
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    json_data = await response.json()

                parsed = self.parse_json(json_data)
                for date_str, imps, spent in parsed:
                    parsed_date = self.parse_date(date_str)
                    all_data.append(self._create_partner_data(parsed_date, imps, spent))

            except Exception as e:
                logging.getLogger(__name__).error(f"Error fetching {self.name}: {e}")

        return aggregate_partner_data(all_data)
