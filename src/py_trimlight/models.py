from datetime import datetime
from enum import IntEnum
from typing import Any

from pydantic import BaseModel, Field, model_serializer, model_validator


class ConnectivityState(IntEnum):
    Offline = 0
    Online = 1


class DeviceState(IntEnum):
    Normal = 0
    Upgrading = 1


class SwitchState(IntEnum):
    Off = 0
    Manual = 1
    Timer = 2


class EffectCategory(IntEnum):
    BuiltIn = 0
    Custom = 1


class DateTime(BaseModel):
    year: int
    month: int
    day: int
    weekday: int
    hours: int
    minutes: int
    seconds: int

    @classmethod
    def from_datetime(cls, dt: datetime) -> "DateTime":
        return cls(
            year=dt.year - 2000,
            month=dt.month,
            day=dt.day,
            weekday=dt.weekday(),
            hours=dt.hour,
            minutes=dt.minute,
            seconds=dt.second,
        )

    @classmethod
    def get_current_datetime(cls) -> "DateTime":
        return cls.from_datetime(datetime.now())


class DeviceBase(BaseModel):
    name: str
    connectivity: ConnectivityState
    state: DeviceState
    switch_state: SwitchState = Field(..., alias="switchState")
    fw_version_name: str = Field(..., alias="fwVersionName")


class Device(DeviceBase):
    device_id: str = Field(..., alias="deviceId")


class DevicePort(BaseModel):
    id: int
    start: int
    end: int


class RGBColor(BaseModel):
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)

    @model_validator(mode="before")
    @classmethod
    def _from_int(cls, data: Any) -> Any:
        if isinstance(data, int):
            if not 0 <= data <= 0xFFFFFF:
                raise ValueError(f"color out of range: {data}")
            return {"r": (data >> 16) & 0xFF, "g": (data >> 8) & 0xFF, "b": data & 0xFF}
        return data  # also allows {"r":..,"g":..,"b":..}

    @model_serializer
    def _to_int(self) -> int:
        return (self.r << 16) | (self.g << 8) | self.b

    @property
    def hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


class Pixel(BaseModel):
    index: int
    count: int
    color: RGBColor
    disable: bool


class EffectBase(BaseModel):
    category: EffectCategory
    mode: int
    speed: int
    brightness: int
    pixels: list[Pixel] = Field(default_factory=list)
    pixel_len: int | None = Field(None, alias="pixelLen")
    reverse: bool | None = None


class Effect(EffectBase):
    id: int
    name: str


class CombinedEffect(BaseModel):
    effect_ids: list[int] = Field(..., alias="effectIds")
    interval: int


class OverlayEffect(BaseModel):
    overlay_type: int = Field(..., alias="overlayType")
    target_effect: int = Field(..., alias="targetEffect")


class TimeOfDay(BaseModel):
    hours: int
    minutes: int


class DayOfYear(BaseModel):
    month: int
    day: int


class ScheduleBase(BaseModel):
    id: int
    effect_id: int = Field(..., alias="effectId")
    start_time: TimeOfDay = Field(..., alias="startTime")
    end_time: TimeOfDay = Field(..., alias="endTime")


class DailySchedule(ScheduleBase):
    enable: bool
    repetition: int


class CalendarSchedule(ScheduleBase):
    start_date: DayOfYear = Field(..., alias="startDate")
    end_date: DayOfYear = Field(..., alias="endDate")


class DeviceDetails(DeviceBase):
    color_order: int = Field(..., alias="colorOrder")
    ic: int
    ports: list[DevicePort]
    effects: list[Effect]
    combined_effect: CombinedEffect = Field(..., alias="combinedEffect")
    daily: list[DailySchedule]
    calendar: list[CalendarSchedule]
    current_effect: EffectBase = Field(..., alias="currentEffect")
    overlay_effects: list[OverlayEffect] = Field(..., alias="overlayEffects")
    current_datetime: DateTime = Field(..., alias="currentDatetime")


class GetDevicesPayload(BaseModel):
    total: int
    current: int
    data: list[Device]


class ApiResponse[T](BaseModel):
    code: int
    desc: str
    payload: T
