"""Partner auto-discovery and loading."""

import importlib
import logging
import pkgutil
from typing import TYPE_CHECKING

from src.config import Settings, get_settings

if TYPE_CHECKING:
    from src.partners.base import BasePartner

logger = logging.getLogger(__name__)


class PartnerLoader:
    """Discovers and loads partner implementations."""

    def __init__(self, config: Settings | None = None) -> None:
        """Initialize the loader."""
        self.config = config or get_settings()
        self._partners: dict[str, BasePartner] = {}
        self._discovered = False

    def discover_partners(self) -> list["BasePartner"]:
        """
        Auto-discover all partner implementations.

        Scans src.partners.ssp and src.partners.dsp packages for partner classes.
        """
        if self._discovered:
            return list(self._partners.values())

        from src.partners.base import BasePartner

        for package_name in ["src.partners.ssp", "src.partners.dsp"]:
            try:
                package = importlib.import_module(package_name)
                for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                    full_module_name = f"{package_name}.{module_name}"
                    try:
                        module = importlib.import_module(full_module_name)
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (
                                isinstance(attr, type)
                                and issubclass(attr, BasePartner)
                                and attr is not BasePartner
                                and hasattr(attr, "name")
                                and attr.name
                            ):
                                partner = attr(config=self.config)
                                self._partners[partner.name] = partner
                                logger.debug(f"Discovered partner: {partner.name}")
                    except Exception as e:
                        logger.error(f"Error loading module {full_module_name}: {e}")
            except ModuleNotFoundError:
                logger.warning(f"Package {package_name} not found")

        self._discovered = True
        logger.info(f"Discovered {len(self._partners)} partners")
        return list(self._partners.values())

    def get_partner(self, name: str) -> "BasePartner | None":
        """Get a partner by name."""
        if not self._discovered:
            self.discover_partners()
        return self._partners.get(name)

    def register_partner(self, partner: "BasePartner") -> None:
        """Manually register a partner."""
        self._partners[partner.name] = partner
        logger.debug(f"Registered partner: {partner.name}")

    def get_all_partners(self) -> list["BasePartner"]:
        """Get all discovered partners."""
        if not self._discovered:
            self.discover_partners()
        return list(self._partners.values())

    def get_ssp_partners(self) -> list["BasePartner"]:
        """Get all SSP partners."""
        from src.partners.base import PartnerType

        return [p for p in self.get_all_partners() if p.partner_type == PartnerType.SSP]

    def get_dsp_partners(self) -> list["BasePartner"]:
        """Get all DSP partners."""
        from src.partners.base import PartnerType

        return [p for p in self.get_all_partners() if p.partner_type == PartnerType.DSP]
