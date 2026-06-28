import appdaemon.plugins.hass.hassapi as hass

from kaomy.core import CacheManager, SensorManager, KaomyBanner
from kaomy.providers import CDEProvider


class WaterPrincipalCollector(hass.Hass):
    """
    AppDaemon collector for principal water consumption.
    """

    def initialize(self):
        self.prefix = "water_principal"

        self.cache = CacheManager("water_principal")
        self.sensors = SensorManager(self)

        self.provider = CDEProvider(
            username=self.args["username"],
            password=self.args["password"],
            collector=self.prefix,
            location="principal",
            point_installation_id=self.args["point_installation_id"],
            simulation=self.args.get("simulation", False),
        )

        self.log("[Kaomy][WaterPrincipal][INFO] Collector started")

        cache_status = "OK" if self.cache.exists() else "Missing"

        self.log(KaomyBanner.collector(
            name=self.prefix,
            provider=self.provider.name,
            location=self.provider.location,
            cache_status=cache_status,
            simulation=self.provider.simulation,
        ))

        self.restore_from_cache()

        # self.run_in(self.collect_and_publish, 10)

        self.run_daily(
            self.collect_and_publish,
            self.args.get("schedule", "02:00:00")
        )

    def restore_from_cache(self):
        state = self.cache.load()

        if state is None:
            self.log("[Kaomy][WaterPrincipal][WARNING] No cache available")
            return

        self.sensors.publish(state, self.prefix)
        self.log("[Kaomy][WaterPrincipal][INFO] Sensors restored from cache")

    def collect_and_publish(self, kwargs):
        try:
            previous_state = self.cache.load()
            state = self.provider.collect()

            conso_jour = float(state.measurements.get("conso_jour") or 0)
            conso_mois = float(state.measurements.get("conso_mois") or 0)

            if previous_state is None:
                total = conso_mois
            else:
                previous_total = float(previous_state.measurements.get("total") or 0)
                previous_reading = previous_state.metadata.last_reading
                current_reading = state.metadata.last_reading

                if previous_total <= conso_jour and conso_mois > previous_total:
                    total = conso_mois

                elif previous_reading != current_reading:
                    total = previous_total + conso_jour

                else:
                    total = previous_total

            state.measurements["total"] = round(total, 3)

            self.cache.save(state)
            self.sensors.publish(state, self.prefix)

            self.log(
                "[Kaomy][WaterPrincipal][INFO] Collection OK - "
                f"Jour: {state.measurements.get('conso_jour')} "
                f"{state.metadata.unit} / "
                f"Mois: {state.measurements.get('conso_mois')} "
                f"{state.metadata.unit} / "
                f"Total: {state.measurements.get('total')} "
                f"{state.metadata.unit}"
            )

        except Exception as exc:
            self.log(
                f"[Kaomy][WaterPrincipal][ERROR] Collection failed: {exc}",
                level="ERROR"
            )
