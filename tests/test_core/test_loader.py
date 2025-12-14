"""Tests for partner loader using AAA pattern."""

from src.config import Settings
from src.core.loader import PartnerLoader
from src.partners.base import PartnerType


class TestPartnerLoader:
    """Tests for PartnerLoader class."""

    def test_discover_partners_finds_ssp_partners(self, test_settings: Settings) -> None:
        """Test that discover_partners finds SSP partner implementations."""
        # Arrange
        loader = PartnerLoader(config=test_settings)

        # Act
        partners = loader.discover_partners()

        # Assert
        ssp_partners = [p for p in partners if p.partner_type == PartnerType.SSP]
        assert len(ssp_partners) > 0
        assert any(p.name == "superpartner" for p in ssp_partners)

    def test_discover_partners_finds_dsp_partners(self, test_settings: Settings) -> None:
        """Test that discover_partners finds DSP partner implementations."""
        # Arrange
        loader = PartnerLoader(config=test_settings)

        # Act
        partners = loader.discover_partners()

        # Assert
        dsp_partners = [p for p in partners if p.partner_type == PartnerType.DSP]
        assert len(dsp_partners) > 0

    def test_get_partner_returns_correct_partner(self, test_settings: Settings) -> None:
        """Test that get_partner returns the correct partner by name."""
        # Arrange
        loader = PartnerLoader(config=test_settings)
        loader.discover_partners()

        # Act
        partner = loader.get_partner("superpartner")

        # Assert
        assert partner is not None
        assert partner.name == "superpartner"
        assert partner.partner_type == PartnerType.SSP

    def test_get_partner_returns_none_for_unknown(self, test_settings: Settings) -> None:
        """Test that get_partner returns None for unknown partner."""
        # Arrange
        loader = PartnerLoader(config=test_settings)
        loader.discover_partners()

        # Act
        partner = loader.get_partner("unknown-partner")

        # Assert
        assert partner is None

    def test_get_ssp_partners_filters_correctly(self, test_settings: Settings) -> None:
        """Test that get_ssp_partners returns only SSP partners."""
        # Arrange
        loader = PartnerLoader(config=test_settings)

        # Act
        ssp_partners = loader.get_ssp_partners()

        # Assert
        assert all(p.partner_type == PartnerType.SSP for p in ssp_partners)

    def test_get_dsp_partners_filters_correctly(self, test_settings: Settings) -> None:
        """Test that get_dsp_partners returns only DSP partners."""
        # Arrange
        loader = PartnerLoader(config=test_settings)

        # Act
        dsp_partners = loader.get_dsp_partners()

        # Assert
        assert all(p.partner_type == PartnerType.DSP for p in dsp_partners)

    def test_register_partner_adds_to_registry(self, test_settings: Settings) -> None:
        """Test that register_partner manually adds a partner."""
        # Arrange
        from src.partners.ssp.superpartner import SSPSuperPartner

        loader = PartnerLoader(config=test_settings)
        custom_partner = SSPSuperPartner(config=test_settings)
        custom_partner.name = "custom-test-partner"

        # Act
        loader.register_partner(custom_partner)
        result = loader.get_partner("custom-test-partner")

        # Assert
        assert result is not None
        assert result.name == "custom-test-partner"

    def test_discover_partners_is_idempotent(self, test_settings: Settings) -> None:
        """Test that calling discover_partners multiple times is safe."""
        # Arrange
        loader = PartnerLoader(config=test_settings)

        # Act
        partners1 = loader.discover_partners()
        partners2 = loader.discover_partners()

        # Assert
        assert len(partners1) == len(partners2)
