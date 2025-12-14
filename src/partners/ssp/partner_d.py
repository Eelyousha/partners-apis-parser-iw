"""SSP Partner D implementation."""

from xml.etree.ElementTree import Element

from src.partners.base import PartnerType
from src.partners.xml_partner import XMLPartner


class SSPPartnerD(XMLPartner):
    """SSP Partner D - XML API with multiple URLs."""

    name = "ssp-partner-d"
    partner_type = PartnerType.SSP
    currency = "usd"

    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        base = "https://ssp-partner-d.example/xml-report"
        return [
            f"{base}?format=xml&start={start_date}&end={end_date}",
            f"{base}?format=xml&start={start_date}&end={end_date}",
            f"{base}?format=xml&start={start_date}&end={end_date}",
        ]

    def parse_xml(self, root: Element) -> list[tuple[str, int, float]]:
        result = []
        for item in root:
            date_str = item.attrib.get("date", "")
            imps_elem = item.find("impressions")
            rev_elem = item.find("revenue")

            imps = int(float(imps_elem.text)) if imps_elem is not None and imps_elem.text else 0
            spent = float(rev_elem.text) if rev_elem is not None and rev_elem.text else 0.0

            result.append((date_str, imps, spent))
        return result
