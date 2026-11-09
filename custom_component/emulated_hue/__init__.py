"""Support for local control of entities by emulating a Philips Hue bridge."""

import logging
import re

from aiohttp import web
import probatio

from homeassistant.components.http import KEY_HASS
from homeassistant.components.network import async_get_source_ip
from homeassistant.const import (
    CONF_ENTITIES,
    CONF_TYPE,
    EVENT_HOMEASSISTANT_STARTED,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.typing import ConfigType

from .config import (
    CONF_ADVERTISE_IP,
    CONF_ADVERTISE_PORT,
    CONF_ENTITY_HIDDEN,
    CONF_ENTITY_NAME,
    CONF_EXPOSE_BY_DEFAULT,
    CONF_EXPOSED_DOMAINS,
    CONF_HOST_IP,
    CONF_LIGHTS_ALL_DIMMABLE,
    CONF_LISTEN_PORT,
    CONF_OFF_MAPS_TO_ON_DOMAINS,
    CONF_UPNP_ALLOWED_IPS,
    CONF_UPNP_BIND_MULTICAST,
    DEFAULT_LIGHTS_ALL_DIMMABLE,
    DEFAULT_LISTEN_PORT,
    DEFAULT_TYPE,
    TYPE_ALEXA,
    TYPE_GOOGLE,
    Config,
)
from .const import DOMAIN
from .hue_api import (
    HueAllGroupsStateView,
    HueAllLightsStateView,
    HueConfigView,
    HueFullStateView,
    HueGroupView,
    HueOneLightChangeView,
    HueOneLightStateView,
    HueUnauthorizedUser,
    HueUsernameView,
)
from .stats import BridgeStats
from .upnp import DescriptionXmlView, async_create_upnp_datagram_endpoint

_LOGGER = logging.getLogger(__name__)


# Config del bridge, usata dal log HTTP per tradurre numero -> entity_id
CONFIG_KEY = web.AppKey("emulated_hue_config", Config)

_LIGHT_PATH = re.compile(r"^/api/[^/]+/lights/([^/]+)")


def _describe_request(request: web.Request) -> str:
    """Metodo + percorso, con l'entity_id quando la richiesta riguarda una luce."""
    desc = f"{request.method} {request.path}"
    match = _LIGHT_PATH.match(request.path)
    config = request.app.get(CONFIG_KEY)
    if match and config is not None:
        entity_id = config.number_to_entity_id(match.group(1))
        desc += f" ({entity_id or 'numero sconosciuto'})"
    return desc


@web.middleware
async def _log_http_requests(request: web.Request, handler):
    """Log (in debug) ogni richiesta HTTP al bridge: chi, cosa, esito."""
    stats: BridgeStats | None = request.app[KEY_HASS].data.get(DOMAIN)
    if stats is not None:
        stats.record_request(request.remote)
    try:
        response = await handler(request)
    except web.HTTPException as err:
        if _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug(
                "HTTP %s da %s -> %s",
                _describe_request(request),
                request.remote,
                err.status,
            )
        raise
    if _LOGGER.isEnabledFor(logging.DEBUG):
        _LOGGER.debug(
            "HTTP %s da %s -> %s",
            _describe_request(request),
            request.remote,
            response.status,
        )
    return response


CONFIG_ENTITY_SCHEMA = probatio.Schema(
    {
        probatio.Optional(CONF_ENTITY_NAME): cv.string,
        probatio.Optional(CONF_ENTITY_HIDDEN): cv.boolean,
        probatio.Optional("hue_type"): probatio.In(["light", "other"]),
        probatio.Optional("reset_id"): cv.boolean,
    }
)


CONFIG_SCHEMA = probatio.Schema(
    {
        DOMAIN: probatio.Schema(
            {
                probatio.Optional(CONF_HOST_IP): cv.string,
                probatio.Optional(
                    CONF_LISTEN_PORT, default=DEFAULT_LISTEN_PORT
                ): probatio.Port(),
                probatio.Optional(CONF_ADVERTISE_IP): cv.string,
                probatio.Optional(CONF_ADVERTISE_PORT): probatio.Port(),
                probatio.Optional(CONF_UPNP_BIND_MULTICAST): cv.boolean,
                probatio.Optional(CONF_UPNP_ALLOWED_IPS): probatio.EnsureList(),
                probatio.Optional(CONF_OFF_MAPS_TO_ON_DOMAINS): probatio.EnsureList(),
                probatio.Optional(CONF_EXPOSE_BY_DEFAULT): cv.boolean,
                probatio.Optional(CONF_EXPOSED_DOMAINS): probatio.EnsureList(),
                probatio.Optional(CONF_TYPE, default=DEFAULT_TYPE): probatio.Any(
                    TYPE_ALEXA, TYPE_GOOGLE
                ),
                probatio.Optional(CONF_ENTITIES): probatio.Schema(
                    {cv.entity_id: CONFIG_ENTITY_SCHEMA}
                ),
                probatio.Optional(
                    CONF_LIGHTS_ALL_DIMMABLE, default=DEFAULT_LIGHTS_ALL_DIMMABLE
                ): cv.boolean,
            }
        )
    },
    extra=probatio.ALLOW_EXTRA,
)


async def start_emulated_hue_bridge(
    hass: HomeAssistant, config: Config, app: web.Application
) -> None:
    """Start the emulated hue bridge."""
    protocol = await async_create_upnp_datagram_endpoint(
        config.host_ip_addr,
        config.upnp_bind_multicast,
        config.advertise_ip,
        config.advertise_port or config.listen_port,
        config.upnp_allowed_ips,
    )

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, config.host_ip_addr, config.listen_port)

    try:
        await site.start()
    except OSError as error:
        _LOGGER.error(
            "Failed to create HTTP server at port %d: %s", config.listen_port, error
        )
        protocol.close()
        return

    master = (
        ", ".join(sorted(config.upnp_allowed_ips))
        if config.upnp_allowed_ips
        else "tutti (upnp_allowed_ips non impostato)"
    )
    _LOGGER.info(
        "Emulated Hue avviato su %s:%s · %d entità esposte · master: %s",
        config.host_ip_addr,
        config.listen_port,
        len(config.get_exposed_entity_ids()),
        master,
    )

    async def stop_emulated_hue_bridge(event: Event) -> None:
        """Stop the emulated hue bridge."""
        protocol.close()
        await site.stop()
        await runner.cleanup()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, stop_emulated_hue_bridge)


async def async_setup(hass: HomeAssistant, yaml_config: ConfigType) -> bool:
    """Activate the emulated_hue component."""
    local_ip = await async_get_source_ip(hass)
    config = Config(hass, yaml_config.get(DOMAIN, {}), local_ip)
    await config.async_setup()

    # Statistiche per i sensori di diagnostica
    hass.data[DOMAIN] = BridgeStats(hass, config.upnp_allowed_ips)

    app = web.Application(middlewares=[_log_http_requests])
    app[KEY_HASS] = hass
    app[CONFIG_KEY] = config

    # We misunderstood the startup signal. You're not allowed to change
    # anything during startup. Temp workaround.
    app._on_startup.freeze()  # noqa: SLF001
    await app.startup()

    DescriptionXmlView(config).register(hass, app, app.router)
    HueUsernameView().register(hass, app, app.router)
    HueConfigView(config).register(hass, app, app.router)
    HueUnauthorizedUser().register(hass, app, app.router)
    HueAllLightsStateView(config).register(hass, app, app.router)
    HueOneLightStateView(config).register(hass, app, app.router)
    HueOneLightChangeView(config).register(hass, app, app.router)
    HueAllGroupsStateView(config).register(hass, app, app.router)
    HueGroupView(config).register(hass, app, app.router)
    HueFullStateView(config).register(hass, app, app.router)

    async def _start(event: Event) -> None:
        """Start the bridge."""
        await start_emulated_hue_bridge(hass, config, app)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _start)

    # Sensori di diagnostica (ultimo contatto master, IP non autorizzati)
    hass.async_create_task(
        discovery.async_load_platform(
            hass, Platform.SENSOR, DOMAIN, {}, yaml_config
        )
    )

    return True
