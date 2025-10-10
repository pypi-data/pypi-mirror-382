from typing import ClassVar

from lunatone_rest_api_client import Auth
from lunatone_rest_api_client.models import InfoData


ARTICLE_NUMBER_NAME_MAPPING = {
    86456840: "DALI-2 Display 7''",
    86456841: "DALI-2 Display 4''",
    89453886: "DALI-2 IoT",
    22176625: "DALI-2 IoT4",
}

ARTICLE_INFO_NAME_MAPPING = {
    "NR": "Node-RED",
    "PS": "integrated power supply",
}


class Info:
    """Class that represents a info object in the API."""

    path: ClassVar[str] = "info"

    def __init__(self, auth: Auth) -> None:
        """Initialize an info object."""
        self._auth = auth
        self._data = None

    @property
    def data(self) -> InfoData | None:
        """Return the raw info data."""
        return self._data

    @property
    def name(self) -> str | None:
        """Return the name of the API interface."""
        return self.data.name if self.data else None

    @property
    def version(self) -> str | None:
        """Return the software version of the API interface."""
        return self.data.version if self.data else None

    @property
    def article_number(self) -> int | None:
        """Return the article number of the API interface."""
        return self.data.device.article_number if self.data else None

    @property
    def article_info(self) -> str | None:
        """Return the article info of the API interface."""
        return self.data.device.article_info if self.data else None

    @property
    def serial_number(self) -> int | None:
        """Return the serial number of the API interface."""
        return self.data.device.serial if self.data else None

    @property
    def product_name(self) -> str | None:
        """Return the product name of the API interface."""
        name = ARTICLE_NUMBER_NAME_MAPPING.get(self.article_number, None)
        if name is not None:
            for key, value in ARTICLE_INFO_NAME_MAPPING.items():
                if self.article_info is not None and self.article_info.find(key) > 0:
                    name += f" {value}"
        return name

    async def async_update(self) -> None:
        """Update the info data."""
        response = await self._auth.get(self.path)
        self._data = InfoData.model_validate(await response.json())
