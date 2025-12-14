"""DSP Partner G implementation - TXT format."""

import re
from datetime import date, timedelta

from aiohttp import ClientSession

from src.core.models import PartnerData, aggregate_partner_data
from src.partners.base import PartnerType
from src.partners.txt_partner import TXTPartner


class DSPPartnerG(TXTPartner):
    """DSP Partner G (ID: 123) - TXT API with daily iteration."""

    name = "dsp-partner-g"
    partner_type = PartnerType.DSP
    dsp_id = 123
    currency = "rub"

    def get_urls(self, start_date: str, end_date: str) -> list[str]:  # noqa: ARG002
        # Partner G requires one request per day
        return [f"https://dsp-partner-g.example/api/v2/reports?start={start_date}&end={start_date}"]

    def parse_txt(self, text: str) -> list[tuple[str, int, float]]:
        """Parse tab-separated text response."""
        result = []
        for line in text.split("\n"):
            if re.match(r"^[0-9]", line):
                parts = line.split("\t")
                if len(parts) >= 2:
                    imps = int(float(parts[0]))
                    spent = float(parts[1])
                    result.append(("", imps, spent))  # Date set externally
        return result

    async def fetch_data(
        self, session: ClientSession, start_date: date, end_date: date
    ) -> list[PartnerData]:
        """Override to iterate day by day."""
        import logging

        all_data: list[PartnerData] = []
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            url = f"https://dsp-partner-g.example/api/v2/reports?start={date_str}&end={date_str}"

            try:
                logging.getLogger(__name__).info(f"Fetching {self.name}: {url}")
                async with session.get(url) as response:
                    response.raise_for_status()
                    text = await response.text()

                parsed = self.parse_txt(text)
                for _, imps, spent in parsed:
                    all_data.append(self._create_partner_data(current_date, imps, spent))

            except Exception as e:
                logging.getLogger(__name__).error(f"Error fetching {self.name}: {e}")

            current_date += timedelta(days=1)

        return aggregate_partner_data(all_data)
