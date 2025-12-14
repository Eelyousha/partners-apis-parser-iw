"""Data models for the parser."""

from dataclasses import asdict, dataclass
from datetime import date


@dataclass
class PartnerData:
    """Data collected from a partner API."""

    date: date
    dsp_id: int = 0
    ssp: str = ""
    imps: int = 0
    spent: float = 0.0
    currency: str = "usd"

    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion."""
        return asdict(self)


@dataclass
class AggregatedPartnerData:
    """Extended partner data with additional metrics."""

    date: date
    dsp_id: int = 0
    ssp: str = ""
    imps: int = 0
    spent: float = 0.0
    dsp_reqs: int = 0
    dsp_resp: int = 0
    clicks: int = 0
    view100: int = 0
    currency: str = "usd"

    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion."""
        return asdict(self)


def aggregate_partner_data(data_list: list[PartnerData]) -> list[PartnerData]:
    """Aggregate partner data by ssp/dsp_id and date."""
    aggregated: dict[str, PartnerData] = {}

    for item in data_list:
        key = f"{item.ssp}{item.dsp_id}{item.date}"
        if key in aggregated:
            aggregated[key].imps += item.imps
            aggregated[key].spent += item.spent
        else:
            aggregated[key] = PartnerData(
                date=item.date,
                dsp_id=item.dsp_id,
                ssp=item.ssp,
                imps=item.imps,
                spent=item.spent,
                currency=item.currency,
            )

    return list(aggregated.values())
