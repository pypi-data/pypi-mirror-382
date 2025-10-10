import aiohttp
import pytest
from aioresponses.core import aioresponses

from lunatone_rest_api_client import Auth, Info
from lunatone_rest_api_client.info import (
    ARTICLE_INFO_NAME_MAPPING,
    ARTICLE_NUMBER_NAME_MAPPING,
)
from lunatone_rest_api_client.models import InfoData

from .common import INFO_DATA_RAW


@pytest.fixture
def info_data() -> InfoData:
    return InfoData.model_validate(INFO_DATA_RAW)


@pytest.mark.asyncio
async def test_info_update(
    aioresponses: aioresponses, base_url: str, info_data: InfoData
) -> None:
    json_data = info_data.model_dump(by_alias=True)
    aioresponses.get(f"{base_url}/{Info.path}", payload=json_data)

    async with aiohttp.ClientSession() as session:
        info = Info(Auth(session, base_url))
        await info.async_update()
        assert info.data == info_data


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "article_number, article_info",
    [
        (86456840, "-NR"),
        (86456841, ""),
        (89453886, ""),
        (22176625, ""),
        (22176625, "-PS-NR"),
    ],
)
async def test_product_name(
    aioresponses: aioresponses,
    base_url: str,
    info_data: InfoData,
    article_number: int,
    article_info: str,
) -> None:
    info_data.device.article_number = article_number
    info_data.device.article_info = article_info

    json_data = info_data.model_dump(by_alias=True)
    aioresponses.get(f"{base_url}/{Info.path}", payload=json_data)

    async with aiohttp.ClientSession() as session:
        info = Info(Auth(session, base_url))
        await info.async_update()
        assert info.data == info_data

        expected_product_name = ARTICLE_NUMBER_NAME_MAPPING[article_number]
        if info.article_info:
            for key, value in ARTICLE_INFO_NAME_MAPPING.items():
                if key in info.article_info:
                    expected_product_name += f" {value}"
        assert expected_product_name == info.product_name
