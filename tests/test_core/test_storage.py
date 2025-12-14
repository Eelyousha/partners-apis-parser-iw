"""Tests for ClickHouse storage using AAA pattern."""

from datetime import date
from unittest.mock import MagicMock, patch

from src.config import Settings
from src.core.models import PartnerData
from src.core.storage import ClickHouseStorage


class TestClickHouseStorage:
    """Tests for ClickHouseStorage class."""

    def test_insert_returns_row_count(self, test_settings: Settings) -> None:
        """Test that insert returns the number of inserted rows."""
        # Arrange
        with patch("src.core.storage.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            storage = ClickHouseStorage(config=test_settings)
            data = [
                PartnerData(date=date(2025, 1, 15), ssp="test", imps=1000, spent=10.5),
                PartnerData(date=date(2025, 1, 16), ssp="test", imps=2000, spent=20.5),
            ]

            # Act
            result = storage.insert(data)

            # Assert
            assert result == 2
            mock_client.execute.assert_called_once()

    def test_insert_empty_list_returns_zero(self, test_settings: Settings) -> None:
        """Test that insert returns 0 for empty data list."""
        # Arrange
        storage = ClickHouseStorage(config=test_settings)

        # Act
        result = storage.insert([])

        # Assert
        assert result == 0

    def test_insert_uses_correct_table(self, test_settings: Settings) -> None:
        """Test that insert uses the configured table name."""
        # Arrange
        with patch("src.core.storage.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            storage = ClickHouseStorage(
                config=test_settings, table="custom_table", database="custom_db"
            )
            data = [PartnerData(date=date(2025, 1, 15), ssp="test", imps=1000, spent=10.5)]

            # Act
            storage.insert(data)

            # Assert
            call_args = mock_client.execute.call_args
            assert "custom_db.custom_table" in call_args[0][0]

    def test_client_created_lazily(self, test_settings: Settings) -> None:
        """Test that client is created only when accessed."""
        # Arrange
        with patch("src.core.storage.Client") as mock_client_class:
            # Act
            storage = ClickHouseStorage(config=test_settings)

            # Assert - client not created yet
            mock_client_class.assert_not_called()

            # Act - access client
            _ = storage.client

            # Assert - now client is created
            mock_client_class.assert_called_once()

    def test_close_disconnects_client(self, test_settings: Settings) -> None:
        """Test that close disconnects the client."""
        # Arrange
        with patch("src.core.storage.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            storage = ClickHouseStorage(config=test_settings)
            _ = storage.client  # Create client

            # Act
            storage.close()

            # Assert
            mock_client.disconnect.assert_called_once()
            assert storage._client is None
