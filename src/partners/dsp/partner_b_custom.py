"""DSP Partner B Custom implementation - POST API with daily iteration."""

import logging
from datetime import date, timedelta

from aiohttp import ClientSession

from src.core.models import PartnerData, aggregate_partner_data
from src.partners.base import PartnerType
from src.partners.custom_partner import CustomPartner

logger = logging.getLogger(__name__)


class DSPPartnerBCustom(CustomPartner):
    """DSP Partner B Custom (ID: 376) - POST API with daily iteration."""

    name = "dsp-partner-b-custom"
    partner_type = PartnerType.DSP
    dsp_id = 376
    currency = "usd"

    API_URL = "https://dsp-partner-b.example/stats"

    async def fetch_data(
        self, session: ClientSession, start_date: date, end_date: date
    ) -> list[PartnerData]:
        """Fetch data using POST API with daily iteration."""
        all_data: list[PartnerData] = []
        current_date = start_date
        headers = {"Authorization": f"Bearer {self.config.dsp_b_access_token}"}

        while current_date <= end_date:
            date_str = current_date.strftime("%d-%m-%Y")
            payload = {
                "start_date": date_str,
                "end_date": date_str,
                "field_names": ["impressions", "clicks", "revenue"],
                "group_by": ["site_id", "placement_id"],
            }

            try:
                async with session.post(self.API_URL, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()

                total_impressions = 0
                total_revenue = 0.0

                for item in data.get("statistic", []):
                    total_impressions += int(item.get("impressions", 0))
                    total_revenue += float(item.get("revenue", 0))

                if total_impressions > 0 or total_revenue > 0:
                    all_data.append(
                        PartnerData(
                            date=current_date,
                            dsp_id=self.dsp_id,
                            imps=total_impressions,
                            spent=total_revenue,
                            currency=self.currency,
                        )
                    )

            except Exception as e:
                logger.error(f"Error fetching {self.name} for {current_date}: {e}")

            current_date += timedelta(days=1)

        return aggregate_partner_data(all_data)
