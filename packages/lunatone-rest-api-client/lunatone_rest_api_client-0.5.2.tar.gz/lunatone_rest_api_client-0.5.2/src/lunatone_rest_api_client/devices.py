from lunatone_rest_api_client import Auth
from lunatone_rest_api_client.base import Controllable
from lunatone_rest_api_client.models import (
    ControlData,
    DeviceData,
    DevicesData,
    DeviceUpdateData,
)

_PATH = "devices"


class Device(Controllable):
    """Class that represents a Device object in the API."""

    base_path: str = _PATH[:-1]

    def __init__(self, auth: Auth, data: DeviceData) -> None:
        """Initialize a device object."""
        self._auth = auth
        self._data = data

    @property
    def path(self) -> str:
        """Return the resource path."""
        return f"{self.base_path}/{self.id}"

    @property
    def data(self) -> DeviceData:
        """Return the raw device data."""
        return self._data

    @property
    def id(self) -> int:
        """Return the ID of the device."""
        return self.data.id

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self.data.name

    @property
    def is_on(self) -> bool:
        """Return if the light is on."""
        return (
            self.data.features.switchable.status
            if self.data.features.switchable
            else False
        )

    @property
    def brightness(self) -> float:
        """Return the brightness of the light."""
        return (
            self.data.features.dimmable.status if self.data.features.dimmable else 0.0
        )

    @property
    def color_temperature(self) -> int:
        """Return the color temperature of the light in kelvin."""
        return (
            self.data.features.color_kelvin.status
            if self.data.features.color_kelvin
            else 0
        )

    @property
    def rgb_color(self) -> tuple[float, float, float]:
        """Return the RGB color of the light as tuple."""
        rgb_color = (0.0, 0.0, 0.0)
        if self.data.features.color_rgb:
            rgb_color = (
                self.data.features.color_rgb.status.red or 0.0,
                self.data.features.color_rgb.status.green or 0.0,
                self.data.features.color_rgb.status.blue or 0.0,
            )
        return rgb_color

    @property
    def rgbw_color(self) -> tuple[float, float, float, float]:
        """Return the RGBW color of the light as tuple."""
        rgbw_color = (0.0, 0.0, 0.0, 0.0)
        if self.data.features.color_waf:
            rgbw_color = (
                *self.rgb_color,
                self.data.features.color_waf.status.white or 0.0,
            )
        return rgbw_color

    @property
    def xy_color(self) -> tuple[float, float]:
        """Return the XY color of the light as tuple."""
        xy_color = (0.0, 0.0)
        if self.data.features.color_xy:
            xy_color = (
                self.data.features.color_xy.status.x or 0.0,
                self.data.features.color_xy.status.y or 0.0,
            )
        return xy_color

    @property
    def is_dimmable(self) -> bool:
        """Return if the light is dimmable."""
        return True  # At the moment this is not possible to determine in the REST API

    async def async_update(self, data: DeviceUpdateData | None = None) -> None:
        """Update the device data."""
        if data is not None:
            json_data = data.model_dump(by_alias=True, exclude_none=True)
            response = await self._auth.put(self.path, json=json_data)
        else:
            response = await self._auth.get(self.path)
        self._data = DeviceData.model_validate(await response.json())

    async def async_control(self, data: ControlData) -> None:
        """Control the device."""
        json_data = data.model_dump(by_alias=True, exclude_none=True)
        await self._auth.post(f"{self.path}/control", json=json_data)


class Devices:
    """Class that represents a Devices object in the API."""

    path: str = _PATH
    _data: DevicesData | None = None

    def __init__(self, auth: Auth) -> None:
        """Initialize a Devices object."""
        self._auth = auth

    @property
    def data(self) -> DevicesData | None:
        """Return the raw devices data."""
        return self._data

    @property
    def devices(self) -> list[Device]:
        """Return a list of devices."""
        return (
            [Device(self._auth, device) for device in self.data.devices]
            if self.data
            else []
        )

    async def async_update(self) -> None:
        """Update the devices data."""
        response = await self._auth.get(self.path)
        self._data = DevicesData.model_validate(await response.json())
