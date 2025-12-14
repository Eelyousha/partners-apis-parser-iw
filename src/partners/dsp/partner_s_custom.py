"""DSP Partner S Custom implementation - XMLRPC protocol."""

import asyncio
import logging
import ssl
import xmlrpc.client
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import Any

from aiohttp import ClientSession

from src.core.models import PartnerData, aggregate_partner_data
from src.partners.base import PartnerType
from src.partners.custom_partner import CustomPartner

logger = logging.getLogger(__name__)


class CookiesTransport(xmlrpc.client.SafeTransport):
    """A SafeTransport (HTTPS) subclass that retains cookies over its lifetime."""

    def __init__(self, context: ssl.SSLContext | None = None) -> None:
        super().__init__(context=context)
        self._cookies: list[str] = []

    def send_headers(self, connection: Any, headers: Any) -> None:
        if self._cookies:
            connection.putheader("Cookie", "; ".join(self._cookies))
        super().send_headers(connection, headers)

    def parse_response(self, response: Any) -> Any:
        if response.msg.get_all("Set-Cookie"):
            for header in response.msg.get_all("Set-Cookie"):
                cookie = header.split(";", 1)[0]
                self._cookies.append(cookie)
        return super().parse_response(response)


class DSPPartnerSCustom(CustomPartner):
    """DSP Partner S (ID: 58) - XMLRPC API."""

    name = "dsp-partner-s-custom"
    partner_type = PartnerType.DSP
    dsp_id = 58
    currency = "rub"

    ENDPOINTS = [178, 209, 211, 213]
    XMLRPC_URL = "https://dsp-partner-s.example/xmlrpc/"

    def _fetch_sync(self, start_date: date, end_date: date) -> list[dict]:
        """Synchronous XMLRPC fetch (to be run in executor)."""

        transport = CookiesTransport(context=ssl._create_unverified_context())
        results: list[dict] = []

        for ep in self.ENDPOINTS:
            try:
                with xmlrpc.client.ServerProxy(self.XMLRPC_URL, transport=transport) as proxy:
                    proxy.partner_s.login(
                        self.config.partner_s_dsp_login, self.config.partner_s_dsp_token
                    )

                with xmlrpc.client.ServerProxy(self.XMLRPC_URL, transport=transport) as proxy:
                    res = proxy.rtb.get_openrtb_stats(
                        start_date.strftime("%Y-%m-%d %H:%M:%S"),
                        end_date.strftime("%Y-%m-%d %H:%M:%S"),
                        1,
                        ep,
                    )
                    if isinstance(res, list):
                        for row in res:
                            if isinstance(row, dict):
                                results.append(row)
                logger.info(f"Partner S ep={ep} fetched successfully")
            except Exception as e:
                logger.error(f"Partner S ep={ep} failed: {e}")

        return results

    async def fetch_data(
        self,
        session: ClientSession,  # noqa: ARG002
        start_date: date,
        end_date: date,  # noqa: ARG002
    ) -> list[PartnerData]:
        """Fetch data using XMLRPC protocol."""
        import pandas as pd

        loop = asyncio.get_event_loop()

        with ThreadPoolExecutor(max_workers=1) as executor:
            results = await loop.run_in_executor(executor, self._fetch_sync, start_date, end_date)

        if not results:
            return []

        # Process results
        df = pd.DataFrame(results)
        if df.empty:
            return []

        df["date"] = df["date_view"].apply(
            lambda x: pd.to_datetime(str(x), format="%Y%m%dT%H:%M:%S").date()
        )
        aggregated = df.groupby("date", as_index=False).agg({"imps": "sum", "amount": "sum"})

        all_data = [
            PartnerData(
                date=row["date"],
                dsp_id=self.dsp_id,
                imps=int(row["imps"]),
                spent=float(row["amount"]),
                currency=self.currency,
            )
            for _, row in aggregated.iterrows()
        ]

        return aggregate_partner_data(all_data)
