"""Tests for XML partner implementations using AAA pattern."""

import xml.etree.ElementTree as ET
from datetime import date

import pytest
from aioresponses import aioresponses

from src.config import Settings
from src.partners.dsp.partner_f import DSPPartnerF
from src.partners.ssp.partner_c import SSPPartnerC


class TestSSPPartnerC:
    """Tests for SSP Partner C (XML)."""

    def test_get_urls_returns_correct_format(self, test_settings: Settings) -> None:
        """Test that get_urls returns properly formatted XML URLs."""
        # Arrange
        partner = SSPPartnerC(config=test_settings)
        start_date = "2025-01-15"
        end_date = "2025-01-16"

        # Act
        urls = partner.get_urls(start_date, end_date)

        # Assert
        assert len(urls) == 1
        assert start_date in urls[0]
        assert end_date in urls[0]
        assert "dsp-report.xml" in urls[0]

    def test_parse_xml_extracts_data_from_attributes(self, test_settings: Settings) -> None:
        """Test that parse_xml correctly extracts data from XML attributes."""
        # Arrange
        partner = SSPPartnerC(config=test_settings)
        xml_str = """<report>
            <item date="2025-01-15">
                <impressions>1000</impressions>
                <revenue>10.5</revenue>
            </item>
            <item date="2025-01-16">
                <impressions>2000</impressions>
                <revenue>20.5</revenue>
            </item>
        </report>"""
        root = ET.fromstring(xml_str)

        # Act
        result = partner.parse_xml(root)

        # Assert
        assert len(result) == 2
        assert result[0] == ("2025-01-15", 1000, 10.5)
        assert result[1] == ("2025-01-16", 2000, 20.5)

    def test_parse_xml_handles_empty_values(self, test_settings: Settings) -> None:
        """Test that parse_xml handles missing or empty values gracefully."""
        # Arrange
        partner = SSPPartnerC(config=test_settings)
        xml_str = """<report>
            <item date="2025-01-15">
                <impressions></impressions>
                <revenue></revenue>
            </item>
        </report>"""
        root = ET.fromstring(xml_str)

        # Act
        result = partner.parse_xml(root)

        # Assert
        assert len(result) == 1
        assert result[0] == ("2025-01-15", 0, 0.0)

    @pytest.mark.asyncio
    async def test_fetch_data_returns_partner_data(
        self, test_settings: Settings, xml_partner_response: str
    ) -> None:
        """Test that fetch_data returns PartnerData objects from XML."""
        # Arrange
        partner = SSPPartnerC(config=test_settings)
        start_date = date(2025, 1, 15)
        end_date = date(2025, 1, 16)

        with aioresponses() as mocked:
            mocked.get(
                "https://ssp-partner-c.example/dsp-report.xml?start=2025-01-15&end=2025-01-16",
                body=xml_partner_response,
                content_type="application/xml",
            )

            # Act
            import aiohttp

            async with aiohttp.ClientSession() as session:
                result = await partner.fetch_data(session, start_date, end_date)

            # Assert
            assert len(result) == 2
            assert result[0].ssp == "ssp-partner-c"
            assert result[0].imps == 1000


class TestDSPPartnerF:
    """Tests for DSP Partner F (XML)."""

    def test_partner_type_is_dsp(self, test_settings: Settings) -> None:
        """Test that partner is correctly identified as DSP."""
        # Arrange
        from src.partners.base import PartnerType

        partner = DSPPartnerF(config=test_settings)

        # Act & Assert
        assert partner.partner_type == PartnerType.DSP
        assert partner.dsp_id == 110

    def test_parse_xml_uses_element_text_for_date(self, test_settings: Settings) -> None:
        """Test that parse_xml extracts date from element text."""
        # Arrange
        partner = DSPPartnerF(config=test_settings)
        xml_str = """<report>
            <item>
                <date>2025-01-15</date>
                <impressions>3000</impressions>
                <revenue>30.5</revenue>
            </item>
        </report>"""
        root = ET.fromstring(xml_str)

        # Act
        result = partner.parse_xml(root)

        # Assert
        assert len(result) == 1
        assert result[0] == ("2025-01-15", 3000, 30.5)
