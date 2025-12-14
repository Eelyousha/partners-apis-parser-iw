"""Tests for custom partner implementations using AAA pattern."""

from datetime import date

import pytest
from aioresponses import aioresponses

from src.config import Settings
from src.partners.dsp.partner_b_custom import DSPPartnerBCustom
from src.partners.dsp.partner_g import DSPPartnerG


class TestDSPPartnerG:
    """Tests for DSP Partner G (TXT format)."""

    def test_parse_txt_extracts_tab_separated_values(self, test_settings: Settings) -> None:
        """Test that parse_txt correctly parses tab-separated text."""
        # Arrange
        partner = DSPPartnerG(config=test_settings)
        text = """Header line
1000\t10.5
2000\t20.5
some other line"""

        # Act
        result = partner.parse_txt(text)

        # Assert
        assert len(result) == 2
        assert result[0] == ("", 1000, 10.5)
        assert result[1] == ("", 2000, 20.5)

    def test_parse_txt_ignores_non_numeric_lines(self, test_settings: Settings) -> None:
        """Test that parse_txt ignores lines not starting with digits."""
        # Arrange
        partner = DSPPartnerG(config=test_settings)
        text = """Header
Description
5000\t50.0
Footer"""

        # Act
        result = partner.parse_txt(text)

        # Assert
        assert len(result) == 1
        assert result[0] == ("", 5000, 50.0)

    def test_partner_attributes(self, test_settings: Settings) -> None:
        """Test that partner has correct attributes."""
        # Arrange & Act
        from src.partners.base import PartnerType

        partner = DSPPartnerG(config=test_settings)

        # Assert
        assert partner.name == "dsp-partner-g"
        assert partner.partner_type == PartnerType.DSP
        assert partner.dsp_id == 123
        assert partner.currency == "rub"

    @pytest.mark.asyncio
    async def test_fetch_data_iterates_daily(self, test_settings: Settings) -> None:
        """Test that fetch_data makes one request per day."""
        # Arrange
        partner = DSPPartnerG(config=test_settings)
        start_date = date(2025, 1, 15)
        end_date = date(2025, 1, 16)

        with aioresponses() as mocked:
            mocked.get(
                "https://dsp-partner-g.example/api/v2/reports?start=2025-01-15&end=2025-01-15",
                body="1000\t10.5",
            )
            mocked.get(
                "https://dsp-partner-g.example/api/v2/reports?start=2025-01-16&end=2025-01-16",
                body="2000\t20.5",
            )

            # Act
            import aiohttp

            async with aiohttp.ClientSession() as session:
                result = await partner.fetch_data(session, start_date, end_date)

            # Assert
            assert len(result) == 2
            assert result[0].dsp_id == 123
            assert result[0].date == date(2025, 1, 15)
            assert result[1].date == date(2025, 1, 16)


class TestDSPPartnerBCustom:
    """Tests for DSP Partner B Custom (POST API)."""

    def test_partner_attributes(self, test_settings: Settings) -> None:
        """Test that partner has correct attributes."""
        # Arrange & Act
        from src.partners.base import PartnerType

        partner = DSPPartnerBCustom(config=test_settings)

        # Assert
        assert partner.name == "dsp-partner-b-custom"
        assert partner.partner_type == PartnerType.DSP
        assert partner.dsp_id == 376
        assert partner.currency == "usd"

    @pytest.mark.asyncio
    async def test_fetch_data_uses_post_method(self, test_settings: Settings) -> None:
        """Test that fetch_data uses POST method with correct payload."""
        # Arrange
        partner = DSPPartnerBCustom(config=test_settings)
        start_date = date(2025, 1, 15)
        end_date = date(2025, 1, 15)

        response = {
            "statistic": [
                {"impressions": 1000, "clicks": 50, "revenue": 10.5},
                {"impressions": 2000, "clicks": 100, "revenue": 20.5},
            ]
        }

        with aioresponses() as mocked:
            mocked.post(
                "https://dsp-partner-b.example/stats",
                payload=response,
            )

            # Act
            import aiohttp

            async with aiohttp.ClientSession() as session:
                result = await partner.fetch_data(session, start_date, end_date)

            # Assert
            assert len(result) == 1
            assert result[0].dsp_id == 376
            assert result[0].imps == 3000  # 1000 + 2000
            assert result[0].spent == 31.0  # 10.5 + 20.5
