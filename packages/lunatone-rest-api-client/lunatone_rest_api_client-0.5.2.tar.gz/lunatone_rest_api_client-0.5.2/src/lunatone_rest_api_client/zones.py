from lunatone_rest_api_client import Auth
from lunatone_rest_api_client.base import Controllable
from lunatone_rest_api_client.models import (
    ControlData,
    ZoneData,
    ZonesData,
)

_PATH = "zones"


class Zone(Controllable):
    """Class that represents a zone object in the API."""

    base_path: str = _PATH[:-1]

    def __init__(self, auth: Auth, data: ZoneData) -> None:
        """Initialize a zone object."""
        self._auth = auth
        self._data = data

    @property
    def path(self) -> str:
        """Return the resource path."""
        return f"{self.base_path}/{self.id}"

    @property
    def data(self) -> ZoneData:
        """Return the raw zone data."""
        return self._data

    @property
    def id(self) -> int:
        """Return the ID of the zone."""
        return self.data.id

    @property
    def name(self) -> str:
        """Return the name of the zone."""
        return self.data.name

    async def async_update(self) -> None:
        """Update the zone data."""
        response = await self._auth.get(self.path)
        self._data = ZoneData.model_validate(await response.json())

    async def async_control(self, data: ControlData) -> None:
        """Control the zone."""
        json_data = data.model_dump(by_alias=True, exclude_none=True)
        await self._auth.post(f"{self.path}/control", json=json_data)


class Zones:
    """Class that represents a zones object in the API."""

    path: str = _PATH
    _data: ZonesData | None = None

    def __init__(self, auth: Auth) -> None:
        """Initialize a zones object."""
        self._auth = auth

    @property
    def data(self) -> ZonesData | None:
        """Return the raw zones data."""
        return self._data

    @property
    def zones(self) -> list[Zone]:
        """Return a list of zones."""
        return [Zone(self._auth, zone) for zone in self.data.zones] if self.data else []

    async def async_update(self) -> None:
        """Update the zones data."""
        response = await self._auth.get(self.path)
        self._data = ZonesData.model_validate(await response.json())
