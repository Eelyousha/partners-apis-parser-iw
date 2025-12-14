"""Pytest configuration and fixtures."""

from datetime import date
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.config import Settings
from src.core.loader import PartnerLoader
from src.core.models import PartnerData
from src.core.storage import ClickHouseStorage
from src.queue.manager import MockQueueManager, reset_queue_manager


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with mock values."""
    return Settings(
        clickhouse_host="localhost",
        clickhouse_user="test",
        clickhouse_password="test",
        mongodb_host="mongodb://localhost:27017",
        partner_m_ssp_access_token="test_token",
        partner_m_dsp_access_token="test_token",
        partner_b_ssp_login="test@test.com",
        partner_b_ssp_password="test_password",
        partner_b_ssp_user_id=12345,
        partner_b_dsp_login="test@test.com",
        partner_b_dsp_password="test_password",
        partner_b_dsp_user_id=12345,
        partner_s_dsp_login="test",
        partner_s_dsp_token="test_token",
        dsp_b_access_token="test_token",
        superpartner_token="test_token",
    )


@pytest.fixture
def partner_loader(test_settings: Settings) -> PartnerLoader:
    """Create partner loader with test settings."""
    return PartnerLoader(config=test_settings)


@pytest.fixture
def mock_storage() -> MagicMock:
    """Create mock ClickHouse storage."""
    storage = MagicMock(spec=ClickHouseStorage)
    storage.insert.return_value = 10
    return storage


@pytest.fixture
def sample_partner_data() -> list[PartnerData]:
    """Create sample partner data for testing."""
    return [
        PartnerData(
            date=date(2025, 1, 15),
            ssp="test-partner",
            imps=1000,
            spent=10.5,
            currency="usd",
        ),
        PartnerData(
            date=date(2025, 1, 16),
            ssp="test-partner",
            imps=2000,
            spent=20.5,
            currency="usd",
        ),
    ]


@pytest.fixture
def mock_queue_manager() -> MockQueueManager:
    """Create mock queue manager."""
    reset_queue_manager()
    return MockQueueManager(mongo_host="mongodb://localhost", tag="test")


@pytest.fixture
def superpartner_ok_response() -> dict[str, Any]:
    """Sample OK response from SuperPartner API."""
    return {
        "code": 0,
        "message": "success",
        "total_count": 1,
        "data": {
            "20250820": {
                "impression_count": 12345678,
                "click_count": 87654321,
                "cost": 100.500,
            }
        },
    }


@pytest.fixture
def superpartner_error_response() -> dict[str, Any]:
    """Sample error response from SuperPartner API."""
    return {
        "code": 1,
        "message": "Invalid token",
        "total_count": 0,
        "data": {},
    }


@pytest.fixture
def json_partner_response() -> dict[str, Any]:
    """Sample JSON response for generic partner."""
    return {
        "items": [
            {
                "rows": [
                    {"date": "2025-01-15", "base": {"shows": 1000, "spent": 10.5}},
                    {"date": "2025-01-16", "base": {"shows": 2000, "spent": 20.5}},
                ]
            }
        ]
    }


@pytest.fixture
def xml_partner_response() -> str:
    """Sample XML response for generic partner."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<report>
    <item date="2025-01-15">
        <impressions>1000</impressions>
        <revenue>10.5</revenue>
    </item>
    <item date="2025-01-16">
        <impressions>2000</impressions>
        <revenue>20.5</revenue>
    </item>
</report>"""


@pytest.fixture(autouse=True)
def reset_queue():
    """Reset queue manager before each test."""
    reset_queue_manager()
    yield
    reset_queue_manager()
