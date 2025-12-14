"""SSP Partner C implementation."""

from xml.etree.ElementTree import Element

from src.partners.base import PartnerType
from src.partners.xml_partner import XMLPartner


class SSPPartnerC(XMLPartner):
    """SSP Partner C - XML API."""

    name = "ssp-partner-c"
    partner_type = PartnerType.SSP
    currency = "usd"

    def get_urls(self, start_date: str, end_date: str) -> list[str]:
        return [f"https://ssp-partner-c.example/dsp-report.xml?start={start_date}&end={end_date}"]

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
