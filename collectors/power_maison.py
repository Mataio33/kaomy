import appdaemon.plugins.hass.hassapi as hass

from kaomy.core import CacheManager, SensorManager, KaomyBanner
from kaomy.providers import EnercalProvider


class PowerMaisonCollector(hass.Hass):
    """
    AppDaemon collector for maison electricity consumption.

    Workflow:
        1. Restore last valid state from cache at startup.
        2. Publish cached sensors to Home Assistant.
        3. Collect fresh data once per day.
        4. Save fresh state to cache.
        5. Publish fresh sensors.
    """

    def initialize(self):
        self.prefix = "power_maison"

        self.cache = CacheManager("power_maison")
        self.sensors = SensorManager(self)

        self.provider = EnercalProvider(
            username=self.args["username"],
            password=self.args["password"],
            collector=self.prefix,
            location="maison",
            simulation=self.args.get("simulation", False),
        )

        self.log("[Kaomy][PowerMaison][INFO] Collector started")

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
            self.args.get("schedule", "03:00:00")
        )

    def restore_from_cache(self):
        state = self.cache.load()

        if state is None:
            self.log("[Kaomy][PowerMaison][WARNING] No cache available")
            return

        self.sensors.publish(state, self.prefix)
        self.log("[Kaomy][PowerMaison][INFO] Sensors restored from cache")

    def collect_and_publish(self, kwargs):
        try:
            state = self.provider.collect()

            self.cache.save(state)
            self.sensors.publish(state, self.prefix)

            self.log(
                "[Kaomy][PowerMaison][INFO] Collection OK - "
                f"Jour: {state.measurements.get('conso_jour')} "
                f"{state.metadata.unit} / "
                f"Mois: {state.measurements.get('conso_mois')} "
                f"{state.metadata.unit}"
            )

        except Exception as exc:
            self.log(
                f"[Kaomy][PowerMaison][ERROR] Collection failed: {exc}",
                level="ERROR"
            )
