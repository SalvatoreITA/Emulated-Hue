"""Sensori di diagnostica di Emulated Hue."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN
from .stats import SIGNAL_STATS_UPDATED, BridgeStats


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Crea i sensori (caricati automaticamente dal componente)."""
    if discovery_info is None:
        return
    stats: BridgeStats = hass.data[DOMAIN]
    async_add_entities(
        [LastMasterContactSensor(stats), UnauthorizedIpSensor(stats)]
    )


class _StatsSensor(SensorEntity):
    """Base: si aggiorna quando cambiano le statistiche del bridge."""

    _attr_should_poll = False

    def __init__(self, stats: BridgeStats) -> None:
        """Initialize."""
        self._stats = stats

    async def async_added_to_hass(self) -> None:
        """Iscriviti agli aggiornamenti."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_STATS_UPDATED, self.async_write_ha_state
            )
        )


class LastMasterContactSensor(_StatsSensor):
    """Ultima volta che l'Echo master ha contattato il bridge."""

    _attr_name = "Emulated Hue ultimo contatto master"
    _attr_unique_id = "emulated_hue_last_master_contact"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:access-point-check"

    @property
    def native_value(self) -> datetime | None:
        """Return the state."""
        return self._stats.last_master_contact


class UnauthorizedIpSensor(_StatsSensor):
    """Quanti IP non autorizzati hanno chiamato le API del bridge."""

    _attr_name = "Emulated Hue IP non autorizzati"
    _attr_unique_id = "emulated_hue_unauthorized_ips"
    _attr_icon = "mdi:shield-alert-outline"

    @property
    def native_value(self) -> int:
        """Return the state."""
        return len(self._stats.unauthorized)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """IP visti e ultima richiesta di ciascuno."""
        return {
            "ip": {
                ip: ts.isoformat()
                for ip, ts in sorted(self._stats.unauthorized.items())
            }
        }
