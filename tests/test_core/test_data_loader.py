"""Tests for data loader using AAA pattern."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config import Settings
from src.core.data_loader import PartnerDataLoader, load_insert_data
from src.core.models import PartnerData


class TestPartnerDataLoader:
    """Tests for PartnerDataLoader class."""

    @pytest.mark.asyncio
    async def test_load_all_uses_default_dates(self, test_settings: Settings) -> None:
        """Test that load_all uses yesterday as default dates."""
        # Arrange
        mock_storage = MagicMock()
        mock_storage.insert.return_value = 0

        mock_loader = MagicMock()
        mock_loader.discover_partners.return_value = []

        data_loader = PartnerDataLoader(
            config=test_settings, storage=mock_storage, loader=mock_loader
        )

        # Act
        result = await data_loader.load_all()

        # Assert
        assert result == []
        mock_loader.discover_partners.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_all_fetches_from_all_partners(self, test_settings: Settings) -> None:
        """Test that load_all fetches data from all discovered partners."""
        # Arrange
        mock_partner1 = MagicMock()
        mock_partner1.name = "partner1"
        mock_partner1.fetch_data = AsyncMock(
            return_value=[
                PartnerData(date=date(2025, 1, 15), ssp="partner1", imps=1000, spent=10.0)
            ]
        )

        mock_partner2 = MagicMock()
        mock_partner2.name = "partner2"
        mock_partner2.fetch_data = AsyncMock(
            return_value=[
                PartnerData(date=date(2025, 1, 15), ssp="partner2", imps=2000, spent=20.0)
            ]
        )

        mock_storage = MagicMock()
        mock_storage.insert.return_value = 2

        mock_loader = MagicMock()
        mock_loader.discover_partners.return_value = [mock_partner1, mock_partner2]
        mock_loader.get_partner.side_effect = lambda name: (
            mock_partner1 if name == "partner1" else mock_partner2
        )

        data_loader = PartnerDataLoader(
            config=test_settings, storage=mock_storage, loader=mock_loader
        )

        # Act
        result = await data_loader.load_all(
            start_date=date(2025, 1, 15), end_date=date(2025, 1, 15), insert_to_db=True
        )

        # Assert
        assert len(result) == 2
        mock_storage.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_all_handles_partner_errors(self, test_settings: Settings) -> None:
        """Test that load_all handles individual partner errors gracefully."""
        # Arrange
        mock_partner1 = MagicMock()
        mock_partner1.name = "partner1"
        mock_partner1.fetch_data = AsyncMock(side_effect=Exception("API Error"))

        mock_partner2 = MagicMock()
        mock_partner2.name = "partner2"
        mock_partner2.fetch_data = AsyncMock(
            return_value=[
                PartnerData(date=date(2025, 1, 15), ssp="partner2", imps=2000, spent=20.0)
            ]
        )

        mock_storage = MagicMock()
        mock_storage.insert.return_value = 1

        mock_loader = MagicMock()
        mock_loader.discover_partners.return_value = [mock_partner1, mock_partner2]
        mock_loader.get_partner.side_effect = lambda name: (
            mock_partner1 if name == "partner1" else mock_partner2
        )

        data_loader = PartnerDataLoader(
            config=test_settings, storage=mock_storage, loader=mock_loader
        )

        # Act
        result = await data_loader.load_all(
            start_date=date(2025, 1, 15), end_date=date(2025, 1, 15)
        )

        # Assert - should still have data from partner2
        assert len(result) == 1
        assert result[0].ssp == "partner2"

    @pytest.mark.asyncio
    async def test_load_partner_fetches_single_partner(self, test_settings: Settings) -> None:
        """Test that load_partner fetches data from a specific partner."""
        # Arrange
        mock_partner = MagicMock()
        mock_partner.name = "test-partner"
        mock_partner.fetch_data = AsyncMock(
            return_value=[
                PartnerData(date=date(2025, 1, 15), ssp="test-partner", imps=1000, spent=10.0)
            ]
        )

        mock_storage = MagicMock()
        mock_storage.insert.return_value = 1

        mock_loader = MagicMock()
        mock_loader.get_partner.return_value = mock_partner

        data_loader = PartnerDataLoader(
            config=test_settings, storage=mock_storage, loader=mock_loader
        )

        # Act
        result = await data_loader.load_partner(
            "test-partner",
            start_date=date(2025, 1, 15),
            end_date=date(2025, 1, 15),
        )

        # Assert
        assert len(result) == 1
        assert result[0].ssp == "test-partner"


class TestLoadInsertDataFunction:
    """Tests for load_insert_data entry point function."""

    @pytest.mark.asyncio
    async def test_load_insert_data_parses_dates(self) -> None:
        """Test that load_insert_data correctly parses date strings."""
        # Arrange
        with patch("src.core.data_loader.PartnerDataLoader") as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader.load_all = AsyncMock(return_value=[])
            mock_loader_class.return_value = mock_loader

            # Act
            await load_insert_data("2025-01-15", "2025-01-16")

            # Assert
            mock_loader.load_all.assert_called_once_with(date(2025, 1, 15), date(2025, 1, 16))

    @pytest.mark.asyncio
    async def test_load_insert_data_handles_none_dates(self) -> None:
        """Test that load_insert_data handles None dates."""
        # Arrange
        with patch("src.core.data_loader.PartnerDataLoader") as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader.load_all = AsyncMock(return_value=[])
            mock_loader_class.return_value = mock_loader

            # Act
            await load_insert_data(None, None)

            # Assert
            mock_loader.load_all.assert_called_once_with(None, None)
