from typing import Any, Dict

from kaomy.core.exceptions import SensorError
from kaomy.models.resource_state import ResourceState


class SensorManager:
    """
    Publish ResourceState data to Home Assistant sensors.

    This class is the only Kaomy core component allowed to call
    AppDaemon's set_state method.
    """

    def __init__(self, hass_app):
        self.hass = hass_app

    def publish(self, state: ResourceState, prefix: str) -> None:
        """
        Publish a ResourceState into Home Assistant sensors.

        Args:
            state: Normalized Kaomy resource state.
            prefix: Sensor prefix, for example 'power_maison' or 'water_principal'.
        """
        try:
            self._publish_measurements(state, prefix)
            self._publish_releve_date(state, prefix)

        except Exception as exc:
            raise SensorError(f"Unable to publish sensors for {prefix}: {exc}") from exc

    def _publish_measurements(self, state: ResourceState, prefix: str) -> None:
        for name, value in state.measurements.items():
            sensor_id = self._build_sensor_id(prefix, name)
            attributes = self._build_attributes(state, prefix, name)

            self.hass.set_state(
                sensor_id,
                state=value,
                attributes=attributes
            )

    def _publish_releve_date(self, state: ResourceState, prefix: str) -> None:
        if not state.metadata.last_reading:
            return

        self.hass.set_state(
            self._build_sensor_id(prefix, "releve_date"),
            state=state.metadata.last_reading,
            attributes={
                "friendly_name": self._friendly_name(prefix, "releve_date")
            }
        )

    def _build_attributes(self, state: ResourceState, prefix: str, name: str) -> Dict[str, Any]:
        attributes: Dict[str, Any] = {
            "friendly_name": self._friendly_name(prefix, name),
        }

        if state.metadata.unit:
            attributes["unit_of_measurement"] = state.metadata.unit

        if state.metadata.device_class:
            attributes["device_class"] = state.metadata.device_class

        if state.metadata.icon:
            attributes["icon"] = state.metadata.icon

        if name == "total":
            attributes["state_class"] = "total_increasing"
        else:
            attributes["state_class"] = "measurement"

        if state.history and name == "conso_mois":
            attributes["daily_data"] = state.history

        if state.attributes:
            attributes.update(state.attributes.get(name, {}))

        return attributes

    @staticmethod
    def _build_sensor_id(prefix: str, name: str) -> str:
        return f"sensor.{prefix}_{name}"

    @staticmethod
    def _friendly_name(prefix: str, name: str) -> str:
        return f"{prefix.replace('_', ' ').title()} {name.replace('_', ' ').title()}"
