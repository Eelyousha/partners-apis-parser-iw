"""DSP Partner F implementation."""

from xml.etree.ElementTree import Element

from src.partners.base import PartnerType
from src.partners.xml_partner import XMLPartner


class DSPPartnerF(XMLPartner):
    """DSP Partner F (ID: 110) - XML API."""

    name = "dsp-partner-f"
    partner_type = PartnerType.DSP
    dsp_id = 110
    currency = "usd"

    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        return [
            f"https://dsp-partner-f.example/ssp_xml?start={start_date}&end={end_date}",
            f"https://dsp-partner-f.example/ssp_xml?start={start_date}&end={end_date}",
        ]

    def parse_xml(self, root: Element) -> list[tuple[str, int, float]]:
        result = []
        for item in root:
            date_elem = item.find("date")
            imps_elem = item.find("impressions")
            rev_elem = item.find("revenue")

            date_str = date_elem.text if date_elem is not None and date_elem.text else ""
            imps = int(float(imps_elem.text)) if imps_elem is not None and imps_elem.text else 0
            spent = float(rev_elem.text) if rev_elem is not None and rev_elem.text else 0.0

            result.append((date_str, imps, spent))
        return result
