from lunatone_rest_api_client import Auth
from lunatone_rest_api_client.models import SensorData, SensorsData

_PATH = "sensors"


class Sensor:
    """Class that represents a Sensor object in the API."""

    base_path: str = _PATH

    def __init__(self, auth: Auth, data: SensorData) -> None:
        """Initialize a Sensor object."""
        self._auth = auth
        self._data = data

    @property
    def path(self) -> str:
        """Return the resource path."""
        return f"{self.base_path}/{self.id}"

    @property
    def data(self) -> SensorData:
        """Return the raw sensor data."""
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
        """Update the sensor data."""
        response = await self._auth.get(self.path)
        self._data = SensorData.model_validate(await response.json())

    async def async_refresh(self) -> None:
        """Refresh the sensor data by reading it from the DALI bus."""
        response = await self._auth.post(self.path)
        self._data = SensorData.model_validate(await response.json())


class Sensors:
    """Class that represents a Sensors object in the API."""

    path: str = _PATH
    _data: SensorsData | None = None

    def __init__(self, auth: Auth) -> None:
        """Initialize a Sensors object."""
        self._auth = auth

    @property
    def data(self) -> SensorsData | None:
        """Return the raw sensors data."""
        return self._data

    @property
    def sensors(self) -> list[Sensor]:
        """Return a list of sensors."""
        return (
            [Sensor(self._auth, sensor) for sensor in self.data.sensors]
            if self.data
            else []
        )

    async def async_update(self) -> None:
        """Update the sensors data."""
        response = await self._auth.get(self.path)
        self._data = SensorsData.model_validate(await response.json())

    async def async_refresh(self) -> None:
        """Refresh the sensors data by reading it from the DALI bus."""
        response = await self._auth.post(self.path)
        self._data = SensorsData.model_validate(await response.json())
