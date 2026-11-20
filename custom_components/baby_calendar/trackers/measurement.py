"""Measurement trackers: weight, length and temperature readings.

One class, parameterised by unit, range and precision, registered once per
measurement. The reading is stored in the event's amount column.
"""

from dataclasses import dataclass
from typing import Any, Final

import probatio
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfLength, UnitOfMass, UnitOfTemperature
from homeassistant.exceptions import ServiceValidationError

from ..calendar_strings import format_amount
from ..const import DOMAIN, TRACKER_LENGTH, TRACKER_TEMPERATURE, TRACKER_WEIGHT
from ..store import Event, EventStore
from .base import Columns, Day, Tracker, TrackerState

VALUE: Final = "value"

# A temperature reading stops being the sensor's state after this long.
TEMPERATURE_EXPIRY: Final = 24 * 3600


@dataclass(frozen=True, slots=True)
class Measurement:
    """What differs between measurements."""

    key: str
    unit: str
    device_class: SensorDeviceClass
    minimum: float
    maximum: float
    step: float
    precision: int
    emoji: str
    icon: str
    # Seconds after which the latest reading is no longer the sensor's state.
    expires_after: int | None = None


class MeasurementTracker(Tracker):
    """Readings of one measurement."""

    def __init__(self, measurement: Measurement) -> None:
        """Register one measurement."""
        self.measurement = measurement
        self.key = measurement.key
        self.log_service = f"log_{measurement.key}"
        # The range is checked in check(), so the error names it.
        self.log_fields = {probatio.Required(VALUE): probatio.Coerce(float)}
        self.update_fields = {probatio.Optional(VALUE): probatio.Coerce(float)}

    def to_columns(self, fields: dict[str, Any]) -> Columns:
        """Store the reading in the amount column."""
        return Columns(amount=float(fields[VALUE]))

    def to_fields(self, event: Event) -> dict[str, Any]:
        """Return the reading."""
        return {VALUE: event.amount}

    def check(self, fields: dict[str, Any]) -> None:
        """Refuse a reading outside the plausible range."""
        m = self.measurement
        value = fields.get(VALUE)
        if value is None or not m.minimum <= float(value) <= m.maximum:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="value_out_of_range",
                translation_placeholders={
                    "measurement": m.key,
                    "minimum": f"{m.minimum:g}",
                    "maximum": f"{m.maximum:g}",
                    "unit": m.unit,
                },
            )

    def summary(self, event: Event, language: str, now: int) -> str:
        """Return "⚖️ 3450 g" and the like."""
        m = self.measurement
        value = format_amount(round(event.amount or 0, m.precision), language)
        return f"{m.emoji} {value} {m.unit}"

    def compute(
        self, store: EventStore, baby_id: str, day: Day, now: int
    ) -> TrackerState:
        """Return the latest reading by event time, and its value until it expires."""
        last = store.last_event(baby_id, self.key)
        value = None if last is None else last.amount
        refresh_at = None
        if last is not None and (expires := self.measurement.expires_after):
            expiry = last.start_ts + expires
            if now >= expiry:
                value = None
            else:
                refresh_at = expiry
        return TrackerState(
            values={self.key: value, f"{self.key}_last": last},
            refresh_at=refresh_at,
        )


WEIGHT = MeasurementTracker(
    Measurement(
        key=TRACKER_WEIGHT,
        unit=UnitOfMass.GRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        minimum=300,
        maximum=30000,
        step=1,
        precision=0,
        emoji="⚖️",
        icon="mdi:scale-bathroom",
    )
)
LENGTH = MeasurementTracker(
    Measurement(
        key=TRACKER_LENGTH,
        unit=UnitOfLength.CENTIMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        minimum=20,
        maximum=130,
        step=0.5,
        precision=1,
        emoji="📏",
        icon="mdi:human-male-height",
    )
)
TEMPERATURE = MeasurementTracker(
    Measurement(
        key=TRACKER_TEMPERATURE,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        minimum=30.0,
        maximum=45.0,
        step=0.1,
        precision=1,
        emoji="🌡️",
        icon="mdi:thermometer",
        expires_after=TEMPERATURE_EXPIRY,
    )
)

MEASUREMENTS: Final = (WEIGHT, LENGTH, TEMPERATURE)
