from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from kaomy.core.exceptions import ProviderError
from kaomy.models import ResourceMetadata, ResourceState
from kaomy.providers.base_provider import BaseProvider


class EnercalProvider(BaseProvider):
    """
    Provider for Enercal electricity consumption data.
    """

    def __init__(self, username: str, password: str, collector: str, location: str, simulation: bool = False):
        super().__init__(name="enercal", simulation=simulation)
        self.username = username
        self.password = password
        self.collector = collector
        self.location = location
        self.session = None
        self.token = None
        self.site_id = None

    def authenticate(self) -> None:
        if self.simulation:
            return

        self._init_session()

        try:
            response = self.session.post(
                "https://ael.enercal.nc/api/signin",
                json={
                    "username": self.username,
                    "password": self.password,
                    "remember": False,
                },
                verify=False,
                timeout=30,
            )

            if response.status_code != 200:
                raise ProviderError(f"Enercal login failed: HTTP {response.status_code}")

            data = response.json()
            self.token = data.get("token", {}).get("accessToken")
            self.site_id = data.get("user", {}).get("selected_site")

            # print("[Kaomy][Enercal][DEBUG] selected_site:", self.site_id)
            # print("[Kaomy][Enercal][DEBUG] sites:", data.get("user", {}).get("s"))
            # print("[Kaomy][Enercal][DEBUG] roles:", data.get("user", {}).get("roles"))

            if not self.token:
                raise ProviderError("Enercal token missing after login")

            if not self.site_id:
                raise ProviderError("Enercal selected_site missing after login")

        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"Enercal authentication error: {exc}") from exc

    def collect(self) -> ResourceState:
        if self.simulation:
            return self._simulation_state()

        self.authenticate()
        series = self._get_consumption_series()
        history = self._build_history(series)

        if not history:
            raise ProviderError("Enercal returned no consumption values")

        return self._build_state(history)

    def _init_session(self) -> None:
        if self.session is not None:
            return

        try:
            import requests
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            self.session = requests.Session()
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "Referer": "https://ael.enercal.nc/signin",
            })

        except Exception as exc:
            raise ProviderError(f"Unable to initialize Enercal HTTP session: {exc}") from exc

    def _get_consumption_series(self) -> list:
        now_utc = datetime.utcnow()

        date_start = (
            now_utc
            .replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            - timedelta(hours=11)
        )

        date_end = now_utc + timedelta(days=1)

        url = (
            "https://ael.enercal.nc/api/timeseries/consumption"
            f"?site[]={self.site_id}"
            f"&from={date_start.isoformat()}Z"
            f"&to={date_end.isoformat()}Z"
            f"&granularity=day"
            f"&datasource=indexes"
        )

        try:
            response = self.session.get(
                url,
                cookies={"token": self.token},
                verify=False,
                timeout=30,
            )

            if response.status_code != 200:
                raise ProviderError(
                    f"Enercal consumption failed: HTTP {response.status_code} - {response.text[:300]}"
                )

            data = response.json()
            return data["sitesData"][0]["series"]

        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"Enercal consumption API error: {exc}") from exc

    def _build_history(self, series: list) -> list:
        history = []

        for entry in series:
            base = entry.get("data", {}).get("BASE")
            date_from = entry.get("range", {}).get("from")

            if base is None or not date_from:
                continue

            kwh = round(float(base) / 1000, 2)

            dt_utc = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
            dt_local = dt_utc.astimezone(ZoneInfo("Pacific/Noumea"))

            history.append({
                "date": dt_local.date().isoformat(),
                "value": kwh,
            })

        return history

    def _build_state(self, history: list) -> ResourceState:
        values = [item["value"] for item in history]

        conso_jour = values[-1]
        conso_mois = round(sum(values), 2)
        releve_date = history[-1]["date"]

        metadata = ResourceMetadata(
            provider="enercal",
            collector=self.collector,
            resource="power",
            location=self.location,
            unit="kWh",
            currency="XPF",
            device_class="energy",
            icon="mdi:flash",
            last_sync=ResourceState.now_iso(),
            last_reading=releve_date,
        )

        return ResourceState(
            metadata=metadata,
            measurements={
                "conso_jour": conso_jour,
                "conso_mois": conso_mois,
                "total": conso_jour,
            },
            history=history,
        )

    def _simulation_state(self) -> ResourceState:
        history = [
            {"date": "2026-05-22", "value": 4.99},
            {"date": "2026-05-23", "value": 4.46},
            {"date": "2026-05-24", "value": 3.67},
        ]

        return self._build_state(history)
