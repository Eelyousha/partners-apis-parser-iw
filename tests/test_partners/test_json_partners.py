"""Tests for JSON partner implementations using AAA pattern."""

from datetime import date
from typing import Any

import pytest
from aioresponses import aioresponses

from src.config import Settings
from src.partners.ssp.partner_m import SSPPartnerM
from src.partners.ssp.partner_o import SSPPartnerO
from src.partners.ssp.superpartner import SSPSuperPartner


class TestSSPPartnerM:
    """Tests for SSP Partner M."""

    def test_get_urls_returns_correct_format(self, test_settings: Settings) -> None:
        """Test that get_urls returns properly formatted URLs."""
        # Arrange
        partner = SSPPartnerM(config=test_settings)
        start_date = "2025-01-15"
        end_date = "2025-01-16"

        # Act
        urls = partner.get_urls(start_date, end_date)

        # Assert
        assert len(urls) == 1
        assert start_date in urls[0]
        assert end_date in urls[0]
        assert "ssp-partner-m.example" in urls[0]

    def test_get_headers_includes_bearer_token(self, test_settings: Settings) -> None:
        """Test that get_headers returns Bearer token."""
        # Arrange
        partner = SSPPartnerM(config=test_settings)

        # Act
        headers = partner.get_headers()

        # Assert
        assert headers is not None
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")

    def test_parse_json_extracts_data_correctly(
        self, test_settings: Settings, json_partner_response: dict[str, Any]
    ) -> None:
        """Test that parse_json correctly extracts data from response."""
        # Arrange
        partner = SSPPartnerM(config=test_settings)

        # Act
        result = partner.parse_json(json_partner_response)

        # Assert
        assert len(result) == 2
        assert result[0] == ("2025-01-15", 1000, 10.5)
        assert result[1] == ("2025-01-16", 2000, 20.5)

    @pytest.mark.asyncio
    async def test_fetch_data_returns_partner_data(
        self, test_settings: Settings, json_partner_response: dict[str, Any]
    ) -> None:
        """Test that fetch_data returns PartnerData objects."""
        # Arrange
        partner = SSPPartnerM(config=test_settings)
        start_date = date(2025, 1, 15)
        end_date = date(2025, 1, 16)

        with aioresponses() as mocked:
            mocked.get(
                "https://ssp-partner-m.example/v2/statistics?date_from=2025-01-15&date_to=2025-01-16",
                payload=json_partner_response,
            )

            # Act
            import aiohttp

            async with aiohttp.ClientSession() as session:
                result = await partner.fetch_data(session, start_date, end_date)

            # Assert
            assert len(result) == 2
            assert result[0].ssp == "ssp-partner-m"
            assert result[0].imps == 1000
            assert result[0].spent == 10.5


class TestSSPSuperPartner:
    """Tests for SSP SuperPartner (new partner)."""

    def test_get_urls_uses_correct_date_format(self, test_settings: Settings) -> None:
        """Test that get_urls converts dates to YYYYMMDD format."""
        # Arrange
        partner = SSPSuperPartner(config=test_settings)
        start_date = "2025-07-31"
        end_date = "2025-08-01"

        # Act
        urls = partner.get_urls(start_date, end_date)

        # Assert
        assert len(urls) == 1
        assert "start_date=20250731" in urls[0]
        assert "end_date=20250801" in urls[0]
        assert "token=test_token" in urls[0]
        assert "group=date" in urls[0]

    def test_parse_json_handles_ok_response(
        self, test_settings: Settings, superpartner_ok_response: dict[str, Any]
    ) -> None:
        """Test that parse_json correctly handles OK response."""
        # Arrange
        partner = SSPSuperPartner(config=test_settings)

        # Act
        result = partner.parse_json(superpartner_ok_response)

        # Assert
        assert len(result) == 1
        assert result[0] == ("20250820", 12345678, 100.500)

    def test_parse_json_handles_error_response(
        self, test_settings: Settings, superpartner_error_response: dict[str, Any]
    ) -> None:
        """Test that parse_json returns empty list for error response."""
        # Arrange
        partner = SSPSuperPartner(config=test_settings)

        # Act
        result = partner.parse_json(superpartner_error_response)

        # Assert
        assert len(result) == 0

    def test_parse_date_handles_yyyymmdd_format(self, test_settings: Settings) -> None:
        """Test that parse_date correctly parses YYYYMMDD format."""
        # Arrange
        partner = SSPSuperPartner(config=test_settings)

        # Act
        result = partner.parse_date("20250820")

        # Assert
        assert result == date(2025, 8, 20)

    @pytest.mark.asyncio
    async def test_fetch_data_returns_correct_partner_data(
        self, test_settings: Settings, superpartner_ok_response: dict[str, Any]
    ) -> None:
        """Test that fetch_data returns correctly formatted PartnerData."""
        # Arrange
        partner = SSPSuperPartner(config=test_settings)
        start_date = date(2025, 8, 20)
        end_date = date(2025, 8, 20)

        with aioresponses() as mocked:
            url_pattern = "https://superpartner.example/v1/api/report"
            mocked.get(
                f"{url_pattern}?token=test_token&start_date=20250820&end_date=20250820&group=date",
                payload=superpartner_ok_response,
            )

            # Act
            import aiohttp

            async with aiohttp.ClientSession() as session:
                result = await partner.fetch_data(session, start_date, end_date)

            # Assert
            assert len(result) == 1
            assert result[0].ssp == "superpartner"
            assert result[0].imps == 12345678
            assert result[0].spent == 100.500
            assert result[0].currency == "usd"
            assert result[0].date == date(2025, 8, 20)


class TestSSPPartnerO:
    """Tests for SSP Partner O."""

    def test_get_headers_returns_none(self, test_settings: Settings) -> None:
        """Test that Partner O doesn't require auth headers."""
        # Arrange
        partner = SSPPartnerO(config=test_settings)

        # Act
        headers = partner.get_headers()

        # Assert
        assert headers is None

    def test_parse_json_extracts_data(self, test_settings: Settings) -> None:
        """Test that parse_json correctly extracts data."""
        # Arrange
        partner = SSPPartnerO(config=test_settings)
        response = {
            "data": [
                {"date": "2025-01-15", "impressionCount": 5000, "spent": 50.0},
            ]
        }

        # Act
        result = partner.parse_json(response)

        # Assert
        assert len(result) == 1
        assert result[0] == ("2025-01-15", 5000, 50.0)
