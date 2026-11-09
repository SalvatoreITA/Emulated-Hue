"""Statistiche di diagnostica del bridge: contatti dal master e IP non autorizzati."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util import dt as dt_util

SIGNAL_STATS_UPDATED = "emulated_hue_stats_updated"

# Il master interroga il bridge di continuo (anche più volte al secondo):
# aggiorniamo i sensori al massimo una volta al minuto per non riempire il
# database del recorder.
UPDATE_THROTTLE = timedelta(seconds=60)


class BridgeStats:
    """Tiene traccia di chi contatta le API HTTP del bridge."""

    def __init__(self, hass: HomeAssistant, allowed_ips: set[str]) -> None:
        """Initialize."""
        self.hass = hass
        self.allowed_ips = allowed_ips
        self.last_master_contact: datetime | None = None
        self.unauthorized: dict[str, datetime] = {}
        self._last_push: datetime | None = None

    @callback
    def record_request(self, remote: str | None) -> None:
        """Registra una richiesta HTTP arrivata al bridge."""
        if not remote:
            return
        now = dt_util.utcnow()
        new_ip = False

        # Senza upnp_allowed_ips qualunque client conta come "master".
        if not self.allowed_ips or remote in self.allowed_ips:
            self.last_master_contact = now
        else:
            new_ip = remote not in self.unauthorized
            self.unauthorized[remote] = now

        if (
            new_ip
            or self._last_push is None
            or now - self._last_push >= UPDATE_THROTTLE
        ):
            self._last_push = now
            async_dispatcher_send(self.hass, SIGNAL_STATS_UPDATED)
