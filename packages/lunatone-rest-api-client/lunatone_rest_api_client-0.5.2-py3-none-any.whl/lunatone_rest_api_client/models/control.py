from pydantic import BaseModel, ConfigDict, Field, NonNegativeFloat, NonNegativeInt

from lunatone_rest_api_client.models.common import (
    ColorRGBData,
    ColorWAFData,
    ColorWithFadeTime,
    ColorXYData,
    DimmableKelvinData,
    DimmableRGBData,
    DimmableWAFData,
    DimmableWithFadeTime,
    DimmableXYData,
    FadeTime,
)


class SceneWithFadeData(FadeTime):
    scene: int = Field(ge=0, lt=16)


class ControlData(BaseModel):
    """Data model for ``ControlData``."""

    switchable: bool | None = None
    dimmable: float | None = Field(None, ge=0.0, le=100.0)
    dimmable_with_fade: DimmableWithFadeTime | None = Field(
        None, alias="dimmableWithFade"
    )
    dim_up: int | None = Field(None, alias="dimUp", ge=1, le=1)
    dim_down: int | None = Field(None, alias="dimDown", ge=1, le=1)
    goto_last_active: bool | None = Field(
        None,
        description="Value must be ``true``.",
        alias="gotoLastActive",
    )
    goto_last_active_with_fade: FadeTime | None = Field(
        None,
        description="Dim to the last level within a fade time in seconds.",
        alias="gotoLastActiveWithFade",
    )
    scene: int | None = Field(
        None,
        description="Scene number of the scene to recall.",
        ge=0,
        lt=16,
    )
    scene_with_fade: SceneWithFadeData | None = Field(
        None,
        description="Scene number of the scene to recall, within a fade time in seconds.",
        alias="sceneWithFade",
    )
    fade_time: NonNegativeFloat | None = Field(
        None,
        description="Set the fade time in seconds.",
        alias="fadeTime",
    )
    fade_rate: NonNegativeFloat | None = Field(
        None,
        description="Set the fade rate in steps per second.",
        alias="fadeRate",
    )
    save_to_scene: NonNegativeInt | None = Field(
        None, alias="saveToScene", ge=0, lt=16
    )
    color_rgb: ColorRGBData | None = Field(None, alias="colorRGB")
    dimmable_rgb: DimmableRGBData | None = Field(None, alias="dimmableRGB")
    color_rgb_with_fade: ColorWithFadeTime[ColorRGBData] | None = Field(
        None, alias="colorRGBWithFade"
    )
    color_waf: ColorWAFData | None = Field(None, alias="colorWAF")
    dimmable_waf: DimmableWAFData | None = Field(None, alias="dimmableWAF")
    color_waf_with_fade: ColorWithFadeTime[ColorWAFData] | None = Field(
        None, alias="colorWAFWithFade"
    )
    color_kelvin: NonNegativeInt | None = Field(
        None, alias="colorKelvin", gt=15, le=1000000
    )
    dimmable_kelvin: DimmableKelvinData | None = Field(None, alias="dimmableKelvin")
    color_kelvin_with_fade: ColorWithFadeTime[NonNegativeFloat] | None = Field(
        None, alias="colorKelvinWithFade"
    )
    color_xy: ColorXYData | None = Field(None, alias="colorXY")
    dimmable_xy: DimmableXYData | None = Field(None, alias="dimmableXY")
    color_xy_with_fade: ColorWithFadeTime[ColorXYData] | None = Field(
        None, alias="colorXYWithFade"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "gotoLastActive": True,
                    "gotoLastActiveWithFade": FadeTime(fadeTime=1.0),
                    "scene": 15,
                    "sceneWithFade": SceneWithFadeData(scene=15, fadeTime=1.0),
                    "fadeTime": 1.0,
                    "fadeRate": 15.8,
                }
            ]
        }
    )
